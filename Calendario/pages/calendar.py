import reflex as rx
from Calendario.components.meal_editor import meal_editor
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info, position="top-center")

@rx.page(route="/calendar", on_load=[CalendarState.reset_calendars, CalendarState.clean,UserState.on_load,CalendarState.load_meals])
def calendar() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        meal_editor(),
        rx.container(
            rx.vstack(
                rx.cond(
                    UserState.current_user,
                    rx.cond(
                        CalendarState.calendars,
                        user_calendar(),
                        rx.vstack(
                            rx.text("No tienes ningún calendario"),
                            rx.button("Crear Calendario", on_click=CalendarState.open_calendar_creator),
                            align_items="center"  # Centrar contenido dentro del vstack
                        ),
                    ),
                    rx.vstack(
                        rx.text("No hay nadie loggeado"),
                        rx.button("Volver al inicio", on_click=rx.redirect("/")),
                        align_items="center"
                    ),
                ),
                width="100%",
                align_items="center",  # Centrar todo dentro del vstack principal
            ),
            width="100%",
            max_width="1200px",
            padding_x="2em",
            padding_top="6em",
            align="center"  # Centrar el container horizontalmente
        ),
        width="100%",
        spacing="0",
        align_items="center",  # Centrar la pila de elementos
        style={"overflow-x": "hidden"},
    )
