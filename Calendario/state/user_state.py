#user_state.py

import reflex as rx
import time
from Calendario.model.model import User
from Calendario.utils.api import authenticate_user

class UserState(rx.State):
    """
    Manejador de estado para los datos del usuario en Reflex.
    """

    username: str = ""  # Guarda el nombre de usuario ingresado
    password: str = ""  # Guarda la contraseña ingresada
    current_user: User = None  # Mantiene al usuario autenticado


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
    async def login(self):

        if not self.username or not self.password:
            self.clear_paswd()

        try:
            user_data = await authenticate_user(self.username.lower(), self.password)

            
            if user_data:
                self.current_user = user_data
                self.username = ""
                self.password = ""
                # Llamamos al evento para cargar los calendarios en el estado de CalendarState
                return [rx.toast.success(
                    position="top-center",
                    title=f"!Bienvenido! \n{self.current_user.username.capitalize()}"
                ),rx.redirect("/calendar")]
            else:
                # Limpiamos los campos de usuario y contraseña
                self.username = ""
                self.password = ""
                return rx.toast.error(
                    position="top-center",
                    title="Usuario o contraseña incorrectos."
                )
        except Exception as e:
            print(f"Error al intentar iniciar sesión: {e}")
            return rx.toast.error(
                position="top-center",
                title="Error al intentar autenticar al usuario. Intente nuevamente más tarde."
            )


    @rx.event
    def clear_paswd(self):
        self.password = ""
        print("Contraseña borrada:", self.password)  # Para depuración

    



    @rx.event

    async def logout(self):
        from Calendario.state.calendar_state import CalendarState
        """
        Cierra la sesión del usuario actual.
        """
        calendar_state = await self.get_state(CalendarState)
        calendar_state.clean()
        self.current_user = None
        self.username = ""
        self.password = ""
        CalendarState.toast_info = "Cerrando la sesión"
        return [
            rx.redirect("/")
        ]
    

    @rx.event
    def restart_pasw(self):
        self.password=""