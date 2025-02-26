from calendar import Calendar
import reflex as rx
from Calendario.model.model import User
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState


def calendar_view(user: User) -> rx.Component:
    # Encabezado para la lista de calendarios
    return rx.cond(
        UserState.current_user,
        rx.container(
            rx.box(
                rx.heading(f"{UserState.current_user.username}", size="1"),
                rx.text(f"{CalendarState.calendars}"),
                # Iterar por los calendarios en el estado
                rx.foreach(
                    CalendarState.calendars,
                    lambda calendar: rx.box(
                        rx.text(f"Nombre: {calendar.name}", font_weight="bold"),
                        rx.text(f"Creado el: {calendar.created_at}"),
                        rx.divider(),

                        border="1px solid #ccc",
                        border_radius="8px",
                    )
                ),
                padding=6,
                border="1px solid #000",
                border_radius="8px",
            ),
            

        ),
        rx.text("NO HAY NADIE LOGGEADO!")
    )