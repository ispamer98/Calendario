# Calendario/components/user_calendar.py
"""
Rejilla del mes.

Solo la cuadrícula de días y sus acciones (compartir / eliminar): la cabecera,
el selector de calendario y las estadísticas los pone la página, que es quien
sabe cómo se compone la pantalla.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.calendar_sharer import calendar_sharer
from Calendario.components.day_button import day_button
from Calendario.components.ui import legend_item, panel
from Calendario.state.calendar_state import CalendarState


def _weekday_header() -> rx.Component:
    return rx.grid(
        *[
            rx.center(
                rx.text(
                    day,
                    size="1",
                    weight="bold",
                    color=theme.PURPLE if index >= 5 else theme.DIM,
                    letter_spacing="0.08em",
                ),
                width="100%",
                padding_y="4px",
            )
            for index, day in enumerate(theme.DIAS_SEMANA_CORTOS)
        ],
        grid_template_columns="repeat(7, 1fr)",
        gap="6px",
        width="100%",
    )


#Componente que contiene los días del mes
def calendar_grid() -> rx.Component:
    return rx.vstack(
        _weekday_header(),
        rx.grid(
            rx.foreach(  #Iteramos sobre los dias del calendario
                CalendarState.display_days,
                lambda day: rx.cond(
                    day,  #Si existe registro de dia, lo crea
                    day_button(day),
                    #Hueco de los días anteriores al día 1 del mes
                    rx.box(style={"visibility": "hidden", "aspect_ratio": "1 / 1"}),
                ),
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="6px",
            width="100%",
        ),
        spacing="2",
        width="100%",
        align_items="center",
    )


def _legend() -> rx.Component:
    return rx.hstack(
        legend_item(theme.MEAL, "Comida", "utensils-crossed"),
        legend_item(theme.DINNER, "Cena", "utensils-crossed"),
        legend_item(theme.COMMENT, "Comentarios", "message-square-more"),
        legend_item(theme.OWNER, "Tareas pendientes", "list-todo"),
        legend_item(theme.AGENDA, "Agenda (eventos y notas)", "list-checks"),
        spacing="4",
        wrap="wrap",
        justify="center",
        width="100%",
    )


def _delete_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("calendar-off", size=15),
                rx.text("Eliminar mes", size="2"),
                variant="soft",
                color_scheme="red",
                size="2",
                cursor="pointer",
                radius="full",
            )
        ),
        rx.dialog.content(
            rx.dialog.title("Eliminar el calendario"),
            rx.dialog.description(
                "Se borrarán el mes entero y todo lo que contiene: comidas, cenas, comentarios y agenda. No se puede deshacer.",
                size="2",
                color=theme.MUTED,
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                rx.dialog.close(
                    rx.button(
                        "Eliminar",
                        color_scheme="red",
                        #Solo el propietario puede borrar (la base de datos lo
                        #vuelve a comprobar antes de tocar nada)
                        on_click=CalendarState.delete_calendar(CalendarState.current_calendar_id),
                    )
                ),
                spacing="3",
                margin_top="1.5em",
                justify="end",
            ),
            style={
                "max_width": "430px",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
    )


#Panel principal: rejilla del mes + leyenda + acciones
def calendar_panel() -> rx.Component:
    return panel(
        rx.vstack(
            rx.hstack(
                rx.icon("calendar-range", size=15, color=theme.ACCENT),
                rx.text(CalendarState.calendar_title, size="2", weight="bold", color=theme.TEXT),
                rx.spacer(),
                #Sin botón de refrescar: el calendario se sincroniza solo
                rx.hstack(
                    rx.box(
                        width="6px", height="6px", border_radius="50%",
                        background=theme.SUCCESS,
                        box_shadow=f"0 0 8px {theme.SUCCESS}",
                    ),
                    rx.text("En vivo", size="1", color=theme.DIM),
                    spacing="2", align="center", flex_shrink="0",
                    title="Los cambios de quien comparta el calendario aparecen solos",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            calendar_grid(),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            _legend(),
            rx.hstack(
                #Compartir y eliminar son cosa del propietario (la base de datos
                #ya lo comprobaba; faltaba no ofrecerlo en la interfaz)
                rx.cond(CalendarState.can_share, calendar_sharer()),
                rx.cond(CalendarState.is_owner, _delete_dialog()),
                spacing="2",
                justify="center",
                width="100%",
                wrap="wrap",
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        padding=["14px", "16px", "20px"],
    )
