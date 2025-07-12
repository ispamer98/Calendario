# Calendario/pages/security.py

import reflex as rx
from Calendario.components.show_pasw_switch import show_pasw_switch_security
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

#Página de cambio de contraseña
@rx.page( #Decorador que indica componente de página
    route="/security",
    title="Seguridad | CalendPy",
    on_load=[ #Funciones al cargar la página
        UserState.on_load,
        UserState.check_autenticated,
        UserState.reset_switch,
        UserState.reset_security
        ],
)

def security() -> rx.Component:
    return rx.hstack( #Componente principal
        user_navbar(), #Insertamos la navbar de usuario
        rx.center(
            rx.container( #Cabecera
                rx.heading("Seguridad de la Cuenta", size="5", margin_bottom="1em",margin_top="3em"),
                rx.separator(), #Separador visual
                rx.form(
                    rx.vstack(
                        #Campo para introducir la contraseña actual
                        rx.text("Contraseña actual", size="4", weight="medium" , margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type="password",
                            name="current_password",
                            placeholder="Contraseña actual",
                            value=UserState.current_password,
                            on_change=UserState.set_current_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
                            required=True,
                        ),
                        #Campo para la nueva contraseña
                        rx.text("Nueva contraseña", size="4", weight="medium", margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type=rx.cond(UserState.show_new_pasw, "text", "password"),
                            name="new_password",
                            placeholder="Nueva contraseña",
                            value=UserState.new_password,
                            on_change=UserState.set_new_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
                            required=True,
                        ),
                        show_pasw_switch_security(), #Switch que muestra la contraseña
                        #Campo para confirmar la nueva contraseña
                        rx.text("Confirmar nueva contraseña", size="4", weight="medium", margin_top="1em"),
                        rx.input(
                            rx.input.slot(rx.icon("lock")),
                            type="password",
                            name="confirm_password",
                            placeholder="Confirmar nueva contraseña",
                            value=UserState.confirm_password,
                            on_change=UserState.set_confirm_password,
                            size="3",
                            width="100%",
                            _focus={"border_color": "#3182CE"},
                            required=True,
                        ),
                        #Botón que valida los campos y si está correcto, cambia la contraseña
                        rx.button(
                            "Cambiar contraseña",
                            on_click=UserState.change_password,
                            color_scheme="blue",
                            margin_top="1.5em",
                        ),
                    ),
                    width="100%",
                    spacing="1.5",
                ),
                width="100%",
                max_width="500px",
                padding="2em",
            ),
            width="100%",
        )
    )
