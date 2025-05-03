import reflex as rx
from calendar import Calendar
from Calendario.components.day_button import day_button
from Calendario.components.calendar_sharer import calendar_sharer
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

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
                    rx.text(
                        day,
                        size="2",
                        weight="bold",
                        color="gray.500",
                        text_transform="uppercase",
                    ),
                    width="100%",
                    padding="2px",
                ),
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding_x="1em",
        ),
        # Grid de días del mes
        rx.grid(
            rx.foreach(
                CalendarState.display_days,
                lambda day: rx.cond(
                    day,
                    day_button(day),
                    rx.box(
                        style={
                            "width": "12vw",
                            "height": "12vw",
                            "min_width": "40px",
                            "min_height": "40px",
                            "max_width": "70px",
                            "max_height": "70px",
                            "visibility": "hidden",
                        }
                    ),
                ),
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding="1em",
        ),
        spacing="3",
        width="100%",
        align_items="center",
    )

def user_calendar() -> rx.Component:
    return rx.vstack(
        # ─── 2) Resto de la UI ───
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
                                            ),
                                        )
                                    ),
                                    position="popper",
                                    side="bottom",
                                    align="start",
                                ),
                                value=rx.cond(
                                    CalendarState.current_calendar,
                                    CalendarState.current_calendar.id.to(str),
                                    "",
                                ),
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
                                style={"cursor": "pointer"},
                            ),
                        ),
                        rx.cond(
                            CalendarState.current_calendar,
                            rx.hstack(
                                rx.vstack(
                                    rx.heading(
                                        CalendarState.calendar_title,
                                        size="6",
                                        padding_bottom="1em",
                                        padding_top="2em",
                                    ),
                                    calendar_grid(),
                                    rx.hstack(
                                        calendar_sharer(),
                                        rx.dialog.root(
                                            rx.dialog.trigger(
                                                rx.hstack(
                                                    rx.text("Eliminar"),
                                                    rx.icon(
                                                        "calendar-off",
                                                        color_scheme="red",
                                                        variant="ghost",
                                                    ),
                                                    style={
                                                        "_hover": {
                                                            "color": "red",
                                                            "transform": "scale(1.12)",
                                                            "cursor": "pointer",
                                                        }
                                                    },
                                                    margin_top="0.5em",
                                                ),
                                            ),
                                            rx.dialog.content(
                                                rx.dialog.title("Confirmar eliminación"),
                                                rx.dialog.description(
                                                    "¿Estás seguro de querer eliminar este calendario y todos sus datos?"
                                                ),
                                                rx.flex(
                                                    rx.dialog.close(
                                                        rx.button(
                                                            "Cancelar",
                                                            variant="soft",
                                                            color_scheme="gray",
                                                        )
                                                    ),
                                                    rx.dialog.close(
                                                        rx.button(
                                                            "Eliminar",
                                                            color_scheme="red",
                                                            on_click=CalendarState.delete_calendar(
                                                                CalendarState.current_calendar.id
                                                            ),
                                                        )
                                                    ),
                                                    spacing="3",
                                                    margin_top="2em",
                                                    justify="end",
                                                ),
                                            ),
                                        ),
                                        spacing="7",
                                    ),
                                    
                                    spacing="4",
                                    align_items="center",
                                ),
                            ),
                        ),
                        align_items="center",
                        width="100%",
                    ),
                )
            ),
            align_items="center",
            justify_content="center",
            width="100%",
            padding="2em",
        ),

        # ─── 3) Props de rx.vstack (siempre al final) ───
        on_mount=UserState.today_info,
        align_items="center",
        justify_content="center",
        width="100vw",
        
    )
