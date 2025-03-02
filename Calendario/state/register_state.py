
# register_state.py


from Calendario.utils.api import check_existing_user, register_user
from Calendario.utils.send_email import send_welcome_email
from datetime import datetime
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
    def reset_errors(self):
        self.errors = {k: "" for k in self.errors}
    @rx.event
    async def register(self):
        # Resetear errores
        self.errors = {k: "" for k in self.errors}
        has_errors = False

        # Verificar si el usuario/email ya existen
        existing = await check_existing_user(self.username, self.email)
        if existing["username"]:
            self.errors["username"] = "El nombre de usuario ya está registrado"
            has_errors = True
        if existing["email"]:
            self.errors["email"] = "El correo electrónico ya está registrado"
            has_errors = True


        # Validación de username
        if not self.username:
            self.errors["username"] = "Usuario requerido"
            has_errors = True
        else:
            # Verificar que la longitud esté entre 6 y 16 caracteres
            if len(self.username) < 4 or len(self.username) > 16:
                self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                has_errors = True

            # Verificar que contenga al menos un número
            elif not any(char.isdigit() for char in self.username):
                self.errors["username"] = "El usuario debe contener al menos un número"
                has_errors = True

            # Verificar que no contenga caracteres especiales (solo letras y números)
            elif not self.username.isalnum():
                self.errors["username"] = "El usuario no puede contener caracteres especiales"
                has_errors = True

        # Validación de email
        if not self.validate_email(self.email.lower()):
            self.errors["email"] = "Email inválido"
            has_errors = True
        elif self.email.lower() != self.confirm_email.lower():
            self.errors["confirm_email"] = "Los emails no coinciden"
            has_errors = True

        import re
        # Validación de contraseña
        if not self.password:
            self.errors["password"] = "Contraseña requerida"
            has_errors = True
        else:
            # Patrón que requiere:
            # - Al menos 8 caracteres
            # - Al menos una letra mayúscula
            # - Al menos un dígito
            # - Al menos un carácter especial (no alfanumérico)
            pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
            if not re.match(pattern, self.password):
                self.errors["password"] = ("La contraseña debe tener mínimo 8 caracteres, "
                                            "al menos 1 mayúscula, 1 número y 1 carácter especial")
                has_errors = True
            elif self.password != self.confirm_password:
                self.errors["confirm_password"] = "Las contraseñas no coinciden"
                has_errors = True

        # Validación de fecha
        if not self.birthday:
            self.errors["birthday"] = "Fecha requerida"
            has_errors = True
        else:
            try:
                birth_date = datetime.strptime(self.birthday, '%Y-%m-%d')
                if birth_date > datetime.now():
                    self.errors["birthday"] = "Fecha inválida"
                    has_errors = True
            except ValueError:
                self.errors["birthday"] = "Formato inválido\n (DD-MM-AAAA)"
                has_errors = True

        if has_errors:
            return rx.toast.error("No ha sido posible el registro",
                                  position="top-center")


        # Si no hay errores, proceder con registro
        if not has_errors:
            try:
                # Aquí iría la lógica de registro en la base de datos
                new_user = await register_user(
                    self.username,
                    self.password,
                    self.email,
                    self.birthday,
                )
                
                if new_user:
                # Enviar correo de bienvenida
                    send_welcome_email(self.email, self.username)
                
                    from Calendario.state.login_state import LoginState

                    LoginState.login()
                    return rx.toast.success(
                        "¡Registro exitoso! Revisa tu correo electrónico",
                        position="top-center"
                    )
                else:
                    self.password="",
                    self.confirm_password="",
                    return rx.toast.error(
                        "No se ha podido registrar el usuario",
                        position="top-center",
                    )
            except Exception as e:
                return rx.toast.error(
                    f"Error en el registro: {str(e)}",
                    position="top-center"
                )

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
    
