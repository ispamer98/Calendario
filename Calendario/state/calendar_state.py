#calendar_state.py

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment, Calendar, User
from Calendario.state.user_state import UserState
from Calendario.utils.api import get_today_info,delete_calendar_and_days,get_shared_users,fetch_and_transform_calendars, get_all_meals, get_days_for_calendar, get_user_by_id, share_calendar_with_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz


class CalendarState(rx.State):
    """
    Manejador de estado para un calendario.
    """
    meals: List[Meal] = []  # Lista de opciones de comidas
    comments: List[Comment] = []  # Lista de comentarios para el día seleccionado
    calendars: List[Calendar] = []  # Almacena todos los calendarios del usuario
    toast_info: Optional[str] = None
    new_calendar_name : str = ""
    new_calendar_month: str = datetime.today().strftime("%Y-%m")
    loading : bool = False
    show_calendar_creator: bool = False
    error_message : Optional[str] = None 
    current_calendar: Optional[Calendar] = None
    days : List[Day] = [] 
    hovered_day: Optional[int] = None
    display_days: list[Optional[Day]] = []
    current_date_str: str
    loading: bool = True
    username_to_share: str = ""  # Nombre de usuario con quien compartir
    show_calendar_sharer: bool = False  # Nuevo estado
    shared_users: list[User] = []
    owner_username: str = ""
    @rx.event
    async def refresh_page(self):
        """Redirige a /calendar con el ID del calendario actual para recargarlo."""
        if not self.current_calendar:
            # Si no hay calendario seleccionado, no hace nada
            return 
        # Redirige a /calendar pasando el parámetro calendar_id
        else: 
            await self.set_current_calendar(self.current_calendar.id)
            await get_days_for_calendar(self.current_calendar.id)
            await self.load_calendars()
            

            print("refresh funciona")

        
    @rx.event
    async def delete_calendar(self, calendar_id: int):
        try:
            success = await delete_calendar_and_days(calendar_id)
            
            if success:
                # Actualizar lista de calendarios
                self.calendars = [cal for cal in self.calendars if cal.id != calendar_id]
                
                # Resetear calendario actual si era el eliminado
                if self.current_calendar and self.current_calendar.id == calendar_id:
                    self.current_calendar = None
                    self.days = []
                    self.display_days = []
                
                return rx.toast.success("Calendario eliminado exitosamente", position="top-center")
            else:
                return rx.toast.error("Error eliminando el calendario", position="top-center")
                
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}", position="top-center")

    @rx.event
    def open_calendar_sharer(self):
        self.show_calendar_sharer = True
        self.error_message = None
        self.username_to_share = ""
        

    @rx.event
    def close_calendar_sharer(self):
        self.show_calendar_sharer = False
# Calendario/state/calendar_state.py
    async def share_calendar(self):
        try:
            # Resetear mensajes previos
            self.error_message = None
            
            # Validaciones básicas
            if not self.current_calendar:
                
                return rx.toast.error("Selecciona un calendario primero", position="top-center")
                
            if not self.username_to_share.strip():
                self.username_to_share = ""
                return rx.toast.error("Escribe un nombre de usuario", position="top-center")

            # Verificar auto-compartición
            user_state = await self.get_state(UserState)
            if self.username_to_share.lower() == user_state.current_user.username.lower():
                self.username_to_share = ""
                return rx.toast.error("No puedes compartir contigo mismo", position="top-center")

            # Llamar a la API
            success, message = await share_calendar_with_user(self.current_calendar, self.username_to_share)
            
            if success:
                
                # Éxito: limpiar input y cerrar diálogo
                self.username_to_share = ""
                self.close_calendar_sharer()
                return rx.toast.success(message, position="top-center")
            else:
                # Error: mantener diálogo abierto y mostrar mensaje
                self.username_to_share = ""
                return rx.toast.error(message, position="top-center")
                
        except Exception as e:
            return rx.toast.error(f"Error inesperado: {str(e)}", position="top-center")
        

    @rx.event
    async def load_shared_users(self):
        if not self.current_calendar:
            return
            
        try:
            users = await get_shared_users(self.current_calendar.id)
            if users:
                self.owner_username = users[0].username
                self.shared_users = users[1:] if len(users) > 1 else []
            else:
                self.shared_users = []
                
        except Exception as e:
            print(f"Error cargando usuarios compartidos: {e}")
            self.shared_users = []

    @rx.var
    def calendar_title(self) -> str:
        if self.current_calendar and self.current_calendar.start_date:
            meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            mes = meses[self.current_calendar.start_date.month - 1]
            año = self.current_calendar.start_date.year
            return f" Calendario de {mes} del {año}"
        return ""
    

    def update_current_date(self):
        madrid_tz = pytz.timezone('Europe/Madrid')
        madrid_time = datetime.now(madrid_tz)
        self.current_date_str = madrid_time.strftime("%Y-%m-%d 00:00:00")
        print(self.current_date_str)
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
                    self.update_current_date()
                    
                    
                    return
        except ValueError:
            print(f"Error convirtiendo el valor: {value}")

    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True
            
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
                # Cargar los días del nuevo calendario
                self.days = await get_days_for_calendar(new_calendar.id)
                
                # Actualizar display_days para el nuevo calendario
                first_weekday = start_date.weekday()
                self.display_days = [None] * first_weekday + self.days
                
                self.close_calendar_creator()
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
        self.loading = True  # Activa el loader al iniciar la carga
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
                
            self.loading = False  # Desactiva el loader solo después de cargar

                
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
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None


