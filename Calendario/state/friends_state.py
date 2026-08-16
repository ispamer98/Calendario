# Calendario/state/friends_state.py
"""
Amigos: solicitudes, lista y preferencia de avisos.

Un amigo no es un adorno: es con quien compartes calendarios, recetario y lista
de la compra, y con quien puedes hablar por el chat de la app (eso vive en
`chat_state.py`). Aquí está el trámite: buscar a alguien, pedirle amistad,
aceptar, quitar y decidir si quieres que te avisen de los cambios en lo
compartido.
"""

import asyncio
import logging
from typing import Dict, List
from urllib.parse import quote

import reflex as rx

from Calendario.state.notification_state import NotificationState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    get_friendships,
    get_notify_preference,
    remove_friendship,
    respond_friend_request,
    send_friend_request,
    set_notify_preference,
)

logger = logging.getLogger(__name__)


class FriendsState(rx.State):
    friends: List[Dict] = []
    incoming: List[Dict] = []
    outgoing: List[Dict] = []

    new_friend: str = ""
    error: str = ""
    loading: bool = False

    #Diálogo de "añadir amigo": la página es el chat, esto es el trámite
    show_add: bool = False

    #Preferencia propia: recibir avisos de cambios en calendarios compartidos
    notify_changes: bool = True

    @rx.event
    async def load(self):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        data = await get_friendships(user_state.current_user.id)
        self.friends = [self._con_inicial(f) for f in data["friends"]]
        self.incoming = [self._con_inicial(f) for f in data["incoming"]]
        self.outgoing = [self._con_inicial(f) for f in data["outgoing"]]
        self.notify_changes = await get_notify_preference(user_state.current_user.id)

    @staticmethod
    def _con_inicial(fila: dict) -> dict:
        """Añade la inicial del avatar, ya calculada.

        Tiene que salir de aquí y no del navegador: estas filas son diccionarios
        sin tipar, así que sacar la inicial en el componente obligaba a un
        `.to_string()`, y eso en Reflex es un `JSON.stringify`. El nombre
        llegaba entrecomillado y la "inicial" acababa siendo la comilla en vez
        de la primera letra. El chat ya lo hacía así (`chat_state.py`).
        """
        nombre = str(fila.get("username") or "").strip()
        return {**fila, "initial": nombre[:1].upper()}

    @rx.var
    def friend_count(self) -> int:
        return len(self.friends)

    @rx.var
    def incoming_count(self) -> int:
        return len(self.incoming)

    @rx.var
    def outgoing_count(self) -> int:
        return len(self.outgoing)

    @rx.var
    def has_nothing(self) -> bool:
        return not (self.friends or self.incoming or self.outgoing)

    @rx.event
    def set_new_friend(self, value: str):
        self.new_friend = value
        self.error = ""

    @rx.event
    def open_add(self):
        self.new_friend = ""
        self.error = ""
        self.show_add = True

    @rx.event
    def close_add(self):
        self.show_add = False
        self.new_friend = ""
        self.error = ""

    @rx.event
    async def send_request(self):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        username = self.new_friend.strip()
        if not username:
            self.error = "Escribe un nombre de usuario"
            return

        self.loading = True
        try:
            ok, msg = await send_friend_request(user_state.current_user.id, username)
            if not ok:
                self.error = msg
                return
            self.new_friend = ""
            self.error = ""
            self.show_add = False
            await self.load()
            #Avisamos al destinatario, si tiene dispositivos vinculados. En un
            #hilo aparte: `webpush` es HTTP síncrono y bloquearía la respuesta
            await asyncio.to_thread(
                NotificationState.enviar_notificacion,
                titulo="👋 Nueva solicitud de amistad",
                mensaje=f"{user_state.current_user.username} quiere ser tu amigo en CalendPy",
                destino=username,
                url="/amigos",
                tag="amistad",
            )
            return rx.toast.success(msg, position="top-center")
        finally:
            self.loading = False

    @rx.event
    async def respond(self, friendship_id: int, accept: bool, username: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if not await respond_friend_request(friendship_id, user_state.current_user.id, accept):
            return rx.toast.error("No se pudo procesar la solicitud", position="top-center")
        await self.load()
        if accept:
            await asyncio.to_thread(
                NotificationState.enviar_notificacion,
                titulo="🤝 Solicitud aceptada",
                mensaje=f"{user_state.current_user.username} y tú ya sois amigos: escríbele",
                destino=username,
                url=f"/amigos?con={quote(user_state.current_user.username)}",
                tag="amistad",
            )
            return rx.toast.success(f"Ahora sois amigos, {username} y tú", position="top-center")
        return rx.toast.info("Solicitud rechazada", position="top-center")

    @rx.event
    async def remove(self, friendship_id: int):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if not await remove_friendship(friendship_id, user_state.current_user.id):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        await self.load()
        return rx.toast.success("Amistad eliminada", position="top-center")

    # ------------------------------------------------------------------
    # Preferencias
    # ------------------------------------------------------------------
    #Los avisos sueltos a un amigo ya no viven aquí: ahora cada aviso es un
    #mensaje del chat (`ChatState.send`), que además queda escrito y se puede
    #contestar. El push es solo el mensajero.

    @rx.event
    async def toggle_notify_changes(self, value: bool):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        self.notify_changes = value
        if not await set_notify_preference(user_state.current_user.id, value):
            return rx.toast.error(
                "No se pudo guardar. ¿Está aplicada la migración 011_friends.sql?",
                position="top-center",
            )
        return rx.toast.success(
            "Te avisaremos de los cambios" if value else "No te avisaremos de los cambios",
            position="top-center",
        )
