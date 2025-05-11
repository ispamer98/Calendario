# File: Calendario/pages/calendar.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.meal_editor import meal_editor
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState
from Calendario.components.today_box import today_box


@rx.page(
    route="/profile",
    title="Calendario | CalendPy",
)
def profile() -> rx.Component:
    return rx.vstack(
    )