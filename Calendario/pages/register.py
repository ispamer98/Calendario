# Calendario/pages/registro.py
import reflex as rx
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState

@rx.page(route="/register", title="Registro | Calendario")
def register() -> rx.Component:
    return rx.container(
        register_form(),
        center_content=True,
        max_width="100vw",
        height="100vh"
    )