from fastapi import background
import reflex as rx
from Calendario.components.calendar_creator import calendar_creator
from Calendario.state.user_state import UserState
from Calendario.state.calendar_state import CalendarState

def user_navbar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                
                # Logo/Texto con efecto gradiente
                rx.heading(
                    rx.hstack(
                        rx.image(
                            src="/favicon.ico",
                            width="30px",
                            height="20px"),
                        rx.text("CalendPy",
                                font_family="Sarina,cursive",
                                font_size="1.5em",),
                        
                    ),
                    background_image="linear-gradient(45deg, #4F46E5, #EC4899)",
                    background_clip="text",
                    font_weight="800",
                    font_size="1em",
                    user_select="none",
                    on_click=rx.redirect("/calendar"),
                    _hover={"transform": "scale(1.05)",
                            "cursor": "pointer"},
                ),
                rx.button(
                    "Ir a Calendario",
                    on_click=rx.redirect("/calendar"),
                    variant="outline",
                    color_scheme="jade",
                    size="1",
                    ml="1em",  # pequeño margen izquierdo
                ),
                
                rx.spacer(),
                calendar_creator(),
                # Menú de usuario
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.hstack(
                                rx.spacer(" "),
                                rx.icon("user"),
                                rx.cond(
                                    UserState.current_user,
                                    rx.text(UserState.current_user.username),
                                    rx.text("Usuario")
                                ),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",  # Color del texto en blanco
                                
                            ),
                            variant="ghost",
                            radius="full",
                            background="#23282b",
                            style={
                                "background": "transparent",
                                "color": "white",  # Color del texto en blanco
                                "border": "1px solid rgba(255, 255, 255, 0.3)",  # Borde gris claro semi-transparente
                                "_hover": {
                                    "background": "rgba(0, 0, 0, 0.2)",
                                    "cursor": "pointer",
                                    "transform": "scale(1.05)"
                                }
                            }
                        )
                    ),
                    rx.menu.content(
                        rx.menu.item("Crear Calendario",
                                     rx.icon("calendar-plus"),
                                     style={"_hover" : { "background " : "#23282b"}},
                                     on_click=CalendarState.open_calendar_creator()
                                     ),
                        rx.menu.item("Perfil", 
                                     rx.icon("user"),
                                     style={"_hover" : { "background " : "#23282b"}},
                                     on_click=rx.redirect("/profile")
                                     ),
                        rx.menu.item("Configuración",
                                      rx.icon("settings"),
                                      style={"_hover" : { "background " : "#23282b"}}
                                      ), 
                        rx.menu.separator(),
                        rx.menu.item(
                            "Cerrar sesión",
                            rx.icon("log-out"), 
                            on_click=UserState.logout,
                            color="#EF4444",
                            style={"_hover" : { "background " : "#23282b"}}
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
        border_bottom="1.5px solid #eee",
        border_radius="0 0 20px 20px",
        background="#1e1e1e"
    )
