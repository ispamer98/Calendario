================================================
File: README.md
================================================
================================================
File: README.md
================================================
"# Calendario" 



================================================
File: requirements.txt
================================================
reflex==0.7.1
dotenv
supabase


================================================
File: rxconfig.py
================================================
import reflex as rx

config = rx.Config(
    app_name="Calendario",
)


================================================
File: Calendario/Calendario.py
================================================
"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.calendar import calendar
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState

import reflex as rx



app = rx.App()
app.add_page(index, on_load=[Login_state.swith_off,
                             RegisterState.swith_off,
                             UserState.set_password(""),
                             RegisterState.set_password(""),
                             RegisterState.set_confirm_password(""),
                             ]
                )



================================================
File: Calendario/__init__.py
================================================



================================================
File: Calendario/components/calendar_view.py
================================================
from calendar import Calendar
import reflex as rx
from Calendario.model.model import User
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState


def calendar_view(user: User) -> rx.Component:
    # Encabezado para la lista de calendarios
    return rx.cond(
        UserState.current_user,
        rx.container(
            rx.box(
                rx.heading(f"{UserState.current_user.username}", size="1"),
                rx.text(f"{CalendarState.calendars}"),
                # Iterar por los calendarios en el estado
                rx.foreach(
                    CalendarState.calendars,
                    lambda calendar: rx.box(
                        rx.text(f"Nombre: {calendar.name}", font_weight="bold"),
                        rx.text(f"Creado el: {calendar.created_at}"),
                        rx.divider(),

                        border="1px solid #ccc",
                        border_radius="8px",
                    )
                ),
                padding=6,
                border="1px solid #000",
                border_radius="8px",
            ),
            

        ),
        rx.text("NO HAY NADIE LOGGEADO!")
    )


================================================
File: Calendario/components/current_user_button.py
================================================
#current_user_button.py

import reflex as rx

from Calendario.state.user_state import UserState

def current_user_button() -> rx.Component:
    return rx.button(

        rx.text(f"{UserState.current_user.username}"),
        on_click=UserState.logout
    )


================================================
File: Calendario/components/day_button.py
================================================
import reflex as rx

def day_button(day: str = None) -> rx.Component:

    return rx.box(
            rx.button(
                rx.text("Día",day),
                rx.box(
                    rx.text("Línea 1", style={"margin": "0"}),
                    rx.text("Línea 2", style={"margin": "0"}),
                    class_name="extra_text",
                ),
                class_name="day_button",
            ),
            _hover="a",
            style={"display": "flex", "justifyContent": "center", "alignItems": "center"
            },
        )



================================================
File: Calendario/components/login_form.py
================================================
# Calendario/components/login_form.py

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_login

def login_form() -> rx.Component:
    """Componente del formulario de inicio de sesión."""
    return rx.center(  # Centra horizontalmente
        rx.container(
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
                        on_change=UserState.set_username,
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
                        type=rx.cond(Login_state.show_pasw, "text", "password"),
                        size="3",
                        width="100%",
                        required=True,
                        value=UserState.password,
                        on_change=UserState.set_password,
                        on_key_down=UserState.press_enter,
                    ),
                    show_pasw_switch_login(),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Iniciar Sesión",
                    on_click=[UserState.login],
                    size="3",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿No tienes cuenta?", size="3"),
                            rx.link(
                                "Registrate",
                                on_click=Login_state.register,
                                size="3",
                            ),
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
            padding="2em",  # Puedes añadir algo de padding para más consistencia visual
        ),
        width="100%",  # Asegura que el centro ocupa el ancho completo
        padding_top="4em",  # Añade este padding para dar espacio arriba
    )



================================================
File: Calendario/components/login_register.py
================================================
#login_register.py

# Calendario/components/login_card.py

import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.components.login_form import login_form
from Calendario.components.register_form import register_form

def login_card() -> rx.Component:
    """Componente que maneja el cambio entre login y registro."""
    return rx.cond(
        Login_state.mode == "login",
        login_form(),  # Muestra el formulario de inicio de sesión
        register_form(),  # Muestra el formulario de registro
    )


================================================
File: Calendario/components/register_form.py
================================================
# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register

def register_form() -> rx.Component:
    """Componente de registro con vistas separadas para móvil y desktop"""
    
    # Campos comunes
    username_field = rx.vstack(
    rx.hstack(
            rx.text("Usuario", size="3", weight="medium"),
            rx.button(
                rx.icon("user-check", color="white"),
                background="transparent",
                on_click=RegisterState.check_aviable_username,
                size="1",
                padding="2",
                _hover={"opacity": 0.8},
                is_disabled=RegisterState.username == ""
            ),
            rx.match(
                RegisterState.username_valid,
                (None, rx.text("")),  # Nada cuando es None
                (True, rx.icon("check", color="green")),  # Check verde independiente
                (False, rx.icon("x", color="red")),  # X roja independiente
            ),
            spacing="2",
            align="center"
        ),
            

        rx.input(
            rx.input.slot(rx.icon("user")),
            placeholder="Usuario",
            type="text",
            size="3",
            width="100%",
            value=RegisterState.username,
            on_change=RegisterState.set_username,
            border_color=rx.cond(
                RegisterState.errors["username"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(
            RegisterState.errors["username"] != "",
            rx.text(RegisterState.errors["username"], color="#EF4444", size="2")
        ),
        spacing="2",
        width="100%"
    )
    
    password_field = rx.vstack(
        rx.text("Contraseña", size="4", weight="medium"),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Contraseña",
            type=rx.cond(RegisterState.show_pasw, "text", "password"),
            size="3",
            width="100%",
            value=RegisterState.password,
            on_change=RegisterState.set_password,
            border_color=rx.cond(
                RegisterState.errors["password"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error contraseña
            RegisterState.errors["password"] != "",
            rx.text(
                RegisterState.errors["password"],
                size="2",
                color="#EF4444"
            )
        ),
        show_pasw_switch_register(),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Confirmar Contraseña",
            type="password",
            size="3",
            width="100%",
            value=RegisterState.confirm_password,
            on_change=RegisterState.set_confirm_password,
            border_color=rx.cond(
                RegisterState.errors["confirm_password"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error confirmar contraseña
            RegisterState.errors["confirm_password"] != "",
            rx.text(
                RegisterState.errors["confirm_password"],
                size="2",
                color="#EF4444"
            )
        ),
        spacing="2",
        width="100%"
    )
    
    email_field = rx.vstack(
        rx.text("Correo electrónico", size="4", weight="medium"),
        rx.input(
            rx.input.slot(rx.icon("mail")),
            placeholder="Correo electrónico",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.email,
            on_change=RegisterState.set_email,
            border_color=rx.cond(
                RegisterState.errors["email"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error email
            RegisterState.errors["email"] != "",
            rx.text(
                RegisterState.errors["email"],
                size="2",
                color="#EF4444"
            )
        ),
        rx.input(
            rx.input.slot(rx.icon("mail")),
            placeholder="Confirmar Correo",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.confirm_email,
            on_change=RegisterState.set_confirm_email,
            border_color=rx.cond(
                RegisterState.errors["confirm_email"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error confirmacion email
            RegisterState.errors["confirm_email"] != "",
            rx.text(
                RegisterState.errors["confirm_email"],
                size="2",
                color="#EF4444"
            )
        ),
        spacing="4",
        width="100%"
    )
    
    birthday_field = rx.vstack(
        rx.center(rx.text("Fecha de Nacimiento", size="4", weight="medium")),
        rx.hstack(
            rx.input(
                type="date",
                size="3",
                width="100%",
                value=RegisterState.birthday,
                on_change=RegisterState.set_birthday,
                border=rx.cond(
                    RegisterState.errors["birthday"] != "",
                    "1px solid #EF4444", "1px solid #666666"),
                _focus={"border": "1px solid #3182CE"},
                required=True
            ),
            rx.cond(  # Mensaje error cumpleaños
                RegisterState.errors["birthday"] != "",
                rx.text(
                    RegisterState.errors["birthday"],
                    size="2",
                    color="#EF4444"
                )
            ),
            
            rx.button(
                rx.icon("rotate-ccw"),
                on_click=rx.set_value("birthday", ""),
                background="transparent",
                _hover={"transform": "scale(1.2)"}
            ),
            width="100%",
            align="center"
        ),
        spacing="4",
        width="100%"
    )
    
    # Versión móvil
    mobile_view = rx.mobile_only(
        rx.vstack(
            username_field,
            password_field,
            email_field,
            birthday_field,
            spacing="6",
            width="100%"
        )
    )
    
    # Versión desktop
    desktop_view = rx.tablet_and_desktop(
        rx.hstack(
            rx.vstack(
                username_field,
                password_field,
                spacing="6",
                width="80%"
            ),
            rx.vstack(
                email_field,
                birthday_field,
                spacing="6",
                width="80%"
            ),
            spacing="6",
            width=["20","30em","40em","50em","60em"],
            max_width="60em",
            
        )
    )
    
    return rx.container(
        rx.vstack(
            rx.heading("Registra tu Usuario", size="6", text_align="center"),
            mobile_view,
            desktop_view,
            rx.button(
                "Registrarse",
                size="3",
                width=["90%", "50%"],
                on_click=RegisterState.register
            ),
            rx.hstack(
                rx.text("¿Ya estás registrado?"),
                rx.link("Inicia Sesión", on_click=Login_state.login),
                justify="center",
                opacity="0.8"
            ),
            
            spacing="6",
            width="100%",
            align="center"
        ),

        padding="2em",
        padding_top="4em",
        class_name="register-container"
    )


================================================
File: Calendario/components/register_form2.py
================================================

# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register
from Calendario.utils.api import check_existing_user

def register_form() -> rx.Component:
    """Componente del formulario de registro responsive."""
    return rx.container(
        rx.vstack(
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
            
            rx.cond(
                rx.is_mobile,
                # Versión móvil - Todo en VStack
                rx.vstack(
                    # Sección Usuario y Contraseña
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
                            value=RegisterState.username,
                            on_change=RegisterState.set_username,
                            border_color=rx.cond(
                                RegisterState.errors["username"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["username"] != "",
                            rx.text(
                                RegisterState.errors["username"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    
                    # Sección Contraseñas
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
                            value=RegisterState.password,
                            on_change=RegisterState.set_password,
                            border_color=rx.cond(
                                RegisterState.errors["password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["password"] != "",
                            rx.text(
                                RegisterState.errors["password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
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
                            value=RegisterState.confirm_password,
                            on_change=RegisterState.set_confirm_password,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_password"] != "",
                            rx.text(
                                RegisterState.errors["confirm_password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    
                    # Sección Email
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
                            value=RegisterState.email,
                            on_change=RegisterState.set_email,
                            border_color=rx.cond(
                                RegisterState.errors["email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["email"] != "",
                            rx.text(
                                RegisterState.errors["email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
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
                            value=RegisterState.confirm_email,
                            on_change=RegisterState.set_confirm_email,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_email"] != "",
                            rx.text(
                                RegisterState.errors["confirm_email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Sección Fecha de Nacimiento
                    rx.vstack(
                        rx.center(
                            rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.center(
                                rx.input(
                                    id="birthday",
                                    type="date",
                                    size="3",
                                    width="100%",
                                    justify="center",
                                    required=True,
                                    value=RegisterState.birthday,
                                    on_change=RegisterState.set_birthday,
                                    border=rx.cond(
                                        RegisterState.errors["birthday"] != "",
                                        "1px solid #EF4444",
                                        "1px solid #666666"
                                    ),
                                    border_radius="8px",
                                    _hover={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        )
                                    },
                                    _focus={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        ),
                                        "box_shadow": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "0 0 0 1px #EF4444",
                                            "0 0 0 1px #3182CE"
                                        )
                                    }
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("rotate-ccw"),
                                on_click=rx.set_value("birthday",""),
                                background="transparent",
                                size="1",
                                margin_top="8px",
                                _hover={
                                    "transform": "scale(1.2)",
                                    "transition": "transform 0.2s ease",
                                    "cursor": "pointer"
                                },
                            ),
                        ),
                        rx.cond(
                            RegisterState.errors["birthday"] != "",
                            rx.text(
                                RegisterState.errors["birthday"],
                                size="2",
                                text_align="center",
                                width="100%",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="100%",
                        align="center",
                    ),
                    spacing="6",
                    width="100%",
                ),

                # Version desktop 2 columnas
                rx.hstack(
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
                                value=RegisterState.username,
                                on_change=[RegisterState.set_username,],
                                border_color=rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["username"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["username"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["username"] != "",
                                rx.text(
                                    RegisterState.errors["username"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.password,
                                on_change=RegisterState.set_password,
                                border_color=rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["password"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["password"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["password"] != "",
                                rx.text(
                                    RegisterState.errors["password"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.confirm_password,
                                on_change=RegisterState.set_confirm_password,
                                border_color=rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["confirm_password"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["confirm_password"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["confirm_password"] != "",
                                rx.text(
                                    RegisterState.errors["confirm_password"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
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
                                value=RegisterState.email,
                                on_change=RegisterState.set_email,
                                border_color=rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["email"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["email"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["email"] != "",
                                rx.text(
                                    RegisterState.errors["email"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.confirm_email,
                                on_change=RegisterState.set_confirm_email,
                                border_color=rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["confirm_email"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["confirm_email"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["confirm_email"] != "",
                                rx.text(
                                    RegisterState.errors["confirm_email"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.center(
                                rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.center(
                                    rx.input(
                                        id="birthday",
                                        type="date",
                                        size="3",
                                        width="100%",
                                        justify="center",
                                        required=True,
                                        value=RegisterState.birthday,
                                        on_change=RegisterState.set_birthday,
                                        border=rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #666666"
                                        ),
                                        border_radius="8px",
                                        _hover={
                                            "border": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "1px solid #EF4444",
                                                "1px solid #3182CE"
                                            )
                                        },
                                        _focus={
                                            "border": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "1px solid #EF4444",
                                                "1px solid #3182CE"
                                            ),
                                            "box_shadow": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "0 0 0 1px #EF4444",
                                                "0 0 0 1px #3182CE"
                                            )
                                        }
                                    ),
                                    width="100%",
                                ),
                                rx.button(
                                    rx.icon("rotate-ccw"),
                                    on_click=rx.set_value("birthday",""),
                                    background="transparent",
                                    size="1",
                                    margin_top="8px",
                                    _hover={
                                        "transform": "scale(1.2)",
                                        "transition": "transform 0.2s ease",
                                        "cursor": "pointer"
                                    },
                                ),
                            ),
                                    
                            
                            rx.cond(
                                RegisterState.errors["birthday"] != "",
                                rx.text(
                                    RegisterState.errors["birthday"],
                                    size="2",
                                    text_align="center",
                                    width="100%",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="4",
                            width="50%",
                            align="center",
                            margin_left="20%"
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.button(
                            "Registrarse",
                            size="3",
                            width="50%",
                            justify="center",
                            on_click=RegisterState.register
                        ),
                        rx.hstack(
                            rx.text("¿Ya estás registrado?", size="3"),
                            rx.link(
                                "Inicia Sesión",
                                on_click=Login_state.login,
                                size="3",
                            ),
                            spacing="2",
                            justify="center",
                            opacity="0.8",
                        ),
                        spacing="6",
                        width="100%",
                        align="center",
                    ),
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            max_width="60em",
            padding="2em",
            padding_top="4em",
            on_mount=[RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    RegisterState.reset_errors()]
        )
    )


================================================
File: Calendario/components/show_pasw_switch.py
================================================
import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
def show_pasw_switch_login() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )

def show_pasw_switch_register() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=RegisterState.swith_on,  # Cambia el estado del switch
            is_checked=RegisterState.show_pasw,  # Estado actual del switch
            color_scheme="jade",
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )





================================================
File: Calendario/database/database.py
================================================
#database.py


import os
import dotenv
from typing import Union,List
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class SupabaseAPI:

    dotenv.load_dotenv()

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def authenticate_user(self, username: str, password: str) -> Union[dict, None]:
        """
        Autentica a un usuario verificando su nombre y contraseña.

        Args:
            username (str): Nombre de usuario a buscar.
            password (str): Contraseña del nnnnnnn.

        Returns:
            dict | None: Datos del usuario si la autenticación es exitosa, o None si falla.
        """
        try:
            response = self.supabase.from_("user").select("*").ilike("username", username).execute()
            print(response.data)

            if response.data:
                user = response.data[0]
                if user["pasw"] == password:
                    logging.info(f"Usuario autenticado: {username}")
                    return user
        except Exception as e:
            logging.error(f"Error autenticando al usuario: {e}")
        return None
    

    def check_existing_user(self,username: str, email: str) -> dict:
        """
        Verifica si el username o email ya existen en la base de datos.

        Args:
            username (str): Nombre de usuario a verificar.
            email (str): Email a verificar.

        Returns:
            dict: Indica si existen el usuario o email.
        """
        existing_username= False
        existing_email = False

        try:

            response_user = self.supabase.from_("user").select("username").ilike("username", username).execute()
            existing_username= len(response_user.data) > 0

            response_email= self.supabase.from_("user").select("email").ilike("email",email).execute()
            existing_email= len(response_email.data) > 0

            return {'username':existing_username, 'email':existing_email}
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario o email: {e}")
            return {'username': False, 'email': False}
        
    def check_existing_username(self, username):
        try:
            response = self.supabase.from_("user").select("username").ilike("username", username).execute()
            return len(response.data) > 0  # Devuelve directamente el booleano
        
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario: {e}")
            return False

    def get_calendars(self, user_id: int) -> Union[List[Calendar], None]:
        try:
            response = (
                self.supabase
                .from_("calendars")
                .select("*")
                .eq("owner_id", user_id)
                .execute()
            )

            if response.data:
                calendars = [
                    Calendar(
                        id=cal['id'],
                        name=cal['name'],
                        owner_id=cal['owner_id'],
                        shared_with=cal.get('shared_with', []),
                        created_at=datetime.fromisoformat(
                            cal['created_at'].replace('Z', '+00:00')
                        ) if cal.get('created_at') else datetime.now()
                    )
                    for cal in response.data
                ]
                return calendars
                
        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None


================================================
File: Calendario/model/model.py
================================================
import reflex as rx
from datetime import datetime

class User(rx.Base):
    """
    Modelo para usuarios.
    """
    id: int
    username: str
    pasw: str
    email: str
    birthday: str
    created_at: datetime


class Calendar(rx.Base):
    """
    Modelo para calendarios.
    """
    id: int
    name: str
    owner_id: int  # Relación con el usuario propietario
    shared_with: list[int] = []  # Lista de IDs de usuarios compartidos
    created_at: datetime


class Meal(rx.Base):
    """
    Modelo para opciones de comidas y cenas.
    """
    id: int
    name: str  # Nombre de la comida o cena (ejemplo: "Pizza", "Ensalada")
    description: str = None  # Descripción opcional (ejemplo: ingredientes)


class Day(rx.Base):
    """
    Modelo para días dentro de un calendario.
    """
    id: int
    calendar_id: int  # Relación con el calendario
    date: datetime
    meal_id: int = None  # Relación con el modelo Meal (comida)
    dinner_id: int = None  # Relación con el modelo Meal (cena)
    comments: list[int] = []  # Lista de IDs de comentarios


class Comment(rx.Base):
    """
    Modelo para comentarios asociados a un día.
    """
    id: int
    day_id: int  # Relación con el día
    content: str  # Contenido del comentario
    owner_id: int  # Usuario que hizo el comentario
    created_at: datetime



================================================
File: Calendario/pages/calendar.py
================================================

import reflex as rx
from Calendario.components.calendar_view import calendar_view
from Calendario.components.current_user_button import current_user_button
from Calendario.state import user_state
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info,position="top-center")

@rx.page(route="/calendar",on_load=CalendarState.load_calendars)
def calendar() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.text(UserState.username),
            rx.cond(
                UserState.current_user,
                rx.vstack(
                    rx.button(
                        "Logout",
                        on_click=[UserState.logout]

                    ),
                    rx.text("CALENDARIOS"),
                    rx.button(on_click=CalendarState.load_calendars),
                    rx.cond(
                        CalendarState.calendars.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                CalendarState.calendars,
                                lambda calendar: rx.text(calendar.name)
                            )
                        ),
                        rx.text("NO HAY CALENDARIOS EN CALENDAR.PY")
                    ),
                ),
                rx.container(
                    rx.text("NO HAY NADIE LOGGEADO EN CALENDAR.PY"),
                    rx.button(
                        "Go Home",
                        on_click=rx.redirect("/")
                    )
                )
            ),

        )
    ),



    


================================================
File: Calendario/pages/index.py
================================================
from calendar import Calendar
import reflex as rx
 


from Calendario.components.current_user_button import current_user_button
from Calendario.components.calendar_view import calendar_view
from Calendario.components.login_register import login_card
from Calendario.state.calendar_state import CalendarState
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
from Calendario.database.database import SupabaseAPI
@rx.page(route="/", title="Calendario | Python", on_load=RegisterState.load_page()
         )
def index() -> rx.Component:
    return rx.container(
        rx.cond(
            UserState.current_user,
            rx.container(
                rx.spacer(
                    height="200px"
                ),
                rx.text("Redirecting..."),
                current_user_button()


            ),
            login_card()
        )
    )


================================================
File: Calendario/state/calendar_state.py
================================================
#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import fetch_and_transform_calendars


class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    current_month: datetime = datetime.today()  # Fecha del mes actual
    selected_day: Optional[datetime] = None  # Día seleccionado
    selected_day_data: Optional[Day] = None  # Datos del día seleccionado
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    current_calendar: Optional[Calendar] = None
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info : str = None


    @rx.event
    async def load_calendars(self):
        print("EN CALENDAR STATE LOAD  CALENDARS")

        try:
            user_state = await self.get_state(UserState)
            user_id = user_state.current_user.id
            
            if user_state.current_user is None:
                return rx.toast.error(
                    position="top-center",
                    title="Debes iniciar sesión para ver tus calendarios."
                )
                
            calendars = await fetch_and_transform_calendars(user_id)
            if calendars:
                self.calendars = calendars
                print(f"Calendarios cargados: {[f'ID: {cal.id}, Nombre: {cal.name}, Propietario ID: {cal.owner_id}, Compartido con: {cal.shared_with}, Creado en: {cal.created_at}' for cal in self.calendars]}")
            else:
                print("No se encontraron calendarios.")
                
        except Exception as e:
            print(e)


    @rx.event
    def set_current_calendar(self, calendar : Calendar):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.current_calendar = calendar
        print(f"Calendario actualizado: {self.current_calendar.name}")

    @rx.event
    def clean(self):
        self.current_month = datetime.today()
        self.selected_day = None
        self.selected_day_data = None
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.current_calendar = None 
        self.calendars = []  # Reset to empty list

        return rx.toast.info(
             position="top-center",
             title="")



================================================
File: Calendario/state/login_state.py
================================================
#login_card_state

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
class Login_state(rx.State):
    """
    Manejador de estado para la tarjeta de inicio de sesión en Reflex.
    """
    is_open: bool = False
    mode: str = "login"
    show_pasw: bool = False


    @rx.event
    def login(self, mode="login"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return UserState.restart_pasw()

    @rx.event
    def register(self, mode="register"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return [RegisterState.reset_switch(),
                RegisterState.reset_inputs(),
                ]  # Reinicia el switch en el formulario de registro


    @rx.event
    def close(self):
        self.is_open = False

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value





================================================
File: Calendario/state/register_state.py
================================================

# register_state.py


from Calendario.utils.api import check_existing_user, register_user, check_existing_username
from Calendario.utils.send_email import send_welcome_email
from datetime import datetime
import reflex as rx 

class RegisterState(rx.State):
    username : str = ""
    password : str = ""
    confirm_password : str = ""
    email : str = ""
    confirm_email : str = ""
    birthday : str = ""
    show_pasw : bool = False
    errors: dict = {
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }
    username_valid : bool = None


    @rx.event
    def reset_errors(self):
        self.errors = {k: "" for k in self.errors}
    @rx.event
    async def register(self):
        # Resetear errores
        self.errors = {k: "" for k in self.errors}
        has_errors = False

        # Verificar si el usuario/email ya existen
        existing = await check_existing_user(self.username, self.email)
        if existing["username"]:
            self.errors["username"] = "El nombre de usuario ya está registrado"
            has_errors = True
        if existing["email"]:
            self.errors["email"] = "El correo electrónico ya está registrado"
            has_errors = True


        # Validación de username
        if not self.username:
            self.errors["username"] = "Usuario requerido"
            has_errors = True
        else:
            # Verificar que la longitud esté entre 6 y 16 caracteres
            if len(self.username) < 4 or len(self.username) > 16:
                self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                has_errors = True

            # Verificar que contenga al menos un número
            elif not any(char.isdigit() for char in self.username):
                self.errors["username"] = "El usuario debe contener al menos un número"
                has_errors = True

            # Verificar que no contenga caracteres especiales (solo letras y números)
            elif not self.username.isalnum():
                self.errors["username"] = "El usuario no puede contener caracteres especiales"
                has_errors = True

        # Validación de email
        if not self.validate_email(self.email.lower()):
            self.errors["email"] = "Email inválido"
            has_errors = True
        elif self.email.lower() != self.confirm_email.lower():
            self.errors["confirm_email"] = "Los emails no coinciden"
            has_errors = True

        import re
        # Validación de contraseña
        if not self.password:
            self.errors["password"] = "Contraseña requerida"
            has_errors = True
        else:
            # Patrón que requiere:
            # - Al menos 8 caracteres
            # - Al menos una letra mayúscula
            # - Al menos un dígito
            # - Al menos un carácter especial (no alfanumérico)
            pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
            if not re.match(pattern, self.password):
                self.errors["password"] = ("La contraseña debe tener mínimo 8 caracteres, "
                                            "al menos 1 mayúscula, 1 número y 1 carácter especial")
                has_errors = True
            elif self.password != self.confirm_password:
                self.errors["confirm_password"] = "Las contraseñas no coinciden"
                has_errors = True

        # Validación de fecha
        if not self.birthday:
            self.errors["birthday"] = "Fecha requerida"
            has_errors = True
        else:
            try:
                birth_date = datetime.strptime(self.birthday, '%Y-%m-%d')
                if birth_date > datetime.now():
                    self.errors["birthday"] = "Fecha inválida"
                    has_errors = True
            except ValueError:
                self.errors["birthday"] = "Formato inválido\n (DD-MM-AAAA)"
                has_errors = True

        if has_errors:
            return rx.toast.error("No ha sido posible el registro",
                                  position="top-center")


        # Si no hay errores, proceder con registro
        if not has_errors:
            try:
                # Aquí iría la lógica de registro en la base de datos
                new_user = await register_user(
                    self.username,
                    self.password,
                    self.email,
                    self.birthday,
                )
                
                if new_user == True:
                # Enviar correo de bienvenida
                    send_welcome_email(self.email, self.username)
                
                    from Calendario.state.login_state import Login_state

                    
                    return [rx.toast.success(
                        "¡Registro exitoso! Revisa tu correo electrónico",
                        position="top-center"
                    ),Login_state.login()]
                else:
                    self.password=""
                    self.confirm_password=""
                    return rx.toast.error(
                        "No se ha podido registrar el usuario",
                        position="top-center",
                    )
            except Exception as e:
                return rx.toast.error(
                    f"Error en el registro: {str(e)}",
                    position="top-center"
                )

    def validate_email(self, email: str) -> bool:
        import re
        pattern = r"""
        ^                           # Inicio de la cadena
        (?!.*\.\.)                  # No permite dos puntos consecutivos
        [\w.%+-]+                   # Parte local (caracteres permitidos)
        (?<!\.)                     # No termina con un punto
        @                           # Separador
        (?:                         # Dominio:
            [a-zA-Z0-9]             #   - Inicia con alfanumérico
            (?:[a-zA-Z0-9-]{0,61}  #   - Permite hasta 61 caracteres (incluyendo guiones)
            [a-zA-Z0-9])?           #   - Termina con alfanumérico (no guión)
            \.                      #   - Separador por punto
        )+                          # Múltiples subdominios
        [a-zA-Z]{2,63}              # TLD (2-63 caracteres alfabéticos)
        $                           # Fin de la cadena
        """
        return bool(re.fullmatch(pattern, email, re.VERBOSE))


    @rx.event
    async def check_aviable_username(self):
        if not self.username:
            return
        
        try:
            existing = await check_existing_username(self.username)
            if existing:
                self.username_valid = False
                self.errors["username"] = "El nombre de usuario ya está registrado"
            else:

                                            # Verificar que la longitud esté entre 6 y 16 caracteres
                if len(self.username) < 4 or len(self.username) > 16:
                    self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                    self.username_valid = False


                # Verificar que contenga al menos un número
                elif not any(char.isdigit() for char in self.username):
                    self.errors["username"] = "El usuario debe contener al menos un número"
                    self.username_valid = False

                # Verificar que no contenga caracteres especiales (solo letras y números)
                elif not self.username.isalnum():
                    self.errors["username"] = "El usuario no puede contener caracteres especiales"
                    self.username_valid = False
                
                else:
                    self.username_valid = True
                    self.errors["username"] = ""

        except Exception as e:
            print(f"Error al verificar el nombre de usuario: {str(e)}")
            self.username_valid = None


    @rx.event
    def set_username(self, username: str):
        self.username = username
        print(f"Usuario para registro actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        self.password = password
        print(f"Contraseña para registro actualizada: {self.password}")

    @rx.event
    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password
        print(f"Confirmar contraseña para registro actualizada: {self.confirm_password}")
    @rx.event
    def set_email(self, email: str):
        self.email = email
        print(f"Correo electrónico para registro actualizado: {self.email}")
    @rx.event
    def set_confirm_email(self, confirm_email: str):
        self.confirm_email = confirm_email
        print(f"Confirmar correo electrónico para registro actualizado: {self.confirm_email}")

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def reset_switch(self):
        """Reinicia el estado del switch a False."""
        self.show_pasw = False
    
    @rx.event
    def reset_inputs(self):
        """Reinicia todos los inputs."""
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.email = ""
        self.confirm_email = ""
        self.birthday = ""
        self.errors = {k: "" for k in self.errors}
        self.username_valid = None

    @rx.event
    def load_page(self):
        self.password = ""
        self.confirm_password = ""
        self.confirm_email = ""
        self.birthday = ""
        self.reset_errors()
        self.username_valid = None


================================================
File: Calendario/state/user_state.py
================================================
#user_state.py

import reflex as rx
import time
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user

class UserState(rx.State):
    """
    Manejador de estado para los datos del usuario en Reflex.
    """

    username: str = ""  # Guarda el nombre de usuario ingresado
    password: str = ""  # Guarda la contraseña ingresada
    current_user: User = None  # Mantiene al usuario autenticado


    @rx.event
    def press_enter(self, key: str):
        if key == "Enter":
            # Return the event instead of calling it directly
            return UserState.login
    
    def return_username(self) -> str:
        return self.username
    
    @rx.event
    def set_username(self, username: str):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.username = username
        print(f"Username actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        """
        Actualiza la contraseña en el estado.
        """
        self.password = password
        print(f"Password actualizado: {self.password}")

    @rx.event
    async def login(self):

        if not self.username or not self.password:
            self.clear_paswd()

        try:
            user_data = await authenticate_user(self.username.lower(), self.password)

            
            if user_data:
                self.current_user = user_data
                self.username = ""
                self.password = ""
                # Llamamos al evento para cargar los calendarios en el estado de CalendarState
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                # Limpiamos los campos de usuario y contraseña
                self.username = ""
                self.password = ""
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        except Exception as e:
            print(f"Error al intentar iniciar sesión: {e}")
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )


    @rx.event
    def clear_paswd(self):
        self.password = ""
        print("Contraseña borrada:", self.password)  # Para depuración

    



    @rx.event

    async def logout(self):
        from Calendario.state.calendar_state import CalendarState
        """
        Cierra la sesión del usuario actual.
        """
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()
        self.current_user = None
        self.username = ""
        self.password = ""
        CalendarState.toast_info = "Cerrando la sesión"
        return [
            rx.redirect("/")
        ]
    

    @rx.event
    def restart_pasw(self):
        self.password=""


================================================
File: Calendario/utils/api.py
================================================
#api.py
import reflex as rx
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment
from datetime import datetime

from typing import Union,List,Optional

SUPABASE_API = SupabaseAPI()

async def authenticate_user(username: str, password: str) -> Union[User, None]:
    """
    Autentica al usuario y devuelve un objeto User si es exitoso.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña del usuario.

    Returns:
        User | None: Instancia del usuario autenticado o None si falla.
    """
    if not username or not password:
        return None

    user_data = SUPABASE_API.authenticate_user(username, password)
    if user_data:
        
        return User(**user_data)  # Convierte los datos en una instancia de User

    return None

async def check_existing_user(username: str, email: str,) -> dict:
    return SUPABASE_API.check_existing_user(username, email)

async def check_existing_username(username: str) -> bool:
    return SUPABASE_API.check_existing_username(username)

async def register_user(username: str, password: str, email: str, birthday: str) -> Union[User, None]:
    try: 
        user_data = {
            "username": username,
            "pasw": password,
            "email": email,
            "birthday": birthday
        }
        
        # Inserta el usuario en la base de datos
        response = SUPABASE_API.supabase.table("user").insert(user_data).execute()
        
        if response.data:
            # Convierte los datos de Supabase a un objeto User
            return True
        return None
        
    except Exception as e:
        print(f"Error al registrar el usuario: {e}")
        return None
    
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    calendars = SUPABASE_API.get_calendars(user_id)
    if calendars is None:
        print("No se encontraron datos de calendarios.")
        return []
    return calendars





================================================
File: Calendario/utils/send_email.py
================================================
import smtplib

def send_welcome_email(email, username):
    # Configuración del servidor SMTP (Gmail en este ejemplo)
    servidor_smtp = "smtp.gmail.com"
    puerto = 587
    admin = "verificacionespython@gmail.com"
    pasw = "cmblnedixejwrqag"  # Reemplaza con tu contraseña de aplicación

    # Configuración del mensaje de bienvenida
    asunto = "¡Bienvenido a tu Calendario!"
    cuerpo = f"""
    Hola {username},

    ¡Bienvenido a tu Calendario!

    Estamos emocionados de tenerte con nosotros. Ahora puedes organizar tus comidas/cenas, e interactuar con los comentarios.

    ¡Gracias por unirte a nuestra comunidad!

    Saludos,
    El equipo de Calendario
    """
    correo = f"Subject: {asunto}\n\n{cuerpo}"

    try:
        with smtplib.SMTP(servidor_smtp, puerto) as server:
            server.starttls()
            server.login(admin, pasw)
            server.sendmail(admin, email, correo.encode('utf-8'))
        print(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")




================================================
File: assets/css/styles.css
================================================
/* assets/css/styles.css */
@media (max-width: 768px) {
    .register-container {
        padding: 1em !important;
    }
    
    .register-input {
        font-size: 16px; /* Mejor para inputs móviles */
    }
}



================================================
File: requirements.txt
================================================
reflex==0.7.1
dotenv
supabase



================================================
File: rxconfig.py
================================================
import reflex as rx

config = rx.Config(
    app_name="Calendario",
    show_built_with_reflex=False
)



================================================
File: Calendario/Calendario.py
================================================
"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.calendar import calendar
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState

import reflex as rx



app = rx.App()
app.add_page(index, on_load=[Login_state.swith_off,
                             RegisterState.swith_off,
                             UserState.set_password(""),
                             RegisterState.set_password(""),
                             RegisterState.set_confirm_password(""),
                             ]
                )


================================================
File: Calendario/__init__.py
================================================



================================================
File: Calendario/components/calendar_creator.py
================================================
#calendar_creator.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState

def calendar_creator() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Crear Nuevo Calendario",
                variant="solid",
                color_scheme="jade",
                size="3"
            )
        ),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading("Crear nuevo Calendario", size="5"),
                    rx.text("Nombre del Calendario",size="2",color="gray"),
                    rx.input(
                        placeholder="Ej: Comidas de Marzo 2025",
                        name="calendar_name",
                        required=True,
                        value=CalendarState.new_calendar_name,
                        on_change=CalendarState.set_new_calendar_name
                    ),
                    rx.text("Selecciona el mes", size="2", color="gray", margin_top="1em"),
                    rx.input(
                        type="month",
                        name="calendar_month",
                        required=True,
                        value=CalendarState.new_calendar_month,
                        on_change=CalendarState.set_new_calendar_month
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Calncelar", variant="soft")
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Crear",
                                type="submit",
                                variant="solid",
                                color_scheme="jade"
                            )
                        ),
                        spacing="3",
                        margin_top="2em",
                        justify="end"
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=CalendarState.create_calendar,
            ),
            style={"max_width":450},
            box_shadow="1g",
            padding="2em",
            border_radius="8px",
        ),
    )


================================================
File: Calendario/components/calendar_view.py
================================================
from calendar import Calendar
import reflex as rx
from Calendario.model.model import User
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState


def calendar_view(user: User) -> rx.Component:
    # Encabezado para la lista de calendarios
    return rx.cond(
        UserState.current_user,
        rx.container(
            rx.box(
                rx.heading(f"{UserState.current_user.username}", size="1"),
                rx.text(f"{CalendarState.calendars}"),
                # Iterar por los calendarios en el estado
                rx.foreach(
                    CalendarState.calendars,
                    lambda calendar: rx.box(
                        rx.text(f"Nombre: {calendar.name}", font_weight="bold"),
                        rx.text(f"Creado el: {calendar.created_at}"),
                        rx.divider(),

                        border="1px solid #ccc",
                        border_radius="8px",
                    )
                ),
                padding=6,
                border="1px solid #000",
                border_radius="8px",
            ),
            

        ),
        rx.text("NO HAY NADIE LOGGEADO!")
    )


================================================
File: Calendario/components/current_user_button.py
================================================
#current_user_button.py

import reflex as rx

from Calendario.state.user_state import UserState

def current_user_button() -> rx.Component:
    return rx.button(

        rx.text(f"{UserState.current_user.username}"),
        on_click=UserState.logout
    )



================================================
File: Calendario/components/day_button.py
================================================
import reflex as rx

def day_button(day: str = None) -> rx.Component:

    return rx.box(
            rx.button(
                rx.text("Día",day),
                rx.box(
                    rx.text("Línea 1", style={"margin": "0"}),
                    rx.text("Línea 2", style={"margin": "0"}),
                    class_name="extra_text",
                ),
                class_name="day_button",
            ),
            _hover="a",
            style={"display": "flex", "justifyContent": "center", "alignItems": "center"
            },
        )


================================================
File: Calendario/components/login_form.py
================================================
# Calendario/components/login_form.py

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_login

def login_form() -> rx.Component:
    """Componente del formulario de inicio de sesión."""
    return rx.center(  # Centra horizontalmente
        rx.container(
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
                        on_change=UserState.set_username,
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
                        type=rx.cond(Login_state.show_pasw, "text", "password"),
                        size="3",
                        width="100%",
                        required=True,
                        value=UserState.password,
                        on_change=UserState.set_password,
                        on_key_down=UserState.press_enter,
                    ),
                    show_pasw_switch_login(),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Iniciar Sesión",
                    on_click=[UserState.login],
                    size="3",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿No tienes cuenta?", size="3"),
                            rx.link(
                                "Registrate",
                                on_click=Login_state.register,
                                size="3",
                            ),
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
            padding="2em",  # Puedes añadir algo de padding para más consistencia visual
        ),
        width="100%",  # Asegura que el centro ocupa el ancho completo
        padding_top="4em",  # Añade este padding para dar espacio arriba
    )


================================================
File: Calendario/components/login_register.py
================================================
#login_register.py

# Calendario/components/login_card.py

import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.components.login_form import login_form
from Calendario.components.register_form import register_form

def login_card() -> rx.Component:
    """Componente que maneja el cambio entre login y registro."""
    return rx.cond(
        Login_state.mode == "login",
        login_form(),  # Muestra el formulario de inicio de sesión
        register_form(),  # Muestra el formulario de registro
    )


================================================
File: Calendario/components/register_form.py
================================================
# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register

def register_form() -> rx.Component:
    """Componente de registro con vistas separadas para móvil y desktop"""
    
    # Campos comunes
    username_field = rx.vstack(
    rx.hstack(
            rx.text("Usuario", size="3", weight="medium"),
            rx.button(
                rx.icon("user-check", color="white"),
                background="transparent",
                on_click=RegisterState.check_aviable_username,
                size="1",
                padding="2",
                _hover={"opacity": 0.8},
                is_disabled=RegisterState.username == ""
            ),
            rx.match(
                RegisterState.username_valid,
                (None, rx.text("")),  # Nada cuando es None
                (True, rx.icon("check", color="green")),  # Check verde independiente
                (False, rx.icon("x", color="red")),  # X roja independiente
            ),
            spacing="2",
            align="center"
        ),
            

        rx.input(
            rx.input.slot(rx.icon("user")),
            placeholder="Usuario",
            type="text",
            size="3",
            width="100%",
            value=RegisterState.username,
            on_change=RegisterState.set_username,
            border_color=rx.cond(
                RegisterState.errors["username"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(
            RegisterState.errors["username"] != "",
            rx.text(RegisterState.errors["username"], color="#EF4444", size="2")
        ),
        spacing="2",
        width="100%"
    )
    
    password_field = rx.vstack(
        rx.text("Contraseña", size="4", weight="medium"),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Contraseña",
            type=rx.cond(RegisterState.show_pasw, "text", "password"),
            size="3",
            width="100%",
            value=RegisterState.password,
            on_change=RegisterState.set_password,
            border_color=rx.cond(
                RegisterState.errors["password"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error contraseña
            RegisterState.errors["password"] != "",
            rx.text(
                RegisterState.errors["password"],
                size="2",
                color="#EF4444"
            )
        ),
        show_pasw_switch_register(),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Confirmar Contraseña",
            type="password",
            size="3",
            width="100%",
            value=RegisterState.confirm_password,
            on_change=RegisterState.set_confirm_password,
            border_color=rx.cond(
                RegisterState.errors["confirm_password"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error confirmar contraseña
            RegisterState.errors["confirm_password"] != "",
            rx.text(
                RegisterState.errors["confirm_password"],
                size="2",
                color="#EF4444"
            )
        ),
        spacing="2",
        width="100%"
    )
    
    email_field = rx.vstack(
        rx.text("Correo electrónico", size="4", weight="medium"),
        rx.input(
            rx.input.slot(rx.icon("mail")),
            placeholder="Correo electrónico",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.email,
            on_change=RegisterState.set_email,
            border_color=rx.cond(
                RegisterState.errors["email"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error email
            RegisterState.errors["email"] != "",
            rx.text(
                RegisterState.errors["email"],
                size="2",
                color="#EF4444"
            )
        ),
        rx.input(
            rx.input.slot(rx.icon("mail")),
            placeholder="Confirmar Correo",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.confirm_email,
            on_change=RegisterState.set_confirm_email,
            border_color=rx.cond(
                RegisterState.errors["confirm_email"] != "", "#EF4444", "#666666"),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  # Mensaje error confirmacion email
            RegisterState.errors["confirm_email"] != "",
            rx.text(
                RegisterState.errors["confirm_email"],
                size="2",
                color="#EF4444"
            )
        ),
        spacing="4",
        width="100%"
    )
    
    birthday_field = rx.vstack(
        rx.center(rx.text("Fecha de Nacimiento", size="4", weight="medium")),
        rx.hstack(
            rx.input(
                type="date",
                size="3",
                width="100%",
                value=RegisterState.birthday,
                on_change=RegisterState.set_birthday,
                border=rx.cond(
                    RegisterState.errors["birthday"] != "",
                    "1px solid #EF4444", "1px solid #666666"),
                _focus={"border": "1px solid #3182CE"},
                required=True
            ),
            rx.cond(  # Mensaje error cumpleaños
                RegisterState.errors["birthday"] != "",
                rx.text(
                    RegisterState.errors["birthday"],
                    size="2",
                    color="#EF4444"
                )
            ),
            
            rx.button(
                rx.icon("rotate-ccw"),
                on_click=rx.set_value("birthday", ""),
                background="transparent",
                _hover={"transform": "scale(1.2)"}
            ),
            width="100%",
            align="center"
        ),
        spacing="4",
        width="100%"
    )
    
    # Versión móvil
    mobile_view = rx.mobile_only(
        rx.vstack(
            username_field,
            password_field,
            email_field,
            birthday_field,
            spacing="6",
            width="100%"
        )
    )
    
    # Versión desktop
    desktop_view = rx.tablet_and_desktop(
        rx.hstack(
            rx.vstack(
                username_field,
                password_field,
                spacing="6",
                width="80%"
            ),
            rx.vstack(
                email_field,
                birthday_field,
                spacing="6",
                width="80%"
            ),
            spacing="6",
            width=["20","30em","40em","50em","60em"],
            max_width="60em",
            
        )
    )
    
    return rx.container(
        rx.vstack(
            rx.heading("Registra tu Usuario", size="6", text_align="center"),
            mobile_view,
            desktop_view,
            rx.button(
                "Registrarse",
                size="3",
                width=["90%", "50%"],
                on_click=RegisterState.register
            ),
            rx.hstack(
                rx.text("¿Ya estás registrado?"),
                rx.link("Inicia Sesión", on_click=Login_state.login),
                justify="center",
                opacity="0.8"
            ),
            
            spacing="6",
            width="100%",
            align="center"
        ),

        padding="2em",
        padding_top="4em",
        class_name="register-container"
    )


================================================
File: Calendario/components/register_form2.py
================================================
# Calendario/components/register_form.py

import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state
from Calendario.components.show_pasw_switch import show_pasw_switch_register
from Calendario.utils.api import check_existing_user

def register_form() -> rx.Component:
    """Componente del formulario de registro responsive."""
    return rx.container(
        rx.vstack(
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
            
            rx.cond(
                rx.is_mobile,
                # Versión móvil - Todo en VStack
                rx.vstack(
                    # Sección Usuario y Contraseña
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
                            value=RegisterState.username,
                            on_change=RegisterState.set_username,
                            border_color=rx.cond(
                                RegisterState.errors["username"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["username"] != "",
                            rx.text(
                                RegisterState.errors["username"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    
                    # Sección Contraseñas
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
                            value=RegisterState.password,
                            on_change=RegisterState.set_password,
                            border_color=rx.cond(
                                RegisterState.errors["password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["password"] != "",
                            rx.text(
                                RegisterState.errors["password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
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
                            value=RegisterState.confirm_password,
                            on_change=RegisterState.set_confirm_password,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_password"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_password"] != "",
                            rx.text(
                                RegisterState.errors["confirm_password"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    
                    # Sección Email
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
                            value=RegisterState.email,
                            on_change=RegisterState.set_email,
                            border_color=rx.cond(
                                RegisterState.errors["email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["email"] != "",
                            rx.text(
                                RegisterState.errors["email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
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
                            value=RegisterState.confirm_email,
                            on_change=RegisterState.set_confirm_email,
                            border_color=rx.cond(
                                RegisterState.errors["confirm_email"] != "", 
                                "#EF4444", 
                                "#666666"
                            ),
                            _focus={
                                "border_color": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "#EF4444", 
                                    "#3182CE"
                                ),
                                "box_shadow": rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "0 0 0 1px #EF4444", 
                                    "0 0 0 1px #3182CE"
                                )
                            }
                        ),
                        rx.cond(
                            RegisterState.errors["confirm_email"] != "",
                            rx.text(
                                RegisterState.errors["confirm_email"],
                                size="2",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Sección Fecha de Nacimiento
                    rx.vstack(
                        rx.center(
                            rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.center(
                                rx.input(
                                    id="birthday",
                                    type="date",
                                    size="3",
                                    width="100%",
                                    justify="center",
                                    required=True,
                                    value=RegisterState.birthday,
                                    on_change=RegisterState.set_birthday,
                                    border=rx.cond(
                                        RegisterState.errors["birthday"] != "",
                                        "1px solid #EF4444",
                                        "1px solid #666666"
                                    ),
                                    border_radius="8px",
                                    _hover={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        )
                                    },
                                    _focus={
                                        "border": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #3182CE"
                                        ),
                                        "box_shadow": rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "0 0 0 1px #EF4444",
                                            "0 0 0 1px #3182CE"
                                        )
                                    }
                                ),
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("rotate-ccw"),
                                on_click=rx.set_value("birthday",""),
                                background="transparent",
                                size="1",
                                margin_top="8px",
                                _hover={
                                    "transform": "scale(1.2)",
                                    "transition": "transform 0.2s ease",
                                    "cursor": "pointer"
                                },
                            ),
                        ),
                        rx.cond(
                            RegisterState.errors["birthday"] != "",
                            rx.text(
                                RegisterState.errors["birthday"],
                                size="2",
                                text_align="center",
                                width="100%",
                                style={"color": "#EF4444"}
                            )
                        ),
                        spacing="4",
                        width="100%",
                        align="center",
                    ),
                    spacing="6",
                    width="100%",
                ),

                # Version desktop 2 columnas
                rx.hstack(
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
                                value=RegisterState.username,
                                on_change=[RegisterState.set_username,],
                                border_color=rx.cond(
                                    RegisterState.errors["username"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["username"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["username"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["username"] != "",
                                rx.text(
                                    RegisterState.errors["username"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.password,
                                on_change=RegisterState.set_password,
                                border_color=rx.cond(
                                    RegisterState.errors["password"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["password"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["password"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["password"] != "",
                                rx.text(
                                    RegisterState.errors["password"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.confirm_password,
                                on_change=RegisterState.set_confirm_password,
                                border_color=rx.cond(
                                    RegisterState.errors["confirm_password"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["confirm_password"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["confirm_password"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["confirm_password"] != "",
                                rx.text(
                                    RegisterState.errors["confirm_password"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
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
                                value=RegisterState.email,
                                on_change=RegisterState.set_email,
                                border_color=rx.cond(
                                    RegisterState.errors["email"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["email"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["email"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["email"] != "",
                                rx.text(
                                    RegisterState.errors["email"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
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
                                value=RegisterState.confirm_email,
                                on_change=RegisterState.set_confirm_email,
                                border_color=rx.cond(
                                    RegisterState.errors["confirm_email"] != "", 
                                    "#EF4444", 
                                    "#666666"
                                ),
                                _focus={
                                    "border_color": rx.cond(
                                        RegisterState.errors["confirm_email"] != "", 
                                        "#EF4444", 
                                        "#3182CE"
                                    ),
                                    "box_shadow": rx.cond(
                                        RegisterState.errors["confirm_email"] != "", 
                                        "0 0 0 1px #EF4444", 
                                        "0 0 0 1px #3182CE"
                                    )
                                }
                            ),
                            rx.cond(
                                RegisterState.errors["confirm_email"] != "",
                                rx.text(
                                    RegisterState.errors["confirm_email"],
                                    size="2",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.center(
                                rx.text("Fecha de Nacimiento", size="4", weight="medium"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.center(
                                    rx.input(
                                        id="birthday",
                                        type="date",
                                        size="3",
                                        width="100%",
                                        justify="center",
                                        required=True,
                                        value=RegisterState.birthday,
                                        on_change=RegisterState.set_birthday,
                                        border=rx.cond(
                                            RegisterState.errors["birthday"] != "",
                                            "1px solid #EF4444",
                                            "1px solid #666666"
                                        ),
                                        border_radius="8px",
                                        _hover={
                                            "border": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "1px solid #EF4444",
                                                "1px solid #3182CE"
                                            )
                                        },
                                        _focus={
                                            "border": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "1px solid #EF4444",
                                                "1px solid #3182CE"
                                            ),
                                            "box_shadow": rx.cond(
                                                RegisterState.errors["birthday"] != "",
                                                "0 0 0 1px #EF4444",
                                                "0 0 0 1px #3182CE"
                                            )
                                        }
                                    ),
                                    width="100%",
                                ),
                                rx.button(
                                    rx.icon("rotate-ccw"),
                                    on_click=rx.set_value("birthday",""),
                                    background="transparent",
                                    size="1",
                                    margin_top="8px",
                                    _hover={
                                        "transform": "scale(1.2)",
                                        "transition": "transform 0.2s ease",
                                        "cursor": "pointer"
                                    },
                                ),
                            ),
                                    
                            
                            rx.cond(
                                RegisterState.errors["birthday"] != "",
                                rx.text(
                                    RegisterState.errors["birthday"],
                                    size="2",
                                    text_align="center",
                                    width="100%",
                                    style={"color": "#EF4444"}
                                )
                            ),
                            spacing="4",
                            width="50%",
                            align="center",
                            margin_left="20%"
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.button(
                            "Registrarse",
                            size="3",
                            width="50%",
                            justify="center",
                            on_click=RegisterState.register
                        ),
                        rx.hstack(
                            rx.text("¿Ya estás registrado?", size="3"),
                            rx.link(
                                "Inicia Sesión",
                                on_click=Login_state.login,
                                size="3",
                            ),
                            spacing="2",
                            justify="center",
                            opacity="0.8",
                        ),
                        spacing="6",
                        width="100%",
                        align="center",
                    ),
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            max_width="60em",
            padding="2em",
            padding_top="4em",
            on_mount=[RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    RegisterState.reset_errors()]
        )
    )


================================================
File: Calendario/components/show_pasw_switch.py
================================================
import reflex as rx
from Calendario.state.login_state import Login_state
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
def show_pasw_switch_login() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=Login_state.swith_on,
            color_scheme="jade"  # Pasar el estado del switch
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )

def show_pasw_switch_register() -> rx.Component:
    return rx.hstack(
        rx.switch(
            on_change=RegisterState.swith_on,  # Cambia el estado del switch
            is_checked=RegisterState.show_pasw,  # Estado actual del switch
            color_scheme="jade",
        ),
        rx.text("Mostrar contraseña"),
        padding_top="0.5em",
    )




================================================
File: Calendario/database/database.py
================================================
#database.py


import os
import dotenv
from typing import Union,List
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logging.basicConfig(level=logging.INFO)

class SupabaseAPI:

    dotenv.load_dotenv()

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def authenticate_user(self, username: str, password: str) -> Union[dict, None]:
        """
        Autentica a un usuario verificando su nombre y contraseña.

        Args:
            username (str): Nombre de usuario a buscar.
            password (str): Contraseña del nnnnnnn.

        Returns:
            dict | None: Datos del usuario si la autenticación es exitosa, o None si falla.
        """
        try:
            response = self.supabase.from_("user").select("*").ilike("username", username).execute()
            print(response.data)

            if response.data:
                user = response.data[0]
                if user["pasw"] == password:
                    logging.info(f"Usuario autenticado: {username}")
                    return user
        except Exception as e:
            logging.error(f"Error autenticando al usuario: {e}")
        return None
    

    def check_existing_user(self,username: str, email: str) -> dict:
        """
        Verifica si el username o email ya existen en la base de datos.

        Args:
            username (str): Nombre de usuario a verificar.
            email (str): Email a verificar.

        Returns:
            dict: Indica si existen el usuario o email.
        """
        existing_username= False
        existing_email = False

        try:

            response_user = self.supabase.from_("user").select("username").ilike("username", username).execute()
            existing_username= len(response_user.data) > 0

            response_email= self.supabase.from_("user").select("email").ilike("email",email).execute()
            existing_email= len(response_email.data) > 0

            return {'username':existing_username, 'email':existing_email}
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario o email: {e}")
            return {'username': False, 'email': False}
        
    def check_existing_username(self, username):
        try:
            response = self.supabase.from_("user").select("username").ilike("username", username).execute()
            return len(response.data) > 0  # Devuelve directamente el booleano
        
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario: {e}")
            return False

    def get_calendars(self, user_id: int) -> Union[List[Calendar], None]:
        try:
            response = (
                self.supabase
                .from_("calendars")
                .select("*")
                .eq("owner_id", user_id)
                .execute()
            )

            if response.data:
                calendars = [
                    Calendar(
                        id=cal['id'],
                        name=cal['name'],
                        owner_id=cal['owner_id'],
                        start_date=cal['start_date'],
                        end_date=cal['end_date'],
                        shared_with=cal.get('shared_with', []),
                        created_at=datetime.fromisoformat(
                            cal['created_at'].replace('Z', '+00:00')
                        ) if cal.get('created_at') else datetime.now(),
                        
                    )
                    for cal in response.data
                ]
                return calendars
                
        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None


    def create_calendar_with_days(self, user_id: int, calendar_name: str):
        try:
            # Calcular fechas de inicio y fin del mes actual
            today = datetime.today()
            start_date = today.replace(day=1)
            end_date = start_date + relativedelta(months=1) - timedelta(days=1)
            
            # Insertar calendario con las fechas calculadas
            calendar_data = {
                "name": calendar_name,
                "owner_id": user_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table("calendars").insert(calendar_data).execute()
            
            if response.data:
                # Crear días del mes
                days = []
                current_day = start_date
                while current_day <= end_date:
                    days.append({
                        "calendar_id": response.data[0]["id"],
                        "date": current_day.isoformat()
                    })
                    current_day += timedelta(days=1)
                
                # Insertar días en lote
                self.supabase.table("days").insert(days).execute()
                
                return Calendar(
                    id=response.data[0]["id"],
                    name=calendar_name,
                    owner_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    created_at=datetime.fromisoformat(response.data[0]["created_at"])
                )
        except Exception as e:
            print(f"Error creating calendar: {str(e)}")
        return None


================================================
File: Calendario/model/model.py
================================================
import reflex as rx
from datetime import datetime

class User(rx.Base):
    """
    Modelo para usuarios.
    """
    id: int
    username: str
    pasw: str
    email: str
    birthday: str
    created_at: datetime


class Calendar(rx.Base):
    """
    Modelo para calendarios.
    """
    id: int
    name: str
    owner_id: int  # Relación con el usuario propietario
    shared_with: list[int] = []  # Lista de IDs de usuarios compartidos
    created_at: datetime
    start_date : datetime
    end_date : datetime


class Meal(rx.Base):
    """
    Modelo para opciones de comidas y cenas.
    """
    id: int
    name: str  # Nombre de la comida o cena (ejemplo: "Pizza", "Ensalada")
    description: str = None  # Descripción opcional (ejemplo: ingredientes)


class Day(rx.Base):
    """
    Modelo para días dentro de un calendario.
    """
    id: int
    calendar_id: int  # Relación con el calendario
    date: datetime
    meal_id: int = None  # Relación con el modelo Meal (comida)
    dinner_id: int = None  # Relación con el modelo Meal (cena)
    comments: list[int] = []  # Lista de IDs de comentarios


class Comment(rx.Base):
    """
    Modelo para comentarios asociados a un día.
    """
    id: int
    day_id: int  # Relación con el día
    content: str  # Contenido del comentario
    owner_id: int  # Usuario que hizo el comentario
    created_at: datetime



================================================
File: Calendario/pages/calendar.py
================================================
import reflex as rx
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.calendar_view import calendar_view
from Calendario.components.current_user_button import current_user_button
from Calendario.state import user_state
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info,position="top-center")

@rx.page(route="/calendar",on_load=CalendarState.load_calendars)
def calendar() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.text(UserState.username),
            rx.cond(
                UserState.current_user,
                rx.vstack(
                    rx.button(
                        "Logout",
                        on_click=[UserState.logout]

                    ),
                    rx.text("CALENDARIOS"),
                    rx.button(on_click=CalendarState.load_calendars),
                    rx.cond(
                        CalendarState.calendars.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                CalendarState.calendars,
                                lambda calendar: rx.text(calendar.name)
                            ),
                            
                        ),
                        rx.text("NO HAY CALENDARIOS EN CALENDAR.PY")
                    ),
                ),
                rx.container(
                    rx.text("NO HAY NADIE LOGGEADO EN CALENDAR.PY"),
                    rx.button(
                        "Go Home",
                        on_click=rx.redirect("/")
                    )
                )
            ),
            calendar_creator(),

        )
    ),



================================================
File: Calendario/pages/index.py
================================================
from calendar import Calendar
import reflex as rx
 


from Calendario.components.current_user_button import current_user_button
from Calendario.components.calendar_view import calendar_view
from Calendario.components.login_register import login_card
from Calendario.state.calendar_state import CalendarState
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
from Calendario.database.database import SupabaseAPI
@rx.page(route="/", title="Calendario | Python", on_load=RegisterState.load_page()
         )
def index() -> rx.Component:
    return rx.container(
        rx.cond(
            UserState.current_user,
            rx.container(
                rx.spacer(
                    height="200px"
                ),
                rx.text("Redirecting..."),
                current_user_button()


            ),
            login_card()
        )
    )



================================================
File: Calendario/state/calendar_state.py
================================================
#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import SUPABASE_API, fetch_and_transform_calendars
from datetime import datetime
from dateutil.relativedelta import relativedelta



class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    current_month: datetime = datetime.today()  # Fecha del mes actual
    selected_day: Optional[datetime] = None  # Día seleccionado
    selected_day_data: Optional[Day] = None  # Datos del día seleccionado
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    current_calendar: Optional[Calendar] = None
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info : str = None
    new_calendar_name : str = ""
    new_calendar_month: str = datetime.today().strftime("%Y-%m")
    loading : bool = False

    def show_date_picker(self):
        return datetime.strptime(self.new_calendar_month, "%Y-%m").strftime("%B %Y")
    
    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True  # Activamos carga
            
            if not UserState.current_user:
                raise Exception("Usuario no autenticado")

            # Convertir mes seleccionado a fechas
            start_date = datetime.strptime(self.new_calendar_month, "%Y-%m")
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

            # Crear calendario en Supabase
            db = SupabaseAPI()
            user_state = await self.get_state(UserState)
            new_calendar = db.create_calendar_with_days(
                user_id=user_state.current_user.id,
                calendar_name=self.new_calendar_name,
                start_date=start_date,
                end_date=end_date
            )

            if new_calendar:
                self.calendars.append(new_calendar)
                return rx.window_alert(f"Calendario '{self.new_calendar_name}' creado con éxito!")
            
        except Exception as e:
            return rx.window_alert(f"Error: {str(e)}")
        finally:
            self.loading = False
            self.new_calendar_name = ""
            self.new_calendar_month = datetime.today().strftime("%Y-%m")

    def update_month(self, value: str):
        self.new_calendar_month = value


    @rx.event
    async def load_calendars(self):
        print("EN CALENDAR STATE LOAD  CALENDARS")

        try:
            user_state = await self.get_state(UserState)
            user_id = user_state.current_user.id
            
            if user_state.current_user is None:
                return rx.toast.error(
                    position="top-center",
                    title="Debes iniciar sesión para ver tus calendarios."
                )
                
            calendars = await fetch_and_transform_calendars(user_id)
            if calendars:
                self.calendars = calendars
                print(f"Calendarios cargados: {[f'ID: {cal.id}, Nombre: {cal.name}, Propietario ID: {cal.owner_id}, Compartido con: {cal.shared_with}, Creado en: {cal.created_at}' for cal in self.calendars]}")
            else:
                print("No se encontraron calendarios.")
                
        except Exception as e:
            print(e)


    @rx.event
    def set_current_calendar(self, calendar : Calendar):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.current_calendar = calendar
        print(f"Calendario actualizado: {self.current_calendar.name}")

    @rx.event
    def clean(self):
        self.current_month = datetime.today()
        self.selected_day = None
        self.selected_day_data = None
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.current_calendar = None 
        self.calendars = []  # Reset to empty list

        return rx.toast.info(
             position="top-center",
             title="")


================================================
File: Calendario/state/login_state.py
================================================
#login_card_state

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
class Login_state(rx.State):
    """
    Manejador de estado para la tarjeta de inicio de sesión en Reflex.
    """
    is_open: bool = False
    mode: str = "login"
    show_pasw: bool = False


    @rx.event
    def login(self, mode="login"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return UserState.restart_pasw()

    @rx.event
    def register(self, mode="register"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return [RegisterState.reset_switch(),
                RegisterState.reset_inputs(),
                ]  # Reinicia el switch en el formulario de registro


    @rx.event
    def close(self):
        self.is_open = False

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value


================================================
File: Calendario/state/register_state.py
================================================
# register_state.py


from Calendario.utils.api import check_existing_user, register_user, check_existing_username
from Calendario.utils.send_email import send_welcome_email
from datetime import datetime
import reflex as rx 

class RegisterState(rx.State):
    username : str = ""
    password : str = ""
    confirm_password : str = ""
    email : str = ""
    confirm_email : str = ""
    birthday : str = ""
    show_pasw : bool = False
    errors: dict = {
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }
    username_valid : bool = None


    @rx.event
    def reset_errors(self):
        self.errors = {k: "" for k in self.errors}
    @rx.event
    async def register(self):
        # Resetear errores
        self.errors = {k: "" for k in self.errors}
        has_errors = False

        # Verificar si el usuario/email ya existen
        existing = await check_existing_user(self.username, self.email)
        if existing["username"]:
            self.errors["username"] = "El nombre de usuario ya está registrado"
            has_errors = True
        if existing["email"]:
            self.errors["email"] = "El correo electrónico ya está registrado"
            has_errors = True


        # Validación de username
        if not self.username:
            self.errors["username"] = "Usuario requerido"
            has_errors = True
        else:
            # Verificar que la longitud esté entre 6 y 16 caracteres
            if len(self.username) < 4 or len(self.username) > 16:
                self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                has_errors = True

            # Verificar que contenga al menos un número
            elif not any(char.isdigit() for char in self.username):
                self.errors["username"] = "El usuario debe contener al menos un número"
                has_errors = True

            # Verificar que no contenga caracteres especiales (solo letras y números)
            elif not self.username.isalnum():
                self.errors["username"] = "El usuario no puede contener caracteres especiales"
                has_errors = True

        # Validación de email
        if not self.validate_email(self.email.lower()):
            self.errors["email"] = "Email inválido"
            has_errors = True
        elif self.email.lower() != self.confirm_email.lower():
            self.errors["confirm_email"] = "Los emails no coinciden"
            has_errors = True

        import re
        # Validación de contraseña
        if not self.password:
            self.errors["password"] = "Contraseña requerida"
            has_errors = True
        else:
            # Patrón que requiere:
            # - Al menos 8 caracteres
            # - Al menos una letra mayúscula
            # - Al menos un dígito
            # - Al menos un carácter especial (no alfanumérico)
            pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
            if not re.match(pattern, self.password):
                self.errors["password"] = ("La contraseña debe tener mínimo 8 caracteres, "
                                            "al menos 1 mayúscula, 1 número y 1 carácter especial")
                has_errors = True
            elif self.password != self.confirm_password:
                self.errors["confirm_password"] = "Las contraseñas no coinciden"
                has_errors = True

        # Validación de fecha
        if not self.birthday:
            self.errors["birthday"] = "Fecha requerida"
            has_errors = True
        else:
            try:
                birth_date = datetime.strptime(self.birthday, '%Y-%m-%d')
                if birth_date > datetime.now():
                    self.errors["birthday"] = "Fecha inválida"
                    has_errors = True
            except ValueError:
                self.errors["birthday"] = "Formato inválido\n (DD-MM-AAAA)"
                has_errors = True

        if has_errors:
            return rx.toast.error("No ha sido posible el registro",
                                  position="top-center")


        # Si no hay errores, proceder con registro
        if not has_errors:
            try:
                # Aquí iría la lógica de registro en la base de datos
                new_user = await register_user(
                    self.username,
                    self.password,
                    self.email,
                    self.birthday,
                )
                
                if new_user == True:
                # Enviar correo de bienvenida
                    send_welcome_email(self.email, self.username)
                
                    from Calendario.state.login_state import Login_state

                    
                    return [rx.toast.success(
                        "¡Registro exitoso! Revisa tu correo electrónico",
                        position="top-center"
                    ),Login_state.login()]
                else:
                    self.password=""
                    self.confirm_password=""
                    return rx.toast.error(
                        "No se ha podido registrar el usuario",
                        position="top-center",
                    )
            except Exception as e:
                return rx.toast.error(
                    f"Error en el registro: {str(e)}",
                    position="top-center"
                )

    def validate_email(self, email: str) -> bool:
        import re
        pattern = r"""
        ^                           # Inicio de la cadena
        (?!.*\.\.)                  # No permite dos puntos consecutivos
        [\w.%+-]+                   # Parte local (caracteres permitidos)
        (?<!\.)                     # No termina con un punto
        @                           # Separador
        (?:                         # Dominio:
            [a-zA-Z0-9]             #   - Inicia con alfanumérico
            (?:[a-zA-Z0-9-]{0,61}  #   - Permite hasta 61 caracteres (incluyendo guiones)
            [a-zA-Z0-9])?           #   - Termina con alfanumérico (no guión)
            \.                      #   - Separador por punto
        )+                          # Múltiples subdominios
        [a-zA-Z]{2,63}              # TLD (2-63 caracteres alfabéticos)
        $                           # Fin de la cadena
        """
        return bool(re.fullmatch(pattern, email, re.VERBOSE))


    @rx.event
    async def check_aviable_username(self):
        if not self.username:
            return
        
        try:
            existing = await check_existing_username(self.username)
            if existing:
                self.username_valid = False
                self.errors["username"] = "El nombre de usuario ya está registrado"
            else:

                                            # Verificar que la longitud esté entre 6 y 16 caracteres
                if len(self.username) < 4 or len(self.username) > 16:
                    self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                    self.username_valid = False


                # Verificar que contenga al menos un número
                elif not any(char.isdigit() for char in self.username):
                    self.errors["username"] = "El usuario debe contener al menos un número"
                    self.username_valid = False

                # Verificar que no contenga caracteres especiales (solo letras y números)
                elif not self.username.isalnum():
                    self.errors["username"] = "El usuario no puede contener caracteres especiales"
                    self.username_valid = False
                
                else:
                    self.username_valid = True
                    self.errors["username"] = ""

        except Exception as e:
            print(f"Error al verificar el nombre de usuario: {str(e)}")
            self.username_valid = None


    @rx.event
    def set_username(self, username: str):
        self.username = username
        print(f"Usuario para registro actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        self.password = password
        print(f"Contraseña para registro actualizada: {self.password}")

    @rx.event
    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password
        print(f"Confirmar contraseña para registro actualizada: {self.confirm_password}")
    @rx.event
    def set_email(self, email: str):
        self.email = email
        print(f"Correo electrónico para registro actualizado: {self.email}")
    @rx.event
    def set_confirm_email(self, confirm_email: str):
        self.confirm_email = confirm_email
        print(f"Confirmar correo electrónico para registro actualizado: {self.confirm_email}")

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def reset_switch(self):
        """Reinicia el estado del switch a False."""
        self.show_pasw = False
    
    @rx.event
    def reset_inputs(self):
        """Reinicia todos los inputs."""
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.email = ""
        self.confirm_email = ""
        self.birthday = ""
        self.errors = {k: "" for k in self.errors}
        self.username_valid = None

    @rx.event
    def load_page(self):
        self.password = ""
        self.confirm_password = ""
        self.confirm_email = ""
        self.birthday = ""
        self.reset_errors()
        self.username_valid = None



================================================
File: Calendario/state/user_state.py
================================================
#user_state.py

import reflex as rx
import time
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user

class UserState(rx.State):
    """
    Manejador de estado para los datos del usuario en Reflex.
    """

    username: str = ""  # Guarda el nombre de usuario ingresado
    password: str = ""  # Guarda la contraseña ingresada
    current_user: User = None  # Mantiene al usuario autenticado


    @rx.event
    def press_enter(self, key: str):
        if key == "Enter":
            # Return the event instead of calling it directly
            return UserState.login
    
    def return_username(self) -> str:
        return self.username
    
    @rx.event
    def set_username(self, username: str):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.username = username
        print(f"Username actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        """
        Actualiza la contraseña en el estado.
        """
        self.password = password
        print(f"Password actualizado: {self.password}")

    @rx.event
    async def login(self):

        if not self.username or not self.password:
            self.clear_paswd()

        try:
            user_data = await authenticate_user(self.username.lower(), self.password)

            
            if user_data:
                self.current_user = user_data
                self.username = ""
                self.password = ""
                # Llamamos al evento para cargar los calendarios en el estado de CalendarState
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                # Limpiamos los campos de usuario y contraseña
                self.username = ""
                self.password = ""
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        except Exception as e:
            print(f"Error al intentar iniciar sesión: {e}")
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )


    @rx.event
    def clear_paswd(self):
        self.password = ""
        print("Contraseña borrada:", self.password)  # Para depuración

    



    @rx.event

    async def logout(self):
        from Calendario.state.calendar_state import CalendarState
        """
        Cierra la sesión del usuario actual.
        """
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()
        self.current_user = None
        self.username = ""
        self.password = ""
        CalendarState.toast_info = "Cerrando la sesión"
        return [
            rx.redirect("/")
        ]
    

    @rx.event
    def restart_pasw(self):
        self.password=""


================================================
File: Calendario/utils/api.py
================================================
#api.py
import reflex as rx
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment
from datetime import datetime

from typing import Union,List,Optional

SUPABASE_API = SupabaseAPI()

async def authenticate_user(username: str, password: str) -> Union[User, None]:
    """
    Autentica al usuario y devuelve un objeto User si es exitoso.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña del usuario.

    Returns:
        User | None: Instancia del usuario autenticado o None si falla.
    """
    if not username or not password:
        return None

    user_data = SUPABASE_API.authenticate_user(username, password)
    if user_data:
        
        return User(**user_data)  # Convierte los datos en una instancia de User

    return None

async def check_existing_user(username: str, email: str,) -> dict:
    return SUPABASE_API.check_existing_user(username, email)

async def check_existing_username(username: str) -> bool:
    return SUPABASE_API.check_existing_username(username)

async def register_user(username: str, password: str, email: str, birthday: str) -> Union[User, None]:
    try: 
        user_data = {
            "username": username,
            "pasw": password,
            "email": email,
            "birthday": birthday
        }
        
        # Inserta el usuario en la base de datos
        response = SUPABASE_API.supabase.table("user").insert(user_data).execute()
        
        if response.data:
            # Convierte los datos de Supabase a un objeto User
            return True
        return None
        
    except Exception as e:
        print(f"Error al registrar el usuario: {e}")
        return None
    
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    calendars = SUPABASE_API.get_calendars(user_id)
    if calendars is None:
        print("No se encontraron datos de calendarios.")
        return []
    return calendars



================================================
File: Calendario/utils/send_email.py
================================================
import smtplib

def send_welcome_email(email, username):
    # Configuración del servidor SMTP (Gmail en este ejemplo)
    servidor_smtp = "smtp.gmail.com"
    puerto = 587
    admin = "verificacionespython@gmail.com"
    pasw = "cmblnedixejwrqag"  # Reemplaza con tu contraseña de aplicación

    # Configuración del mensaje de bienvenida
    asunto = "¡Bienvenido a tu Calendario!"
    cuerpo = f"""
    Hola {username},

    ¡Bienvenido a tu Calendario!

    Estamos emocionados de tenerte con nosotros. Ahora puedes organizar tus comidas/cenas, e interactuar con los comentarios.

    ¡Gracias por unirte a nuestra comunidad!

    Saludos,
    El equipo de Calendario
    """
    correo = f"Subject: {asunto}\n\n{cuerpo}"

    try:
        with smtplib.SMTP(servidor_smtp, puerto) as server:
            server.starttls()
            server.login(admin, pasw)
            server.sendmail(admin, email, correo.encode('utf-8'))
        print(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


================================================
File: assets/css/styles.css
================================================
/* assets/css/styles.css */
@media (max-width: 768px) {
    .register-container {
        padding: 1em !important;
    }
    
    .register-input {
        font-size: 16px; /* Mejor para inputs móviles */
    }
}


