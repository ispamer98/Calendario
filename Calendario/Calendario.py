"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar


import reflex as rx



app = rx.App(
        theme=rx.theme(
        appearance="dark",
        has_background=False,
        radius="large",
        accent_color="blue",
        height="100vh"
        ),
        
)
