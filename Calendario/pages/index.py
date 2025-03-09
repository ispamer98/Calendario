from calendar import Calendar
import reflex as rx
 


from Calendario.components.current_user_button import current_user_button
from Calendario.components.calendar_view import calendar_view
from Calendario.components.login_register import login_card
from Calendario.state.calendar_state import CalendarState
from Calendario.state.register_state import RegisterState
from Calendario.state.user_state import UserState
from Calendario.database.database import SupabaseAPI
@rx.page(route="/", title="Calendario | Python", on_load=RegisterState.load_page()
         )
def index() -> rx.Component:
    return rx.container(
        rx.cond(
            UserState.current_user,
            rx.container(
                rx.spacer(
                    height="200px"
                ),
                rx.text("Redirecting..."),
                current_user_button()


            ),
            login_card()
        )
    )
