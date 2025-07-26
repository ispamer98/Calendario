# Calendario/pages/index.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.user_state import UserState

#Función que redirije a la página de calendario
def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

#Página indice/principal
@rx.page( #Decorador indicando página
        route="/",
        title="CalendPy",
        on_load=[UserState.on_load,]) #Comprobaciones al cargar página
@footer #Insertamos el pie de página
def index() -> rx.Component:
    return rx.cond( #Comprueba el estado de usuario, y si hay usuario, redirije directamente al calendario
        UserState.current_user,
        redirect_to_calendar(),
        rx.container( #Si no hay usuario, muestra la página de inicio
            rx.vstack( #Stack vertical que muestra icono y mensaje de bienvenida
                rx.image("/favicon.ico",width="300px", height="220px"),
                rx.heading(
                    rx.text(
                        "¡Bienvenido a ",
                        rx.text(
                            "CalendPy!",
                            as_="span",
                            style={
                                "background": "linear-gradient(45deg, #3b4c6b, #5a6e8d, #7a8f9e, #9baeb0, #b9c8d1, #d0d9e2)",
                                "-webkit-background-clip": "text",
                                "background-clip": "text",
                                "-webkit-text-fill-color": "transparent",
                                "color": "transparent",
                            },
                        ),
                        as_="span",
                    ),
                    size=rx.breakpoints(initial="7", md="8", lg="9"),
                    text_align="center",
                    padding_bottom="0.5em",
                ),

                #Info sobre el proyecto
                rx.text(
                    "Organiza tus comidas de manera eficiente ",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "Comparte calendarios con tus amigos " ,
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "Actualiza tu lista de la compra ",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "¡ Y mucho más !",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.box( #Botones de acción de inicio
                    rx.mobile_only( #Vista de movil
                        rx.vstack(
                            rx.link(
                                rx.button( #Botón para iniciar sesión
                                    rx.icon("user-check",size=18),
                                    "Iniciar Sesión",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    color_scheme="blue",
                                    radius="full",
                                    _hover={"transform": "scale(1.05)"},
                                    padding_x="3em",
                                    padding_y="1em",
                                    variant="surface"
                                ),
                                href="/login", #Regirije a la página de login
                            ),
                            rx.link(
                                rx.button( #Botón para registrar usuario
                                    rx.icon("user-plus",size=18),
                                    "Registrarse",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    variant="surface",
                                    color_scheme="blue",
                                    radius="full",
                                    padding_y="1em",
                                    padding_x="3em",
                                    _hover={"transform": "scale(1.05)"},

                                    
                                ),
                                href="/register", #Redirige a la página de registro
                            ),
                            spacing="3",
                            width="100%",
                            align="center"
                        )
                    ),
                    rx.tablet_and_desktop( #Vista de escritorio
                        rx.hstack(
                            rx.link(
                                rx.button( #Botón de inicio de sesión
                                    rx.icon("user-check",size=18),
                                    "Iniciar Sesión",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    color_scheme="blue",
                                    radius="full",
                                    _hover={"transform": "scale(1.05)"},
                                    padding_x="3em",
                                    padding_y="1em",
                                    variant="surface"
                                ),
                                href="/login" #Regirije a la página de login
                            ),
                            rx.link(
                                rx.button( #Botón para registrar usuario
                                    rx.icon("user-plus",size=18),
                                    "Registrarse",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    variant="surface",
                                    color_scheme="blue",
                                    radius="full",
                                    padding_y="1em",
                                    padding_x="3em",
                                    _hover={"transform": "scale(1.05)"},

                                ),
                                href="/register" #Redirige a la página de registro
                            ),
                            spacing="4",
                            margin_top="2em",
                            justify="center",
                        )
                    ),
                    width="100%",
                    margin_top="2em"
                ),
                align="center",
                spacing="4",
                width="100%"
            ),
            padding="2em",
            max_width="1200px",
            margin_top=rx.breakpoints(initial="0em", md="0em", lg="0px"),
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            center_content=True,
            width="100%",
            text_align="center"
        )
    )
