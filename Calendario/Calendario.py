"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.calendar import calendar
from Calendario.components.show_pasw_switch import initialize_index
import reflex as rx



app = rx.App()
app.add_page(index, on_load=initialize_index())
