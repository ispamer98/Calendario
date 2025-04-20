================================================
FILE: requirements.txt
================================================
reflex==0.7.7
dotenv
supabase
bcrypt>=4.0.1
pytz


================================================
FILE: rxconfig.py
================================================
import reflex as rx

config = rx.Config(
    app_name="Calendario",
    show_built_with_reflex=False
)



================================================
FILE: assets/manifest.json
================================================
{
    "name": "CalendPy",
    "short_name": "CalendPy",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#000000",
    "theme_color": "#1e1e1e",
    "description": "Calendario de comidas",
    "icons": [
      {
        "src": "logo.png",
        "type": "image/png",
        "sizes": "512x256",
        "purpose": "any maskable"
      },
      {
        "src": "logo.png",
        "type": "image/png",
        "sizes": "256x128",
        "purpose": "any maskable"
      }
    ]
  }


================================================
FILE: assets/css/styles.css
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
FILE: Calendario/__init__.py
================================================



================================================
FILE: Calendario/Calendario.py
================================================
"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar


import reflex as rx



app = rx.App(
        theme=rx.theme(
        appearance="dark",
        has_background=False,
        radius="large",
        accent_color="blue",
        height="100vh",
        stylesheets=[
        "https://fonts.googleapis.com/css2?family=Sarina&display=swap",
        ],
        ),
        head_components=[rx.el.link(rel="manifest", href="/manifest.json")]
        
)



================================================
FILE: Calendario/components/calendar_creator.py
================================================
# Calendario/components/calendar_creator.py
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calendar_creator() -> rx.Component:
    # Obtener fecha actual
    today = datetime.today()
    
    # Calcular rango permitido (mes actual hasta 12 meses en el futuro)
    min_date = today.strftime("%Y-%m")
    max_date = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.box()
        ),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading("Crear nuevo Calendario", size="5"),
                    rx.text("Nombre del Calendario", size="2", color="gray"),
                    rx.input(
                        placeholder="Ej: Comidas de Marzo",
                        name="calendar_name",
                        required=True,
                        value=CalendarState.new_calendar_name,
                        on_change=CalendarState.set_new_calendar_name,
                        _hover={"border_color": "blue.400"}
                    ),
                    rx.text("Selecciona el mes", size="2", color="gray", margin_top="1em"),
                    rx.input(
                        type="month",
                        name="calendar_month",
                        required=True,
                        min=min_date,
                        max=max_date,
                        value=CalendarState.new_calendar_month,
                        on_change=CalendarState.set_new_calendar_month
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                type="button",
                                color_scheme="red",
                                size="3",
                                variant="soft",
                                on_click=CalendarState.close_calendar_creator,
                                _hover={
                                    "background": "var(--red-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        rx.button(
                            "Crear",
                            type="submit",
                            variant="soft",
                            color_scheme="green",
                            on_click=CalendarState.create_calendar,
                            size="3",
                            _hover={
                                "background": "var(--green-9)",
                                "color": "white"
                            }
                        ),
                        spacing="3",
                        margin_top="2em",
                        justify="end"
                    ),
                    spacing="3",
                    width="100%",
                    align_items="center",
                ),
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="2em",
            border_radius="8px",
            
        ),
        open=CalendarState.show_calendar_creator,
    )


================================================
FILE: Calendario/components/calendar_sharer.py
================================================
import reflex as rx
from Calendario.state.calendar_state import CalendarState



# Calendario/components/calendar_sharer.py
def calendar_sharer() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Compartir calendario", variant="soft", size="3")
        ),
        rx.dialog.content(
            rx.vstack(
                rx.heading("Compartir calendario", size="5"),
                rx.input(
                    placeholder="Nombre de usuario",
                    value=CalendarState.username_to_share,
                    on_change=CalendarState.set_username_to_share,
                    autofocus=True
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray")
                    ),
                    rx.button(
                        "Compartir", 
                        color_scheme="blue",
                        on_click=CalendarState.share_calendar
                    )
                ),
                rx.cond(
                    CalendarState.error_message,
                    rx.text(CalendarState.error_message, color="red", size="2")
                )
            ),
            title="Compartir calendario",
            size="3"
        ),
        open=CalendarState.show_calendar_sharer,
        on_open_change=lambda opened: (
            rx.cond(
    opened,
    CalendarState.open_calendar_sharer(),
    CalendarState.close_calendar_sharer()
)
        )
    )


================================================
FILE: Calendario/components/current_user_button.py
================================================



================================================
FILE: Calendario/components/day_button.py
================================================
import reflex as rx
from Calendario.components import meal_editor
from Calendario.model.model import Day, Meal
from datetime import datetime
from Calendario.state.calendar_state import CalendarState
from Calendario.components.meal_editor import meal_editor
from Calendario.state.day_state import DayState

