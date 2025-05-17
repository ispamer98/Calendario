# Calendario/components/sidebar.py
import reflex as rx
from Calendario.state.user_state import UserState

def sidebar() -> rx.Component:
    """Menú lateral con pestañas Perfil, Seguridad y Cerrar Sesión."""
    def nav_item(label: str, route: str, key: str) -> rx.Component:
        # ÚNICAMENTE rx.text va como child posicional
        return rx.link(
            rx.text(
                label,
                size="3",
                weight="medium",
                color=rx.cond(UserState.active_tab == key, "white", "gray.400"),
                _hover={"color": "white"},
            ),  # <- atención a la coma
            href=route,
            on_click=UserState.set_active_tab(key),
            padding_y="1em",
            padding_x="1.5em",
            background=rx.cond(UserState.active_tab == key, "blue.600", None),
            border_radius="md",
        )

    return rx.box(
        rx.vstack(
            rx.heading("Mi Cuenta", size="4", color="white", margin_bottom="2em"),
            nav_item("Perfil", "/profile", "profile"),
            nav_item("Seguridad", "/security", "security"),
            rx.button(
                "Cerrar Sesión",
                on_click=UserState.logout,
                variant="ghost",
                justify_content="start",
                padding_y="1em",
                padding_x="1.5em",
                color="gray.400",
                _hover={"color": "white", "background": "rgba(255,255,255,0.1)"},
            ),
            spacing="1",
            width="220px",
            height="100vh",
            background="gray.800",
            padding_top="2em",
        )
    )
