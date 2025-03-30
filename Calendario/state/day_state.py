
import reflex as rx
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment


class DayState(rx.State):
    meals: List[Meal] = []
    comments : List[Comment] = []
    current_day: Optional[Day] = None  # Cambiado a current_day para más claridad


