# Calendario/components/today_box.py
"""
Panel lateral "Hoy".

Resume, para cada calendario activo, qué toca comer y cenar hoy, los
comentarios del día y la agenda pendiente. Cuando no hay nada planificado ya
no se queda en blanco: propone qué hacer.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, panel
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.state.user_state import UserState


def _meal_line(label: str, icon: str, color: str, value) -> rx.Component:
    return rx.hstack(
        icon_badge(icon, color, size=14, box="30px"),
        rx.vstack(
            rx.text(label, size="1", color=color, weight="bold", letter_spacing="0.04em"),
            rx.text(value, size="2", color=theme.TEXT, line_height="1.3"),
            spacing="0",
            align="start",
            min_width="0",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _task_row(task) -> rx.Component:
    return rx.hstack(
        rx.cond(
            task["completable"],
            rx.icon(
                rx.cond(task["completed"], "square-check", task["type_icon"]),
                size=14,
                color=rx.cond(task["completed"], theme.AGENDA, task["type_color"]),
                style={"cursor": "pointer"},
                on_click=UserState.toggle_today_task(task["id"]),
                flex_shrink="0",
            ),
            rx.icon(task["type_icon"], size=14, color=task["type_color"], flex_shrink="0"),
        ),
        rx.cond(
            task["time_label"],
            rx.text(
                task["time_label"],
                size="1",
                color=theme.AGENDA,
                font_family=theme.FONT_MONO,
                white_space="nowrap",
                flex_shrink="0",
            ),
        ),
        rx.text(
            task["title"],
            size="1",
            text_decoration=rx.cond(task["completed"], "line-through", "none"),
            color=rx.cond(task["completed"], theme.DIM, theme.TEXT),
        ),
        spacing="2",
        align="center",
        width="100%",
    )


def _comment_row(comment) -> rx.Component:
    return rx.hstack(
        rx.text(
            comment["username"],
            size="1",
            color=theme.COMMENT,
            weight="bold",
            flex_shrink="0",
        ),
        rx.text(comment["content"], size="1", color=theme.MUTED),
        spacing="2",
        align="start",
        width="100%",
    )


def _calendar_block(cal) -> rx.Component:
    has_content = cal["meal"] | cal["dinner"] | cal["comments"] | cal["tasks"]
    return rx.cond(
        has_content,
        rx.vstack(
            rx.hstack(
                rx.icon("calendar-days", size=12, color=theme.DIM),
                rx.text(
                    cal["calendar_name"],
                    size="1",
                    color=theme.DIM,
                    weight="medium",
                    letter_spacing="0.04em",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            rx.cond(cal["meal"], _meal_line("COMIDA", "sun", theme.MEAL, cal["meal"])),
            rx.cond(cal["dinner"], _meal_line("CENA", "moon", theme.DINNER, cal["dinner"])),
            rx.cond(
                cal["tasks"],
                rx.vstack(
                    rx.hstack(
                        rx.icon("list-checks", size=12, color=theme.AGENDA),
                        rx.text("AGENDA", size="1", color=theme.AGENDA, weight="bold", letter_spacing="0.04em"),
                        spacing="2",
                        align="center",
                    ),
                    rx.foreach(cal["tasks"], _task_row),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
            ),
            rx.cond(
                cal["comments"],
                rx.vstack(
                    rx.hstack(
                        rx.icon("message-square-more", size=12, color=theme.COMMENT),
                        rx.text("COMENTARIOS", size="1", color=theme.COMMENT, weight="bold", letter_spacing="0.04em"),
                        spacing="2",
                        align="center",
                    ),
                    rx.foreach(cal["comments"], _comment_row),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
            ),
            spacing="3",
            width="100%",
            align="start",
            padding="12px",
            border_radius=theme.RADIUS_SM,
            cursor="pointer",
            on_click=DayState.open_today,
            _hover={"border_color": theme.BORDER_STRONG},
            background=theme.BG_SUNKEN,
            border=f"1px solid {theme.BORDER}",
        ),
        rx.fragment(),
    )


#Componente que registra la información del dia actual de todos los calendarios
def today_box() -> rx.Component:
    return panel(
        rx.vstack(
            rx.hstack(
                icon_badge("calendar-check", theme.ACCENT, size=17, box="38px"),
                rx.vstack(
                    rx.text("HOY", size="1", color=theme.DIM, weight="bold", letter_spacing="0.12em"),
                    rx.text(
                        rx.moment(
                            CalendarState.current_date_str,
                            format="dddd D [de] MMMM",
                            locale="es",
                            #Actualizamos la fecha actual al montar
                            on_mount=CalendarState.update_current_date,
                        ),
                        size="2",
                        weight="bold",
                        color=theme.TEXT,
                        style={"textTransform": "capitalize"},
                    ),
                    spacing="0",
                    align="start",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            #Editar el día de hoy sin buscarlo en la rejilla
            rx.hstack(
                rx.icon("square-pen", size=14, color=theme.ACCENT),
                rx.text("Editar hoy", size="1", color=theme.ACCENT, weight="medium"),
                rx.spacer(),
                rx.icon("chevron-right", size=14, color=theme.DIM),
                on_click=DayState.open_today,
                cursor="pointer",
                width="100%",
                align="center",
                spacing="2",
                padding="8px 10px",
                border_radius=theme.RADIUS_SM,
                background=theme.alpha(theme.ACCENT, 0.08),
                border=f"1px solid {theme.alpha(theme.ACCENT, 0.2)}",
                _hover={"background": theme.alpha(theme.ACCENT, 0.16)},
                transition="background 0.15s ease",
            ),
            rx.cond(
                #Si tenemos información para el día de hoy
                UserState.has_today_content,
                rx.vstack(
                    rx.foreach(UserState.today_data, _calendar_block),
                    spacing="3",
                    width="100%",
                ),
                #Antes esto era una caja vacía; ahora propone qué hacer
                rx.vstack(
                    rx.center(
                        rx.icon("utensils-crossed", size=22, color=theme.DIM),
                        width="52px",
                        height="52px",
                        border_radius="50%",
                        background=theme.BG_SUNKEN,
                        border=f"1px solid {theme.BORDER}",
                    ),
                    rx.text("Hoy no hay nada planificado", size="2", color=theme.MUTED, text_align="center"),
                    rx.text(
                        "Pulsa en el día de hoy en el calendario, o planifica la semana entera de una vez.",
                        size="1",
                        color=theme.DIM,
                        text_align="center",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("clipboard-list", size=14),
                            rx.text("Planificar la semana", size="1"),
                            variant="soft",
                            color_scheme="blue",
                            size="2",
                            radius="full",
                            cursor="pointer",
                        ),
                        href="/menu_semanal",
                        underline="none",
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                    padding_y="1.5em",
                ),
            ),
            spacing="3",
            width="100%",
            align="start",
        ),
        width="100%",
    )
