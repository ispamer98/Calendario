# Calendario/pages/login.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.login_form import login_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state

#Función que redirige a la pagina de calendario
def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

#Página de login
@rx.page( #Decorador que indica componente de página
            route="/login",
            title="Iniciar Sesión | CalendPy",
            on_load=[Login_state.swith_off, #Funciones al cargar la página
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    UserState.on_load])
@footer #Insertamos el pie de página
def login() -> rx.Component: 
    return rx.cond(UserState.current_user, #Si existe usuario loggeado
                   redirect_to_calendar(), #Redirige a calendario
                   login_form() #En caso contrario lanza el formulario de loggin
                   )
