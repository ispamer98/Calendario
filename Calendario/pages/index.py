# Calendario/pages/index.py (nueva versión)
import reflex as rx
@rx.page(route="/", title="Calendario")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("¡Bienvenido a Calendario!", size="9"),
            rx.text("Organiza tus comidas de manera eficiente", size="6"),
            rx.hstack(
                rx.link(
                    rx.button("Iniciar Sesión", size="4"),
                    href="/login"
                ),
                rx.link(
                    rx.button("Registrarse", size="4", variant="soft"),
                    href="/register"
                ),
                spacing="4",
                margin_top="2em"
            ),
            align="center",
            height="100%"
        ),
        padding="2em",
        max_width="1200px",
        center_content=True
    )