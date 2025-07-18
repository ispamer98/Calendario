#Calendario/pages/forgot_pasword.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.password_reset_state import PasswordResetState
from Calendario.state.user_state import UserState

#Página de contraseña olvidada
@rx.page( #Decorador indicando componente de página
        route="/forgot_password",
        title="Recuperar contraseña | CalendPy",
        on_load=[PasswordResetState.on_load_forgot_password,]) #Acción al cargar la página

@footer #Insertamos el pie de página

def forgot_password() -> rx.Component: 
    #Estructura principal de la página
    return rx.center(
        rx.container(
            rx.box( #Visión en movil
                rx.mobile_only(
                    rx.button( #Botón que redirige al inicio
                        rx.icon("arrow-left", size=18),
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
                    )
                ), #Visión en escritorio
                rx.tablet_and_desktop(
                    rx.button( #Botón que redirige al inicio
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

            rx.vstack( #Componente principal
                rx.center(
                    rx.heading( #Cabecera de página
                        "Restablecer contraseña",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                rx.vstack(
                    #Introducir email
                    rx.text( 
                        "Correo electrónico",
                        size="3",
                        weight="medium",
                        width="100%",
                        text_align="left",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("mail")),
                        placeholder="Correo electrónico",
                        type="email",
                        size="3",
                        width="100%",
                        required=True,
                        #Se envía el email introducido al estado
                        value=PasswordResetState.email, 
                        on_change=PasswordResetState.set_email,
                    ),
                    spacing="2",
                    width="100%",
                ),

                #Botón de acción
                rx.button(
                    rx.icon("send", size=18),
                    "Enviar enlace",
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    #Acción de envío, link de reset de contraseña
                    on_click=PasswordResetState.send_reset_link,
                    is_loading=PasswordResetState.loading,
                    width="100%",
                ),

                #Botón de vuelta a login
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿Recuerdas tu contraseña?", size="3"),
                            rx.link(
                                "Inicia sesión",
                                on_click=rx.redirect("/login"),
                                size="3",
                            ),
                        ),
                    ),
                    opacity="0.8",
                    spacing="2",
                    direction="column",
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