def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.vstack(
                        rx.mobile_only(
                            rx.text(
                                rx.moment(day.date, format="D"),
                                size="3",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.tablet_and_desktop(
                            rx.text(
                                rx.moment(day.date, format="DD"),
                                size="2",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.cond(
                                    day.meal != None,
                                    rx.icon("utensils-crossed", 
                                            size=12,  # Tamaño fijo pequeño
                                            color="var(--green-9)"),
                                    
                                ),
                                rx.cond(
                                    day.dinner != None,
                                    rx.icon("utensils-crossed",
                                            size=12,
                                            color="var(--blue-9)"),
                                    
                                ),
                                rx.cond(
                                    day.comments == True,
                                    rx.icon("message-square-more",
                                            size=12,
                                            color="var(--orange-9)"),
                                    
                                ),
                                spacing="1",
                                justify="center",
                                padding_x="1",
                                position="relative"  # Añadido para mejor control
                            ),
                            spacing="1",
                            align="center",
                            width="100%",
                            height="20px"
                        ),
                        spacing="1",
                        align="center",
                        width="100%"
                    ),
                    style={
                        # Estilos base (móvil primero)
                        "width": "12vw",
                        "height": "12vw",
                        "min_width": "40px",
                        "min_height": "40px",
                        "max_width": "70px",
                        "max_height": "70px",
                        
                        # Media queries usando reflex
                        "@media (min-width: 768px)": {
                            "width": "10vw",
                            "height": "10vw",
                            "max_width": "60px",
                            "max_height": "60px"
                        },
                        "@media (min-width: 1024px)": {
                            "width": "8vw",
                            "height": "8vw",
                            "max_width": "70px",
                            "max_height": "70px"
                        }
                    },
                    padding="1",
                    border_radius="md",
                    background=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "linear-gradient(45deg, #4F46E5, #3B82F6)",
                        "rgba(255, 255, 255, 0.05)"
                    ),
                    border=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "none",
                        "1px solid rgba(255, 255, 255, 0.1)"
                    ),
                    box_shadow=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "lg",
                        "sm"
                    ),
                    _hover={
                        "transform": "scale(1.05)",
                        "box_shadow": "xl"
                    },
                    transition="all 0.2s",
                    
                    
                )
            ),
            rx.popover.content(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                        rx.moment(
                            day.date,
                            format="dddd, D [de] MMMM [del] YYYY", 
                            locale="es"
                        ),
                        size="2",
                        style={"text-transform": "capitalize"}
                        ),
                        
                        rx.icon(
                            "utensils-crossed",
                            color="grey",  # Color razonable para un botón de edición
                            size=18,
                            
                            style={
                                "cursor": "pointer",    # Cambia el cursor al pasar sobre el icono
                            },
                            _hover={
                                "transform": "scale(1.3)",  # Aumenta de tamaño en hover
                                "transition": "transform 0.2s"  # Transición suave
                            },
                            on_click=DayState.set_current_day(day)  # Al hacer clic, se abre meal_editor(day)
                        ),
                        rx.icon(
                            "message-square-more",
                            color="grey",
                            size=18,
                            style={
                                "cursor": "pointer",    # Cambia el cursor al pasar sobre el icono
                            },
                            _hover={
                                
                                "transform": "scale(1.3)",  # Aumenta de tamaño en hover
                                "transition": "transform 0.2s"  # Transición suave
                            },
                            on_click=DayState.toggle_comment_input
                        ),
                        width="100%",
                        justify="between",
                    ),
                    
                    
                    rx.divider(),
                    rx.cond(
                        day.meal != None,
                        rx.vstack(
                            rx.text("Comida:", 
                                    size="2", 
                                    color="var(--green-9)", 
                                    weight="bold"),
                            rx.text(day.meal, 
                                    size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        day.dinner != None,
                        rx.vstack(
                            rx.text("Cena:", 
                                    size="2", 
                                    color="var(--blue-9)", 
                                    weight="bold"),
                            rx.text(day.dinner, 
                                    size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        DayState.current_comments.length() > 0,
                        rx.vstack(
                            rx.text(
                                "Comentarios:", 
                                size="2", 
                                color="var(--orange-9)", 
                                weight="bold",
                                width="100%"
                            ),
                            rx.box(
                                rx.foreach(
                                    DayState.reversed_comments,
                                    lambda comment: rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.box(
                                                    rx.text(
                                                        comment.user.username,
                                                        weight="bold",
                                                        color="var(--accent-9)",
                                                        size="2",
                                                        padding_x="0.5em",
                                                    ),
                                                    background="rgba(255, 255, 255, 0.1)",
                                                    border_radius="4px",
                                                    margin_right="1em"
                                                ),
                                                rx.box(
                                                    rx.moment(
                                                        comment.created_at, 
                                                        format="DD/MM HH:mm",
                                                        color="gray.500",
                                                        size="1"
                                                    ),
                                                    margin_left="auto"
                                                ),
                                                rx.icon(
                                                    "trash",
                                                    color="var(--red-9)",
                                                    size=16,
                                                    style={"cursor" : "pointer"},
                                                    _hover={
                                                        "transform" : "scale(1.3)",
                                                        "transition" : "transform 0.2s"
                                                    },
                                                    on_click= lambda: DayState.delete_comment(comment.id,day),
                                                    margin_right="1em"

                                                ),
                                                width="100%",
                                                align_items="center"
                                            ),
                                            rx.hstack(
                                                rx.text("·", color="var(--jade-9)", size="2"),
                                                rx.scroll_area(
                                                    rx.text(
                                                        comment.content,
                                                        color="var(--jade-11)",
                                                        size="2",
                                                        weight="light",
                                                        style={
                                                            "display": "block",
                                                            "overflow": "auto",
                                                            "text_overflow": "ellipsis",
                                                            "max_height": "2.8em",  # Aproximadamente 2 líneas (ajusta según tu fuente/size)
                                                            "line_height": "1.4em", # Asegura el cálculo de altura de línea
                                                        },
                                                        white_space="normal",  # Permite saltos de línea
                                                    ),
                                                    style={
                                                        "max_height": "2.8em",  # Igual que el texto para dos líneas
                                                        "overflow_y": "auto",   # Scroll si hay más de dos líneas
                                                        "width": "100%",
                                                    },
                                                ),
                                                spacing="2",
                                                padding_left="0.5em",
                                                width="100%"
                                            ),
                                            spacing="1",
                                            padding_y="0.5em",
                                            width="100%"
                                        ),
                                        border_bottom="1px solid rgba(255, 255, 255, 0.05)",
                                        padding_bottom="2px",
                                        margin_bottom="2px",
                                        width="100%",
                                        min_height="40px",
                                    )
                                ),
                                max_height="180px",  # Ajusta según tu diseño
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        DayState.show_comment_input,
                        rx.hstack(
                            rx.input(
                                placeholder="Escribe tu comentario...",
                                value=DayState.new_comment_text,
                                on_change=lambda value: DayState.set_new_comment_text(value),
                                size="1",
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("check"),
                                on_click=DayState.add_comment(day),
                                size="1",
                                variant="soft",
                                color_scheme="green",
                                disabled=DayState.new_comment_text.strip() == ""
                            ),
                            spacing="2",
                            width="100%"
                        )
                    ),
                    spacing="2",
                    padding="2",
                    width="260px",
                    min_width="200px"
                ),

                style={
                    "max-width": "100vw"
                },
                align="start", 
                collision_padding=20,  # Añade padding para evitar colisiones
                avoid_collisions=True,  # Intenta evitar colisiones con otros elementos
                sticky="partial",  # Mantiene el popover visible mientras sea posible
            ),
            on_open_change=DayState.close_comment_input
            
        ),
        position="relative",
        margin="2px",
        flex_shrink="0",
        on_focus=lambda: [DayState.load_day_comments(day.id),],
        
    )


================================================
FILE: Calendario/components/footer.py
================================================
import reflex as rx
from typing import Callable

