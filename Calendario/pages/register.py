# Calendario/pages/registro.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

@footer
@rx.page(route="/register",on_load=UserState.on_load)
def register() -> rx.Component:
    return rx.cond(
        UserState.current_user,
        redirect_to_calendar(),
        rx.container(
            register_form(),
        )
    )