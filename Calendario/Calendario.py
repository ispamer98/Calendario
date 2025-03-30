"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState

import reflex as rx



app = rx.App(
        theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        accent_color="blue",
        ),
        
)
app.add_page(login, 
            route="/login",
            title="Iniciar Sesión | Calendario",
            on_load=[Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    
                    ]
                ),
app.add_page(register,
            route="/register",
            title="Registro | Calendario",
            on_load=[RegisterState.load_page,
                    Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),])