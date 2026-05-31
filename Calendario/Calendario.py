from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.pages.forgot_pasword import forgot_password
from Calendario.pages.reset_pasword import reset_password
from Calendario.pages.profile import profile
from Calendario.pages.security import security
from Calendario.pages.meal_list import meal_list
from Calendario.pages.shopping_list import shopping_list
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

 
    ]
)
