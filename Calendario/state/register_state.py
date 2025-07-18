# register_state.py


from typing import Optional
from Calendario.utils.api import check_existing_user, register_user, check_existing_username
from Calendario.utils.send_email import send_welcome_email
from datetime import datetime
import reflex as rx 

#Clase para manejar el estado del registro
class RegisterState(rx.State):
    username : str = "" #Guarda el nombre de usuario
    password : str = "" #Guarda la contraseña  
    confirm_password : str = "" #Guarda la confirmación de contraseña
    email : str = "" #Guarda el email
    confirm_email : str = "" #Guarda la confirmación del email
    birthday : str = "" #Guarda la fecha de nacimiento
    show_pasw : bool = False #Switch para mostrar la contraseña
    errors: dict = { #Diccionario de errores para mostrar
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }
    username_valid : Optional[bool] = None #Manejador de comprobación de username

    #Reseteamos todos los mensajes de error
    @rx.event
    def reset_errors(self):
        self.errors ={
        "username": "",
        "password": "",
        "confirm_password": "",
        "email": "",
        "confirm_email": "",
        "birthday": ""
    }
        
    #Lógica para registrar al usuario
    @rx.event
    async def register(self):
        #Reseteamos todos los errores al comenzar
        self.errors = {k: "" for k in self.errors}
        has_errors = False

        #Verificar si el usuario/email ya existen
        existing = await check_existing_user(self.username, self.email)
        if existing["username"]:
            self.errors["username"] = "El nombre de usuario ya está registrado"
            has_errors = True
        if existing["email"]:
            self.errors["email"] = "El correo electrónico ya está registrado"
            has_errors = True


        #Validación de username
        if not self.username:
            self.errors["username"] = "Usuario requerido"
            has_errors = True
        else:
            #Verificamos que la longitud esté entre 6 y 16 caracteres
            if len(self.username) < 4 or len(self.username) > 16:
                self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                has_errors = True

            #Verificamos que contenga al menos un número
            elif not any(char.isdigit() for char in self.username):
                self.errors["username"] = "El usuario debe contener al menos un número"
                has_errors = True

            #Verificamos que no contenga caracteres especiales
            elif not self.username.isalnum():
                self.errors["username"] = "El usuario no puede contener caracteres especiales"
                has_errors = True

        #Validación de email
        if not self.validate_email(self.email.lower()):
            self.errors["email"] = "Email inválido"
            has_errors = True
        elif self.email.lower() != self.confirm_email.lower():
            self.errors["confirm_email"] = "Los emails no coinciden"
            has_errors = True

        import re
        #Validación de contraseña
        if not self.password:
            self.errors["password"] = "Contraseña requerida"
            has_errors = True
        else:
            #Patrón que requiere:
            #Al menos 8 caracteres
            #Al menos una letra mayúscula
            #Al menos un dígito
            #Al menos un carácter especial
            pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
            if not re.match(pattern, self.password):
                self.errors["password"] = ("La contraseña debe tener mínimo 8 caracteres, "
                                            "al menos 1 mayúscula, 1 número y 1 carácter especial")
                has_errors = True
            elif self.password != self.confirm_password:
                self.errors["confirm_password"] = "Las contraseñas no coinciden"
                has_errors = True

        #Validación de fecha
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


        #Si no hay errores, registramos al usuario
        if not has_errors:
            try:
                new_user = await register_user(
                    self.username,
                    self.password,
                    self.email,
                    self.birthday,
                )
                
                if new_user == True:
                #Enviamos correo de bienvenida
                    send_welcome_email(self.email, self.username)
            
                    return [rx.toast.success(
                        "¡Registro exitoso! Revisa tu correo electrónico",
                        position="top-center"
                    ),rx.redirect("/login")]
                else:
                    self.password=""
                    self.confirm_password=""
                    return rx.toast.error(
                        "No se ha podido registrar el usuario",
                        position="top-center",
                    )
            except Exception as e:
                return rx.toast.error(
                    f"Error en el registro: {str(e)}",
                    position="top-center"
                )

    #Validamos el correo
    def validate_email(self, email: str) -> bool:
        import re
        pattern = r"""
        ^                           #Inicio de la cadena
        (?!.*\.\.)                  #No permite dos puntos consecutivos
        [\w.%+-]+                   #Parte local (caracteres permitidos)
        (?<!\.)                     #No termina con un punto
        @                           #Separador
        (?:                         #Dominio:
            [a-zA-Z0-9]             #Inicia con alfanumérico
            (?:[a-zA-Z0-9-]{0,61}   #Permite hasta 61 caracteres (incluyendo guiones)
            [a-zA-Z0-9])?           #Termina con alfanumérico (no guión)
            \.                      #Separador por punto
        )+                          # Múltiples subdominios
        [a-zA-Z]{2,63}              #TLD (2-63 caracteres alfabéticos)
        $                           #Fin de la cadena
        """
        return bool(re.fullmatch(pattern, email, re.VERBOSE))

    #Comprobamos si el usuario es válido para el registro
    @rx.event
    async def check_aviable_username(self):
        if not self.username:
            self.username_valid = None
            return
        
        try:
            existing = await check_existing_username(self.username)
            if existing:
                self.username_valid = False
                self.errors["username"] = "El nombre de usuario ya está registrado"
            else:

                #Verificamos que la longitud esté entre 6 y 16 caracteres
                if len(self.username) < 4 or len(self.username) > 16:
                    self.errors["username"] = "El usuario debe tener entre 4 y 16 caracteres"
                    self.username_valid = False


                #Verificamos que contenga al menos un número
                elif not any(char.isdigit() for char in self.username):
                    self.errors["username"] = "El usuario debe contener al menos un número"
                    self.username_valid = False

                #Verificamos que no contenga caracteres especiales (solo letras y números)
                elif not self.username.isalnum():
                    self.errors["username"] = "El usuario no puede contener caracteres especiales"
                    self.username_valid = False
                
                else:
                    self.username_valid = True
                    self.errors["username"] = ""

        except Exception as e:
            print(f"Error al verificar el nombre de usuario: {str(e)}")
            self.username_valid = None


    @rx.event
    def set_username(self, username: str):
        self.username = username

    @rx.event
    def set_password(self, password: str):
        self.password = password

    @rx.event
    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password

    @rx.event
    def set_email(self, email: str):
        self.email = email

    @rx.event
    def set_confirm_email(self, confirm_email: str):
        self.confirm_email = confirm_email

    @rx.event
    def swith_on(self, value: bool = True):
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        self.show_pasw = value

    @rx.event
    def reset_switch(self):
        self.show_pasw = False
    
    @rx.event
    def reset_inputs(self):
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.email = ""
        self.confirm_email = ""
        self.birthday = ""
        self.errors = {k: "" for k in self.errors}
        self.username_valid = None

    @rx.event
    def load_page(self):
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.email = ""
        self.confirm_email = ""
        self.birthday = ""
        self.reset_errors()
        self.username_valid = None
        

