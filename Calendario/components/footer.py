from typing import Callable
import reflex as rx

def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        rx.box(
            page(),
            width="100%",
            flex="1",  # Hace que el contenido principal crezca y empuje el footer hacia abajo
            display="flex",
            justify_content="center",
            align_items="center",
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Calendario", size="6"),
                        rx.text("Organiza tus comidas de manera eficiente"),
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.link("Inicio", href="/"),
                        rx.link("Sobre Nosotros", href="/about"),
                        rx.link("Contacto", href="/contact"),
                        spacing="8",
                    ),
                    width="100%",
                ),
                rx.divider(),
                rx.text(
                    "© 2024 Calendario. Todos los derechos reservados.",
                    color="gray.500",
                    size="3",
                ),
                width="100%",
                spacing="8",
                py="8",
            ),
            width="100%",
            bg="gray.900",
            color="white",
            padding="2em",
        ),
        width="100%",
        spacing="0",
        height="100vh",  # El vstack ocupa todo el alto de la ventana
        align_items="stretch",
        style={"display": "flex", "flexDirection": "column"},  # Layout columna flex
    )