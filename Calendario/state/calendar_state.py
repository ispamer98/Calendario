#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import SUPABASE_API, fetch_and_transform_calendars
from datetime import datetime
from dateutil.relativedelta import relativedelta



class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info : str = None
    new_calendar_name : str = ""
    new_calendar_month: str = datetime.today().strftime("%Y-%m")
    loading : bool = False
    show_calendar_creator: bool = False
    error_message : Optional[str] = None 
    current_calendar: Optional[Calendar] = None
    @rx.event
    def open_calendar_creator(self):
        self.show_calendar_creator = True
    
    @rx.event
    def close_calendar_creator(self):
        self.show_calendar_creator = False

    @rx.event
    def select_calendar(self, calendar = Calendar):
        self.current_calendar = calendar


    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True  # Activamos carga
            
            if UserState.current_user is None:
                raise Exception("Usuario no autenticado")

            # Convertir mes seleccionado a fechas
            start_date = datetime.strptime(self.new_calendar_month, "%Y-%m")
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

            # Crear calendario en Supabase
            db = SupabaseAPI()
            user_state = await self.get_state(UserState)
            new_calendar = db.create_calendar_with_days(
                user_id=user_state.current_user.id,
                calendar_name=self.new_calendar_name,
                start_date=start_date,
                end_date=end_date
            )

            if new_calendar:
                self.calendars.append(new_calendar)
                self.current_calendar = new_calendar
                self.close_calendar_creator()  # Cierra el diálogo solo si se crea correctamente
                return rx.toast.success(f"Calendario '{self.new_calendar_name}' creado con éxito!", position="top-center")
        
        except ValueError as ve:
            return rx.toast.error(str(ve), position="top-center")
        except Exception as e:
            return rx.window_alert(f"Error: {str(e)}")
        finally:
            self.loading = False
            self.new_calendar_name = ""
            self.new_calendar_month = datetime.today().strftime("%Y-%m")



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
    def reset_calendars(self):
        """Resetea y recarga los calendarios"""
        self.calendars = []
        return CalendarState.load_calendars()
    @rx.event
    def clean(self):
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.calendars = []  # Reset to empty list

        return rx.toast.info(
             position="top-center",
             title="")