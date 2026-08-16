# Calendario/components/footer.py

import reflex as rx
from typing import Callable
from datetime import datetime

from Calendario import theme

#Enlaces del pie: (etiqueta, ruta)
FOOTER_LINKS = [
    ("Inicio", "/"),
    ("Calendario", "/calendar"),
    ("Menú semanal", "/menu_semanal"),
    ("Comidas", "/meal_list"),
    ("Lista de compra", "/shopping_list"),
]


def _link(label: str, href: str) -> rx.Component:
    return rx.link(
        label,
        href=href,
        size="2",
        color=theme.MUTED,
        underline="none",
        _hover={"color": theme.TEXT},
        transition="color 0.15s ease",
    )


#Componente principal, pasamos la página como parámetro
def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        #Contenido principal, página y ajustes de formato.
        #`flex: 1` + `min-height` empuja el pie hasta abajo en páginas cortas
        #(login, registro) sin recortar las largas, como la portada — antes el
        #`height="100vh"` del contenedor cortaba cualquier página larga.
        rx.box(
            page(),
            width="100%",
            flex="1",
            display="flex",
            justify_content="center",
            align_items="center",
            min_height="80vh",
            position="relative",
        ),
        rx.box(  #Contenedor para el pie de página
            rx.vstack(
                rx.flex(
                    rx.vstack(
                        rx.heading(  #Cabecera
                            "CalendPy",
                            size=rx.breakpoints(initial="5", md="6"),
                            class_name="brand-gradient-text",
                        ),
                        rx.text(
                            #Texto secundario
                            "Planifica tus comidas y tu compra",
                            size="2",
                            color=theme.MUTED,
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.vstack(
                        #Contenedor para enlaces rápidos
                        rx.text(
                            "ENLACES RÁPIDOS",
                            size="1",
                            weight="bold",
                            color=theme.DIM,
                            letter_spacing="0.12em",
                        ),
                        rx.flex(
                            *[_link(label, href) for label, href in FOOTER_LINKS],
                            wrap="wrap",
                            direction=rx.breakpoints(initial="column", md="row"),
                            gap="14px",
                        ),
                        align_items=rx.breakpoints(initial="start", md="end"),
                        spacing="2",
                    ),
                    width="100%",
                    gap="24px",
                    wrap="wrap",
                    align="start",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.center(  #Texto de copyright centrado
                    rx.text(
                        f"© {datetime.now().year} CalendPy · Hecho en casa, para casa.",
                        color=theme.DIM,
                        size="1",
                    ),
                    width="100%",
                ),
                spacing="4",
                padding_y="4",
                width="100%",
                max_width="1100px",
                margin="0 auto",
            ),
            #Estilo del fondo del footer
            background=f"linear-gradient(180deg, {theme.BG_SIDEBAR} 0%, {theme.BG_APP} 100%)",
            border_top=f"1px solid {theme.BORDER}",
            width="100%",
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            padding_y="1.5em",
        ),
        #Ajustes de tamaño del footer
        width="100%",
        min_height="100vh",
        spacing="0",
        background=theme.BG_APP,
    )
