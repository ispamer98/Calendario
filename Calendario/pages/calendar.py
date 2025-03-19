import reflex as rx
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.components.default_calendar import default_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info,position="top-center")

@rx.page(route="/calendar", on_load=CalendarState.reset_calendars)
def calendar() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        rx.container(
            rx.vstack(
                rx.cond(UserState.current_user,
                    user_calendar(),
                    rx.vstack(
                        rx.text("No hay nadie loggeado"),
                        rx.button("Volver al inicio",
                                  on_click=rx.redirect("/"))
                    ),
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
        style={"overflow-x": "hidden"},
        
    )