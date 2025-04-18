# Calendario/pages/index.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.user_state import UserState

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

@rx.page(route="/", title="Calendario", on_load=UserState.on_load)
@footer
def index() -> rx.Component:
    return rx.cond(
        UserState.current_user,
        redirect_to_calendar(),
        rx.container(
            rx.vstack(
                rx.image("/favicon.ico",width="300px", height="220px"),
                rx.heading(
                    "¡Bienvenido a Calendario!",
                    size=rx.breakpoints(initial="7", md="8", lg="9"),
                    text_align="center",
                    background_image="linear-gradient(45deg, #4F46E5, #3B82F6)",
                    background_clip="text",
                    padding_bottom="0.5em"
                ),
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
                rx.box(
                    rx.mobile_only(
                        rx.vstack(
                            rx.link(
                                rx.button(
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
                                href="/login",
                            ),
                            rx.link(
                                rx.button(
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
                                href="/register",
                            ),
                            spacing="3",
                            width="100%",
                            align="center"
                        )
                    ),
                    rx.tablet_and_desktop(
                        rx.hstack(
                            rx.link(
                                rx.button(
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
                                href="/login"
                            ),
                            rx.link(
                                rx.button(
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
                                href="/register"
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
