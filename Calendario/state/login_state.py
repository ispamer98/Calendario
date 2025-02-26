#login_card_state

import reflex as rx
from Calendario.state.user_state import UserState
class Login_state(rx.State):
    """
    Manejador de estado para la tarjeta de inicio de sesión en Reflex.
    """
    is_open: bool = False
    mode: str = "login"
    show_pasw: bool = False


    @rx.event
    def login(self, mode="login"):
        self.is_open = True
        self.mode = mode
        UserState.set_password("")
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña


    @rx.event
    def register(self, mode="register"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña


    @rx.event
    def close(self):
        self.is_open = False

    @rx.event
    def swith_on(self, value: bool):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value


