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

#Estado que maneja la lógica del calendario
class CalendarState(rx.State):
    meals: List[Meal] = []  #Lista de comidas en bd
    comments: List[Comment] = []  #Lista de comentarios para el día seleccionado
    calendars: List[Calendar] = []  # Lista de los calendarios del usuario
    toast_info: Optional[str] = None #Mensaje de información
    new_calendar_name : str = "" #Nombre para nuevo calendario
    new_calendar_month: str = datetime.today().strftime("%Y-%m") #Mes/año del nuevo calendario
    loading : bool = False #Manejador de carga
    show_calendar_creator: bool = False #Manejador para mostrar el creador de calendario
    error_message : Optional[str] = None #Mensaje de error para inputs
    current_calendar: Optional[Calendar] = None #Calendario actual
    days : List[Day] = [] #Lista de días del calendario seleccionado
    hovered_day: Optional[int] = None #Día seleccionado
    display_days: list[Optional[Day]] = [] #Días para mostrar en el calendario
    current_date_str: str #Fecha del día actual
    username_to_share: str = ""  #Nombre de usuario con quien compartir
    show_calendar_sharer: bool = False  #Manejador para mostrar compartir calendario
    shared_users: list[User] = [] #Lista de usuarios con acceso al calendario
    owner_username: str = "" #Nombre del dueño del calendario


    #Recarga los datos de la página
    @rx.event
    async def refresh_page(self):
        #Si no existe calendario seleccionado, no recarga información
        if not self.current_calendar:
            return 
        #Si existe calendario seleccionado:
        else: 
            #Recarga el calendario actual
            await self.set_current_calendar(self.current_calendar.id)
            #Obtiene los días del calendario
            await get_days_for_calendar(self.current_calendar.id)
            #Carga todos los calendarios
            await self.load_calendars()
            #Devuelve la información del día en curso
            return UserState.today_info()

            
    #Elimina el calendario actual
    @rx.event
    #Pasamnos la id del calendario como parámetro
    async def delete_calendar(self, calendar_id: int):
        try:
            #Eliminamos registros de calendario en base de datos
            success = await delete_calendar_and_days(calendar_id)
            
            #Si la acción se completa
            if success:
                #Creamos una lista de calendarios vacios
                current_calendars = []
                #Iteramos sobre los calendarios del usuario
                for cal in self.calendars:
                    #Comprobamos la id con la del calendario del parámetro
                    if cal.id != calendar_id:
                        #Si la id es distinta, añadimos el calendario a la lista
                        current_calendars.append(cal)
                #Reemplazamos la lista de calendarios por la nueva
                self.calendars = current_calendars
                
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

            # Recalcular aquí el rango exacto que usas en el input type="month"
            today = datetime.today()
            min_month = today.strftime("%Y-%m")
            # Máximo: diciembre del año siguiente
            max_month = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

            # Validación estricta contra esos límites
            if not (min_month <= self.new_calendar_month <= max_month):
                # Mostrar error y abortar, manteniendo el nombre ingresado
                return rx.toast.error(
                    f"Mes fuera de rango: debe ser entre {min_month} y {max_month}",
                    position="top-center"
                )

            # Parseo de fechas de inicio/fin de mes
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
                # Sólo en éxito limpiamos el nombre y añadimos el calendario
                self.calendars.append(new_calendar)
                self.current_calendar = new_calendar
                self.days = await get_days_for_calendar(new_calendar.id)

                first_weekday = start_date.weekday()
                self.display_days = [None] * first_weekday + self.days

                self.close_calendar_creator()
                # Limpiar nombre y mes tras éxito
                self.new_calendar_name = ""
                self.new_calendar_month = today.strftime("%Y-%m")
                return rx.toast.success(
                    f"Calendario '{self.current_calendar.name}' creado con éxito!",
                    position="top-center"
                )

        except ValueError as ve:
            return rx.toast.error(str(ve), position="top-center")
        except Exception as e:
            return rx.window_alert(f"Error: {str(e)}")
        finally:
            self.loading = False

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



    @rx.event
    async def update_day_in_state(self, updated_day: Day):
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
    async def reset_calendars(self):
        """Sincroniza sólo las diferencias: añade, elimina y actualiza calendarios."""
        user_state= await self.get_state(UserState)
        if user_state.current_user:
            # 1) Traer la lista actualizada desde la base de datos
            new_list = await fetch_and_transform_calendars(
                user_state.current_user.id
            )

            # 2) Crear mapas id → calendario para viejo y nuevo
            old_map = {c.id: c for c in self.calendars}
            new_map = {c.id: c for c in new_list}

            # 3) Eliminar los que ya no existen
            removed = set(old_map) - set(new_map)
            if removed:
                self.calendars = [c for c in self.calendars if c.id not in removed]

            # 4) Añadir los nuevos
            added = set(new_map) - set(old_map)
            for cid in added:
                self.calendars.append(new_map[cid])

            # 5) Actualizar los que cambiaron (si cambian propiedades)
            for cid in set(new_map) & set(old_map):
                if new_map[cid] != old_map[cid]:
                    idx = next(i for i, c in enumerate(self.calendars) if c.id == cid)
                    self.calendars[idx] = new_map[cid]
    @rx.event
    def clean(self):
        self.meals = []  # Reset to empty list
        self.comments = []  # Reset to empty list
        self.days = [] # Reset to empty list
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.current_calendar = None
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None


