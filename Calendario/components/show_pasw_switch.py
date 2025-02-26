import reflex as rx
from Calendario.state.login_state import Login_state


def show_pasw_switch() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )
