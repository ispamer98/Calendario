# Calendario/components/show_pasw_switch.py

import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState

#Botón de mostrar contraseña en login
def show_pasw_switch_login() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on, #Cambia el estado del switch
            is_checked=RegisterState.show_pasw,  #Estado actual del switch
            color_scheme="blue" 
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )
#Botón de mostrar contraseña en registro
def show_pasw_switch_register() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=RegisterState.swith_on,  #Cambia el estado del switch
            is_checked=RegisterState.show_pasw,  #Estado actual del switch
            color_scheme="blue",
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )
#Botón de mostrar contraseña en seguridad de la cuenta
def show_pasw_switch_security() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=UserState.swith_on, #Cambia el estado del switch
            is_checked=UserState.show_new_pasw, #Estado actual del switch
            color_scheme="blue"  
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )