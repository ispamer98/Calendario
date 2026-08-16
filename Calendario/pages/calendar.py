#Calendario/pages/calendar.py

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.calendar_switcher import calendar_switcher
from Calendario.components.meal_editor import meal_editor
from Calendario.components.today_box import today_box
from Calendario.components.ui import (
    empty_state,
    page_header,
    progress_bar,
    spinner_block,
    stat_card,
    stats_grid,
    tip,
)
from Calendario.components.user_calendar import calendar_panel
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.state.units_state import UnitsState
from Calendario.state.user_state import UserState


def _header_actions() -> list[rx.Component]:
    return [
        #El selector vive también aquí, en la pantalla principal del calendario
        rx.box(
            calendar_switcher(compact=False),
            display=["none !important", "flex !important", "flex !important"],
        ),
        rx.link(
            rx.button(
                rx.icon("clipboard-list", size=16),
                rx.text("Planificar semana", size="2"),
                color_scheme="blue",
                size="2",
                radius="full",
                cursor="pointer",
            ),
            href="/menu_semanal",
            underline="none",
        ),
    ]


def _progress_strip() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Mes planificado", size="1", color=theme.MUTED),
            rx.spacer(),
            rx.text(
                CalendarState.days_planned.to_string()
                + " / "
                + CalendarState.days.length().to_string()
                + " días",
                size="1",
                color=theme.TEXT,
                weight="bold",
                font_family=theme.FONT_MONO,
            ),
            width="100%",
            align="center",
        ),
        progress_bar(CalendarState.planned_percent, theme.MEAL),
        spacing="2",
        width="100%",
    )


def _shortcut(href: str, icon: str, title: str, description: str, color: str) -> rx.Component:
    """Tarjeta de acceso rápido que lleva de verdad a su pestaña."""
    return rx.link(
        rx.box(
            tip(icon, title, description, color),
            width="100%",
            transition="transform 0.15s ease",
            _hover={"transform": "translateY(-2px)"},
        ),
        href=href,
        underline="none",
        width="100%",
    )


def _calendar_view() -> rx.Component:
    """Rejilla del mes + panel de hoy, en dos columnas en escritorio."""
    return rx.flex(
        rx.box(calendar_panel(), flex="1 1 560px", min_width="0"),
        rx.box(
            rx.vstack(
                today_box(),
                #Accesos rápidos: antes había hueco muerto bajo la caja de hoy.
                #Son enlaces de verdad, no solo texto.
                rx.vstack(
                    _shortcut(
                        "/menu_semanal",
                        "clipboard-list",
                        "Menú semanal",
                        "Rellena la semana entera y genera la lista de la compra de una vez.",
                        theme.ACCENT,
                    ),
                    _shortcut(
                        "/meal_list",
                        "chef-hat",
                        "Recetario",
                        "Guarda tus platos con ingredientes para que la compra se calcule sola.",
                        theme.MEAL,
                    ),
                    _shortcut(
                        "/shopping_list",
                        "shopping-cart",
                        "Lista de la compra",
                        "Lo que hay que comprar, agrupado por secciones del súper.",
                        theme.PURPLE,
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            flex="0 1 330px",
            min_width="280px",
        ),
        width="100%",
        gap="18px",
        wrap="wrap",
        align="start",
    )


#Página de calendario
@rx.page(  #Decorador indicando componente página
    route="/calendar",
    title="Calendario | CalendPy",
    on_load=[  #Acciones al cargar la página
        UserState.on_load,
        UserState.check_autenticated,
        CalendarState.load_meals,
        CalendarState.update_current_date,
        CalendarState.refresh_page,
        CalendarState.sync_loop,
        UnitsState.load_units,
        CalendarState.load_categories,
        DayState.load_task_types,
    ],
)
def calendar() -> rx.Component:
    return app_shell(
        meal_editor(),  # Editor de comidas para el día seleccionado
        rx.cond(
            UserState.current_user,  # Si existe registro de usuario loggeado
            rx.cond(
                CalendarState.has_calendars,  # Si el usuario tiene calendarios creados
                rx.vstack(
                    page_header(
                        icon="calendar-days",
                        title=CalendarState.calendar_title,
                        subtitle=CalendarState.current_calendar_name,
                        accent=theme.ACCENT,
                        actions=_header_actions(),
                        extra=_progress_strip(),
                    ),
                    #En móvil el selector no cabe en la cabecera: va debajo
                    rx.box(
                        calendar_switcher(compact=False),
                        display=["flex !important", "none !important", "none !important"],
                        width="100%",
                    ),
                    stats_grid(
                        stat_card(
                            icon="sun",
                            label="Comidas puestas",
                            value=CalendarState.days_with_meal,
                            color=theme.MEAL,
                        ),
                        stat_card(
                            icon="moon",
                            label="Cenas puestas",
                            value=CalendarState.days_with_dinner,
                            color=theme.DINNER,
                        ),
                        stat_card(
                            icon="circle-dashed",
                            label="Días sin planificar",
                            value=CalendarState.days_pending,
                            color=theme.WARNING,
                        ),
                        stat_card(
                            icon="list-checks",
                            label="Tareas pendientes",
                            value=CalendarState.agenda_pending,
                            color=theme.AGENDA,
                        ),
                    ),
                    _calendar_view(),
                    spacing="5",
                    width="100%",
                    max_width="1400px",
                    margin="0 auto",
                    align="center",
                ),

                #Si no existen calendarios registrados
                empty_state(
                    icon="calendar-plus",
                    title="Aún no tienes ningún calendario",
                    description="Cada calendario cubre un mes completo. Crea el del mes en curso y podrás asignar comidas y cenas, compartirlo con quien quieras y planificar la semana.",
                    action=rx.button(
                        rx.icon("calendar-plus", size=16),
                        rx.text("Crear mi primer calendario", size="2"),
                        color_scheme="blue",
                        size="3",
                        cursor="pointer",
                        radius="full",
                        on_click=CalendarState.open_calendar_creator,  #Acción que abre el creador de calendario
                    ),
                ),
            ),

            #Si no se ha cargado la información del usuario loggeado todavia
            spinner_block("Cargando tu calendario..."),
        ),
    )
