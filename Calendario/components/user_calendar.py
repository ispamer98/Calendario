# Calendario/components/user_calendar.py
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState
from Calendario.components.calendar_creator import calendar_creator

def botones() -> rx.Component:
    return [rx.text("CALENDARIOS"),
    rx.button("Info Calendarios",on_click=CalendarState.load_calendars)]

async def calendars() -> rx.Component:
    calendar_state = await CalendarState.get_state(CalendarState)
    return calendar_state.calendars


def user_calendar() -> rx.Component:
    return rx.vstack(
        rx.container(
            rx.vstack(
                rx.cond(
                    CalendarState.calendars.length() > 0,
                    rx.vstack(
                        botones(),
                        rx.select.root(
                            rx.select.trigger(placeholder="Selecciona un calendario"),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        CalendarState.calendars,
                                        lambda cal: rx.select.item(
                                            f"{cal.name} ( {cal.start_date})",
                                            value=cal.id.to(str),
                                        )
                                    )
                                )
                            ),
                            
                            on_change=CalendarState.set_current_calendar,
                            width="100%",
                            variant="surface",
                            radius="full"
                        ),
                        rx.cond(
                            CalendarState.current_calendar,
                            rx.vstack(
                                rx.text(
                                    f"Calendario: {CalendarState.current_calendar.name}",
                                    weight="bold",
                                    size="5"
                                )
                            )
                        )
                    )
                )
            )
        )
    )