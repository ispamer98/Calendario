# Calendario/pages/registro.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

@footer
def register() -> rx.Component:
    return rx.container(
        register_form(),
    )