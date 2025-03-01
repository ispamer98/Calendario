import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
def show_pasw_switch_login() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )

def show_pasw_switch_register() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=RegisterState.swith_on,  # Cambia el estado del switch
            is_checked=RegisterState.show_pasw,  # Estado actual del switch
            color_scheme="jade",
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )


