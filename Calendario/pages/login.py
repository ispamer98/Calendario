# Calendario/pages/login.py
import reflex as rx
from Calendario.components.login_form import login_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

@rx.page(route="/login", title="Iniciar Sesión | Calendario")
def login() -> rx.Component:
    return rx.container(
        login_form(),
        center_content=True,
        max_width="100vw",
        height="100vh"
    )