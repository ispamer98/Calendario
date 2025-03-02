# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register
from Calendario.utils.api import check_existing_user

def register_form() -> rx.Component:
    """Componente del formulario de registro con dos columnas."""
    return rx.container(
        rx.vstack(
            rx.center(
                rx.heading(
                    "Registra tu Usuario",
                    size="6",
                    as_="h2",
                    text_align="center",
                    width="100%",
                ),
                width="100%",
            ),
            rx.hstack(
                rx.vstack(
                    rx.vstack(
                        rx.text("Usuario", size="3", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("user")),
                            placeholder="Usuario",
                            name="user",
                            type="text",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            autofocus=True,
                            value=RegisterState.username,
                            on_change=[RegisterState.set_username,],
                            border_color=rx.cond(
                                RegisterState.errors["username"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["username"] != "",
                            rx.text(
                                RegisterState.errors["username"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="4", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            placeholder="Contraseña",
                            name="pasw",
                            type=rx.cond(RegisterState.show_pasw, "text", "password"),
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=RegisterState.password,
                            on_change=RegisterState.set_password,
                            border_color=rx.cond(
                                RegisterState.errors["password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["password"] != "",
                            rx.text(
                                RegisterState.errors["password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        show_pasw_switch_register(),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            placeholder="Confirmar Contraseña",
                            name="confirm_pasw",
                            type="password",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=RegisterState.confirm_password,
                            on_change=RegisterState.set_confirm_password,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_password"] != "",
                            rx.text(
                                RegisterState.errors["confirm_password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.vstack(
                    rx.vstack(
                        rx.text("Correo electrónico", size="4", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("mail")),
                            placeholder="Correo electrónico",
                            name="email",
                            type="email",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=RegisterState.email,
                            on_change=RegisterState.set_email,
                            border_color=rx.cond(
                                RegisterState.errors["email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["email"] != "",
                            rx.text(
                                RegisterState.errors["email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        rx.input(
                            rx.input.slot(rx.icon("mail")),
                            placeholder="Confirmar Correo electrónico",
                            name="confirm_email",
                            type="email",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=RegisterState.confirm_email,
                            on_change=RegisterState.set_confirm_email,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_email"] != "",
                            rx.text(
                                RegisterState.errors["confirm_email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.center(
                            rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.center(
                                rx.input(
                                    id="birthday",
                                    type="date",
                                    size="3",
                                    width="100%",
                                    justify="center",
                                    required=True,
                                    value=RegisterState.birthday,
                                    on_change=RegisterState.set_birthday,
                                    border=rx.cond(
                                        RegisterState.errors["birthday"] != "",
                                        "1px solid #EF4444",
                                        "1px solid #666666"
                                    ),
                                    border_radius="8px",
                                    _hover={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        )
                                    },
                                    _focus={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        ),
                                        "box_shadow": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "0 0 0 1px #EF4444",
                                            "0 0 0 1px #3182CE"
                                        )
                                    }
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("rotate-ccw"),
                                on_click=rx.set_value("birthday",""),
                                background="transparent",
                                size="1",
                                margin_top="8px",
                                _hover={
                                    "transform": "scale(1.2)",
                                    "transition": "transform 0.2s ease",
                                    "cursor": "pointer"
                                },
                            ),
                        ),
                                
                        
                        rx.cond(
                            RegisterState.errors["birthday"] != "",
                            rx.text(
                                RegisterState.errors["birthday"],
                                size="2",
                                text_align="center",
                                width="100%",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="50%",
                        align="center",
                        margin_left="20%"
                    ),
                    spacing="6",
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.button(
                        "Registrarse",
                        size="3",
                        width="50%",
                        justify="center",
                        on_click=RegisterState.register
                    ),
                    rx.hstack(
                        rx.text("¿Ya estás registrado?", size="3"),
                        rx.link(
                            "Inicia Sesión",
                            on_click=Login_state.login,
                            size="3",
                        ),
                        spacing="2",
                        justify="center",
                        opacity="0.8",
                    ),
                    spacing="6",
                    width="100%",
                    align="center",
                ),
                width="100%",
            ),
            spacing="6",
            width="100%",
        ),
        max_width="60em",
        padding="2em",
        padding_top="4em",
        on_mount=[RegisterState.set_password(""),
                  RegisterState.set_confirm_password(""),
                  RegisterState.reset_errors()]
    )