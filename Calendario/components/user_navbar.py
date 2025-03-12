#user_navbar.py

import reflex as rx
from Calendario.state.user_state import UserState

def user_navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # Logo/Texto con efecto gradiente
            rx.heading(
                "DevNav",
                background_image="linear-gradient(45deg, #4F46E5, #EC4899)",
                background_clip="text",
                font_weight="800",
                font_size="1.5em",
                _hover={
                    "transform": "scale(1.05)",
                    "transition": "transform 0.3s ease",
                }
            ),
            
            # Links de navegación con animación
            rx.hstack(
                rx.link(
                    "Proyectos",
                    href="#projects",
                    color="gray.700",
                    _hover={
                        "text_decoration": "none",
                        "transform": "translateY(-2px)",
                    },
                    transition="all 0.5s ease",
                ),
                rx.link(
                    "Blog",
                    href="#blog",
                    color="gray.700",
                    _hover={
                        "text_decoration": "none",
                        "transform": "translateY(-2px)",
                    },
                    transition="all 0.3s ease",
                ),
                rx.link(
                    "Contacto",
                    href="#contact",
                    color="gray.700",
                    _hover={
                        "text_decoration": "none",
                        "transform": "translateY(-2px)",
                    },
                    transition="all 0.3s ease",
                ),
                spacing="2",
                padding_right="2em",
            ),
            
            justify="between",
            align="center",
            width="100%",
            padding_x="2em",
            padding_y="1em",
        ),
        
        # Estilos generales
        position="fixed",
        top="0",
        width="100%",
        z_index="1000",
        backdrop_filter="blur(10px)",
        border_bottom="1px solid #eee",
        box_shadow="sm",
        transition="all 0.3s ease",
    )