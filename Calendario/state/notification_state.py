import os
import json
import logging
import reflex as rx
from typing import List
from pywebpush import webpush, WebPushException
from dotenv import load_dotenv
from Calendario.utils.api import (
    SUPABASE_API,
    save_push_subscription,
    get_my_push_subscriptions,
    delete_push_subscription,
)

load_dotenv()

VAPID_PRIVATE = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:admin@calendpy.noxuscmmd.uk")

logger = logging.getLogger(__name__)


class NotificationState(rx.State):
    status_message: str = ""
    #Dispositivos del usuario autenticado, para la gestión en el perfil
    my_devices: List[dict] = []

    #Avisos de "toca comer, ¿descontamos de la despensa?" y a qué hora. Van
    #aparte de los avisos de calendario porque son otra cosa: estos te piden
    #hacer algo (restar el stock), no te cuentan lo que ha hecho otro.
    meal_stock_enabled: bool = True
    meal_time: str = "15:00"
    dinner_time: str = "23:00"

    @rx.event
    async def load_meal_settings(self):
        from Calendario.state.user_state import UserState
        from Calendario.utils.api import get_meal_notify_settings

        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        ajustes = await get_meal_notify_settings(user_state.current_user.id)
        self.meal_stock_enabled = bool(ajustes.get("notify_meal_stock", True))
        self.meal_time = ajustes.get("meal_notify_time", "15:00")
        self.dinner_time = ajustes.get("dinner_notify_time", "23:00")

    async def _save_meal_settings(self) -> bool:
        from Calendario.state.user_state import UserState
        from Calendario.utils.api import set_meal_notify_settings

        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return False
        return await set_meal_notify_settings(
            user_state.current_user.id, self.meal_stock_enabled, self.meal_time, self.dinner_time,
        )

    @rx.event
    async def toggle_meal_stock(self, value: bool):
        anterior = self.meal_stock_enabled
        self.meal_stock_enabled = value
        if not await self._save_meal_settings():
            self.meal_stock_enabled = anterior
            return rx.toast.error(
                "No se pudo guardar. ¿Falta la migración 019_meal_stock.sql?", position="top-center"
            )
        if value:
            return rx.toast.success(
                f"Te avisaremos a las {self.meal_time} y a las {self.dinner_time}",
                position="top-center",
            )
        return rx.toast.info("Avisos de despensa desactivados", position="top-center")

    @rx.event
    async def set_meal_time(self, value: str):
        """Hora del aviso de la comida. Vacío = se deja la que había."""
        if not value:
            return
        self.meal_time = value[:5]
        if not await self._save_meal_settings():
            return rx.toast.error("No se pudo guardar la hora", position="top-center")
        return rx.toast.success(f"Aviso de la comida a las {self.meal_time}", position="top-center")

    @rx.event
    async def set_dinner_time(self, value: str):
        if not value:
            return
        self.dinner_time = value[:5]
        if not await self._save_meal_settings():
            return rx.toast.error("No se pudo guardar la hora", position="top-center")
        return rx.toast.success(f"Aviso de la cena a las {self.dinner_time}", position="top-center")

    @rx.event
    async def guardar_subscripcion(self, js_result: str):
        if js_result == "USER_CANCEL":
            self.status_message = "Registro cancelado"
            return rx.window_alert("Has cancelado la suscripción.")

        if not js_result or "ERROR" in js_result or js_result == "PERMISO_DENEGADO":
            self.status_message = f"Error: {js_result}"
            return rx.window_alert(f"No se pudo completar la suscripción: {js_result}")

        try:
            data = json.loads(js_result)
            sub_dict = data.get("subscription")
            alias = data.get("alias", "").strip()

            if not sub_dict:
                raise ValueError("No se recibió la suscripción")

            if not alias:
                self.status_message = "Alias inválido"
                return rx.window_alert("Debes proporcionar un alias para el dispositivo.")

            from Calendario.state.user_state import UserState
            user_state = await self.get_state(UserState)

            if not user_state.current_user:
                self.status_message = "No hay usuario autenticado"
                return rx.window_alert("Debes iniciar sesión para suscribirte a notificaciones.")

            keys = sub_dict.get("keys", {})
            success = await save_push_subscription(
                user_id=user_state.current_user.id,
                endpoint=sub_dict.get("endpoint", ""),
                p256dh=keys.get("p256dh", ""),
                auth=keys.get("auth", ""),
                alias=alias,
            )

            if not success:
                self.status_message = "Error interno"
                return rx.window_alert("Ocurrió un error inesperado al guardar la suscripción.")

            self.status_message = f"Suscripción exitosa como '{user_state.current_user.username}' con alias '{alias}'"
            #Sin esto, cambiar el nombre del dispositivo no se veía hasta recargar
            await self.load_my_devices()
            return rx.toast.success(f"Dispositivo guardado como '{alias}'", position="top-center")

        except Exception as e:
            logger.error(f"Error guardando suscripción: {e}")
            self.status_message = "Error interno"
            return rx.window_alert("Ocurrió un error inesperado al guardar la suscripción.")

    #Carga los dispositivos suscritos del usuario autenticado (para /profile)
    @rx.event
    async def load_my_devices(self):
        from Calendario.state.user_state import UserState
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            self.my_devices = []
            return
        self.my_devices = await get_my_push_subscriptions(user_state.current_user.id)

    #Elimina un dispositivo de la lista de suscripciones del usuario autenticado
    @rx.event
    async def delete_device(self, subscription_id: int):
        from Calendario.state.user_state import UserState
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        success = await delete_push_subscription(subscription_id, user_state.current_user.id)
        if success:
            await self.load_my_devices()
            return rx.toast.success("Dispositivo eliminado", position="top-center")
        return rx.toast.error("No se pudo eliminar el dispositivo", position="top-center")

    @staticmethod
    def enviar_aviso_despensa(
        titulo: str, mensaje: str, destino: str, url: str = "/despensa", tag: str = "",
    ) -> int:
        """Avisos de comidas y despensa: los gobierna su propio ajuste del perfil.

        Van aparte de los avisos de calendario a propósito: son otra cosa (te
        recuerdan descontar lo que cocinas) y hay quien querrá unos sí y otros
        no. Si el destinatario los tiene apagados, aquí no se manda nada.

        Devuelve cuántas suscripciones recibieron el aviso de verdad (no
        cuántas se intentaron), para que quien llama sepa si de verdad llegó.
        """
        try:
            user = SUPABASE_API.get_user_by_username(destino)
            if not user:
                return 0
            ajustes = SUPABASE_API.get_meal_notify_settings(user["id"])
            if not ajustes.get("notify_meal_stock", True):
                return 0
            return NotificationState.enviar_notificacion(
                titulo=titulo,
                mensaje=mensaje,
                destino=destino,
                #El interruptor que manda es el suyo, no el de los cambios de
                #calendario: si no, apagar aquello apagaría también esto
                respetar_preferencia=False,
                url=url,
                tag=tag,
            )
        except Exception as e:
            logger.warning(f"No se pudo enviar el aviso de despensa a {destino}: {e}")
            return 0

    @staticmethod
    def enviar_notificacion(
        titulo: str, mensaje: str, destino: str = "todos", respetar_preferencia: bool = True,
        url: str = "/", tag: str = "",
    ) -> int:
        """Envía un aviso push.

        `respetar_preferencia=False` para los mensajes que un amigo escribe a
        propósito: esos llegan aunque el destinatario haya desactivado los
        avisos automáticos de cambios de calendario.

        `url` es a dónde lleva el aviso al tocarlo (el service worker la lee):
        un mensaje de chat abre la conversación, no la portada. `tag` agrupa:
        dos avisos con la misma etiqueta se sustituyen en la bandeja del móvil
        en vez de apilarse, que es lo que se quiere con un mismo remitente.

        Devuelve cuántas suscripciones lo recibieron de verdad: reclamar el
        envío en la base de datos no es lo mismo que el aviso llegando al
        navegador, y quien llama necesita distinguirlo.
        """
        entregados = 0
        try:
            if destino == "todos":
                subs = SUPABASE_API.get_all_push_subscriptions()
            else:
                subs = SUPABASE_API.get_push_subscriptions_for_username(destino, respetar_preferencia)

            if not subs:
                logger.warning("No hay suscriptores registrados para este destino")
                return 0

            payload = json.dumps({
                "title": titulo,
                "body": mensaje,
                "icon": "/favicon.ico",
                "badge": "/favicon.ico",
                "url": url,
                "tag": tag,
            })

            for sub in subs:
                subscription_info = {
                    "endpoint": sub["endpoint"],
                    "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
                }
                try:
                    webpush(
                        subscription_info=subscription_info,
                        data=payload,
                        vapid_private_key=VAPID_PRIVATE,
                        vapid_claims={"sub": VAPID_EMAIL},
                        timeout=10
                    )
                    logger.info(f"✅ Notificación enviada (alias: {sub.get('alias')})")
                    entregados += 1
                except WebPushException as ex:
                    logger.error(f"❌ Error enviando a suscripción {sub.get('id')}: {ex}")
                    #410/404: el proveedor confirma que ya no hay nadie al otro
                    #lado (caducó o se desuscribió). Retenerla solo consigue que
                    #vuelva a fallar, en silencio, en cada aviso futuro.
                    status = getattr(ex.response, "status_code", None)
                    if status in (404, 410) and sub.get("id"):
                        if SUPABASE_API.delete_dead_push_subscription(sub["id"]):
                            logger.info(
                                f"🗑️ Suscripción {sub['id']} (alias: {sub.get('alias')}) "
                                f"eliminada por estar caducada ({status})"
                            )
                except Exception as e:
                    logger.warning(f"⚠️ Error inesperado: {e}")

        except Exception as e:
            logger.error(f"Error general en el sistema de envío: {e}")
        return entregados
