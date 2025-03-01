# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register

def register_form() -> rx.Component:
    """Componente del formulario de registro con dos columnas."""
    return rx.container(
        rx.vstack(
            # Título "Registrate" centrado
            rx.center(
                rx.heading(
                    "Registra tu Usuario",
                    size="6",
                    as_="h2",
                    text_align="center",
                    width="100%",
                ),
                width="100%",
            ),
            # Contenedor principal con dos columnas (hstack)
            rx.hstack(
                # Columna izquierda: Usuario y contraseñas
                rx.vstack(
                    rx.vstack(
                        rx.text("Usuario", size="3", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("user")),
                            placeholder="Usuario",
                            name="user",
                            type="text",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            autofocus=True,
                            value=rx.cond(RegisterState.username, RegisterState.username, ""),
                            on_change=RegisterState.set_username,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="4", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            placeholder="Contraseña",
                            name="pasw",
                            type=rx.cond(RegisterState.show_pasw, "text", "password"),
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=rx.cond(RegisterState.password, RegisterState.password, ""),
                            on_change=RegisterState.set_password,
                        ),
                        show_pasw_switch_register(),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            placeholder="Confirmar Contraseña",
                            name="confirm_pasw",
                            type="password",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=rx.cond(RegisterState.confirm_password, RegisterState.confirm_password, ""),
                            on_change=RegisterState.set_confirm_password,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                # Columna derecha: Correo electrónico y fecha de nacimiento
                rx.vstack(
                    rx.vstack(
                        rx.text("Correo electrónico", size="4", weight="medium"),
                        rx.input(
                            rx.input.slot(rx.icon("mail")),
                            placeholder="Correo electrónico",
                            name="email",
                            type="email",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=rx.cond(RegisterState.email, RegisterState.email, ""),
                            on_change=RegisterState.set_email,
                        ),
                        rx.input(
                            rx.input.slot(rx.icon("mail")),
                            placeholder="Confirmar Correo electrónico",
                            name="confirm_email",
                            type="email",
                            size="3",
                            width="100%",
                            justify="center",
                            required=True,
                            value=rx.cond(RegisterState.confirm_email, RegisterState.confirm_email, ""),
                            on_change=RegisterState.set_confirm_email,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.center(  # Centra el texto horizontalmente
                            rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                            width="100%",  # Ocupa todo el ancho disponible
                        ),
                        rx.center(  # Centra el input horizontalmente
                            rx.input(
                                type="date",
                                size="3",
                                width="100%",  # Ocupa todo el ancho disponible
                                justify="center",  # Centra el contenido del input
                                required=True,
                                border="1px solid #666666",  # Borde sutil
                                border_radius="8px",  # Bordes redondeados
                                _hover={
                                    "border": "1px solid #3182ce",  # Borde azul al pasar el mouse
                                },
                                _focus={
                                    "border": "1px solid #3182ce",  # Borde azul al enfocar
                                    "box_shadow": "0 0 0 1px #3182ce",  # Sombra al enfocar
                                },
                            ),
                            width="100%",  # Ocupa todo el ancho disponible
                        ),
                        spacing="4",  # Espacio entre el texto y el input
                        width="50%",  # Ancho del vstack
                        align="center",  # Centra los elementos verticalmente dentro del vstack
                        margin_left="20%"
                    ),
                    spacing="6",
                    width="100%",
                ),
                spacing="6",  # Espacio entre las dos columnas
                width="100%",
            ),
            # Botón de Registrarse y enlace "¿Ya estás registrado?"
            rx.center(
                rx.vstack(
                    rx.button(
                        "Registrarse",
                        size="3",  # Tamaño más pequeño
                        width="50%",  # Ancho reducido
                        justify="center",  # Centrado horizontalmente
                    ),
                    rx.hstack(
                        rx.text("¿Ya estás registrado?", size="3"),
                        rx.link(
                            "Inicia Sesión",
                            on_click=Login_state.login,  # Cambia al modo de inicio de sesión
                            size="3",
                        ),
                        spacing="2",
                        justify="center",  # Centrado horizontalmente
                        opacity="0.8",
                    ),
                    spacing="6",  # Espacio reducido entre el botón y el texto
                    width="100%",
                    align="center",  # Centrado verticalmente

                ),
                width="100%",

            ),
            spacing="6",  # Espacio entre el título y el contenido
            width="100%",
        ),
        max_width="60em",  # Ancho máximo del contenedor
        padding="2em",  # Espaciado interno
        padding_top="4em",  # Añade este padding para dar espacio arriba

    )