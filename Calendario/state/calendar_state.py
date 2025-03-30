#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment,Calendar
from Calendario.state.user_state import UserState
from Calendario.utils.api import SUPABASE_API, fetch_and_transform_calendars, get_all_meals, get_days_for_calendar
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
    days : List[Day] = [] 
    hovered_day: Optional[int] = None
    display_days: list[Optional[Day]] = []
    current_date_str: str = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")  # Variable para almacenar la fecha actual
    # Variable para almacenar la fecha actual
    def update_current_date(self):
        self.current_date_str = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
    @rx.event
    def set_hovered_day(self, day_id: int):
        self.hovered_day = day_id
        
    @rx.event
    def clear_hovered_day(self):
        self.hovered_day = None
    @rx.event
    def open_calendar_creator(self):
        self.show_calendar_creator = True
    
    @rx.event
    def close_calendar_creator(self):
        self.show_calendar_creator = False


    @rx.event
    async def load_meals(self):
        """Carga todas las comidas al iniciar"""
        try:
            total_meals = await get_all_meals()
            self.meals = total_meals
        except Exception as e:
            print(f"Error loading meals: {e}")

        
    @rx.event
    async def set_current_calendar(self, value: str):
        try:
            calendar_id = int(value)
            for calendar in self.calendars:
                if calendar.id == calendar_id:
                    self.current_calendar = calendar
                    self.days = await get_days_for_calendar(self.current_calendar.id)
                    
                    # Calcular espacios vacíos iniciales
                    start_date = self.current_calendar.start_date
                    first_weekday = start_date.weekday()  # Lunes=0, Domingo=6
                    
                    # Crear lista de días con espacios vacíos
                    self.display_days = [None] * first_weekday + self.days
                    
                    return
        except ValueError:
            print(f"Error convirtiendo el valor: {value}")

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




    async def load_days(self, calendar_id: int):
        self.days = await get_days_for_calendar(calendar_id)


    def update_day_in_state(self, updated_day: Day):
        # Actualizar días en el estado
        self.days = [
            updated_day if day.id == updated_day.id else day
            for day in self.days
        ]
        
        # Actualizar display_days manteniendo los espacios vacíos iniciales
        start_date = self.current_calendar.start_date
        first_weekday = start_date.weekday()
        self.display_days = [None] * first_weekday + self.days


    @rx.event
    def reset_calendars(self):
        """Resetea y recarga los calendarios"""
        self.calendars = []
        return CalendarState.load_calendars()
    @rx.event
    def clean(self):
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.days = [] # Reset to empty list
        self.current_calendar = None
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None


        return rx.toast.info(
             position="top-center",
             title="")