def footer(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.vstack(
        rx.box(
            page(),
            width="100%",
            flex="1",
            display="flex",
            justify_content="center",
            align_items="center",
            min_height="calc(100vh - 250px)",  # Aumentar espacio mínimo
            position="relative",
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "Calendario",
                            size=rx.breakpoints(initial="5", md="6"),
                            background_image="linear-gradient(45deg, #4F46E5, #3B82F6)",
                            background_clip="text",
                        ),
                        rx.text(
                            "Organiza tus comidas",
                            size=rx.breakpoints(initial="2", md="3"),
                            color="gray.400",
                        ),
                        align_items="start",
                        spacing="2",
                    ),
                    rx.vstack(
                        rx.text(
                            "Enlaces rápidos",
                            size=rx.breakpoints(initial="3", md="4"),
                            weight="bold",
                            color="gray.300"
                        ),
                        rx.mobile_only(
                            rx.vstack(
                                rx.link("Inicio", href="/", color="gray.400"),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400"),
                                rx.link("Contacto", href="/contact", color="gray.400"),
                                spacing="2",
                            )
                        ),
                        rx.tablet_and_desktop(
                            rx.hstack(
                                rx.link("Inicio", href="/", color="gray.400", _hover={"color": "white"}),
                                rx.link("Sobre Nosotros", href="/about", color="gray.400", _hover={"color": "white"}),
                                rx.link("Contacto", href="/contact", color="gray.400", _hover={"color": "white"}),
                                spacing="4",
                            )
                        ),
                        align_items="end",
                        justify="end",
                        spacing="3",
                        margin_left="auto",  # <- Esto lo alinea a la derecha siempre
                    ),
                    spacing="8",
                    width="100%",
                ),
                rx.divider(margin_y="4", color="gray.700"),
                rx.center(
                    rx.text(
                        "© 2024/25 Calendario. Todos los derechos reservados.",
                        color="gray.500",
                        size=rx.breakpoints(initial="1", md="2"),
                    ),
                    margin_bottom="1em",
                    width="100%",
                ),
                spacing="6",
                padding_y="4",
                width="100%",
                margin_top="2em"
            ),
            background="linear-gradient(180deg, #1a1a1a 0%, #000000 100%)",
            width="100%",
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            box_shadow="0 -4px 20px rgba(0, 0, 0, 0.3)",
        ),
        width="100%",
        height=rx.breakpoints(initial="auto", md="100vh"),
        spacing="0",

    )


================================================
FILE: Calendario/components/login_form.py
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
            rx.box(
                rx.mobile_only(
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
                    )
                ),
                rx.tablet_and_desktop(
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        "Inicio",
                        on_click=rx.redirect("/"),
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
                    rx.icon("user-check",size=18),
                    "Iniciar Sesión",
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    on_click=UserState.login,
                    width="100%",

                ),
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿No tienes cuenta?", size="3"),
                            rx.link(
                                "Registrate",
                                on_click=rx.redirect("/register"),
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
        padding_top="4em",  # Aumentamos padding superior para no solapar con el botón

    )


================================================
FILE: Calendario/components/meal_editor.py
================================================

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.model.model import Day
from Calendario.utils.api import get_all_meals

def meal_editor() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.box()),
        rx.dialog.content(
            rx.form.root(
                rx.vstack(
                    rx.text(
                        rx.moment(DayState.current_day.date,
                                format="dddd, D [de] MMMM [del] YYYY", 
                                locale="es"
                        ),
                        style={"text-transform": "capitalize"},
                        size="5"

                    ),
                    rx.text(
                        "Comida:",
                        color="var(--green-9)",
                        font_weight="bold",
                        margin_bottom="0.2em"
                    ),
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecciona una comida"
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ),
                                    ),
                                ),
                            ),
                            name="meal",
                            value=DayState.current_meal,
                            on_change=DayState.set_meal,
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon(
                            "rotate-ccw",
                            color="red",
                            size=18,
                            style={
                                "cursor": "pointer",
                            },
                            _hover={
                                "transform": "scale(1.3)",
                                "transition": "transform 0.2s"
                            },
                            on_click=DayState.clear_meal
                        ),
                    ),
                    rx.text(
                        "Cena:",
                        color="var(--blue-9)",
                        font_weight="bold",
                        margin_bottom="0.2em",
                        margin_top="0.5em"
                    ),
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecciona una cena"
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ),
                                    ),
                                ),
                            ),
                            name="dinner",
                            value=DayState.current_dinner,
                            on_change=DayState.set_dinner,
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon(
                            "rotate-ccw",
                            color="red", 
                            size=18,
                            style={
                                "cursor": "pointer",
                            },
                            _hover={
                                "transform": "scale(1.3)",
                                "transition": "transform 0.2s"
                            },
                            on_click=DayState.clear_dinner
                        ),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                type="button",
                                on_click=DayState.clear_current_day,
                                color_scheme="red",
                                variant="soft",
                                size="3",
                                _hover={
                                    "background": "var(--red-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Guardar",
                                type="submit",
                                disabled=DayState.loading,
                                color_scheme="green",
                                variant="soft",
                                size="3",
                                _hover={
                                    "background": "var(--green-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        spacing="3",
                        margin_top="1em"
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                on_submit=DayState.update_day
            ),
            max_width="500px",
            align_items="center",
        ),
        open=DayState.show_editor
    )


