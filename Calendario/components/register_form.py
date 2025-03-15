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
                _hover={"opacity": 0.8,
                        "transform": "scale(1.2)"},
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
        # Botón de volver al login (nuevo)
        rx.box(
            rx.button(
                rx.icon("arrow-left", size=18),
                "Volver",
                on_click=rx.redirect("/login"),
                variant="soft",
                color_scheme="blue",
                size="2",
                radius="full",
                _hover={"transform": "scale(1.05)"},
                style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
            ),
            z_index="1000"
        ),
        
        rx.vstack(
            rx.heading("Registra tu Usuario", size="6", text_align="center"),
            mobile_view,
            desktop_view,
            rx.button(
                rx.icon("user-plus",size=18),
                "Registrarse",
                size="3",
                variant="surface",
                color_scheme="blue",
                radius="full",
                width=["90%", "50%"],
                _hover={"transform": "scale(1.05)"},
                on_click=RegisterState.register
            ),
            rx.hstack(
                rx.text("¿Ya estás registrado?"),
                rx.link("Inicia Sesión", on_click=rx.redirect("/login")),
                justify="center",
                opacity="0.8"
            ),
            spacing="6",
            width="100%",
            align="center"
        ),
        padding="2em",
        padding_top="4em",  # Aumentamos padding superior para no solapar con el botón
        class_name="register-container",
        position="relative"
    )