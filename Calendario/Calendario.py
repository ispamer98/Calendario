"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.pages.forgot_pasword import forgot_password
from Calendario.pages.reset_pasword import reset_password
from Calendario.pages.profile import profile


import reflex as rx



app = rx.App(
        theme=rx.theme(
        appearance="dark",
        has_background=False,
        radius="large",
        accent_color="blue",
        height="100vh",
        stylesheets=[
        "https://fonts.googleapis.com/css2?family=Sarina&display=swap",
        ],
        ),
        head_components=[rx.el.link(rel="manifest", href="/manifest.json")]
        
)
