from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.pages.forgot_pasword import forgot_password
from Calendario.pages.reset_pasword import reset_password
from Calendario.pages.profile import profile
from Calendario.pages.security import security
from Calendario.pages.meal_list import meal_list
import reflex as rx
import base64
import json
from Calendario.utils.send_not import VAPID_PUBLIC_KEY, add_subscription, send_notification

# --- Reflex App ---
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=False,
        radius="large",
        accent_color="blue",
        height="100vh"
    ),
    head_components=[
        rx.el.link(rel="manifest", href="/manifest.json"),

        # Registrar service worker
        rx.script("""
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/service-worker.js')
                .then(() => console.log("Service Worker registrado"))
                .catch(console.error);
            }
        """),

        # Suscribirse a push
        rx.script(f"""
            if ('PushManager' in window) {{
                navigator.serviceWorker.ready.then(registration => {{
                    registration.pushManager.subscribe({{
                        userVisibleOnly: true,
                        applicationServerKey: new Uint8Array(
                            atob('{base64.b64encode(base64.urlsafe_b64decode(VAPID_PUBLIC_KEY + "==")).decode("utf-8")}')
                            .split('').map(c => c.charCodeAt(0))
                        )
                    }}).then(sub => {{
                        fetch('/subscribe', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify(sub)
                        }}).catch(console.error);
                    }});
                }});
            }}
        """)
    ]
)

# --- Endpoint Reflex para recibir suscripciones ---
@app.api.post("/subscribe")
async def subscribe(subscription: dict):
    add_subscription(subscription)
    return {"success": True}

# --- Función de prueba para enviar notificación ---
@app.api.get("/notify_test")
def notify_test(message: str):
    send_notification(message)
    return {"sent": True}

# --- Arrancar Reflex ---
if __name__ == "__main__":
    app.run()
