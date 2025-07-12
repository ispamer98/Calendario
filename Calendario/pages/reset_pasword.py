# Calendario/pages/reset_password.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.password_reset_state import PasswordResetState

#Página de reseteo de contraseña
@rx.page( #Decorador que indica componente de página
        route="/reset_password",
        title="Crear nueva contraseña | CalendPy",
        on_load=PasswordResetState.on_load) #Funciones al cargar la página

@footer #Insertamos el pie de página

def reset_password() -> rx.Component: 
    return rx.center( #Componente principal
        rx.container(
            
            rx.box( #Botón que redirige al inicio
                rx.mobile_only( #Vista en movil
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
                    )
                ),
                rx.tablet_and_desktop( #Vista de escritorio
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        "Inicio",
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
                    )
                ),
                z_index="1000",
            ),

            rx.vstack( #Contenedor para el cambio de contraseña
                rx.center(
                    rx.heading( #Cabecera
                        "Crear nueva contraseña",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),

                #Input para la nueva contraseña 
                rx.vstack(
                    rx.text(
                        "Nueva contraseña",
                        size="3",
                        weight="medium",
                        width="100%",
                        text_align="left",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("lock")),
                        placeholder="Nueva contraseña",
                        type="password",
                        size="3",
                        width="100%",
                        value=PasswordResetState.new_password, #Muestra el valor en el estado
                        on_change=PasswordResetState.set_new_password, #Al cambiar el valor, actualiza el estado
                    ),
                    spacing="2",
                    width="100%",
                ),

                #Input para la confirmación de la contraseña
                rx.vstack(
                    rx.text(
                        "Confirmar contraseña",
                        size="3",
                        weight="medium",
                        width="100%",
                        text_align="left",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("lock")),
                        placeholder="Confirmar contraseña",
                        type="password",
                        size="3",
                        width="100%",
                        value=PasswordResetState.confirm_password, #Muestra el valor en el estado
                        on_change=PasswordResetState.set_confirm_password, #Al cambiar el valor, actualiza el estado
                    ),
                    spacing="2",
                    width="100%",
                ),

                #Botón de acción
                rx.button(
                    rx.icon("check", size=18),
                    "Cambiar contraseña",
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    on_click=PasswordResetState.update_password, #Actualiza la contraseña para el usuario
                    is_loading=PasswordResetState.loading, 
                    width="100%",
                ),

                # Link to login
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿Ya recuerdas tu contraseña?", size="3"),
                            rx.link(
                                "Inicia sesión",
                                on_click=rx.redirect("/login"),
                                size="3",
                            ),
                        ),
                    ),
                    opacity="0.8",
                    spacing="2",
                    width="100%",
                ),

                spacing="6",
                width="100%",
            ),

            max_width="28em",
            padding="2em",
        ),
        width="100%",
        padding_top="4em",
    )
