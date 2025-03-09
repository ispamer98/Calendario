#current_user_button.py

import reflex as rx

from Calendario.state.user_state import UserState

def current_user_button() -> rx.Component:
    return rx.button(

        rx.text(f"{UserState.current_user.username}"),
        on_click=UserState.logout
    )
