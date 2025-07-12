# Calendario/components/login_form.py

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_login

def login_form() -> rx.Component:
    #Formulario de inicio de sesión
    return rx.center( 
        rx.container(
            rx.box(
                #Formato para movil
                rx.mobile_only(
                    rx.button( #Botón de atrás
                        rx.icon("arrow-left", size=18),
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
                    )
                ),
                #Formato para tablet/escritorio
                rx.tablet_and_desktop(
                    rx.button( #Botón de atrás
                        rx.icon("arrow-left", size=18),
                        "Inicio",
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
                    )
                ),
                z_index="1000"
            ),
            rx.vstack( #Estilo del formulario de login
                rx.center(
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
                        type=rx.cond(Login_state.show_pasw, "text", "password"), #Alterla el tipo de texto
                        size="3",
                        width="100%",
                        required=True,
                        value=UserState.password,
                        on_change=UserState.set_password,
                        on_key_down=UserState.press_enter,
                    ),
                    show_pasw_switch_login(), #Componente para visualizar la contraseña
                    spacing="2",
                    width="100%",
                ),
                rx.button( #Botón de login
                    rx.icon("user-check",size=18),
                    "Iniciar Sesión",
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    on_click=UserState.login, #Función que realiza el login
                    width="100%",

                ),
                rx.center(
                    rx.vstack(
                        rx.hstack( #Redirige al registro de usuario
                            rx.text("¿No tienes cuenta?", size="3"),
                            rx.link(
                                "Registrate",
                                on_click=rx.redirect("/register"),
                                size="3",
                            ),
                        ),
                        rx.link( #Redirige al formulario de recuperación de contraseña
                            "¿Has olvidado la contraseña?",
                            href="/forgot_password",
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
            padding="2em",  
        ),
        width="100%",  
        padding_top="4em",

    )