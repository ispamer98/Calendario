# Calendario/pages/registro.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))


@rx.page(route="/register",
            title="Registro | CalendPy",
            on_load=[RegisterState.load_page,
                    Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    RegisterState.reset_errors,
                    UserState.on_load])
@footer
def register() -> rx.Component:
    return rx.cond(
        UserState.current_user,
        redirect_to_calendar(),
        rx.container(
            register_form(),
        )
    )