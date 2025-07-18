# Calendario/pages/profile.py

import reflex as rx
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

#Controlador de rotación del icono
class IconState(rx.State):
    rotating: bool = False
    @rx.event
    def start_rotate(self):
        self.rotating = True



#Página de información del usuario
@rx.page( #Decorador indicando complemento de página
    route="/profile",
    title="Perfil | CalendPy",
    on_load=[ #Funciones al cargar la página
        UserState.on_load, 
        UserState.check_autenticated,
        IconState.start_rotate
        ]
    
)
def profile() -> rx.Component: 
    return rx.vstack( #Componente principal
        user_navbar(),
        rx.center(
            rx.card( #Tarjeta con la información
                rx.vstack(
                    rx.text(
                        rx.icon( #Icono visual de usuario
                            "circle-user",
                            size=50,
                            color="#3182CE",
                            style={
                                "transition": "transform 2s cubic-bezier(0.4, 0.2, 0.2, 1)",
                                "transform": rx.cond(IconState.rotating, "rotateY(360deg)", "none"), 
                            },
                            margin_bottom="1em",
                        ),
                        on_mount=IconState.start_rotate,  #Inicia la rotación al montar el componente
                        margin_bottom="1em",
                    ),
                    #Cabecera
                    rx.heading("Perfil de Usuario", size="5", margin_bottom="0.5em",color="#7E9AAF"),
                    rx.text("Información personal", size="3", color="gray.400"),
                    rx.divider(margin_y="1em"),
                    rx.vstack(
                        rx.hstack( #Nombre de usuario
                            rx.hstack(
                                rx.icon("user", color="gray.500"),
                                rx.text("Nombre de usuario:", weight="medium", color="#7E9AAF"),
                            ),
                            rx.text(UserState.current_user.username, color="gray.200"),
                            spacing="2",
                            flex_direction=["column", "row"],

                        ),
                        rx.hstack( #Correo electrónico
                            rx.hstack(
                                rx.icon("mail", color="gray.500"),
                                rx.text("Correo electrónico:", weight="medium", color="#7E9AAF"),
                            ),
                            rx.text( #Muestra las dos primeras letras del correo y el dominio completo
                                f"{UserState.current_user.email[:2]}***@{UserState.current_user.email.split('@')[1]}",
                                color="gray.200"
                            ),
                            spacing="2",
                            flex_direction=["column", "row"],

                        ),
                        rx.hstack( #Fecha de registro
                            rx.hstack(
                                rx.icon("calendar", color="gray.500"),
                                rx.text("Registrado desde:", weight="medium", color="#7E9AAF"),
                            ),
                            rx.text(
                                rx.moment( #Formateo de fecha
                                    UserState.current_user.created_at,
                                    format="MMMM [de] YYYY",
                                    locale="es",
                                    style={"textTransform": "capitalize"}
                                ),
                                color="gray.200"
                            ),
                            spacing="2",
                            flex_direction=["column", "row"],

                        ),
                        spacing="3",
                    ),
                    spacing="4",
                ),
                width="100%",
                max_width="500px",
                padding="2em",
                shadow="lg",
                border_radius="lg",
                background_color=rx.color("gray", 2),
            ),
            width="100%",
            padding_y="3em",
            padding_x="1em",
        ),
        padding_top="3em",
        on_mount=IconState.start_rotate
    )
