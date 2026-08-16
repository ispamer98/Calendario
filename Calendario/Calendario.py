import logging
import os

# Nivel WARNING para librerías de terceros (alembic, httpx, supabase, ...),
# INFO explícito solo para el código propio de la app.
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("Calendario").setLevel(os.environ.get("LOG_LEVEL", "INFO"))

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.pages.forgot_pasword import forgot_password
from Calendario.pages.reset_pasword import reset_password
from Calendario.pages.profile import profile
from Calendario.pages.security import security
from Calendario.pages.meal_list import meal_list
from Calendario.pages.menu_semanal import menu_semanal
from Calendario.pages.shopping_list import shopping_list
from Calendario.pages.pantry import pantry
from Calendario.pages.friends import friends
from Calendario.pages.not_found import not_found
import reflex as rx

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
        #La versión fuerza al navegador a descargar la hoja otra vez: sin esto
        #los móviles seguían usando el CSS viejo (y con él, el zoom al escribir)
        rx.el.link(rel="stylesheet", href="/css/styles.css?v=7"),
        # Reflex emite su propio <meta viewport> después de estos componentes,
        # así que no vale con declarar otro: se ajusta cuando el documento ya
        # está montado. `viewport-fit=cover` es lo que hace que
        # env(safe-area-inset-*) valga algo en iPhone — sin él, la barra de
        # navegación inferior no sabe cuánto tiene que subir.
        rx.el.script(
            "document.addEventListener('DOMContentLoaded', function () {"
            "  var v = document.querySelector('meta[name=viewport]');"
            "  if (v) v.setAttribute('content',"
            "    'width=device-width, initial-scale=1, viewport-fit=cover');"
            "});"
        ),
    ]
)

#Aviso de "toca comer, ¿descontamos de la despensa?" a la hora que cada uno
#tenga puesta. Va como tarea de ciclo de vida (no como bucle de una página)
#porque tiene que sonar aunque nadie tenga la web abierta.
from Calendario.utils.reminders import meal_reminder_loop

app.register_lifespan_task(meal_reminder_loop)
