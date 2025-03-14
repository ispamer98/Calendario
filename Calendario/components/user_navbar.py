from fastapi import background
import reflex as rx
from Calendario.state.user_state import UserState

def user_navbar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                # Logo/Texto con efecto gradiente
                rx.heading(
                    "CalendApp",
                    background_image="linear-gradient(45deg, #4F46E5, #EC4899)",
                    background_clip="text",
                    font_weight="800",
                    font_size="1.5em",
                    _hover={"transform": "scale(1.05)"},
                ),
                
                rx.spacer(),
                
                # Menú de usuario
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.hstack(
                                rx.cond(
                                    UserState.current_user,
                                    rx.avatar(fallback=UserState.current_user.username[0].upper()),
                                    rx.avatar(fallback="U")
                                ),
                                rx.cond(
                                    UserState.current_user,
                                    rx.text(UserState.current_user.username),
                                    rx.text("Usuario")
                                ),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center"
                            ),
                            variant="soft",
                            radius="full"
                        )
                    ),
                    rx.menu.content(
                        rx.menu.item("Perfil", rx.icon("user")),
                        rx.menu.item("Configuración", rx.icon("settings")), 
                        rx.menu.separator(),
                        rx.menu.item(
                            "Cerrar sesión",
                            rx.icon("log-out"), 
                            on_click=UserState.logout,
                            color="#EF4444"
                        ),
                        width="200px",
                    ),
                    modal=False
                ),
                justify="between",
                align="center", 
                width="100%",
                padding_y="1em",
                padding_x="2em",
                style={"box-sizing": "border-box"}
            ),
            width="100%",
            max_width="100vw",
            style={"overflow-x": "hidden"}
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="1000",
        border_bottom="1px solid #eee",
        box_shadow="md",
        border_radius="0 0 8px 8px",
        transition="all 0.3s ease",
        background="grey"
    )
