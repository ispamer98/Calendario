# Calendario/pages/security.py
import reflex as rx

from Calendario.state.user_state import UserState

@rx.page(
    route="/security",
    title="Seguridad | Calendario",
    on_load=[UserState.on_load,UserState.check_autenticated],
)
def security() -> rx.Component:
    from Calendario.components.sidebar import sidebar
    return rx.hstack(
        sidebar(),
        rx.container(
            rx.heading("Seguridad de la Cuenta", size="2", margin_bottom="1em"),
            rx.form(
                rx.vstack(
                    rx.text("Contraseña actual", size="2"),
                    rx.input(
                        type="password",
                        name="current_password",
                        placeholder="●●●●●●",
                        on_change=UserState.set_current_password,
                        required=True,
                    ),
                    rx.text("Nueva contraseña", size="2", margin_top="1em"),
                    rx.input(
                        type="password",
                        name="new_password",
                        placeholder="●●●●●●",
                        on_change=UserState.set_new_password,
                        required=True,
                    ),
                    rx.text("Confirmar nueva contraseña", size="2", margin_top="1em"),
                    rx.input(
                        type="password",
                        name="confirm_password",
                        placeholder="●●●●●●",
                        on_change=UserState.set_confirm_password,
                        required=True,
                    ),
                    rx.button(
                        "Cambiar contraseña",
                        on_click=UserState.change_password,
                        color_scheme="blue",
                        margin_top="1.5em",
                    ),
                ),
                width="100%",
                spacing="1.5",
            ),
            padding="2em",
            flex="1",
        ),
        height="100vh",
    )
