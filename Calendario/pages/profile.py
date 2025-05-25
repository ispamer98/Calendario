# Calendario/pages/profile.py
import reflex as rx

from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

@rx.page(
        
    route="/profile",
    title="Perfil | CalendPy",
    on_load=[UserState.on_load, UserState.check_autenticated],
)
def profile() -> rx.Component:
    from Calendario.components.sidebar import sidebar


    return rx.hstack(
        user_navbar(),
        sidebar(),
        rx.container(
            rx.heading("Perfil de Usuario", size="2", margin_bottom="1em"),
            rx.text(
                f"Usuario: {UserState.current_user.username}",
                size="2",
                color="gray.200",
            ),
            # Aquí puedes añadir más campos o formularios para editar el perfil
            padding="2em",
            flex="1",
        ),
        height="100vh",
    )
