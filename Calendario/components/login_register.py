#login_register.py


from pydoc import text
from turtle import width
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_login, show_pasw_switch_register
def login_card() -> rx.Component:
    return rx.cond(Login_state.mode == "login",
                    rx.flex(
                            rx.vstack(                            
                            rx.center(
                                rx.image(
                                    
                                    width="2.5em",
                                    height="auto",
                                    border_radius="25%",
                                ),
                                rx.heading(
                                    "Accede a tu usuario",
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
                                rx.text(
                                    "Nombre de usuario",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder="Usuario",
                                    name="user",
                                    type="text",
                                    size="3",
                                    width="100%",
                                    required=True,
                                    autofocus=True,
                                    
                                    value=rx.cond(UserState.username, UserState.username, ""),
                                    on_change=UserState.set_username,  # Maneja el cambio de la contraseña
                                    on_key_down=UserState.press_enter,

                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.text(
                                        "Contraseña",
                                        size="3",
                                        weight="medium",
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    name="password",
                                    placeholder="Contraseña",
                                    type=rx.cond(Login_state.show_pasw, "text", "password"),  # Cambia solo el tipo
                                    size="3",
                                    width="100%",
                                    required=True,
                                    value=UserState.password,  # Valor directo del estado
                                    on_change=UserState.set_password,
                                    on_key_down=UserState.press_enter,
                                    
                                ),
                                show_pasw_switch_login(),
                                spacing="2",
                                width="100%",
                            ),
                            

                            rx.button("Iniciar Sesión",
                                    on_click=[UserState.login],
                                    size="3", width="100%"),
                            rx.center(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("¿No tienes cuenta?", size="3"),
                                        rx.link("Registrate", href="#",
                                                on_click=Login_state.register,
                                                size="3"),
                                    ),
                                    rx.link(
                                        "¿Has olvidado la contraseña?",
                                        href="/recovery_pasw",
                                        size="3",
                                    ),
                                ),
                                opacity="0.8",
                                spacing="2",
                                direction="row",
                                width="100%",
                            ), 
                            spacing="6",
                            width="100%",
                        ),
                        max_width="28em",
                        size="4",
                        width="100%",
                        justify="center",
                    ),
                    rx.container(
                        rx.vstack(
                            rx.center(
                                rx.image(
                                    width="2.5em",
                                    height="auto",
                                    border_radius="25%",
                                ),
                                rx.heading(
                                    "Registrate",
                                    size="7",
                                    as_="h2",
                                    text_align="center",
                                    width="100%",
                                ),
                                direction="column",
                                spacing="5",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.text(
                                        "Usuario",
                                        size="4",
                                        weight="medium",
                                    ),
                                    
                                    justify="between",
                                    width="100%",
                                ),
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
                                    value=rx.cond(RegisterState.username,RegisterState.username,""),
                                    on_change=RegisterState.set_username,
                                    
                                ),
                                rx.hstack(
                                    rx.text(
                                        "Contraseña",
                                        size="4",
                                        weight="medium",
                                    ),
                                    
                                    justify="between",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("lock")),
                                    placeholder="Contraseña",
                                    name="pasw",
                                    type=rx.cond(RegisterState.show_pasw, "text", "password"),
                                    size="3",
                                    width="100%",
                                    justify="center",
                                    required=True,
                                    autofocus=True,
                                    value=rx.cond(RegisterState.password,RegisterState.password,""),
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
                                    value=rx.cond(RegisterState.confirm_password,RegisterState.confirm_password,""),
                                    on_change=RegisterState.set_confirm_password,

                                ),
                                
                                spacing="4",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("asDASDDASD")

                            ),

                            rx.center(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("¿Ya estas registrado?", size="3"),
                                        rx.link("Inicia Sesion", href="#",
                                                on_click=Login_state.login,
                                                size="3"),
                                    ),
                                ),
                                opacity="0.8",
                                spacing="2",
                                direction="row",
                                width="100%",
                            ), 
                            spacing="6",
                            width="100%",
                        ),
                        max_width="28em",
                        size="4",
                        width="100%",
                        align="center",

                    )
                )


def show_pasw_switch() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )
