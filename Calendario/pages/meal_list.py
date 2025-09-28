# Calendario/pages/meal_list.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.components.user_navbar import user_navbar
from Calendario.components.meal_editor import new_meal_input

# Página de listado de comidas “premium”
@rx.page(
    route="/meal_list",
    title="Comidas | CalendPy",
    on_load=[
        CalendarState.reset_calendars,
        CalendarState.clean,
        CalendarState.load_meals,
    ],
)
def meal_list() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        new_meal_input(),
        
    )