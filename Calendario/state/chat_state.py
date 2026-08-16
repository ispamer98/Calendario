# Calendario/state/chat_state.py
"""
Chat entre amigos.

Los avisos sueltos al móvil estaban bien para "compra pan", pero se perdían: no
quedaba conversación, no sabías si lo había leído y no se podía contestar. Aquí
cada aviso es un mensaje que queda escrito, con su hora y su doble check, y el
push es solo el mensajero.

El sondeo (`poll_loop`) es lo que hace que parezca tiempo real sin montar
websockets propios: mientras la pestaña de amigos está abierta se relee la
conversación cada pocos segundos y solo se reasigna el estado si algo ha
cambiado de verdad, para no repintar la pantalla mientras escribes.
"""

import asyncio
import logging
from typing import Dict, List, TypedDict
from urllib.parse import quote

import reflex as rx

from Calendario.state.notification_state import NotificationState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    get_chat_overview,
    get_conversation,
    get_friendships,
    get_unread_count,
    mark_messages_read,
    send_message,
)

logger = logging.getLogger(__name__)

#Cada cuánto se relee la conversación abierta
POLL_SECONDS = 3
#Cada cuántos sondeos se refresca además la lista de conversaciones
OVERVIEW_EVERY = 3
#Cada cuánto se actualiza la chincheta de "sin leer" desde cualquier página
BADGE_SECONDS = 30

#Mensajes de un toque, para no tener que escribir siempre lo mismo
QUICK_MESSAGES = [
    "👋 ¿Hablamos?",
    "🛒 Acuérdate de la compra",
    "🍽️ La cena está lista",
    "📅 Mira el menú de la semana",
    "⏰ Voy de camino",
]

#Baja el scroll del todo en las dos copias del panel (la de escritorio y la
#pantalla completa del móvil). El `setTimeout` es para que el navegador haya
#pintado ya los mensajes nuevos cuando se calcula el alto.
SCROLL_SCRIPT = """
setTimeout(function () {
    ['chat-scroll-desk', 'chat-scroll-mob'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.scrollTop = el.scrollHeight;
    });
}, 60);
"""


#Los tipos van declarados (y no `dict` a secas) porque Reflex necesita saber
#qué hay dentro para poder pintarlo en un `rx.foreach`: sin esto, `m["read"]`
#es un valor de tipo desconocido y la plantilla no compila.
class ChatMessage(TypedDict):
    id: int
    mine: bool          # lo he escrito yo
    body: str
    time_label: str     # "18:42"
    day_label: str      # "Hoy", "Ayer", "3 mar"
    show_day: bool      # primer mensaje del día: lleva separador
    read: bool          # el destinatario ya lo ha visto


class Conversation(TypedDict):
    user_id: int
    username: str
    friendship_id: int
    initial: str        # la inicial del avatar
    preview: str        # último mensaje, recortado
    empty: bool         # nunca os habéis escrito
    time_label: str
    day_label: str
    last_id: int        # id del último mensaje, para ordenar
    unread: int