================================================
FILE: Calendario/components/register_form.py
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
            width="100%",

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
            rx.mobile_only(
                rx.button(
                    rx.icon("arrow-left", size=18),
                    on_click=rx.redirect("/"),
                    variant="soft",
                    color_scheme="blue",
                    size="2",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"}
                )
            ),
            rx.tablet_and_desktop(
                rx.button(
                    rx.icon("arrow-left", size=18),
                    "Inicio",
                    on_click=rx.redirect("/"),
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
        
        rx.vstack(
            rx.heading("Registra tu Usuario", size="6", text_align="center",margin_top=["2em", "10em"]),  # Margen superior responsive),
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

      )  # Asegura que ocupe toda la altura        


================================================
FILE: Calendario/components/show_pasw_switch.py
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
FILE: Calendario/components/user_calendar.py
================================================
from calendar import Calendar
import select
import reflex as rx
from Calendario.components.day_button import day_button
from Calendario.components.calendar_sharer import calendar_sharer
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def botones() -> rx.Component:
    return rx.vstack(
        rx.text("CALENDARIOS"),
        rx.button("Info Calendarios", on_click=CalendarState.load_calendars),
        align_items="center",
        spacing="2"
    )

async def calendars() -> rx.Component:
    calendar_state = await CalendarState.get_state(CalendarState)
    return calendar_state.calendars

def calendar_grid() -> rx.Component:
    return rx.vstack(

        # Encabezados de días de la semana
        rx.grid(
            rx.foreach(
                ["L", "M", "X", "J", "V", "S", "D"],
                lambda day: rx.center(
                    rx.text(day, 
                           size="2", 
                           weight="bold", 
                           color="gray.500",
                           text_transform="uppercase"),
                    width="100%",
                    padding="2px"
                )
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding_x="1em"
        ),
        
        # Grid de días del mes
        rx.grid(
            rx.foreach(
                CalendarState.display_days,
                lambda day: rx.cond(
                    day,
                    day_button(day),
                    rx.box(  # Celda vacía para días fuera del rango del mes
                        style={
                            "width": "12vw",
                            "height": "12vw",
                            "min_width": "40px",
                            "min_height": "40px",
                            "max_width": "70px",
                            "max_height": "70px",
                            "visibility": "hidden"  # Mantiene el espacio pero invisible
                        }
                    )
                )
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding="1em"
        ),
        spacing="3",
        width="100%",
        align_items="center"
    )




def user_calendar() -> rx.Component:
    return rx.vstack(
        rx.container(
            rx.vstack(
                rx.cond(
                    CalendarState.calendars.length() > 0,
                    rx.vstack(
                        rx.hstack(
                            rx.select.root(
                                rx.select.trigger(
                                    placeholder="Selecciona un calendario",
                                    width="300px",
                                    min_width="300px",
                                    justify_content="center",
                                ),
                                
                                rx.select.content(
                                    rx.select.group(
                                        rx.foreach(
                                            CalendarState.calendars,
                                            lambda cal: rx.select.item(
                                                f"{cal.name} ",
                                                value=cal.id.to(str),
                                                justify_content="center",
                                            )
                                        )
                                    ),
                                    position="popper",
                                    side="bottom",
                                    align="start",
                                ),
                                value=rx.cond(CalendarState.current_calendar,
                                            CalendarState.current_calendar.id.to(str),
                                            ""),

                                on_change=CalendarState.set_current_calendar,
                                width="100%",
                                variant="surface",
                                radius="full",

                            ),
                            rx.icon(
                                tag="refresh-ccw",
                                color="cyan",
                                size=28,
                                on_click=CalendarState.refresh_page,
                                style={"cursor": "pointer"}
                            ),
                        ),
                        
                        rx.cond(
                            CalendarState.current_calendar,
                            rx.vstack(
                                rx.heading(
                                    
                                    CalendarState.calendar_title, 
                                    size="6",
                                    padding_bottom="1em",
                                    padding_top="2em"
                                ),
                                calendar_grid(),
                                calendar_sharer(),

                                spacing="4",
                                align_items="center",  # Asegura que todo se alinee al centro
                            ),
                        ),
                        align_items="center",  # Centra el contenido
                        width="100%"
                    )
                )
            ),
            align_items="center",  # Centra el contenedor
            justify_content="center",
            width="100%",
            padding="2em"
        ),
        align_items="center",  # Asegura que toda la estructura esté centrada
        justify_content="center",
        width="100vw"
    )



================================================
FILE: Calendario/components/user_navbar.py
================================================
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
                            heigth="20px"),
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
                                     style={"_hover" : { "background " : "#23282b"}}
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



================================================
FILE: Calendario/database/database.py
================================================
#database.py

import bcrypt

import os
import dotenv
from typing import Union,List,Optional
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar,Day,Meal,Comment,User
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
                if bcrypt.checkpw(password.encode('utf-8'), user["pasw"].encode('utf-8')):
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
            # 1) Creamos la condición combinada: owner_id o array shared_with contiene user_id
            condition = f"owner_id.eq.{user_id},shared_with.cs.{{{user_id}}}"

            # 2) Ejecutamos un único query con .or_()
            response = (
                self.supabase
                    .from_("calendars")
                    .select("*")
                    .or_(condition)
                    .execute()
            )

            # 3) Si hay datos, mapeamos al modelo Calendar
            if response.data:
                calendars = []
                for cal in response.data:
                    calendars.append(
                        Calendar(
                            id=cal['id'],
                            name=cal['name'],
                            owner_id=cal['owner_id'],
                            start_date=cal['start_date'],
                            end_date=cal['end_date'],
                            shared_with=cal.get('shared_with', []),
                            created_at=(
                                datetime.fromisoformat(cal['created_at'].replace('Z', '+00:00'))
                                if cal.get('created_at') else datetime.now()
                            )
                        )
                    )
                return calendars

        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None


    def create_calendar_with_days(self, user_id: int, calendar_name: str, start_date: datetime, end_date: datetime):
        try:
            if not calendar_name.strip():
                raise ValueError("El nombre del calendario es obligatorio")
            
            # Normalizar fechas a UTC medianoche
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            end_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            
            calendar_data = {
                "name": calendar_name,
                "owner_id": user_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("calendars").insert(calendar_data).execute()
            
            if response.data:
                days = []
                current_day = start_date
                while current_day <= end_date:
                    days.append({
                        "calendar_id": response.data[0]["id"],
                        "date": current_day.isoformat()
                    })
                    current_day += timedelta(days=1)
                
                self.supabase.table("days").insert(days).execute()
                
                return Calendar(
                    id=response.data[0]["id"],
                    name=calendar_name,
                    owner_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    created_at=datetime.fromisoformat(response.data[0]["created_at"])
                )
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise 
        except Exception as e:
            print(f"Error creating calendar: {str(e)}")
        return None
    

    def get_days_for_calendar(self, calendar_id: int) -> List[Day]:
        try:
            response = (
                self.supabase
                .from_("days")
                .select("*")
                .eq("calendar_id", calendar_id)
                .order("date")
                .execute()
            )
            
            if response.data:
                return [
                    Day(
                        id=day['id'],
                        calendar_id=day['calendar_id'],
                        date=datetime.fromisoformat(
                            day['date'].replace('Z', '+00:00')
                        ).replace(tzinfo=None),
                        meal=day['meal'],
                        dinner=day['dinner'],
                        comments=day['comments'],
                    )
                    for day in response.data
                ]
        except Exception as e:
            print(f"Error getting days: {e}")
        return []
    


    def get_all_meals(self) -> list[Meal]:
        try:
            response = self.supabase.from_("meals").select("*").execute()
            print("COMIDAS TOTALES! EN DATABASE!",response.data)
            return [Meal(**meal) for meal in response.data]
        except Exception as e:
            print(f"Error obteniendo comidas: {e}")
            return []
        

    async def update_day_meal(self, day_id: int, meal: Optional[str]) -> Optional[Day]:
            try:
                response = (
                    self.supabase.table("days")
                    .update({"meal": meal})
                    .eq("id", day_id)
                    .execute()
                )
                return Day(**response.data[0]) if response.data else None
            except Exception as e:
                print(f"Error actualizando comida: {e}")
                return None

    async def update_day_dinner(self, day_id: int, dinner: Optional[str]) -> Optional[Day]:
        try:
            response = (
                self.supabase.table("days")
                .update({"dinner": dinner})
                .eq("id", day_id)
                .execute()
            )
            return Day(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error actualizando cena: {e}")
            return None


    def get_comments_for_day(self, day_id: int) -> List[Comment]:
        try:
            print(f"Buscando comentarios para day_id: {day_id}")  # Debug
            response = (
                self.supabase.from_("comments")
                .select("*, user:owner_id(username)")
                .eq("day_id", day_id)
                .order("created_at", desc=False)  # Cambiar a ascendente para ver nuevos primero
                .execute()
            )
            print("Respuesta de Supabase:", response.data)  # Debug
            return [
                Comment(
                    id=comment['id'],
                    day_id=comment['day_id'],
                    content=comment['content'],
                    owner_id=comment['owner_id'],  # <- aquí estaba el error
                    created_at=datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00')),
                    user=User(
                        id=comment['owner_id'],  # <- aquí también
                        username=comment['user']['username']
                    )
                ) for comment in response.data
            ]
        except Exception as e:
            print(f"Error obteniendo comentarios: {e}")
            return []

    def add_comment(self, day_id: int, owner_id: int, content: str) -> Optional[Comment]:
        try:
            comment_data = {
                "day_id": day_id,
                "owner_id": owner_id,
                "content": content
            }
            
            response = self.supabase.table("comments").insert(comment_data).execute()
            
            if response.data:
                # Obtener el comentario recién creado con datos del usuario
                new_comment = self.get_comments_for_day(day_id)[0]
                return new_comment
        except Exception as e:
            print(f"Error agregando comentario: {e}")
        return None
    
    def update_day_comments_flag(self, day_id: int) -> bool:
        try:
            response = (
                self.supabase.table("days")
                .update({"comments": True})
                .eq("id", day_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error actualizando flag de comentarios: {e}")
            return False
        

    def get_day(self, day_id: int) -> Optional[Day]:
        try:
            response = self.supabase.from_("days").select("*").eq("id", day_id).execute()
            if response.data:
                return Day(**response.data[0])
        except Exception as e:
            print(f"Error obteniendo día: {e}")
        return None
    

    def delete_comment(self, comment_id: int) -> bool:
        try:
            # Obtener day_id del comentario antes de eliminarlo
            comment = self.supabase.table("comments").select("day_id").eq("id", comment_id).execute()
            if not comment.data:
                return False
            day_id = comment.data[0]["day_id"]

            # Eliminar el comentario
            delete_response = self.supabase.table("comments").delete().eq("id", comment_id).execute()
            if not delete_response.data:
                return False

            # Contar comentarios restantes para el día
            count_query = self.supabase.table("comments").select("count", count="exact").eq("day_id", day_id).execute()
            comment_count = count_query.data[0]["count"]

            # Actualizar flag si no hay comentarios
            if comment_count == 0:
                self.update_day_comments_false(day_id)
                
            return True
        except Exception as e:
            print(f"Error eliminando comentario: {e}")
            return False

    def update_day_comments_false(self, day_id: int) -> bool:
        try:
            response = (
                self.supabase.table("days")
                .update({"comments": False})
                .eq("id", day_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error actualizando flag a False: {e}")
            return False
        

# Calendario/database/database.py
    def share_with(self, calendar: Calendar, username: str) -> tuple[bool, str]:
        try:
            # Buscar usuario ignorando mayúsculas/minúsculas
            response_username = self.supabase.from_("user").select("*").ilike("username", username.lower()).execute()
            if not response_username.data:
                return False, "Usuario no encontrado"
            username_id = response_username.data[0]["id"]

            # 2. Obtener calendario actual
            response_calendar = self.supabase.from_("calendars").select("shared_with").eq("id", calendar.id).execute()
            if not response_calendar.data:
                return False, "Calendario no encontrado"
                
            shared_with = response_calendar.data[0].get("shared_with", []) or []
            
            # 3. Verificar si ya tiene acceso
            if username_id in shared_with:
                return False, "El usuario ya tiene acceso a este calendario"

            # 4. Actualizar shared_with
            shared_with.append(username_id)
            update_response = self.supabase.from_("calendars").update({"shared_with": shared_with}).eq("id", calendar.id).execute()
            
            return bool(update_response.data), "Calendario compartido exitosamente"
            
        except Exception as e:
            print(f"Error al compartir calendario: {e}")
            return False, "Error interno al compartir el calendario"


================================================
FILE: Calendario/model/model.py
================================================
from typing import Optional
import reflex as rx
from datetime import datetime

class User(rx.Base):
    """
    Modelo para usuarios.
    """
    id: int
    username: str
    pasw: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    created_at: Optional[datetime] = None


class Calendar(rx.Base):
    """
    Modelo para calendarios.
    """
    id: int
    name: str
    owner_id: int  # Relación con el usuario propietario
    shared_with: Optional[list[int]] = []  # Permite None pero inicializa como lista vacía
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
    id: int
    calendar_id: int
    date: datetime
    meal: str = None
    dinner: str = None
    comments: bool = False


class Comment(rx.Base):
    """
    Modelo para comentarios asociados a un día.
    """
    id: int
    day_id: int  # Relación con el día
    content: str  # Contenido del comentario
    owner_id: int  # Usuario que hizo el comentario
    created_at: datetime
    user: User


================================================
FILE: Calendario/pages/calendar.py
================================================
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.meal_editor import meal_editor
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info, position="top-center")

@rx.page(route="/calendar",
         title="Calendario | CalendPy",
         on_load=[CalendarState.reset_calendars,
                                     CalendarState.clean,
                                     UserState.on_load,
                                     CalendarState.load_meals,
                                     UserState.check_autenticated,
                                     
                                     ])
def calendar() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        meal_editor(),
        rx.container(
            rx.vstack(
                rx.cond(
                    UserState.current_user,
                    rx.cond(
                        CalendarState.calendars,
                        user_calendar(),
                        
                        rx.vstack(
                            rx.text("No tienes ningún calendario"),
                            rx.button("Crear Calendario", on_click=CalendarState.open_calendar_creator),
                            align_items="center"  # Centrar contenido dentro del vstack
                        ),
                    ),
                    rx.vstack(
                        rx.box(
                            # Círculo de carga con animación CSS
                            style={
                                "border": "8px solid #f3f3f3",
                                "borderTop": "8px solid #3182ce",
                                "borderRadius": "50%",
                                "width": "60px",
                                "height": "60px",
                                "animation": "spin 1s linear infinite",
                                # Definición de la animación
                                "@keyframes spin": {
                                    "0%": {"transform": "rotate(0deg)"},
                                    "100%": {"transform": "rotate(360deg)"}
                                },
                            }
                        ),
                        rx.text("Cargando...", margin_top="1em"),
                        align_items="center"
                    ),
                ),
                width="100%",
                align_items="center",  # Centrar todo dentro del vstack principal
            ),
            width="100%",
            max_width="1200px",
            padding_x="2em",
            padding_top="6em",
            align="center"  # Centrar el container horizontalmente
        ),
        width="100%",
        spacing="0",
        align_items="center",  # Centrar la pila de elementos
        style={"overflow-x": "hidden"}, 
        heigth="100%"
    )



================================================
FILE: Calendario/pages/index.py
================================================
# Calendario/pages/index.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.user_state import UserState

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))

@rx.page(route="/", title="CalendPy", on_load=UserState.on_load)
@footer
def index() -> rx.Component:
    return rx.cond(
        UserState.current_user,
        redirect_to_calendar(),
        rx.container(
            rx.vstack(
                rx.image("/favicon.ico",width="300px", height="220px"),
                rx.heading(
                    "¡Bienvenido a CalendPy!",
                    size=rx.breakpoints(initial="7", md="8", lg="9"),
                    text_align="center",
                    background_image="linear-gradient(45deg, #4F46E5, #3B82F6)",
                    background_clip="text",
                    padding_bottom="0.5em"
                ),
                rx.text(
                    "Organiza tus comidas de manera eficiente ",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "Comparte calendarios con tus amigos " ,
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "Actualiza tu lista de la compra ",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.text(
                    "¡ Y mucho más !",
                    size=rx.breakpoints(initial="4", md="5", lg="6"),
                    color="gray.400",
                    text_align="center"
                ),
                rx.box(
                    rx.mobile_only(
                        rx.vstack(
                            rx.link(
                                rx.button(
                                    rx.icon("user-check",size=18),
                                    "Iniciar Sesión",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    color_scheme="blue",
                                    radius="full",
                                    _hover={"transform": "scale(1.05)"},
                                    padding_x="3em",
                                    padding_y="1em",
                                    variant="surface"
                                ),
                                href="/login",
                            ),
                            rx.link(
                                rx.button(
                                    rx.icon("user-plus",size=18),
                                    "Registrarse",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    variant="surface",
                                    color_scheme="blue",
                                    radius="full",
                                    padding_y="1em",
                                    padding_x="3em",
                                    _hover={"transform": "scale(1.05)"},

                                    
                                ),
                                href="/register",
                            ),
                            spacing="3",
                            width="100%",
                            align="center"
                        )
                    ),
                    rx.tablet_and_desktop(
                        rx.hstack(
                            rx.link(
                                rx.button(
                                    rx.icon("user-check",size=18),
                                    "Iniciar Sesión",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    color_scheme="blue",
                                    radius="full",
                                    _hover={"transform": "scale(1.05)"},
                                    padding_x="3em",
                                    padding_y="1em",
                                    variant="surface"
                                ),
                                href="/login"
                            ),
                            rx.link(
                                rx.button(
                                    rx.icon("user-plus",size=18),
                                    "Registrarse",
                                    size=rx.breakpoints(initial="3", md="4"),
                                    variant="surface",
                                    color_scheme="blue",
                                    radius="full",
                                    padding_y="1em",
                                    padding_x="3em",
                                    _hover={"transform": "scale(1.05)"},

                                ),
                                href="/register"
                            ),
                            spacing="4",
                            margin_top="2em",
                            justify="center",
                        )
                    ),
                    width="100%",
                    margin_top="2em"
                ),
                align="center",
                spacing="4",
                width="100%"
            ),
            padding="2em",
            max_width="1200px",
            margin_top=rx.breakpoints(initial="0em", md="0em", lg="0px"),
            padding_x=rx.breakpoints(initial="1em", md="2em"),
            center_content=True,
            width="100%",
            text_align="center"
        )
    )



================================================
FILE: Calendario/pages/login.py
================================================
# Calendario/pages/login.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.login_form import login_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state


def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))


@rx.page(route="/login",
            title="Iniciar Sesión | CalendPy",
            on_load=[Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    UserState.on_load])
@footer
def login() -> rx.Component:
    return rx.cond(UserState.current_user,
                   redirect_to_calendar(),
                   login_form()
                   )



================================================
FILE: Calendario/pages/register.py
================================================
# Calendario/pages/registro.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.register_form import register_form
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
from Calendario.state.login_state import Login_state

def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))


@rx.page(route="/register",
            title="Registro | CalendPy",
            on_load=[RegisterState.load_page,
                    Login_state.swith_off,
                    RegisterState.swith_off,
                    UserState.set_password(""),
                    RegisterState.set_password(""),
                    RegisterState.set_confirm_password(""),
                    RegisterState.reset_errors,
                    UserState.on_load])
@footer
def register() -> rx.Component:
    return rx.cond(
        UserState.current_user,
        redirect_to_calendar(),
        rx.container(
            register_form(),
        )
    )


================================================
FILE: Calendario/state/calendar_state.py
================================================
#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import fetch_and_transform_calendars, get_all_meals, get_days_for_calendar, share_calendar_with_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz


class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info: Optional[str] = None
    new_calendar_name : str = ""
    new_calendar_month: str = datetime.today().strftime("%Y-%m")
    loading : bool = False
    show_calendar_creator: bool = False
    error_message : Optional[str] = None 
    current_calendar: Optional[Calendar] = None
    days : List[Day] = [] 
    hovered_day: Optional[int] = None
    display_days: list[Optional[Day]] = []
    current_date_str: str
    loading: bool = True
    username_to_share: str = ""  # Nombre de usuario con quien compartir
    show_calendar_sharer: bool = False  # Nuevo estado

    @rx.event
    async def refresh_page(self):
        """Redirige a /calendar con el ID del calendario actual para recargarlo."""
        if not self.current_calendar:
            # Si no hay calendario seleccionado, no hace nada
            return 
        # Redirige a /calendar pasando el parámetro calendar_id
        else: 
            await self.set_current_calendar(self.current_calendar.id)
            await get_days_for_calendar(self.current_calendar.id)

            print("refresh funciona")

        

    @rx.event
    def open_calendar_sharer(self):
        self.show_calendar_sharer = True
        self.error_message = None

    @rx.event
    def close_calendar_sharer(self):
        self.show_calendar_sharer = False
# Calendario/state/calendar_state.py
    async def share_calendar(self):
        try:
            # Resetear mensajes previos
            self.error_message = None
            
            # Validaciones básicas
            if not self.current_calendar:
                
                return rx.toast.error("Selecciona un calendario primero", position="top-center")
                
            if not self.username_to_share.strip():
                self.username_to_share = ""
                return rx.toast.error("Escribe un nombre de usuario", position="top-center")

            # Verificar auto-compartición
            user_state = await self.get_state(UserState)
            if self.username_to_share.lower() == user_state.current_user.username.lower():
                self.username_to_share = ""
                return rx.toast.error("No puedes compartir contigo mismo", position="top-center")

            # Llamar a la API
            success, message = await share_calendar_with_user(self.current_calendar, self.username_to_share)
            
            if success:
                # Éxito: limpiar input y cerrar diálogo
                self.username_to_share = ""
                self.close_calendar_sharer()
                return rx.toast.success(message, position="top-center")
            else:
                # Error: mantener diálogo abierto y mostrar mensaje
                self.username_to_share = ""
                return rx.toast.error(message, position="top-center")
                
        except Exception as e:
            return rx.toast.error(f"Error inesperado: {str(e)}", position="top-center")
    @rx.var
    def calendar_title(self) -> str:
        if self.current_calendar and self.current_calendar.start_date:
            meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            mes = meses[self.current_calendar.start_date.month - 1]
            año = self.current_calendar.start_date.year
            return f"Calendario de {mes} del {año}"
        return ""
    

    def update_current_date(self):
        madrid_tz = pytz.timezone('Europe/Madrid')
        madrid_time = datetime.now(madrid_tz)
        self.current_date_str = madrid_time.strftime("%Y-%m-%d 00:00:00")
        print(self.current_date_str)
    @rx.event
    def set_hovered_day(self, day_id: int):
        self.hovered_day = day_id
        
    @rx.event
    def clear_hovered_day(self):
        self.hovered_day = None
    @rx.event
    def open_calendar_creator(self):
        self.show_calendar_creator = True
    
    @rx.event
    def close_calendar_creator(self):
        self.show_calendar_creator = False


    @rx.event
    async def load_meals(self):
        """Carga todas las comidas al iniciar"""
        try:
            total_meals = await get_all_meals()
            self.meals = total_meals
        except Exception as e:
            print(f"Error loading meals: {e}")

        
    @rx.event
    async def set_current_calendar(self, value: str):
        try:
            calendar_id = int(value)
            for calendar in self.calendars:
                if calendar.id == calendar_id:
                    self.current_calendar = calendar
                    self.days = await get_days_for_calendar(self.current_calendar.id)
                    
                    # Calcular espacios vacíos iniciales
                    start_date = self.current_calendar.start_date
                    first_weekday = start_date.weekday()  # Lunes=0, Domingo=6
                    
                    # Crear lista de días con espacios vacíos
                    self.display_days = [None] * first_weekday + self.days
                    self.update_current_date()
                    
                    return
        except ValueError:
            print(f"Error convirtiendo el valor: {value}")

    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True
            
            if UserState.current_user is None:
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
                self.current_calendar = new_calendar
                # Cargar los días del nuevo calendario
                self.days = await get_days_for_calendar(new_calendar.id)
                
                # Actualizar display_days para el nuevo calendario
                first_weekday = start_date.weekday()
                self.display_days = [None] * first_weekday + self.days
                
                self.close_calendar_creator()
                return rx.toast.success(f"Calendario '{self.new_calendar_name}' creado con éxito!", position="top-center")
        
        except ValueError as ve:
            return rx.toast.error(str(ve), position="top-center")
        except Exception as e:
            return rx.window_alert(f"Error: {str(e)}")
        finally:
            self.loading = False
            self.new_calendar_name = ""
            self.new_calendar_month = datetime.today().strftime("%Y-%m")

    @rx.event
    async def load_calendars(self):
        self.loading = True  # Activa el loader al iniciar la carga
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
                
            self.loading = False  # Desactiva el loader solo después de cargar

                
        except Exception as e:
            print(e)




    async def load_days(self, calendar_id: int):
        self.days = await get_days_for_calendar(calendar_id)


    def update_day_in_state(self, updated_day: Day):
        # Actualizar días en el estado
        self.days = [
            updated_day if day.id == updated_day.id else day
            for day in self.days
        ]
        
        # Actualizar display_days manteniendo los espacios vacíos iniciales
        start_date = self.current_calendar.start_date
        first_weekday = start_date.weekday()
        self.display_days = [None] * first_weekday + self.days


    @rx.event
    def reset_calendars(self):
        """Resetea y recarga los calendarios"""
        self.calendars = []
        return CalendarState.load_calendars()
    @rx.event
    def clean(self):
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.days = [] # Reset to empty list
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None





================================================
FILE: Calendario/state/day_state.py
================================================
import reflex as rx
from typing import Optional, List
from Calendario.utils.api import (
    get_day_comments,
    add_comment_to_day,
    delete_comment as api_delete_comment,
    update_day_meal,
    update_day_dinner,
    get_day_details
)
from Calendario.model.model import Day, Comment
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState


class DayState(rx.State):
    current_day: Optional[Day] = None
    show_editor: bool = False
    loading: bool = False
    current_meal: str = ""
    current_dinner: str = ""
    current_comments: List[Comment] = []
    last_loaded_day_id: int = None
    show_comment_input: bool = False
    new_comment_text: str = ""

    @rx.event
    async def load_day_comments(self, day_id: int):
        self.last_loaded_day_id = day_id
        comments = await get_day_comments(day_id)
        self.current_comments = comments

    @rx.var
    def reversed_comments(self) -> list[Comment]:
        return list(reversed(self.current_comments))

    @rx.event
    def clear_current_comments(self):
        self.current_comments = []

    @rx.event
    def close_comment_input(self):
        self.show_comment_input = False

    @rx.event
    def set_new_comment_text(self, value: str):
        self.new_comment_text = value

    @rx.event
    def toggle_comment_input(self):
        self.show_comment_input = not self.show_comment_input
        if not self.show_comment_input:
            self.new_comment_text = ""

    @rx.event
    async def add_comment(self, day: Day):
        if not self.new_comment_text.strip():
            return rx.toast.error("El comentario no puede estar vacío")

        try:
            user_state = await self.get_state(UserState)
            new_comment = await add_comment_to_day(
                day_id=day.id,
                user_id=user_state.current_user.id,
                content=self.new_comment_text.strip()
            )

            if new_comment:
                # Actualizar estado del calendario
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                
                # Actualizar estado local
                await self.load_day_comments(day.id)
                self.toggle_comment_input()
                return rx.toast.success("Comentario añadido")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.new_comment_text = ""

    @rx.event
    async def delete_comment(self, comment_id: int, day: Day):
        try:
            success = await api_delete_comment(comment_id)
            
            if success:
                # Actualizar comentarios
                await self.load_day_comments(day.id)
                
                # Actualizar estado del día
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                
                return rx.toast.success("Comentario eliminado correctamente")
            return rx.toast.error("Error al eliminar el comentario")
            
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")

    @rx.event
    async def set_current_day(self, day: Day):
        self.current_day = day
        self.current_meal = day.meal or ""
        self.current_dinner = day.dinner or ""
        self.show_editor = True

    @rx.event
    def set_meal(self, value: str):
        self.current_meal = value

    @rx.event
    def set_dinner(self, value: str):
        self.current_dinner = value

    @rx.event
    def clear_current_day(self):
        self.current_day = None
        self.show_editor = False

    @rx.event
    def clear_meal(self):
        self.current_meal = ""

    @rx.event
    def clear_dinner(self):
        self.current_dinner = ""

    @rx.event
    async def update_day(self, form_data: dict):
        self.loading = True
        try:
            if not self.current_day:
                return

            meal = self.current_meal or None
            dinner = self.current_dinner or None
            updated = False

            if meal != self.current_day.meal:
                await update_day_meal(self.current_day.id, meal)
                updated = True

            if dinner != self.current_day.dinner:
                await update_day_dinner(self.current_day.id, dinner)
                updated = True

            if updated:
                updated_day = await get_day_details(self.current_day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                toast_message = "Día actualizado correctamente"
            else:
                toast_message = "No se detectaron cambios"

            self.clear_current_day()
            return rx.toast.success(toast_message, position="top-center")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.loading = False


================================================
FILE: Calendario/state/login_state.py
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
FILE: Calendario/state/register_state.py
================================================
# register_state.py


from typing import Optional
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
    username_valid : Optional[bool] = None


    @rx.event
    def reset_errors(self):
        self.errors ={
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }
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
                    ),rx.redirect("/login")]
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
FILE: Calendario/state/user_state.py
================================================
#user_state.py

import reflex as rx
import time
from typing import Optional
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user
from datetime import datetime
import json

class UserState(rx.State):
    """
    Manejador de estado para los datos del usuario en Reflex.
    """

    user_storage: str = rx.LocalStorage("")  # 1. Variable de almacenamiento


    username: str = ""  # Guarda el nombre de usuario ingresado
    password: str = ""  # Guarda la contraseña ingresada
    current_user: Optional[User] = None  # Mantiene al usuario autenticado

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
    def check_autenticated(self):
        if self.current_user == None:
            return rx.redirect("/")

    @rx.var
    def is_authenticated(self) -> bool:
        """Determina si el usuario está autenticado"""
        return self.current_user is not None

    def _load_user_from_storage(self):
        """Carga los datos del usuario desde LocalStorage"""
        if self.user_storage:
            try:
                user_data = json.loads(self.user_storage)
                # Convertir fechas de string a objeto datetime
                user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                self.current_user = User(**user_data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error cargando usuario desde storage: {e}")
                self._clear_storage()

    def _save_user_to_storage(self):
        """Guarda los datos del usuario en LocalStorage"""
        if self.current_user:
            user_dict = self.current_user.__dict__.copy()
            # Convertir datetime a string para serialización
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            self.user_storage = json.dumps(user_dict)
        else:
            self.user_storage = ""

    def _clear_storage(self):
        """Limpia todos los datos de almacenamiento"""
        self.user_storage = ""
        self.current_user = None
        self.username = ""
        self.password = ""

    @rx.event
    async def on_load(self):
        """Evento al cargar la aplicación"""
        self._load_user_from_storage()




    @rx.event
    async def login(self):

        if not self.username or not self.password:
            self.restart_pasw()

        try:
            user_data = await authenticate_user(self.username.lower(), self.password)
            

            
            if user_data:
                self.current_user = user_data
                self._save_user_to_storage()
                self.username = ""
                self.password = ""
                # Llamamos al evento para cargar los calendarios en el estado de CalendarState
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                # Limpiamos los campos de usuario y contraseña
                self._clear_storage()
                self.username = ""
                self.password = ""
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        except Exception as e:
            print(f"Error al intentar iniciar sesión: {e}")
            self._clear_storage
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )


    @rx.event
    async def logout(self):
        """Maneja el cierre de sesión"""
        from Calendario.state.calendar_state import CalendarState
        
        # Limpiar estado relacionado
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()
        
        # 3. Eliminar datos de almacenamiento
        self._clear_storage()
        return [
            rx.remove_local_storage("user_state.user_storage"),
            rx.redirect("/")
        ]

    @rx.event
    def restart_pasw(self):
        self.password=""


================================================
FILE: Calendario/utils/api.py
================================================
# api.py
import bcrypt
from datetime import datetime
from typing import Union, List, Optional, Dict
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment

SUPABASE_API = SupabaseAPI()

# ---------------------- Autenticación de usuario ----------------------
async def authenticate_user(username: str, password: str) -> Union[User, None]:
    user_data = SUPABASE_API.authenticate_user(username, password)
    return User(**user_data) if user_data else None

async def check_existing_user(username: str, email: str) -> Dict[str, bool]:
    return SUPABASE_API.check_existing_user(username, email)

async def check_existing_username(username: str) -> bool:
    return SUPABASE_API.check_existing_username(username)

async def register_user(username: str, password: str, email: str, birthday: str) -> bool:
    try:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_data = {
            "username": username,
            "pasw": hashed_password,
            "email": email,
            "birthday": birthday
        }
        response = SUPABASE_API.supabase.table("user").insert(user_data).execute()
        return bool(response.data)
    except Exception as e:
        print(f"Error registrando usuario: {str(e)}")
        return False

# ---------------------- Calendarios ----------------------
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    return SUPABASE_API.get_calendars(user_id) or []

async def create_calendar(
    user_id: int, 
    name: str, 
    start_date: datetime, 
    end_date: datetime
) -> Union[Calendar, None]:
    return SUPABASE_API.create_calendar_with_days(user_id, name, start_date, end_date)

async def share_calendar_with_user(calendar: Calendar, username: str) -> bool:
    return SUPABASE_API.share_with(calendar, username)

# ---------------------- Días ----------------------
async def get_days_for_calendar(calendar_id: int) -> List[Day]:
    return SUPABASE_API.get_days_for_calendar(calendar_id) or []

async def update_day_meal(day_id: int, meal: Optional[str]) -> Union[Day, None]:
    return await SUPABASE_API.update_day_meal(day_id, meal)

async def update_day_dinner(day_id: int, dinner: Optional[str]) -> Union[Day, None]:
    return await SUPABASE_API.update_day_dinner(day_id, dinner)

async def get_day_details(day_id: int) -> Union[Day, None]:
    return SUPABASE_API.get_day(day_id)

# ---------------------- Comidas ----------------------
async def get_all_meals() -> List[Meal]:
    return SUPABASE_API.get_all_meals()

# ---------------------- Comentarios ----------------------
async def get_day_comments(day_id: int) -> List[Comment]:
    return SUPABASE_API.get_comments_for_day(day_id) or []

async def add_comment_to_day(
    day_id: int, 
    user_id: int, 
    content: str
) -> Union[Comment, None]:
    comment = SUPABASE_API.add_comment(day_id, user_id, content)
    if comment:
        SUPABASE_API.update_day_comments_flag(day_id)
    return comment

async def delete_comment(comment_id: int) -> bool:
    return SUPABASE_API.delete_comment(comment_id)

async def update_comments_flag(day_id: int, has_comments: bool) -> bool:
    if has_comments:
        return SUPABASE_API.update_day_comments_flag(day_id)
    return SUPABASE_API.update_day_comments_false(day_id)



================================================
FILE: Calendario/utils/send_email.py
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

