#api.py
import reflex as rx
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment
from datetime import datetime

from typing import Union,List,Optional

SUPABASE_API = SupabaseAPI()

async def authenticate_user(username: str, password: str) -> Union[User, None]:
    """
    Autentica al usuario y devuelve un objeto User si es exitoso.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña del usuario.

    Returns:
        User | None: Instancia del usuario autenticado o None si falla.
    """
    if not username or not password:
        return None

    user_data = SUPABASE_API.authenticate_user(username, password)
    if user_data:
        
        return User(**user_data)  # Convierte los datos en una instancia de User

    return None


async def verify_user(self, username: str, email: str):
    """
    Verifica la existencia de un usuario/email en la base de datos.
    """
    result = await SUPABASE_API.verify_user(username, email)
    return result["data"] is not None



async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    calendars = SUPABASE_API.get_calendars(user_id)
    if calendars is None:
        print("No se encontraron datos de calendarios.")
        return []
    return calendars


