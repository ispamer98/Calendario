# Calendario/pages/login.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.login_form import login_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

@rx.page(route="/login",on_load=UserState.on_load)
@footer
def login() -> rx.Component:
    return rx.cond(UserState.current_user,
                   redirect_to_calendar(),
                   login_form()
                   )
