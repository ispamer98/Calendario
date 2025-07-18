#user_state.py

from turtle import position
import bcrypt
import reflex as rx
import re
from typing import Optional
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user,get_today_info,change_pasw
from datetime import datetime
import json
from typing import TypedDict

#Clase para incluir los datos relacionados a comentarios
class Comment(TypedDict):
    username: str
    content: str

#Clase para incluir los datos relacionados a la información del día actual del calendario
class CalendarInfo(TypedDict):
    calendar_name: str
    meal: str
    dinner: str
    comments: list[Comment]

#Clase para manejar el estado del usuario
class UserState(rx.State):

    user_storage: str = rx.LocalStorage("")  # 1Almacena en local el login de usuario
    username: str = ""  #Guarda el nombre del usuario
    password: str = ""  #Guarda la contraseña
    current_user: Optional[User] = None  #Información sobre el usuario loggeado
    today_data: list[CalendarInfo] = [] #Datos del día de hoy
    new_password: str = "" #Nueva contraseña al cambiarla
    confirm_password: str = "" #Confirmación
    timezone: str = "UTC+1" #Zona horaria
    current_password : str = "" #Contraseña actual
    current_page : str = "calendar"  #Manejador de cambio de páginas
    show_new_pasw: bool = False #Switch para mostrar la nueva contraseña

    #Reseteo de datos en página security ( cambio de contraseña )
    @rx.event
    def reset_security(self):
        self.new_password = ""
        self.confirm_password = ""
        self. current_password = ""

    #Muestra la nueva contraseña
    @rx.event
    def swith_on(self, value: bool = True):
        self.show_new_pasw = value

    #Oculta la nueva contraseña
    @rx.event
    def swith_off(self, value: bool = False):
        self.show_new_pasw = value

    #Resetea a False el switch para mostrar la contraseña
    @rx.event
    def reset_switch(self):
        self.show_new_pasw = False

    #Función que cambia la contraseña
    async def change_password(self):
        #Si no se introduce contraseña, lanzamos error
        if not self.new_password:
            return rx.toast.error("Contraseña nueva requerida",position="top-center")

        #Establecemos el filtro para la contraseña
        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
        #Si la contraseña no coincide con el filtro, resetea los campos
        if not re.match(pattern, self.new_password):
            self.new_password = ""
            self.confirm_password = ""
            self.current_password = ""
            #Y genera un error
            return rx.toast.error("La contraseña debe tener mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial",position="top-center")

        #Si las contraseñas no coinciden, resetea los campos
        if self.new_password != self.confirm_password:
            self.new_password = ""
            self.confirm_password = ""
            self.current_password = ""
            #Y lanza error
            return rx.toast.error("Las contraseñas no coinciden",position="top-center")

        #Verifica que la contraseña introducida coincida con la actual
        if not bcrypt.checkpw(self.current_password.encode('utf-8'), self.current_user.pasw.encode('utf-8')):
            #Si no coincide resetea los campos
            self.new_password = ""
            self.confirm_password = ""
            self.current_password = ""
            #Y lanza error
            return rx.toast.error("La contraseña actual no coincide",position="top-center")

        #Aplicamos hash a la nueva contraseña
        new_pasw_hash = bcrypt.hashpw(self.new_password.encode(), bcrypt.gensalt()).decode()

        #Cambia la contraseña en base de datos
        response = await change_pasw(self.current_user.username, new_pasw_hash)
        

        if response == True:
            self.new_password = ""
            self.confirm_password = ""
            self.current_password = ""
            #Si tenemos éxito, devuelve mensaje de éxito y cerramos la sesión actual
            return [rx.toast.success(f"Contraseña actualizada para {self.current_user.username}",position="top-center"),
                    UserState.logout(),
                    rx.redirect("/")]
            
        else:
            #Si no, devuelve mensaje de error
            self.new_password = ""
            self.confirm_password = ""
            self.current_password = ""
            return rx.toast.error("No ha sido posible actualizar la contraseña",position="top-center")

    #Recogemos los datos del día de hoy, en segundo plano
    @rx.event(background=True)
    async def today_info(self):
        async with self:
            if self.current_user:
                self.today_data = await get_today_info(self.current_user.id)
    
    #Si presionamos la tecla "Enter", se intenta el login
    @rx.event
    def press_enter(self, key: str):
        if key == "Enter":
            return UserState.login
    
    #Devolvemos el usuario en forma de cadena
    def return_username(self) -> str:
        return self.username
    
    #Actualiza el nombre de usuario
    @rx.event
    def set_username(self, username: str):
        self.username = username

    #Actualiza la contraseña
    @rx.event
    def set_password(self, password: str):
        self.password = password

    #Actualizamos la nueva contraseña
    @rx.event
    def set_new_password(self, password: str):
        self.new_password = password

    #Actualizamos la confirmación de contraseña
    @rx.event
    def set_confirm_password(self, password: str):
        self.confirm_password = password

    #Actualizamos la contraseña actual
    @rx.event
    def set_current_password(self, password: str):
        self.current_password = password

    #Verificamos si existe usuario loggeado
    @rx.event
    def check_autenticated(self):
        if self.current_user == None:
            #Si no existe usuario, redirige al indice
            return rx.redirect("/")

    #Devuelve True o False según exista o no usuario loggeado
    @rx.var
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    #Recuperamos la información del usuario desde el almacenamiento local
    def _load_user_from_storage(self):
        #Si existen datos almacenados
        if self.user_storage:
            try:
                #Convertimos a json y almacenamos los datos
                user_data = json.loads(self.user_storage)
                #Convertimos fechas de string a objeto datetime
                user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                #Guardamos el usuario actual creando una instancia del mismo
                self.current_user = User(**user_data)
            #Si existe error, limpiamos el almacenamiento y devolvemos error
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                self._clear_storage()
                return rx.toast.error(f"Error cargando usuario: {e}")
                
    #Guarda los datos del usuario en el almacenamiento local
    def _save_user_to_storage(self):
        #Si existe usuario loggeado
        if self.current_user:
            #Convertimos los datos del usuario a tipo "dict"
            user_dict = self.current_user.__dict__.copy()
            #Convertimos las fechas de datetime a string
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            #Y guardamos el .json en el almacenamiento local
            self.user_storage = json.dumps(user_dict)
        else:
            #Si no hay usuario, almacenamiento local queda vacio
            self.user_storage = ""

    #Función que limpia el almacenamiento local
    def _clear_storage(self):
        """Limpia todos los datos de almacenamiento"""
        self.user_storage = ""
        self.current_user = None
        self.username = ""
        self.password = ""

    #Carga los datos del usuario al cargar la página
    @rx.event
    async def on_load(self):
        self._load_user_from_storage()

    #Función que da autentica al usuario
    @rx.event
    async def login(self):
        #Si no tenemos usuario o contraseña, resetea el campo de contraseña
        if not self.username or not self.password:
            self.restart_pasw()

        try:
            #Tratamos de autenticar al usuario
            user_data = await authenticate_user(self.username.lower(), self.password)
            
            if user_data:
                #Si recibimos respuesta, guardamos el usuario
                self.current_user = user_data
                #Guardamos en el almacenamiento local tambien
                self._save_user_to_storage()
                #Reseteamos los inputs
                self.username = ""
                self.password = ""
                #Retornamos mensaje de bienvenida y redirigimos al calendario
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                #Si no tenemos éxito, limpiamos almacenamiento local y los inputs
                self._clear_storage()
                self.username = ""
                self.password = ""
                #Devolvemos el error
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        #Si hay algun problema, limpiamos almacenamiento local y devolvemos error
        except Exception as e:
            self._clear_storage()
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )

    #Función que cierra la sesión
    @rx.event
    async def logout(self):
        #Importamos en la función el estado del calendario
        from Calendario.state.calendar_state import CalendarState
        
        #Guardamos el estado y limpiamos los datos del mismo
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()

        #Limpiamos almacenamiento local y redirigimos al indice
        self._clear_storage()
        return [
            rx.remove_local_storage("user_state.user_storage"),
            rx.redirect("/")
        ]

    #Reseteo de campo de contraseña
    @rx.event
    def restart_pasw(self):
        self.password=""

    #Manejadores de páginas dentro de la interfaz de usuario
    @rx.event
    def go_security_page(self):
        self.current_page="security"
        return rx.redirect("/security")
    @rx.event
    def go_profile_page(self):
        self.current_page="profile"
        return rx.redirect("/profile")
    @rx.event
    def go_calendar_page(self):
        self.current_page="calendar"
        return rx.redirect("/calendar")