class ChatState(rx.State):
    #Lista de la izquierda: un amigo por fila, con su último mensaje
    conversations: List[Conversation] = []
    #Sin leer en total (la chincheta de la barra de navegación)
    unread_total: int = 0

    #Conversación abierta
    active_id: int = 0
    active_name: str = ""
    messages: List[ChatMessage] = []

    sending: bool = False
    loading: bool = False
    #False mientras falte la tabla `messages` (migración 016 sin aplicar)
    chat_ready: bool = True

    #Turno de cada sondeo: evita que se solapen dos si se recarga la página
    _poll_gen: int = 0
    _badge_gen: int = 0

    # ------------------------------------------------------------------
    # Vars derivadas
    # ------------------------------------------------------------------
    @rx.var
    def chat_open(self) -> bool:
        return self.active_id > 0

    @rx.var
    def has_unread(self) -> bool:
        return self.unread_total > 0

    @rx.var
    def unread_label(self) -> str:
        #Más de 99 sin leer no cabe en la chincheta (ni hace falta el número)
        return "99+" if self.unread_total > 99 else str(self.unread_total)

    @rx.var
    def has_conversations(self) -> bool:
        return len(self.conversations) > 0

    @rx.var
    def quick_messages(self) -> List[str]:
        return QUICK_MESSAGES

    @rx.var
    def active_initial(self) -> str:
        return self.active_name[:1].upper()

    @rx.var
    def empty_conversation(self) -> bool:
        return self.chat_open and len(self.messages) == 0

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    async def _user_id(self) -> int:
        user_state = await self.get_state(UserState)
        return user_state.current_user.id if user_state.current_user else 0

    def _build_conversations(self, amigos: List[Dict], overview: dict) -> List[Conversation]:
        """Une la lista de amigos con el último mensaje de cada uno.

        Un amigo con el que no has hablado nunca también sale: la lista de
        chats es la lista de amigos, no hace falta "empezar conversación".
        """
        ultimos = overview.get("last", {})
        sin_leer = overview.get("unread", {})
        filas = []
        for amigo in amigos:
            otro = amigo["user_id"]
            ultimo = ultimos.get(otro) or ultimos.get(str(otro)) or {}
            cuerpo = ultimo.get("body", "")
            if cuerpo and ultimo.get("mine"):
                cuerpo = f"Tú: {cuerpo}"
            filas.append({
                "user_id": otro,
                "username": amigo["username"],
                "friendship_id": amigo["id"],
                "initial": amigo["username"][:1].upper(),
                "preview": cuerpo[:70] if cuerpo else "Dile algo",
                "empty": not cuerpo,
                "time_label": ultimo.get("time_label", ""),
                "day_label": ultimo.get("day_label", ""),
                "last_id": ultimo.get("id", 0),
                "unread": sin_leer.get(otro, sin_leer.get(str(otro), 0)),
            })
        #Primero con quien has hablado hace menos; los mudos, por orden alfabético
        filas.sort(key=lambda f: (-f["last_id"], f["username"].lower()))
        return filas

    @rx.event
    async def load(self):
        """Carga la pestaña y, si venimos de una notificación, abre el chat."""
        user_id = await self._user_id()
        if not user_id:
            return rx.redirect("/")
        self.loading = True
        try:
            amigos = (await get_friendships(user_id))["friends"]
            overview = await get_chat_overview(user_id)
            self.conversations = self._build_conversations(amigos, overview)
            self.unread_total = overview.get("total", 0)
            self.chat_ready = overview.get("available", True)
        finally:
            self.loading = False

        #Enlace directo desde el aviso del móvil: /amigos?con=usuario
        destino = self.router.url.query_parameters.get("con", "")
        if destino:
            for fila in self.conversations:
                if fila["username"] == destino:
                    return ChatState.open_chat(fila["user_id"], fila["username"])
        return None

    @rx.event
    async def refresh_conversations(self):
        user_id = await self._user_id()
        if not user_id:
            return
        amigos = (await get_friendships(user_id))["friends"]
        overview = await get_chat_overview(user_id)
        self.conversations = self._build_conversations(amigos, overview)
        self.unread_total = overview.get("total", 0)
        self.chat_ready = overview.get("available", True)

    @rx.event
    async def refresh_badge(self):
        """Solo el número de sin leer: se pide desde cualquier página."""
        user_id = await self._user_id()
        if not user_id:
            self.unread_total = 0
            return
        self.unread_total = await get_unread_count(user_id)

    # ------------------------------------------------------------------
    # Conversación
    # ------------------------------------------------------------------
    @rx.event
    async def open_chat(self, other_id: int, username: str):
        user_id = await self._user_id()
        if not user_id:
            return rx.redirect("/")
        self.active_id = other_id
        self.active_name = username
        self.messages = await get_conversation(user_id, other_id)
        await self._mark_read(user_id, other_id)
        return rx.call_script(SCROLL_SCRIPT)

    async def _mark_read(self, user_id: int, other_id: int):
        """Marca como leído lo que me ha escrito y baja los contadores.

        Mira dos sitios porque llegan por caminos distintos: el contador de la
        lista (lo que había al abrir) y los mensajes en pantalla (lo que ha
        entrado con la conversación abierta, antes de que la lista se refresque).
        """
        pendientes = next(
            (c["unread"] for c in self.conversations if c["user_id"] == other_id), 0
        )
        mirando = self.active_id == other_id
        en_pantalla = mirando and any(not m["mine"] and not m["read"] for m in self.messages)
        if not pendientes and not en_pantalla:
            return
        await mark_messages_read(user_id, other_id)
        if mirando:
            self.messages = [m if m["mine"] else {**m, "read": True} for m in self.messages]
        self.conversations = [
            {**c, "unread": 0} if c["user_id"] == other_id else c
            for c in self.conversations
        ]
        self.unread_total = max(0, self.unread_total - pendientes)

    @rx.event
    def close_chat(self):
        self.active_id = 0
        self.active_name = ""
        self.messages = []

    @rx.event
    async def send(self, form_data: dict):
        """Envía lo escrito en el compositor (`rx.form`)."""
        async for evento in self._send(form_data.get("body", "")):
            yield evento

    @rx.event
    async def send_quick(self, texto: str):
        """Envía uno de los mensajes de un toque."""
        async for evento in self._send(texto):
            yield evento

    async def _send(self, texto: str):
        user_id = await self._user_id()
        if not user_id:
            yield rx.redirect("/")
            return
        cuerpo = (texto or "").strip()
        if not cuerpo:
            return
        if not self.active_id:
            yield rx.toast.error("Abre una conversación primero", position="top-center")
            return

        destinatario_id, destinatario = self.active_id, self.active_name
        self.sending = True
        #El `yield` pelado manda el estado al navegador ya: sin él, el botón no
        #se pondría a girar hasta que terminase todo el envío (que es cuando ya
        #no hace falta)
        yield
        try:
            ok, error, avisar = await send_message(user_id, destinatario_id, cuerpo)
        finally:
            self.sending = False
        if not ok:
            yield rx.toast.error(error, position="top-center")
            return

        self.messages = await get_conversation(user_id, destinatario_id)
        yield rx.call_script(SCROLL_SCRIPT)
        await self.refresh_conversations()

        if not avisar:
            #Ya tiene un aviso mío sin leer en el móvil: no se le manda otro
            return
        user_state = await self.get_state(UserState)
        remitente = user_state.current_user.username if user_state.current_user else "Un amigo"
        #En un hilo aparte: `webpush` es HTTP síncrono contra cada dispositivo y
        #dejaría el chat congelado mientras tanto
        await asyncio.to_thread(
            NotificationState.enviar_notificacion,
            titulo=f"💬 {remitente}",
            mensaje=cuerpo[:120],
            destino=destinatario,
            #Un mensaje escrito a mano llega aunque tengas silenciados los
            #avisos automáticos de calendario: te lo manda una persona
            respetar_preferencia=False,
            #Al tocar el aviso se abre justo esta conversación
            url=f"/amigos?con={quote(remitente)}",
            tag=f"chat-{remitente}",
        )

    # ------------------------------------------------------------------
    # Sondeo
    # ------------------------------------------------------------------
    @rx.event(background=True)
    async def poll_loop(self):
        """Mantiene viva la conversación mientras estás en la pestaña.

        Para no acabar con dos sondeos a la vez se usa un contador en vez de un
        "estoy sondeando" de sí/no: cada arranque coge número y el bucle se
        retira en cuanto ve que hay otro más nuevo. Un `bool` se queda
        encasquillado si el proceso muere a media vuelta (el estado se guarda en
        disco) y entonces el sondeo no vuelve a arrancar nunca.
        """
        async with self:
            self._poll_gen += 1
            mi_turno = self._poll_gen
        try:
            vuelta = 0
            while True:
                await asyncio.sleep(POLL_SECONDS)
                #El scroll se manda **fuera** del `async with`: soltar el hilo
                #con el estado bloqueado es la forma de quedarse colgado
                bajar_scroll = False
                async with self:
                    #Si el usuario se ha ido de la pestaña —o ha arrancado un
                    #sondeo más nuevo—, el bucle se apaga solo
                    if self.router.url.path != "/amigos" or self._poll_gen != mi_turno:
                        return
                    vuelta += 1
                    user_id = await self._user_id()
                    if not user_id:
                        continue
                    try:
                        if self.active_id:
                            frescos = await get_conversation(user_id, self.active_id)
                            if frescos != self.messages:
                                #Solo bajamos el scroll si hay mensaje nuevo; si
                                #solo han cambiado los checks de leído, no
                                bajar_scroll = len(frescos) > len(self.messages)
                                self.messages = frescos
                                await self._mark_read(user_id, self.active_id)
                        if vuelta % OVERVIEW_EVERY == 0:
                            await self.refresh_conversations()
                    except Exception as e:
                        logger.warning(f"Sondeo del chat fallido: {e}")
                if bajar_scroll:
                    yield rx.call_script(SCROLL_SCRIPT)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning(f"Sondeo del chat detenido: {e}")

    @rx.event(background=True)
    async def badge_loop(self):
        """Sondeo ligero de la chincheta, desde cualquier página de la app.

        Arranca al montarse el armazón (`app_shell`), así que basta con estar
        dentro de la app para enterarte de que tienes mensajes sin leer. Mismo
        truco del contador que en `poll_loop` para no duplicar sondeos.
        """
        async with self:
            self._badge_gen += 1
            mi_turno = self._badge_gen
        while True:
            async with self:
                if self._badge_gen != mi_turno:
                    return
                #En la pestaña de amigos manda el sondeo de arriba, que ya trae
                #el contador junto con la lista: aquí no hace falta pedirlo
                if self.router.url.path != "/amigos":
                    try:
                        await self.refresh_badge()
                    except Exception as e:
                        logger.warning(f"Sondeo de mensajes sin leer fallido: {e}")
            await asyncio.sleep(BADGE_SECONDS)
