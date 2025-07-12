# Calendario/components/register_form.py

import datetime
import reflex as rx
from Calendario.state.register_state import RegisterState
from Calendario.components.show_pasw_switch import show_pasw_switch_register


def register_form() -> rx.Component: #Creamos el formulario de registro de usuario
    #Campo de usuario
    username_field = rx.vstack(
    rx.hstack(
            rx.text("Usuario", size="3", weight="medium"),
            rx.button( #Botón que verifica la disponibilidad del nombre de usuario
                rx.icon("user-check", color="white"),
                background="transparent",
                on_click=RegisterState.check_aviable_username, #Función que valida el nombre
                size="1",
                padding="2",
                _hover={"opacity": 0.8,
                        "transform": "scale(1.2)"},
                is_disabled=RegisterState.username == "" #Solo actúa si detecta algo escrito
            ),
            rx.match(
                RegisterState.username_valid, #Valor que determina si el usuario es valido
                (None, rx.text("")),  #No muestra nada si el registro es none
                (True, rx.icon("check", color="green")),  # Check verde cuando el usuario es valido
                (False, rx.icon("x", color="red")),  # X roja cuando el usuario no es valido
            ),
            spacing="2",
            align="center"
        ),
            

        rx.input( #Input de usuario
            rx.input.slot(rx.icon("user")), #Icono dentro del input
            placeholder="Usuario",
            type="text",
            size="3",
            width="100%",
            value=RegisterState.username,
            on_change=RegisterState.set_username, #Cambia el usuario en el estado
border=rx.cond(
    RegisterState.errors["username"] != "",
    "1px solid #EF4444",  # Rojo si hay error
    rx.cond(
        RegisterState.username_valid == None,
        "#666666",  # Gris por defecto
        rx.cond(
            RegisterState.username_valid == True,
            "1px solid #16A34A",  # Verde si es válido
            "1px solid #EF4444"   # Rojo si no es válido
        )
    )
),
            _focus={"border_color": "#3182CE"}, #Borde azul en focus
            required=True
        ),
        rx.cond( #Muestra los errores para usuario si se generan
            RegisterState.errors["username"] != "",
            rx.text(RegisterState.errors["username"],
            color="#EF4444", size="2",
            white_space="pre-line",  # Permite saltos de línea
            max_width=["85vw", "100%"],  # Limita el ancho en móviles
            word_break="break-word",     # Rompe palabras largas si es necesario
            )
        ),
        spacing="2",
        width="100%"
    )
    
    #Campo de contraseña
    password_field = rx.vstack( 
        rx.text("Contraseña", size="4", weight="medium"),
        rx.input( #Input de contraseña
            rx.input.slot(rx.icon("lock")),
            placeholder="Contraseña",
            #Alterna entre campo de texto o de contraseña
            type=rx.cond(RegisterState.show_pasw, "text", "password"), 
            size="3",
            width="100%",
            value=RegisterState.password,
            on_change=RegisterState.set_password,
            border=rx.cond(
                RegisterState.errors["password"] != "",
                "1px solid #EF4444",  
                "#666666"   
            ),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  #Muestra los errores para contreaseña si se generan
            RegisterState.errors["password"] != "",
            rx.text(
                RegisterState.errors["password"],
                size="2",
                color="#EF4444",
                white_space="pre-line",  # Permite saltos de línea
                max_width=["75vw", "100%"],  # Limita el ancho en móviles
                word_break="break-word",     # Rompe palabras largas si es necesario
            )
        ),
        show_pasw_switch_register(), #Componente para mostrar contraseña
        rx.input( #Input de confirmar contraseña
            rx.input.slot(rx.icon("lock")),
            placeholder="Confirmar Contraseña",
            type="password",
            size="3",
            width="100%",
            value=RegisterState.confirm_password,
            on_change=RegisterState.set_confirm_password,
            border=rx.cond(
                RegisterState.errors["confirm_password"] != "",
                "1px solid #EF4444",
                "#666666"   
            ),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  #Muestra los errores para confirmar contreaseña si se generan
            RegisterState.errors["confirm_password"] != "",
            rx.text(
                RegisterState.errors["confirm_password"],
                size="2",
                color="#EF4444",
                max_width=["85vw", "100%"], 
            )
        ),
        spacing="2",
        width="100%"
    )
    #Campo de email
    email_field = rx.vstack(
        rx.text("Correo electrónico", size="4", weight="medium"),
        rx.input( #Input de email
            rx.input.slot(rx.icon("mail")),
            placeholder="Correo electrónico",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.email,
            on_change=RegisterState.set_email,
            border=rx.cond(
                RegisterState.errors["email"] != "",
                "1px solid #EF4444",
                "#666666"   
            ),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  #Muestra los errores para email si se generan
            RegisterState.errors["email"] != "",
            rx.text(
                RegisterState.errors["email"],
                size="2",
                color="#EF4444",
                white_space="pre-line",  # Permite saltos de línea
                max_width=["85vw", "100%"],  # Limita el ancho en móviles
                word_break="break-word",     # Rompe palabras largas si es necesario
            )
        ),
        rx.input( #Input de confirmar email
            rx.input.slot(rx.icon("mail")),
            placeholder="Confirmar Correo",
            type="email",
            size="3",
            width="100%",
            value=RegisterState.confirm_email,
            on_change=RegisterState.set_confirm_email,
            border=rx.cond(
                RegisterState.errors["confirm_email"] != "",
                "1px solid #EF4444",
                "#666666"   
            ),
            _focus={"border_color": "#3182CE"},
            required=True
        ),
        rx.cond(  #Muestra los errores para confirmar email si se generan
            RegisterState.errors["confirm_email"] != "",
            rx.text(
                RegisterState.errors["confirm_email"],
                size="2",
                color="#EF4444",
                white_space="pre-line",  # Permite saltos de línea
                max_width=["85vw", "100%"],  # Limita el ancho en móviles
                word_break="break-word",     # Rompe palabras largas si es necesario
            )
        ),
        spacing="4",
        width="100%"
    )
    
    #Campo para fecha de nacimiento
    birthday_field = rx.vstack(
        rx.center(rx.text("Fecha de Nacimiento", size="4", weight="medium")),
        rx.vstack(
            rx.hstack(


                rx.input(
                    type="date",
                    size="3",
                    width="100%",
                    value=RegisterState.birthday,
                    on_change=RegisterState.set_birthday,
                    border=rx.cond(
                        RegisterState.errors["birthday"] != "",
                        "1px solid #EF4444", "#666666"),
                    _focus={"border": "1px solid #3182CE"},
                    required=True,
                    #Establecemos los parámetros mínimos para el calendario
                    min="1950-01-01",
                    max=datetime.date.today().isoformat(),
                ),
                
                rx.button( #Botón para reiniciar la fecha
                    rx.icon("rotate-ccw"),
                    on_click=rx.set_value("birthday", ""), #Limpia el valor en estado
                    background="transparent",
                    _hover={"transform": "scale(1.2)"}
                ),
                width="100%",
                align="center"
            ),
            rx.cond(  #Muestra los errores para confirmar email si se generan
                RegisterState.errors["birthday"] != "",
                rx.text(
                    RegisterState.errors["birthday"],
                    size="2",
                    color="#EF4444",
                    white_space="pre-line",  # Permite saltos de línea
                    max_width=["85vw", "100%"],  # Limita el ancho en móviles
                    word_break="break-word",     # Rompe palabras largas si es necesario
                )
            ),
            
            spacing="4",
            width="100%",
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
            width="100%",

        )
    )
    
    # Versión tablet/escritorio con dos columnas
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
        # Botón de volver al login, con texto en tablet y escritorio
        rx.box(
            rx.mobile_only(
                rx.button(
                    rx.icon("arrow-left", size=18),
                    on_click=rx.redirect("/"), #Redirecciona al inicio
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    style={"position": "realative", "left": "1.5rem", "top": "1.5rem"}
                )
            ),
            rx.tablet_and_desktop(
                rx.button(
                    rx.icon("arrow-left", size=18),
                    "Inicio",
                    on_click=rx.redirect("/"), #Redirecciona al inicio
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
                )
            ),
            z_index="1000"
        ),
        
        rx.vstack( #Cabecera seguido del formularío en estilo movil o tablet/escritorio
            rx.heading("Registra tu Usuario", size="6", text_align="center",margin_top=["2em", "10em"]),  # Margen superior responsive),
            mobile_view,
            desktop_view,
            rx.button( #Boton de registro
                rx.icon("user-plus",size=18),
                "Registrarse",
                size="3",
                variant="surface",
                color_scheme="blue",
                radius="full",
                width=["90%", "50%"],
                _hover={"transform": "scale(1.05)"},
                on_click=[RegisterState.register,RegisterState.check_aviable_username] #Función que valida el registro
            ),
            rx.hstack( #Mensaje para ir al login
                rx.text("¿Ya estás registrado?"),
                rx.link("Inicia Sesión", on_click=rx.redirect("/login")), #Redirecciona al login
                justify="center",
                opacity="0.8",

            ),
            spacing="6",
            width="100%",
            align="center",
            min_height="85vh",
            position="relative",
        ),
        padding="2em",
        class_name="register-container",
        height="100%",

      )      