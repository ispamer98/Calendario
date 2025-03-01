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
            on_change=RegisterState.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )

def initialize_index():
    RegisterState.password=""
    RegisterState.confirm_password=""
    UserState.password=""
    Login_state.swith_off()
    RegisterState.swith_off()


