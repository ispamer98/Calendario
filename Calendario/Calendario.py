"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.calendar import calendar
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState

import reflex as rx



app = rx.App()
app.add_page(index, on_load=[Login_state.swith_off,
                             RegisterState.swith_off,
                             UserState.set_password(""),
                             RegisterState.set_password(""),
                             RegisterState.set_confirm_password(""),
                             ]
                )