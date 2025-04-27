import re
import bcrypt
import reflex as rx
import uuid
from datetime import datetime, timedelta, timezone
from Calendario.database.database import SupabaseAPI
from Calendario.utils.send_email import send_password_reset_email

class PasswordResetState(rx.State):
    email: str = ""
    loading: bool = False
    token: str = ""
    new_password: str = ""
    confirm_password: str = ""
    password_error: str = ""
    confirm_password_error: str = ""
    general_error: str = ""
    success_message: str = ""

    def on_load(self):
        # Obtener token de la URL
        self.token = self.router.page.params.get("token", "")

    async def send_reset_link(self):
        self.general_error = ""
        self.success_message = ""
        if not self.email:
            self.general_error = "Por favor, ingresa tu correo electrónico."
            return
        self.loading = True
        try:
            # Verificar si el email existe
            user_resp = SupabaseAPI().supabase \
                .from_("user") \
                .select("*") \
                .eq("email", self.email) \
                .execute()
            if not user_resp.data:
                self.general_error = "No existe una cuenta con este correo."
                return

            # Generar token y guardarlo
            token = str(uuid.uuid4())
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            SupabaseAPI().supabase \
                .from_("password_reset_tokens") \
                .insert({
                    "email": self.email,
                    "token": token,
                    "expires_at": expires_at,
                    "used": False
                }) \
                .execute()

            # Enviar correo
            reset_link = f"http://localhost:3000/reset_password?token={token}"
            send_password_reset_email(self.email, reset_link)
            self.success_message = "Enlace de recuperación enviado a tu correo."
        except Exception as e:
            self.general_error = f"Error: {str(e)}"
        finally:
            self.loading = False

    async def update_password(self):
        # Limpiar mensajes de error anteriores
        self.password_error = ""
        self.confirm_password_error = ""
        self.general_error = ""
        self.success_message = ""

        # Validar que las contraseñas coincidan
        if self.new_password != self.confirm_password:
            self.confirm_password_error = "Las contraseñas no coinciden."
            return

        # Validar la fortaleza de la contraseña
        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
        if not re.match(pattern, self.new_password):
            self.password_error = "La contraseña debe tener mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial."
            return

        try:
            # Obtener token de la base de datos
            token_resp = SupabaseAPI().supabase \
                .from_("password_reset_tokens") \
                .select("*") \
                .eq("token", self.token) \
                .execute()

            token_data = token_resp.data
            if not token_data:
                self.general_error = "Enlace inválido."
                return

            token_info = token_data[0]

            # Comprobar expiración del token
            expires = datetime.fromisoformat(token_info["expires_at"])
            now_utc = datetime.now(timezone.utc)
            if token_info["used"] or expires < now_utc:
                self.general_error = "El enlace ha expirado."
                return

            # Hashear y actualizar contraseña
            hashed = bcrypt.hashpw(self.new_password.encode(), bcrypt.gensalt()).decode()
            update_resp = SupabaseAPI().supabase \
                .from_("user") \
                .update({"pasw": hashed}) \
                .eq("email", token_info["email"]) \
                .execute()

            # Verificar si la actualización fue exitosa
            if not update_resp.data:
                self.general_error = "No se pudo actualizar la contraseña."
                return

            # Marcar token como usado
            SupabaseAPI().supabase \
                .from_("password_reset_tokens") \
                .update({"used": True}) \
                .eq("token", self.token) \
                .execute()

            # Notificar éxito y redirigir al login
            self.success_message = "Contraseña actualizada correctamente."
            return rx.redirect("/login")

        except Exception as e:
            self.general_error = f"Error: {str(e)}"
