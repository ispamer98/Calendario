#user_state.py

import reflex as rx
import time
from typing import Optional,Any
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user,get_today_info
from datetime import datetime
import json

from typing import TypedDict

class Comment(TypedDict):
    username: str
    content: str

class CalendarInfo(TypedDict):
    calendar_name: str
    meal: str
    dinner: str
    comments: list[Comment]

class UserState(rx.State):
    """
    Manejador de estado para los datos del usuario en Reflex.
    """

    user_storage: str = rx.LocalStorage("")  # 1. Variable de almacenamiento


    username: str = ""  # Guarda el nombre de usuario ingresado
    password: str = ""  # Guarda la contraseña ingresada
    current_user: Optional[User] = None  # Mantiene al usuario autenticado
    today_data: list[CalendarInfo] = []
    @rx.event
    async def today_info(self):
        self.today_data = await get_today_info(self.current_user.id) if self.current_user else []
    
        print("TODAY DATAAAAAAAAAAAAAAAAA",self.today_data)

    @rx.event
    def press_enter(self, key: str):
        if key == "Enter":
            # Return the event instead of calling it directly
            return UserState.login
    
    def return_username(self) -> str:
        return self.username
    
    @rx.event
    def set_username(self, username: str):
        """
        Actualiza el nombre de usuario en el estado.
        """
        self.username = username
        print(f"Username actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        """
        Actualiza la contraseña en el estado.
        """
        self.password = password
        print(f"Password actualizado: {self.password}")



    @rx.event
    def check_autenticated(self):
        if self.current_user == None:
            return rx.redirect("/")

    @rx.var
    def is_authenticated(self) -> bool:
        """Determina si el usuario está autenticado"""
        return self.current_user is not None

    def _load_user_from_storage(self):
        """Carga los datos del usuario desde LocalStorage"""
        if self.user_storage:
            try:
                user_data = json.loads(self.user_storage)
                # Convertir fechas de string a objeto datetime
                user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                self.current_user = User(**user_data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error cargando usuario desde storage: {e}")
                self._clear_storage()

    def _save_user_to_storage(self):
        """Guarda los datos del usuario en LocalStorage"""
        if self.current_user:
            user_dict = self.current_user.__dict__.copy()
            # Convertir datetime a string para serialización
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            self.user_storage = json.dumps(user_dict)
        else:
            self.user_storage = ""

    def _clear_storage(self):
        """Limpia todos los datos de almacenamiento"""
        self.user_storage = ""
        self.current_user = None
        self.username = ""
        self.password = ""

    @rx.event
    async def on_load(self):
        """Evento al cargar la aplicación"""
        self._load_user_from_storage()




    @rx.event
    async def login(self):

        if not self.username or not self.password:
            self.restart_pasw()

        try:
            user_data = await authenticate_user(self.username.lower(), self.password)
            

            
            if user_data:
                self.current_user = user_data
                self._save_user_to_storage()
                self.username = ""
                self.password = ""
                # Llamamos al evento para cargar los calendarios en el estado de CalendarState
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                # Limpiamos los campos de usuario y contraseña
                self._clear_storage()
                self.username = ""
                self.password = ""
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        except Exception as e:
            print(f"Error al intentar iniciar sesión: {e}")
            self._clear_storage
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )


    @rx.event
    async def logout(self):
        """Maneja el cierre de sesión"""
        from Calendario.state.calendar_state import CalendarState
        
        # Limpiar estado relacionado
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()
        
        # 3. Eliminar datos de almacenamiento
        self._clear_storage()
        return [
            rx.remove_local_storage("user_state.user_storage"),
            rx.redirect("/")
        ]

    @rx.event
    def restart_pasw(self):
        self.password=""