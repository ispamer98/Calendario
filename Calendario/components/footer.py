# Calendario/components/footer.py
from typing import Callable
import reflex as rx

def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        # Contenedor principal que mantiene el centrado
        rx.box(
            page(),
            min_height="100vh",  # Asegura que ocupe al menos toda la altura de la ventana
            width="100%",
            display="flex",
            justify_content="center",
            align_items="center",
        ),
        
        # Footer
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
    )