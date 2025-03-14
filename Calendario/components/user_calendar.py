# Calendario/components/user_calendar.py
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState
from Calendario.components.calendar_creator import calendar_creator

def user_calendar() -> rx.Component:
    return rx.vstack(
        rx.container(
            rx.vstack(
                rx.text(UserState.username),
                rx.cond(
                    UserState.current_user,
                    rx.vstack(
                        rx.button(
                            "Logout",
                            on_click=[UserState.logout]
                        ),
                        rx.text("CALENDARIOS"),
                        rx.button(on_click=CalendarState.load_calendars),
                        rx.cond(
                            CalendarState.calendars.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    CalendarState.calendars,
                                    lambda calendar: rx.text(calendar.name)
                                ),
                            ),
                            rx.text("NO HAY CALENDARIOS EN CALENDAR.PY")
                        ),
                    ),
                    rx.container(
                        rx.text("NO HAY NADIE LOGGEADO EN CALENDAR.PY"),
                        rx.button(
                            "Go Home",
                            on_click=rx.redirect("/")
                        )
                    )
                ),
                width="100%",
                padding_x="0",
            ),
            width="100%",
            max_width="1200px",
            padding_x="2em",
            padding_top="6em",
        ),
        width="100%",
        spacing="0",
        style={"overflow-x": "hidden"}
    )