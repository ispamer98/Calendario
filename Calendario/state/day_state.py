
import reflex as rx
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment
from Calendario.state.calendar_state import CalendarState


class DayState:
    currant_day : Day = None
    meal : Optional[Meal] = None
    dinner : Optional[Meal] = None
    comments : List[Optional[Comment]] = []


    @rx.event
    def set_current_day(self, value: str):
        pass



