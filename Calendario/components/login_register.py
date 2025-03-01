#login_register.py

# Calendario/components/login_card.py

import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.components.login_form import login_form
from Calendario.components.register_form import register_form

def login_card() -> rx.Component:
    """Componente que maneja el cambio entre login y registro."""
    return rx.cond(
        Login_state.mode == "login",
        login_form(),  # Muestra el formulario de inicio de sesión
        register_form(),  # Muestra el formulario de registro
    )