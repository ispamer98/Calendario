import os
import json
import reflex as rx
from pywebpush import webpush, WebPushException
from dotenv import load_dotenv

load_dotenv()

VAPID_PRIVATE = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:admin@calendpy.noxuscmmd.uk")

class NotificationState(rx.State):
    status_message: str = ""

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
            nombre_usuario = user_state.current_user.username if user_state.current_user else None

            if not nombre_usuario:
                self.status_message = "No hay usuario autenticado"
                return rx.window_alert("Debes iniciar sesión para suscribirte a notificaciones.")

            archivo = "suscriptores.json"
            subs = []
            if os.path.exists(archivo):
                with open(archivo, "r") as f:
                    try:
                        subs = json.load(f)
                    except json.JSONDecodeError:
                        subs = []

            # Verificar si este endpoint ya existe
            endpoint_existente = None
            for s in subs:
                if s.get("endpoint") == sub_dict.get("endpoint"):
                    endpoint_existente = s
                    break

            if endpoint_existente:
                # Si ya existe, actualizar alias por si cambió
                if endpoint_existente.get("alias") != alias:
                    endpoint_existente["alias"] = alias
                    with open(archivo, "w") as f:
                        json.dump(subs, f, indent=4)
                    self.status_message = f"Alias actualizado a '{alias}'"
                    return rx.window_alert(f"✅ Dispositivo actualizado con alias '{alias}'")
                else:
                    self.status_message = "Este dispositivo ya está vinculado"
                    return rx.window_alert("Este dispositivo ya está suscrito a notificaciones.")

            # Nuevo dispositivo
            sub_dict["nombre_usuario"] = nombre_usuario
            sub_dict["alias"] = alias
            subs.append(sub_dict)
            with open(archivo, "w") as f:
                json.dump(subs, f, indent=4)

            self.status_message = f"Suscripción exitosa como '{nombre_usuario}' con alias '{alias}'"
            return rx.window_alert(f"✅ Te has suscrito correctamente. Dispositivo: '{alias}'")

        except Exception as e:
            print(f"Error guardando suscripción: {e}")
            self.status_message = "Error interno"
            return rx.window_alert("Ocurrió un error inesperado al guardar la suscripción.")

    @staticmethod
    def enviar_notificacion(titulo: str, mensaje: str, destino: str = "todos"):
        archivo = "suscriptores.json"
        if not os.path.exists(archivo):
            print("No hay suscriptores registrados")
            return

        try:
            with open(archivo, "r") as f:
                subs = json.load(f)

            payload = json.dumps({
                "title": titulo,
                "body": mensaje,
                "icon": "/favicon.ico",
                "badge": "/favicon.ico"
            })

            for sub in subs:
                if destino != "todos" and sub.get("nombre_usuario") != destino:
                    continue

                try:
                    webpush(
                        subscription_info=sub,
                        data=payload,
                        vapid_private_key=VAPID_PRIVATE,
                        vapid_claims={"sub": VAPID_EMAIL},
                        timeout=10
                    )
                    print(f"✅ Notificación enviada a {sub.get('nombre_usuario')} (alias: {sub.get('alias')})")
                except WebPushException as ex:
                    print(f"❌ Error enviando a {sub.get('nombre_usuario')}: {ex}")
                except Exception as e:
                    print(f"⚠️ Error inesperado: {e}")

        except Exception as e:
            print(f"Error general en el sistema de envío: {e}")