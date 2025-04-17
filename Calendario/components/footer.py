import reflex as rx
from typing import Callable

def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        rx.box(
            page(),
            width="100%",
            flex="1",
            display="flex",
            justify_content="center",
            align_items="center",
            min_height="calc(100vh - 200px)",
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "Calendario",
                            size=rx.breakpoints(initial="5", md="6"),
                            background_image="linear-gradient(45deg, #4F46E5, #3B82F6)",
                            background_clip="text",
                        ),
                        rx.text(
                            "Organiza tus comidas",
                            size=rx.breakpoints(initial="2", md="3"),
                            color="gray.400",
                        ),
                        align_items="start",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text(
                            "Enlaces rápidos",
                            size=rx.breakpoints(initial="3", md="4"),
                            weight="bold",
                            color="gray.300"
                        ),
                        rx.mobile_only(
                            rx.vstack(
                                rx.link("Inicio", href="/", color="gray.400"),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400"),
                                rx.link("Contacto", href="/contact", color="gray.400"),
                                spacing="2",
                            )
                        ),
                        rx.tablet_and_desktop(
                            rx.hstack(
                                rx.link("Inicio", href="/", color="gray.400", _hover={"color": "white"}),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400", _hover={"color": "white"}),
                                rx.link("Contacto", href="/contact", color="gray.400", _hover={"color": "white"}),
                                spacing="4",
                            )
                        ),
                        align_items="end",
                        justify="end",
                        spacing="3",
                        margin_left="auto",  # <- Esto lo alinea a la derecha siempre
                    ),
                    spacing="8",
                    width="100%",
                ),
                rx.divider(margin_y="4", color="gray.700"),
                rx.center(
                    rx.text(
                        "© 2024/25 Calendario. Todos los derechos reservados.",
                        color="gray.500",
                        size=rx.breakpoints(initial="1", md="2"),
                    ),
                    margin_bottom="1em",
                    width="100%",
                ),
                spacing="6",
                padding_y="4",
                width="100%",
                margin_top="2em"
            ),
            background="linear-gradient(180deg, #1a1a1a 0%, #000000 100%)",
            width="100%",
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            box_shadow="0 -4px 20px rgba(0, 0, 0, 0.3)",
        ),
        width="100%",
        height="100vh",
        spacing="0",
        style={"display": "flex", "flexDirection": "column"},
    )