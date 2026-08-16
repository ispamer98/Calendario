# Calendario/components/calendar_switcher.py
"""
Selector de calendarios.

Antes era un `rx.select` perdido en mitad de la página que solo mostraba el
nombre del calendario, sin decir a qué mes correspondía. Ahora es un menú con
una tarjeta por calendario: mes y año en grande, nombre, si es tuyo o
compartido, y cuánto lo tienes planificado.

Se usa en dos sitios (misma pieza, dos tamaños):
- `calendar_switcher()` en la barra superior, siempre a mano.
- `calendar_switcher(compact=False)` en la cabecera del calendario.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import pill, progress_bar
from Calendario.model.model import CalendarOption
from Calendario.state.calendar_state import CalendarState


def _option_row(option: rx.Var[CalendarOption]) -> rx.Component:
    is_active = CalendarState.current_calendar_id == option.id
    return rx.box(
        rx.hstack(
            #Mes en grande: es lo que uno busca al cambiar de calendario
            rx.center(
                rx.vstack(
                    rx.text(
                        option.month_abbr,
                        size="2",
                        weight="bold",
                        color=rx.cond(is_active, theme.ACCENT, theme.TEXT),
                        line_height="1",
                    ),
                    rx.text(
                        option.year_abbr,
                        size="1",
                        color=theme.DIM,
                        line_height="1",
                    ),
                    spacing="1",
                    align="center",
                ),
                min_width="52px",
                height="52px",
                border_radius=theme.RADIUS_SM,
                background=rx.cond(is_active, theme.alpha(theme.ACCENT, 0.16), theme.BG_SUNKEN),
                border=rx.cond(
                    is_active,
                    f"1px solid {theme.alpha(theme.ACCENT, 0.4)}",
                    f"1px solid {theme.BORDER}",
                ),
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(
                        option.name,
                        size="2",
                        weight="bold",
                        color=theme.TEXT,
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                        max_width="150px",
                    ),
                    rx.cond(
                        option.is_current_month,
                        pill("Este mes", theme.MEAL, "calendar-check"),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon(
                        rx.cond(option.is_owner, "crown", "users"),
                        size=12,
                        color=rx.cond(option.is_owner, theme.OWNER, theme.PURPLE),
                    ),
                    rx.text(
                        rx.cond(option.is_owner, "Tuyo", "Compartido contigo"),
                        size="1",
                        color=theme.MUTED,
                    ),
                    rx.text("·", size="1", color=theme.DIM),
                    rx.text(option.month_label, size="1", color=theme.MUTED),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    progress_bar(
                        option.percent,
                        rx.cond(option.percent > 60, theme.MEAL, theme.ACCENT),
                        height="5px",
                    ),
                    rx.text(
                        option.days_planned.to_string() + "/" + option.days_total.to_string(),
                        size="1",
                        color=theme.DIM,
                        white_space="nowrap",
                        min_width="42px",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                spacing="1",
                align="start",
                width="100%",
                min_width="0",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        on_click=CalendarState.select_calendar(option.id),
        cursor="pointer",
        padding="10px",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(is_active, theme.alpha(theme.ACCENT, 0.08), "transparent"),
        border=rx.cond(is_active, f"1px solid {theme.alpha(theme.ACCENT, 0.25)}", "1px solid transparent"),
        _hover={"background": theme.BG_CARD_HOVER},
        transition="background 0.15s ease",
        width="100%",
    )


def _trigger(compact: bool) -> rx.Component:
    """Botón que abre el selector: mes actual + nombre del calendario."""
    return rx.hstack(
        rx.icon("calendar-days", size=16, color=theme.ACCENT, flex_shrink="0"),
        rx.vstack(
            rx.text(
                rx.cond(CalendarState.current_calendar, CalendarState.calendar_title, "Sin calendario"),
                size=rx.cond(compact, "1", "2"),
                weight="bold",
                color=theme.TEXT,
                white_space="nowrap",
                line_height="1.2",
            ),
            rx.cond(
                CalendarState.current_calendar,
                rx.text(
                    CalendarState.current_calendar_name,
                    size="1",
                    color=theme.MUTED,
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    max_width=rx.cond(compact, "110px", "200px"),
                    line_height="1.2",
                ),
            ),
            spacing="0",
            align="start",
            min_width="0",
        ),
        rx.icon("chevrons-up-down", size=14, color=theme.MUTED, flex_shrink="0"),
        spacing="2",
        align="center",
        cursor="pointer",
        padding=rx.cond(compact, "5px 10px", "8px 14px"),
        border_radius="999px",
        background=theme.BG_CARD,
        border=f"1px solid {theme.BORDER}",
        _hover={"border_color": theme.alpha(theme.ACCENT, 0.45), "background": theme.BG_CARD_HOVER},
        transition="all 0.15s ease",
        max_width=rx.cond(compact, "220px", "320px"),
        min_width="0",
    )


def calendar_switcher(compact: bool = True) -> rx.Component:
    """Menú de calendarios. `compact=True` para la barra superior."""
    return rx.menu.root(
        rx.menu.trigger(_trigger(compact)),
        rx.menu.content(
            rx.vstack(
                rx.hstack(
                    rx.text("TUS CALENDARIOS", size="1", weight="bold", color=theme.DIM, letter_spacing="0.1em"),
                    rx.spacer(),
                    rx.text(
                        CalendarState.calendar_options.length().to_string() + " meses",
                        size="1",
                        color=theme.DIM,
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.cond(
                    CalendarState.has_calendars,
                    rx.vstack(
                        rx.foreach(CalendarState.calendar_options, _option_row),
                        spacing="1",
                        width="100%",
                        max_height="330px",
                        overflow_y="auto",
                    ),
                    rx.vstack(
                        rx.icon("calendar-x", size=22, color=theme.DIM),
                        rx.text("Todavía no tienes calendarios", size="1", color=theme.MUTED),
                        spacing="2",
                        align="center",
                        width="100%",
                        padding_y="1.5em",
                    ),
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.hstack(
                    rx.icon("calendar-plus", size=15, color=theme.MEAL),
                    rx.text("Crear calendario de un mes", size="2", color=theme.MEAL, weight="medium"),
                    on_click=CalendarState.open_calendar_creator,
                    cursor="pointer",
                    width="100%",
                    padding="9px 10px",
                    border_radius=theme.RADIUS_SM,
                    align="center",
                    spacing="2",
                    _hover={"background": theme.alpha(theme.MEAL, 0.10)},
                ),
                spacing="2",
                width="100%",
            ),
            width="330px",
            style={
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS,
                "padding": "12px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        modal=False,
    )
