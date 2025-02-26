from turtle import title
import reflex as rx
from Calendario.components.calendar_view import calendar_view
from Calendario.components.current_user_button import current_user_button
from Calendario.state import user_state
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info,position="top-center")

@rx.page(route="/calendar",on_load=CalendarState.load_calendars)
def calendar() -> rx.Component:
    return rx.container(
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
                            )
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

        )
    ),



    