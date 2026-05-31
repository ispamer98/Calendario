# api.py
import bcrypt
from datetime import datetime
from typing import Union, List, Optional, Dict
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment


"""
Actua de como intermediario, entre la base de datos y 
el estado de la aplicación.
Habla con la hoja database.py, le entrega la información
y recibe el resultado, luego retornamos ese resultado al frontend.
"""

#Llamamos a supabase
SUPABASE_API = SupabaseAPI()

# ---------------------- Autenticación de usuario ---------------------
async def authenticate_user(username: str, password: str) -> Union[User, None]:
    user_data = SUPABASE_API.authenticate_user(username, password)
    return User(**user_data) if user_data else None

async def check_existing_user(username: str, email: str) -> Dict[str, bool]:
    return SUPABASE_API.check_existing_user(username, email)

async def check_existing_username(username: str) -> bool:
    return SUPABASE_API.check_existing_username(username)

async def register_user(username: str, password: str, email: str, birthday: str) -> bool:
    print("🟢 [API] Llamando a register_user")
    result = SUPABASE_API.register_user(username, password, email, birthday)
    print(f"🟢 [API] Resultado: {result}")
    return result

async def change_pasw(username : str, password : str) -> bool:
    return SUPABASE_API.change_pasw(username,password)

# ---------------------- Calendarios ----------------------
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    return SUPABASE_API.get_calendars(user_id) or []

async def register_user(username: str, password: str, email: str, birthday: str) -> bool:
    return SUPABASE_API.register_user(username, password, email, birthday)

async def share_calendar_with_user(calendar: Calendar, username: str) -> bool:
    return SUPABASE_API.share_with(calendar, username)

# ---------------------- Días ----------------------
async def get_days_for_calendar(calendar_id: int) -> List[Day]:
    return SUPABASE_API.get_days_for_calendar(calendar_id) or []

async def update_day_meal(day_id: int, meal: Optional[str]) -> Union[Day, None]:
    return await SUPABASE_API.update_day_meal(day_id, meal)

async def update_day_dinner(day_id: int, dinner: Optional[str]) -> Union[Day, None]:
    return await SUPABASE_API.update_day_dinner(day_id, dinner)

async def get_day_details(day_id: int) -> Union[Day, None]:
    return SUPABASE_API.get_day(day_id)

# ---------------------- Comidas ----------------------
async def get_all_meals() -> List[Meal]:
    return SUPABASE_API.get_all_meals()

async def add_new_meal(meal:str,description:str) -> Meal:
    return SUPABASE_API.add_meal(meal,description)

# Añadir al final del archivo
async def delete_meal_by_id(meal_id: int) -> bool:
    """Elimina una comida por su ID"""
    return SUPABASE_API.delete_meal_by_id(meal_id)

# ---------------------- Comentarios ----------------------
async def get_day_comments(day_id: int) -> List[Comment]:
    return SUPABASE_API.get_comments_for_day(day_id) or []

async def add_comment_to_day(day_id: int, user_id: int, content: str) -> Union[Comment, None]:
    comment = SUPABASE_API.add_comment(day_id, user_id, content)
    if comment:
        SUPABASE_API.update_day_comments_flag(day_id)
    return comment

async def delete_comment(comment_id: int) -> bool:
    return SUPABASE_API.delete_comment(comment_id)

async def update_comments_flag(day_id: int, has_comments: bool) -> bool:
    if has_comments:
        return SUPABASE_API.update_day_comments_flag(day_id)
    return SUPABASE_API.update_day_comments_false(day_id)

async def get_user_by_id(user_id: int) -> Union[User, None]:
    return SUPABASE_API.get_user_by_id(user_id)

async def get_shared_users(calendar_id: int) -> List[User]:
    return SUPABASE_API.load_shared_users(calendar_id)

# Calendario/utils/api.py
async def delete_calendar_and_days(calendar_id: int) -> bool:
    return SUPABASE_API.delete_calendar(calendar_id)

async def get_today_info(user_id: int) -> Optional[dict]:
    return SUPABASE_API.get_today_info(user_id)

# api.py - Después de los imports

# El resto de funciones para la lista de la compra
async def get_user_shopping_lists(user_id: int):
    return SUPABASE_API.get_shopping_lists(user_id)

async def add_item_to_shopping_list(list_id: int, name: str, qty: int, shop: str = ""):
    return SUPABASE_API.add_or_update_item(list_id, name, qty, shop)

async def toggle_shopping_item_status(list_id: int, item_name: str) -> bool:
    return SUPABASE_API.toggle_item_bought(list_id, item_name)

async def remove_item_from_shopping_list(list_id: int, item_name: str):
    return SUPABASE_API.delete_item(list_id, item_name)

async def share_shopping_list(list_id: int, friend_username: str):
    return SUPABASE_API.share_shopping_list(list_id, friend_username)

# Esta función es útil si quieres crear una lista manualmente (por si acaso)
async def create_fallback_shopping_list(user_id: int):
    return SUPABASE_API.create_shopping_list([user_id])

# api.py - Añade estas funciones al final

async def get_user_id_by_username(username: str) -> Optional[int]:
    """Obtiene el ID de un usuario por su nombre."""
    user_data = SUPABASE_API.get_user_by_username(username)
    return user_data["id"] if user_data else None

async def create_shopping_list_for_user(user_id: int) -> bool:
    """Crea una lista de compra vacía para el usuario."""
    result = SUPABASE_API.create_shopping_list([user_id])
    return result is not None

async def get_shopping_list_users(list_id: int):
    return SUPABASE_API.get_users_in_shopping_list(list_id)

async def add_user_to_list(list_id: int, user_id: int) -> bool:
    return SUPABASE_API.add_user_to_shopping_list(list_id, user_id)

async def remove_user_from_list(list_id: int, user_id: int) -> bool:
    return SUPABASE_API.remove_user_from_shopping_list(list_id, user_id)

async def get_user_by_username(username: str):
    return SUPABASE_API.get_user_by_username(username)

async def merge_and_share_shopping_list(user_id: int, friend_username: str) -> tuple[bool, str]:
    return SUPABASE_API.merge_and_share_shopping_list(user_id, friend_username)