# Calendario/components/footer.py

import reflex as rx
from typing import Callable

#Componente principal, pasamos la página como parámetro
def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        #Contenido principal, página y ajustes de formato
        rx.box(
            page(), 
            width="100%", 
            flex="1", 
            display="flex", #
            justify_content="center", 
            align_items="center", 
            min_height="79vh",  
            position="relative", 
        ),
        rx.box( #Contenedor para el pie de página
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading( #Cabecera
                            "CalendPy",
                            size=rx.breakpoints(initial="5", md="6"), 
                                #Estilos para el texto de cabecera, degradado
                                style={
                                "background": "linear-gradient(45deg, #3b4c6b, #5a6e8d, #7a8f9e, #9baeb0, #b9c8d1, #d0d9e2)", #Gradiente para las letras
                                "-webkit-background-clip": "text", 
                                "background-clip": "text",
                                "-webkit-text-fill-color": "transparent",
                                "color": "transparent",
                            },
                        ),
                        rx.text(
                            #Texto secundario
                            "Organiza tus comidas",
                            size=rx.breakpoints(initial="2", md="3"),
                            color="gray.400",
                        ),
                        align_items="start",
                        spacing="2",
                    ),
                    rx.vstack(
                        #Contenedor para enlaces rápidos
                        rx.text(
                            "Enlaces rápidos",
                            size=rx.breakpoints(initial="3", md="4"),
                            weight="bold",
                            color="gray.300"
                        ),
                        rx.mobile_only(
                            #Versión movil (vertical)
                            rx.vstack(
                                rx.link("Inicio", href="/", color="gray.400"),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400"),
                                rx.link("Contacto", href="/contact", color="gray.400"),
                                spacing="2",
                            )
                        ),
                        rx.tablet_and_desktop(
                            #Versión tablet/escritorio (horizontal)
                            rx.hstack(
                                rx.link("Inicio", href="/", color="gray.400", _hover={"color": "white"}),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400", _hover={"color": "white"}),
                                rx.link("Contacto", href="/contact", color="gray.400", _hover={"color": "white"}),
                                spacing="4",
                            )
                        ),
                        #Ajustes de los componentes
                        align_items="end",
                        justify="end",
                        spacing="3",
                        margin_left="auto",  
                    ),
                    spacing="8",
                    width="100%",
                ),
                rx.divider(margin_y="4", color="gray.700"), # separador visual
                rx.center( #Texto de copyright centrado
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
            #Estilo del fondo del footer
            background="linear-gradient(180deg, #1a1a1a 0%, #000000 100%)",
            width="100%",
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            box_shadow="0 -4px 20px rgba(0, 0, 0, 0.3)",
        ),
        #Ajustes de tamaño del footer
        width="100%",
        height=rx.breakpoints(initial="auto", md="100vh"),
        spacing="0",

    )