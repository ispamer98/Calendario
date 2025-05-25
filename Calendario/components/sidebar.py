import reflex as rx
from Calendario.state.user_state import UserState

def sidebar() -> rx.Component:
    current_page = UserState.current_page

    base_button_props = {
        "variant": "ghost",
        "justify_content": "start",
        "padding_y": "1em",
        "padding_x": "1.5em",
        "width": "100%",
        "font_size": "lg",
        "border_radius": "md",
        "transition": "background-color 0.2s, color 0.2s",
        # OJO: Quitamos font_weight para evitar el error
    }

    return rx.box(
        rx.vstack(
            rx.heading("Mi Cuenta", size="4", color="white", margin_bottom="2em"),

            rx.button(
                "Perfil",
                on_click=UserState.go_profile_page,
                **base_button_props,
                color=rx.cond(current_page == "profile", "white", "gray.400"),
                background=rx.cond(current_page == "profile", "blue.600", "transparent"),
                font_weight=rx.cond(current_page == "profile", "bold", "medium"),
                _hover={
                    "color": "white",
                    "background": rx.cond(current_page == "profile", "blue.700", "blue.600"),
                },
            ),

            rx.button(
                "Seguridad",
                on_click=UserState.go_security_page,
                **base_button_props,
                color=rx.cond(current_page == "security", "white", "gray.400"),
                background=rx.cond(current_page == "security", "blue.600", "transparent"),
                font_weight=rx.cond(current_page == "security", "bold", "medium"),
                _hover={
                    "color": "white",
                    "background": rx.cond(current_page == "security", "blue.700", "blue.600"),
                },
            ),

            spacing="1",
            width="220px",
            height="100vh",
            background="gray.800",
            padding_top="2em",
        )
    )
