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
