# Calendario/components/login_form.py

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_login

def login_form() -> rx.Component:
    """Componente del formulario de inicio de sesión."""
    return rx.center(  # Centra horizontalmente
        rx.container(
            rx.vstack(
                rx.center(
                    rx.image(
                        width="2.5em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading(
                        "Accede a tu usuario",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                rx.vstack(
                    rx.text(
                        "Nombre de usuario",
                        size="3",
                        weight="medium",
                        text_align="left",
                        width="100%",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("user")),
                        placeholder="Usuario",
                        name="user",
                        type="text",
                        size="3",
                        width="100%",
                        required=True,
                        autofocus=True,
                        value=rx.cond(UserState.username, UserState.username, ""),
                        on_change=UserState.set_username,
                        on_key_down=UserState.press_enter,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "Contraseña",
                            size="3",
                            weight="medium",
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("lock")),
                        name="password",
                        placeholder="Contraseña",
                        type=rx.cond(Login_state.show_pasw, "text", "password"),
                        size="3",
                        width="100%",
                        required=True,
                        value=UserState.password,
                        on_change=UserState.set_password,
                        on_key_down=UserState.press_enter,
                    ),
                    show_pasw_switch_login(),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Iniciar Sesión",
                    on_click=[UserState.login],
                    size="3",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿No tienes cuenta?", size="3"),
                            rx.link(
                                "Registrate",
                                on_click=Login_state.register,
                                size="3",
                            ),
                        ),
                        rx.link(
                            "¿Has olvidado la contraseña?",
                            href="/recovery_pasw",
                            size="3",
                        ),
                    ),
                    opacity="0.8",
                    spacing="2",
                    direction="row",
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            max_width="28em",
            padding="2em",  # Puedes añadir algo de padding para más consistencia visual
        ),
        width="100%",  # Asegura que el centro ocupa el ancho completo
        padding_top="4em",  # Añade este padding para dar espacio arriba
    )
