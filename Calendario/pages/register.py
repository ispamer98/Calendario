# Calendario/pages/register.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state

#Función que redirige a la página de calendario
def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

#Página de registro de usuario
@rx.page( #Decorador indicando componente de página
            route="/register",
            title="Registro | CalendPy",
            on_load=[ #Funciones al cargar la página
                    RegisterState.load_page,
                    Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    RegisterState.reset_errors,
                    UserState.on_load])
@footer
def register() -> rx.Component:
    return rx.cond( #Si existe usuario loggeado
        UserState.current_user,
        redirect_to_calendar(), #Redirige a calendario
        rx.container(
            register_form(), #De no ser así, lanza el formulario de registro
        )
    )