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
        #Si no existe calendario seleccionado, solo recarga la info de hoy
        if not self.current_calendar:
            return UserState.today_info()
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
                
                #Resetea la visión del calendario
                self.current_calendar = None
                self.days = []
                self.display_days = []

                #Devuelve un mensaje de información y actualiza la info de hoy por si ha sufrido cambios
                return [rx.toast.success("Calendario eliminado exitosamente", position="top-center"),
                        UserState.today_info()]
            else:
                #Si existe algún error, devuelve un mensaje con el error
                return rx.toast.error("Error eliminando el calendario", position="top-center")
                
        except Exception as e:
            #Si falla la base de datos, devuelve error
            return rx.toast.error(f"Error: {str(e)}", position="top-center")

    #Abrir compartir calendario
    @rx.event
    def open_calendar_sharer(self):
        self.show_calendar_sharer = True
        self.error_message = None
        self.username_to_share = ""
        
    #Cerrar compartir calendario
    @rx.event
    def close_calendar_sharer(self):
        self.show_calendar_sharer = False

    #Compartir calendario
    async def share_calendar(self):
        try:
            #Resetea mensajes de error previos
            self.error_message = None
            
            #Si no existe calendario, muestra error
            if not self.current_calendar:
                return rx.toast.error("Selecciona un calendario primero", position="top-center")
            
            #Si no se ha introducido nombre de usuario para compartir
            if not self.username_to_share.strip():
                self.username_to_share = "" #Resetea el campo
                #Devuelve mensaje de error
                return rx.toast.error("Escribe un nombre de usuario", position="top-center")

            #Si intentas compartir con el usuario loggeado
            #Obtenemos el estado de usuario
            user_state = await self.get_state(UserState)
            #Comparamos los nombres de usuario, si coincide
            if self.username_to_share.lower() == user_state.current_user.username.lower():
                #Resetea el campo
                self.username_to_share = ""
                #Devuelve error
                return rx.toast.error("No puedes compartir contigo mismo", position="top-center")

            #Intentamos llamar a la función que comparte el calendario
            success, message = await share_calendar_with_user(self.current_calendar, self.username_to_share)
            
            #Si tiene éxito
            if success:
                #Limpiamos el campo y cerramos el diálogo
                self.username_to_share = ""
                self.close_calendar_sharer()
                #Devolvemos mensaje de éxito
                return rx.toast.success(message, position="top-center")
            #Si se genera error
            else:
                #Limpiamos el campo y devolvemos el mensaje de error
                self.username_to_share = ""
                return rx.toast.error(message, position="top-center")
        
        #Si se produce error de bd
        except Exception as e:
            #Mostramos mensaje de error
            return rx.toast.error(f"Error inesperado: {str(e)}", position="top-center")
        
    #Carga los usuarios con acceso al calendario
    @rx.event
    async def load_shared_users(self):
        #Si no hay calendario seleccionado
        if not self.current_calendar:
            return #Para el proceso
            
        try:
            #Cargamos los usuarios desde la base de datos
            users = await get_shared_users(self.current_calendar.id) #Pasando el calendario
            if users: 
                #Si tenemos respuesta, el primer usuario es el dueño
                self.owner_username = users[0].username
                #El resto ( si hay, se incluyen como usuarios )
                self.shared_users = users[1:] if len(users) > 1 else []
            else:
                #Si no hay respuesta, enviamos lista vacia
                self.shared_users = []
                
        except Exception as e:
            #Si hay error en el proceso, devolvemos lista vacía
            print(f"Error cargando usuarios compartidos: {e}")
            self.shared_users = []
    
    #Obtenemos el nombre del més del calendario
    @rx.var
    def calendar_title(self) -> str:
        #Si hay calendario seleccionado y tiene fecha de inicio
        if self.current_calendar and self.current_calendar.start_date:
            meses = [ #Creamos una lista con todos los meses en español
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            #Identificamos el mes, comparando con la lista
            mes = meses[self.current_calendar.start_date.month - 1]
            #Guarda el año
            año = self.current_calendar.start_date.year
            #Retornamos la fecha del calendario
            return f" Calendario de {mes} del {año}"
        return "" #Si no hay calendario retorna cadena vacía
    
    #Actualizamos la fecha actual
    def update_current_date(self):
        #Establecemos zona horaria
        madrid_tz = pytz.timezone('Europe/Madrid')
        #Sacamos la hora actual para la zona horaria
        madrid_time = datetime.now(madrid_tz)
        #Guardamos la fecha actual formateada
        self.current_date_str = madrid_time.strftime("%Y-%m-%d 00:00:00")

    #Guardamos el día sobre el que se situa el ratón
    @rx.event
    def set_hovered_day(self, day_id: int):
        self.hovered_day = day_id
    
    #Limpiamos el día sobre el que se situa el ratón
    @rx.event
    def clear_hovered_day(self):
        self.hovered_day = None

    #Controla la apertura del creador de calendario
    @rx.event
    def open_calendar_creator(self):
        self.show_calendar_creator = True
    
    #Controla el cierre del creador de calendario
    @rx.event
    def close_calendar_creator(self):
        self.show_calendar_creator = False

    #Cargamos las comidas desde base de datos
    @rx.event
    async def load_meals(self):
        try:
            #Guardamos los registros que nos aporta la base de datos
            total_meals = await get_all_meals()
            self.meals = total_meals
        except Exception as e:
            print(f"Error loading meals: {e}")

    #Guardamos el calendario que selecciona el usuario
    @rx.event
    async def set_current_calendar(self, value: str):
        try:
            #Guardamos la id
            calendar_id = int(value)
            #Iteramos sobre los calendarios del usuario
            for calendar in self.calendars:
                #Comparamos la id con la del calendario del usuario
                if calendar.id == calendar_id:
                    #Cuando coincide, guardamos el calendario actual
                    self.current_calendar = calendar
                    #Guardamos los dias que nos da la base de datos
                    self.days = await get_days_for_calendar(self.current_calendar.id)
                    start_date = self.current_calendar.start_date
                    #Calculamos el indice en la semana del primer día del més
                    first_weekday = start_date.weekday()
                    
                    #Creamos la lista de días incluyendo días vacios al principio
                    self.display_days = [None] * first_weekday + self.days
                    self.update_current_date()
                    return
        except ValueError:
            print(f"Error convirtiendo el valor: {value}")

    #Función para crear el calendario
    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True
            #Si no encuentra usuario, lanza excepción
            if UserState.current_user is None:
                raise Exception("Usuario no autenticado")

            #Calcula el rango máximo que permite el input
            today = datetime.today()
            #Mínimo el més actual
            min_month = today.strftime("%Y-%m")
            #Máximo, diciembre del año siguiente
            max_month = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

            if not (min_month <= self.new_calendar_month <= max_month):
                return rx.toast.error(
                    f"Mes fuera de rango: debe ser entre {min_month} y {max_month}",
                    position="top-center"
                )

            #Convierte la fecha de inicio del calendario en un objeto datetime
            start_date = datetime.strptime(self.new_calendar_month, "%Y-%m")
            #Convertimos le fecha de fin en un objeto datetime, sumando 1 mes y restando 1 dia
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

            #Creamos el calendario en base de datos
            db = SupabaseAPI()
            #Obtenemos el estado de usuario para obtener los datos del mismo
            user_state = await self.get_state(UserState)
            #Creamos el calendario con los parametros calculados
            new_calendar = db.create_calendar_with_days(
                user_id=user_state.current_user.id,
                calendar_name=self.new_calendar_name,
                start_date=start_date,
                end_date=end_date
            )
            #Si tenemos éxito
            if new_calendar:
                #Añadimos el calendario a la lista de calendarios del usuario
                self.calendars.append(new_calendar)
                #Establecemos el nuevo calendario como actual
                self.current_calendar = new_calendar
                #Guardamos los dias del calendario
                self.days = await get_days_for_calendar(new_calendar.id)
                #Obtenemos la posicion del primer día
                first_weekday = start_date.weekday()
                self.display_days = [None] * first_weekday + self.days
                #Cerramos el creador de calendario
                self.close_calendar_creator()
                #Limpiamos el nombre de nuevo calendario
                self.new_calendar_name = ""
                #Establecemos el nuevo mes por defecto en el mes actual
                self.new_calendar_month = today.strftime("%Y-%m")
                return rx.toast.success(
                    f"Calendario '{self.current_calendar.name}' creado con éxito!",
                    position="top-center"
                )

        except ValueError as ve:
            return rx.toast.error(str(ve), position="top-center")
        except Exception as e:
            return rx.toast.error(str(e), position="top-center")
        finally:
            self.loading = False

    #Cargamos lo calendarios del usuario
    @rx.event
    async def load_calendars(self):
        self.loading = True
        try:
            #Obtenemos el id del usuario
            user_state = await self.get_state(UserState)
            user_id = user_state.current_user.id
            
            #Si no existe usuario loggeado, retornamos error
            if user_state.current_user is None:
                return rx.toast.error(
                    position="top-center",
                    title="Debes iniciar sesión para ver tus calendarios."
                )
            
            #Obtenemos los calendarios desde la base de datos para el usuario loggeado
            calendars = await fetch_and_transform_calendars(user_id)
            if calendars:
                #Guardamos los calendarios obtenidos
                self.calendars = calendars
                
            self.loading = False

                
        except Exception as e:
            return rx.toast.error(str(e), position="top-center")

    #Actualiza los días por si sufren cambios
    @rx.event
    async def update_day_in_state(self, updated_day: Day):
        #Iteramos sobre los días del calendario actual, si encuentra coincidencias, actualiza el día
        self.days = [
            updated_day if day.id == updated_day.id else day
            for day in self.days
        ]
        
        start_date = self.current_calendar.start_date
        first_weekday = start_date.weekday()
        self.display_days = [None] * first_weekday + self.days

    #Vuelve a cargar los calendarios, para aplicar modificaciones
    @rx.event
    async def reset_calendars(self):
        #Obtenemos el estado del usuario
        user_state= await self.get_state(UserState)
        #Si tenemos usuario autenticado
        if user_state.current_user:
            #Recupera los calendarios de la base de datos
            new_list = await fetch_and_transform_calendars(
                user_state.current_user.id
            )
            #Creamos una lista con la id de los calendarios actuales
            old_calendars = {}
            for calendar in self.calendars:
                old_calendars[calendar.id] = calendar

            #Creamos una lista con las id de los calendarios en base de datos
            new_calendars = {}
            for calendar in new_list:
                new_calendars[calendar.id] = calendar

            #Buscamos diferencias entre los actuales y los de base de datos para borrar los eliminados
            removed = set(old_calendars) - set(new_calendars)
            if removed:
                filtered = []
                #Si no aparece en la lista de eliminados, lo añadimos a la lista de filtrados
                for cal in self.calendars:
                    if cal.id not in removed:
                        filtered.append(cal)
                #Guardamos la lista en el estado
                self.calendars = filtered

            #Buscamos diferencias entre los actuales y los de base de datos para añadir los nuevos
            added = set(new_calendars) - set(old_calendars)
            if added:
                for cal_id in added:
                    #Recorre la lista y añade los calendarios que se han creado recientemente
                    new_cal = new_calendars[cal_id]
                    self.calendars.append(new_cal)

    #Limpia todos los datos asociados al calendario ( Cuando el usuario cierra sesión )
    @rx.event
    def clean(self):
        self.meals = []
        self.comments = [] 
        self.days = []
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.current_calendar = None
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None


