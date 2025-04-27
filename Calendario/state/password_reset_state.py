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

    @rx.event
    async def send_reset_link(self):
        self.general_error = ""
        self.success_message = ""
        if not self.email:
            return rx.toast.error("Por favor, ingresa tu correo electrónico.", position="top-center")

        self.loading = True
        try:
            supabase = SupabaseAPI().supabase
            # Si falla, .execute() lanza APIError
            user_resp = (
                supabase
                .table("user")
                .select("*")
                .eq("email", self.email)
                .single()
                .execute()
            )
            # Aquí user_resp.data es None si no hay registro
            if not user_resp.data:
                return rx.toast.error("No existe una cuenta con este correo.", position="top-center")

            token = str(uuid.uuid4())
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            supabase.table("password_reset_tokens").insert({
                "email": self.email,
                "token": token,
                "expires_at": expires_at,
                "used": False,
            }).execute()

            reset_link = f"http://localhost:3000/reset_password?token={token}"
            send_password_reset_email(self.email, reset_link)
            return rx.toast.success("Enlace de recuperación enviado a tu correo.", position="top-center")

        except Exception as e:
            # Captura APIError u otras excepciones
            return rx.toast.error(f"Error al buscar usuario o generar token: {e}", position="top-center")
        finally:
            self.loading = False
    @rx.event
    async def update_password(self):
        supabase = SupabaseAPI().supabase

        # Validaciones previas...
        if self.new_password != self.confirm_password:
            return rx.toast.error("Las contraseñas no coinciden.", position="top-center")
        
        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
        if not re.match(pattern, self.new_password):
            return rx.toast.error(
                "La contraseña debe tener mínimo 8 caracteres, al menos 1 mayúscula, 1 número y 1 carácter especial.",
                position="top-center",
            )

        try:
            # Obtener token
            token_resp = (
                supabase
                .table("password_reset_tokens")
                .select("email, expires_at, used")
                .eq("token", self.token)
                .single()
                .execute()
            )
            if not token_resp.data:
                return rx.toast.error("Enlace inválido o expirado.", position="top-center")
            
            if token_resp.data["used"]:
                return rx.toast.error("Este enlace ya fue utilizado.", position="top-center")
            
            expires_at = datetime.fromisoformat(token_resp.data["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                return rx.toast.error("El enlace ha expirado.", position="top-center")

            # Obtener contraseña actual del usuario
            user_resp = (
                supabase
                .table("user")
                .select("pasw")
                .eq("email", token_resp.data["email"])
                .single()
                .execute()
            )
            current_hashed_pw = user_resp.data["pasw"]

            # Verificar si la nueva contraseña es igual a la actual
            if bcrypt.checkpw(self.new_password.encode(), current_hashed_pw.encode()):
                return rx.toast.error("La nueva contraseña no puede ser igual a la actual.", position="top-center")

            # Hashear y actualizar contraseña
            new_hashed_pw = bcrypt.hashpw(self.new_password.encode(), bcrypt.gensalt()).decode()
            update_resp = (
                supabase
                .table("user")
                .update({"pasw": new_hashed_pw})
                .eq("email", token_resp.data["email"])
                .execute()
            )

            # Marcar token como usado
            supabase.table("password_reset_tokens") \
                .update({"used": True}) \
                .eq("token", self.token) \
                .execute()

            return [
                rx.toast.success("Contraseña actualizada correctamente.", position="top-center"),
                rx.redirect("/login"),
            ]

        except Exception as e:
            return rx.toast.error(f"Error en actualización: {str(e)}", position="top-center")