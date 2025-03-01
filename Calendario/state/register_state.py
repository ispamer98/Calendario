
# register_state.py

import reflex as rx 

class RegisterState(rx.State):
    username : str = ""
    password : str = ""
    confirm_password : str = ""
    email : str = ""
    confirm_email : str = ""
    show_pasw : bool = False
    

    @rx.event
    def set_username(self, username: str):
        self.username = username
        print(f"Usuario para registro actualizado: {self.username}")

    @rx.event
    def set_password(self, password: str):
        self.password = password
        print(f"Contraseña para registro actualizada: {self.password}")

    @rx.event
    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password
        print(f"Confirmar contraseña para registro actualizada: {self.confirm_password}")
    @rx.event
    def set_email(self, email: str):
        self.email = email
        print(f"Correo electrónico para registro actualizado: {self.email}")
    @rx.event
    def set_confirm_email(self, confirm_email: str):
        self.confirm_email = confirm_email
        print(f"Confirmar correo electrónico para registro actualizado: {self.confirm_email}")

    @rx.event
    def swith_on(self, value: bool = True):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        """Controla la visibilidad de la contraseña."""
        self.show_pasw = value

    rx.event()