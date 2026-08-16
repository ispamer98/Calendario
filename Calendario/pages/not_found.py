# Calendario/pages/not_found.py

import reflex as rx

#Página 404 personalizada, con la misma identidad visual que el resto de la app
@rx.page(
    route="404",
    title="Página no encontrada | CalendPy",
)
def not_found() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.image(src="/favicon.ico", width="140px", height="100px"),
            rx.heading(
                "404",
                size="9",
                class_name="brand-gradient-text",
                weight="bold",
            ),
            rx.heading(
                "Esta página se ha ido a hacer la compra...",
                size="5",
                text_align="center",
                color="var(--slate-11)",
            ),
            rx.text(
                "No hemos encontrado lo que buscabas. Puede que el enlace esté roto o la página ya no exista.",
                size="3",
                color="var(--slate-10)",
                text_align="center",
                max_width="380px",
            ),
            rx.link(
                rx.button(
                    rx.icon("house", size=18),
                    "Volver al inicio",
                    color_scheme="blue",
                    radius="full",
                    size="3",
                    variant="surface",
                    _hover={"transform": "scale(1.05)"},
                    margin_top="1em",
                ),
                href="/",
            ),
            spacing="4",
            align="center",
            padding="2em",
        ),
        width="100%",
        min_height="100vh",
    )
