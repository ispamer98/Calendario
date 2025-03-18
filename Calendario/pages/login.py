# Calendario/pages/login.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.login_form import login_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

@rx.page(route="/login")
@footer
def login() -> rx.Component:
    return login_form()