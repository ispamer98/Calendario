
# register_state.py

from Calendario.utils.send_email import send_welcome_email
import reflex as rx 

class RegisterState(rx.State):
    username : str = ""
    password : str = ""
    confirm_password : str = ""
    email : str = ""
    confirm_email : str = ""
    birthday : str = ""
    show_pasw : bool = False
    errors: dict = {
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }

    @rx.event
    def register(self):
        # Resetear errores
        self.errors = {k: "" for k in self.errors}
        
        # Validaciones
        if not self.username:
            self.errors["username"] = "Usuario requerido"
        
        if not self.password:
            self.errors["password"] = "Contraseña requerida"
        elif len(self.password) < 8:
            self.errors["password"] = "Mínimo 8 caracteres"
        
        if self.password != self.confirm_password:
            self.errors["confirm_password"] = "Las contraseñas no coinciden"
        
        if not self.validate_email(self.email):
            self.errors["email"] = "Email inválido"
        elif self.email != self.confirm_email:
            self.errors["confirm_email"] = "Los emails no coinciden"
        
        if not self.birthday:
            self.errors["birthday"] = "Fecha requerida"

        # Si no hay errores
        if all(value == "" for value in self.errors.values()):
            print("Registro exitoso!")
            # Aquí tu lógica de registro

    def validate_email(self, email: str) -> bool:
        import re
        pattern = r"""
        ^                           # Inicio de la cadena
        (?!.*\.\.)                  # No permite dos puntos consecutivos
        [\w.%+-]+                   # Parte local (caracteres permitidos)
        (?<!\.)                     # No termina con un punto
        @                           # Separador
        (?:                         # Dominio:
            [a-zA-Z0-9]             #   - Inicia con alfanumérico
            (?:[a-zA-Z0-9-]{0,61}  #   - Permite hasta 61 caracteres (incluyendo guiones)
            [a-zA-Z0-9])?           #   - Termina con alfanumérico (no guión)
            \.                      #   - Separador por punto
        )+                          # Múltiples subdominios
        [a-zA-Z]{2,63}              # TLD (2-63 caracteres alfabéticos)
        $                           # Fin de la cadena
        """
        return bool(re.fullmatch(pattern, email, re.VERBOSE))


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

    @rx.event
    def reset_switch(self):
        """Reinicia el estado del switch a False."""
        self.show_pasw = False
        return None  # Devuelve None para indicar que no hay más acciones