#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import fetch_and_transform_calendars


class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    current_month: datetime = datetime.today()  # Fecha del mes actual
    selected_day: Optional[datetime] = None  # Día seleccionado
    selected_day_data: Optional[Day] = None  # Datos del día seleccionado
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    current_calendar: Optional[Calendar] = None
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info : str = None


    @rx.event
    async def load_calendars(self):
        print("EN CALENDAR STATE LOAD  CALENDARS")

        try:
            user_state = await self.get_state(UserState)
            user_id = user_state.current_user.id
            
            if user_state.current_user is None:
                return rx.toast.error(
                    position="top-center",
                    title="Debes iniciar sesión para ver tus calendarios."
                )
                
            calendars = await fetch_and_transform_calendars(user_id)
            if calendars:
                self.calendars = calendars
                print(f"Calendarios cargados: {[f'ID: {cal.id}, Nombre: {cal.name}, Propietario ID: {cal.owner_id}, Compartido con: {cal.shared_with}, Creado en: {cal.created_at}' for cal in self.calendars]}")
            else:
                print("No se encontraron calendarios.")
                
        except Exception as e:
            print(e)


    @rx.event
    def set_current_calendar(self, calendar : Calendar):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.current_calendar = calendar
        print(f"Calendario actualizado: {self.current_calendar.name}")

    @rx.event
    def clean(self):
        self.current_month = datetime.today()
        self.selected_day = None
        self.selected_day_data = None
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.current_calendar = None 
        self.calendars = []  # Reset to empty list

        return rx.toast.info(
             position="top-center",
             title="")