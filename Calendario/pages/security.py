# Calendario/pages/security.py
import reflex as rx

from Calendario.components.show_pasw_switch import show_pasw_switch_security
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

@rx.page(
    route="/security",
    title="Seguridad | CalendPy",
    on_load=[UserState.on_load, UserState.check_autenticated, UserState.reset_switch, UserState.reset_security],
)
def security() -> rx.Component:
    from Calendario.components.sidebar import sidebar
    return rx.hstack(
        user_navbar(),
        rx.center(  # Centra el formulario horizontalmente
            rx.container(
                rx.heading("Seguridad de la Cuenta", size="5", margin_bottom="1em",margin_top="3em"),
                rx.separator(),
                rx.form(
                    rx.vstack(
                        rx.text("Contraseña actual", size="4", weight="medium" , margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type="password",
                            name="current_password",
                            placeholder="Contraseña actual",
                            value=UserState.current_password,
                            on_change=UserState.set_current_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
                            required=True,
                        ),
                        rx.text("Nueva contraseña", size="4", weight="medium", margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type=rx.cond(UserState.show_new_pasw, "text", "password"),
                            name="new_password",
                            placeholder="Nueva contraseña",
                            value=UserState.new_password,
                            on_change=UserState.set_new_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
                            required=True,
                        ),
                        show_pasw_switch_security(),
                        rx.text("Confirmar nueva contraseña", size="4", weight="medium", margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type="password",
                            name="confirm_password",
                            placeholder="Confirmar nueva contraseña",
                            value=UserState.confirm_password,
                            on_change=UserState.set_confirm_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
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
                width="100%",
                max_width="500px",  # Ancho razonable
                padding="2em",
            ),
            width="100%",
        )
    )
