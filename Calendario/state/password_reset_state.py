import re
import bcrypt
import reflex as rx
import uuid
from datetime import datetime, timedelta, timezone
from Calendario.database.database import SupabaseAPI
from Calendario.state.user_state import UserState
from Calendario.utils.send_email import send_password_reset_email

class PasswordResetState(rx.State):
    email: str = "" #Email introducido por el usuario
    loading: bool = False #Manejador de carga
    token: str = "" #Token para la validación
    new_password: str = "" #Nueva contraseña
    confirm_password: str = "" #Confirmacion de contraseña
    password_error: str = "" #Error de contraseña
    confirm_password_error: str = "" #Error de validación

    def on_load_forgot_password(self):
        self.email = ""
        #Resetea el email al cargar la página
    def on_load_reset_password(self):
        #Al cargar la página de cambio de contraseña
        #Resetea ambos campos de contraseña
        self.new_password = "" 
        self.confirm_password = ""
        #Obtiene el token de la url
        self.token = self.router.page.params.get("token", "")

        #Si no encuentra token, redirige al indice
        if not self.token:
            return rx.redirect("/")

        #Cargamos la api de base de datos
        supabase = SupabaseAPI().supabase

        #Hacemos una consulta comparando el token de la página con los existentes
        try:
            token_resp = (
                supabase
                .table("password_reset_tokens")
                .select("email, expires_at, used")
                .eq("token", self.token)
                .single()
                .execute()
            )

        #Si no encuentra resultados, lanza excepción
        except Exception:
            return [
                rx.toast.error("Enlace inválido o expirado.", position="top-center"),
                rx.redirect("/")
            ]

        #Si el token está usado, lanza error
        if token_resp.data["used"]:
            return [
                rx.toast.error("Este enlace ya fue utilizado.", position="top-center"),
                rx.redirect("/")
            ]

        #Si la fecha de expiración es anterior a la actual, lanza error
        expires_at = datetime.fromisoformat(token_resp.data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return [
                rx.toast.error("El enlace ha expirado.", position="top-center"),
                rx.redirect("/")
            ]

                
    #Función que envía el link + token
    @rx.event
    async def send_reset_link(self):
        #Si no encuentra email en el input, lanza error
        if not self.email:
            return rx.toast.error("Por favor, ingresa tu correo electrónico.", position="top-center")

        #Si tenemos email, iniciamos la carga
        self.loading = True
        try:
            #Cargamos api y hacemos consulta, comparando el email con los de base de datos
            supabase = SupabaseAPI().supabase
            user_resp = (
                supabase
                .table("user")
                .select("*")
                .eq("email", self.email)
                .single()
                .execute()
            )
            #Si no encontramos coincidencias, lanza error
            if not user_resp.data:
                return rx.toast.error("No existe una cuenta con este correo.", position="top-center")

            #Si encontramos respuesta, generamos un token
            token = str(uuid.uuid4())
            #Generamos una validez de 1h desde la solicitud
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            #Cargamos el token en base de datos
            supabase.table("password_reset_tokens").insert({
                "email": self.email,
                "token": token,
                "expires_at": expires_at,
                "used": False,
            }).execute()

            #Generamos el link de reseteo para contraseña
            reset_link = f"https://calendario-red-ocean.reflex.run/reset_password?token={token}"
            #Y enviamos el enlace al correo introducido
            send_password_reset_email(self.email, reset_link)
            return rx.toast.success("Enlace de recuperación enviado a tu correo.", position="top-center")

        except Exception as e:
            return rx.toast.error(f"Error al buscar usuario o generar token: {e}", position="top-center")
        finally:
            #Detenemos la carga
            self.loading = False
    
    #Función que actualiza la contraseña
    @rx.event
    async def update_password(self):
        #Cargamos la api de supabase
        supabase = SupabaseAPI().supabase

        #Si las contraseñas no coinciden, lanza error
        if self.new_password != self.confirm_password:
            return rx.toast.error("Las contraseñas no coinciden.", position="top-center")
        
        #Creamos el filtro para la contraseña
        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'

        #Si la contraseña no coincide con el filtro, lanza error
        if not re.match(pattern, self.new_password):
            return rx.toast.error(
                "La contraseña debe tener mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial.",
                position="top-center",
            )

        #Validamos el token de nuevo
        try:
            token_resp = (
                supabase
                .table("password_reset_tokens")
                .select("email, expires_at, used")
                .eq("token", self.token)
                .single()
                .execute()
            )
        except Exception:
            return rx.toast.error("Enlace inválido o expirado.", position="top-center")

        if not token_resp.data:
            return rx.toast.error("Enlace inválido o expirado.", position="top-center")

        if token_resp.data["used"]:
            return rx.toast.error("Este enlace ya fue utilizado.", position="top-center")

        expires_at = datetime.fromisoformat(token_resp.data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return rx.toast.error("El enlace ha expirado.", position="top-center")
        
        try:
            #Obtenemos la contraseña actual del usuario comparando con el email asociado al token
            user_resp = (
                supabase
                .table("user")
                .select("pasw")
                .eq("email", token_resp.data["email"])
                .single()
                .execute()
            )

            #Guardamos la contraseña
            current_hashed_pw = user_resp.data["pasw"]

            #Si ambas contraseñas son iguales, lanzamos error
            if bcrypt.checkpw(self.new_password.encode(), current_hashed_pw.encode()):
                return rx.toast.error("La nueva contraseña no puede ser igual a la actual.", position="top-center")

            #Aplicamos hash a la nueva contraseña y actualizamos en base de datos
            new_hashed_pw = bcrypt.hashpw(self.new_password.encode(), bcrypt.gensalt()).decode()
            update_resp = (
                supabase
                .table("user")
                .update({"pasw": new_hashed_pw})
                .eq("email", token_resp.data["email"])
                .execute()
            )

            #Marcamos el token como usado
            supabase.table("password_reset_tokens") \
                .update({"used": True}) \
                .eq("token", self.token) \
                .execute()

            #Retornamos mensaje de éxito y redirigimos al indice
            return [
                rx.toast.success("Contraseña actualizada correctamente.", position="top-center"),
                rx.redirect("/login"),
            ]
        #Si existe algún problema lanza error
        except Exception as e:
            return rx.toast.error(f"Error en actualización: {str(e)}", position="top-center")