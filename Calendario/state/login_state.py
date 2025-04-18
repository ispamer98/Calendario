#login_card_state

import reflex as rx
from Calendario.state.user_state import UserState
from Calendario.state.register_state import RegisterState
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
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return UserState.restart_pasw()

    @rx.event
    def register(self, mode="register"):
        self.is_open = True
        self.mode = mode
        self.show_pasw = False  # Reinicia la visibilidad de la contraseña
        return [RegisterState.reset_switch(),
                RegisterState.reset_inputs(),
                ]  # Reinicia el switch en el formulario de registro


    @rx.event
    def close(self):
        self.is_open = False

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value