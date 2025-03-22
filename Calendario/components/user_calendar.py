# Calendario/components/user_calendar.py
from turtle import position
import reflex as rx
from Calendario.components.day_button import day_button
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState
from Calendario.components.calendar_creator import calendar_creator

def botones() -> rx.Component:
    return [rx.text("CALENDARIOS"),
    rx.button("Info Calendarios",on_click=CalendarState.load_calendars)]

async def calendars() -> rx.Component:
    calendar_state = await CalendarState.get_state(CalendarState)
    return calendar_state.calendars

def calendar_grid() -> rx.Component:
    return rx.grid(
        rx.foreach(
            CalendarState.days,
            lambda day: day_button(day)
        ),
        grid_template_columns="repeat(7, 1fr)",
        gap="4px",
        width="100%",
        padding="1em"
    )

def user_calendar() -> rx.Component:
    return rx.vstack(
        rx.container(
            rx.vstack(
                rx.cond(
                    CalendarState.calendars.length() > 0,
                    rx.vstack(
                        botones(),
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecciona un calendario",
                                width="300px",
                                min_width="300px",
                                justify_content="center"),
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
                                align="start"
                            ),
                            
                            on_change=CalendarState.set_current_calendar,
                            width="100%",
                            variant="surface",
                            radius="full"
                        ),
                        rx.cond(
                            CalendarState.current_calendar,
                            rx.vstack(
                                rx.heading(
                                    CalendarState.current_calendar.name, 
                                    size="6",
                                    padding_bottom="1em"
                                ),
                                calendar_grid(),
                                spacing="4"
                            ),
                            rx.text("Selecciona un calendario")
                        ),
                        
                    )
                    
                )
            )
        )
    )