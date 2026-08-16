# api.py
import bcrypt
import logging
from datetime import datetime
from typing import Union, List, Optional, Dict
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment, DayItem

logger = logging.getLogger(__name__)


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
    logger.debug("🟢 [API] Llamando a register_user")
    result = SUPABASE_API.register_user(username, password, email, birthday)
    logger.debug(f"🟢 [API] Resultado: {result}")
    return result

async def change_pasw(username : str, password : str) -> bool:
    return SUPABASE_API.change_pasw(username,password)

# ---------------------- Calendarios ----------------------
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    return SUPABASE_API.get_calendars(user_id) or []

async def get_calendars_summary(calendar_ids: List[int]) -> dict:
    return SUPABASE_API.get_calendars_summary(calendar_ids)

async def share_calendar_with_user(calendar: Calendar, username: str, requesting_user_id: int) -> tuple[bool, str]:
    return SUPABASE_API.share_with(calendar, username, requesting_user_id)

# ---------------------- Días ----------------------
async def get_days_for_calendar(calendar_id: int) -> List[Day]:
    return SUPABASE_API.get_days_for_calendar(calendar_id) or []

async def get_days_in_range(
    user_id: int, start: datetime, end: datetime, preferred_calendar_id: Optional[int] = None
) -> List[Day]:
    return SUPABASE_API.get_days_in_range(user_id, start, end, preferred_calendar_id)

async def update_day_meal(day_id: int, meal: Optional[str], user_id: int) -> Union[Day, None]:
    return await SUPABASE_API.update_day_meal(day_id, meal, user_id)

async def update_day_dinner(day_id: int, dinner: Optional[str], user_id: int) -> Union[Day, None]:
    return await SUPABASE_API.update_day_dinner(day_id, dinner, user_id)

async def get_day_details(day_id: int, user_id: int) -> Union[Day, None]:
    return SUPABASE_API.get_day(day_id, user_id)

# ---------------------- Comidas ----------------------
async def get_all_meals(user_id: int) -> List[Meal]:
    """Comidas del recetario del usuario (el suyo o el que comparta)."""
    return SUPABASE_API.get_all_meals(user_id)

async def get_recipe_book(user_id: int) -> Optional[dict]:
    return SUPABASE_API.get_or_create_recipe_book(user_id)

async def get_recipe_book_users(book_id: int) -> List[User]:
    return SUPABASE_API.get_users_in_recipe_book(book_id)

async def share_recipe_book(user_id: int, friend_username: str) -> tuple[bool, str]:
    return SUPABASE_API.merge_and_share_recipe_book(user_id, friend_username)

async def remove_user_from_recipe_book(book_id: int, user_id: int, requesting_user_id: int) -> bool:
    return SUPABASE_API.remove_user_from_recipe_book(book_id, user_id, requesting_user_id)

async def add_new_meal(
    meal: str, description: str, ingredients: Optional[list] = None,
    category: str = "otros", prep_minutes: int = 20, user_id: Optional[int] = None,
) -> Optional[Meal]:
    return SUPABASE_API.add_meal(meal, description, ingredients, category, prep_minutes, user_id)

async def update_meal(
    meal_id: int, name: str, description: str, ingredients: Optional[list] = None,
    category: str = "otros", prep_minutes: int = 20, user_id: Optional[int] = None,
) -> Optional[Meal]:
    return SUPABASE_API.update_meal(
        meal_id, name, description, ingredients, category, prep_minutes, user_id
    )

# Añadir al final del archivo
async def delete_meal_by_id(meal_id: int, user_id: Optional[int] = None) -> bool:
    """Elimina una comida del recetario del usuario"""
    return SUPABASE_API.delete_meal_by_id(meal_id, user_id)

# ---------------------- Unidades de medida ----------------------
async def get_units() -> List[str]:
    return SUPABASE_API.get_units()

async def add_unit(name: str) -> bool:
    return SUPABASE_API.add_unit(name)

async def update_unit(old_name: str, new_name: str) -> bool:
    return SUPABASE_API.update_unit(old_name, new_name)

async def delete_unit(name: str) -> bool:
    return SUPABASE_API.delete_unit(name)

async def get_unit_usage() -> Dict[str, int]:
    """{unidad en minúsculas: veces que está escrita} en todo lo que guarda la app."""
    return SUPABASE_API.get_unit_usage()

async def convert_unit(old_name: str, new_name: str) -> int:
    """Pasa a `new_name` todo lo que usaba `old_name`. Devuelve cuántas cosas cambió."""
    return SUPABASE_API.convert_unit(old_name, new_name)

# ---------------------- Roles de calendario ----------------------
async def get_calendar_role(calendar_id: int, user_id: int) -> Optional[str]:
    return SUPABASE_API.get_calendar_role(calendar_id, user_id)

async def get_calendar_members(calendar_id: int) -> List[dict]:
    return SUPABASE_API.get_calendar_members(calendar_id)

async def set_member_role(calendar_id: int, target_user_id: int, role: str, requesting_user_id: int) -> bool:
    return SUPABASE_API.set_member_role(calendar_id, target_user_id, role, requesting_user_id)

async def remove_calendar_member(calendar_id: int, target_user_id: int, requesting_user_id: int) -> bool:
    return SUPABASE_API.remove_calendar_member(calendar_id, target_user_id, requesting_user_id)

# ---------------------- Amigos ----------------------
async def get_friendships(user_id: int) -> dict:
    return SUPABASE_API.get_friendships(user_id)

async def send_friend_request(user_id: int, username: str) -> tuple[bool, str]:
    return SUPABASE_API.send_friend_request(user_id, username)

async def respond_friend_request(friendship_id: int, user_id: int, accept: bool) -> bool:
    return SUPABASE_API.respond_friend_request(friendship_id, user_id, accept)

async def remove_friendship(friendship_id: int, user_id: int) -> bool:
    return SUPABASE_API.remove_friendship(friendship_id, user_id)

async def get_notify_preference(user_id: int) -> bool:
    return SUPABASE_API.get_notify_preference(user_id)

async def set_notify_preference(user_id: int, value: bool) -> bool:
    return SUPABASE_API.set_notify_preference(user_id, value)

# ---------------------- Chat entre amigos ----------------------
async def send_message(sender_id: int, recipient_id: int, body: str) -> tuple[bool, str, bool]:
    return SUPABASE_API.send_message(sender_id, recipient_id, body)

async def get_conversation(user_id: int, other_id: int) -> List[dict]:
    return SUPABASE_API.get_conversation(user_id, other_id)

async def mark_messages_read(user_id: int, other_id: int) -> bool:
    return SUPABASE_API.mark_messages_read(user_id, other_id)

async def get_chat_overview(user_id: int) -> dict:
    return SUPABASE_API.get_chat_overview(user_id)

async def get_unread_count(user_id: int) -> int:
    return SUPABASE_API.get_unread_count(user_id)

# ---------------------- Categorías de plato ----------------------
async def get_meal_categories() -> List[dict]:
    return SUPABASE_API.get_meal_categories()

async def save_meal_category(key: str, label: str, color: str, icon: str) -> bool:
    return SUPABASE_API.save_meal_category(key, label, color, icon)

async def delete_meal_category(key: str) -> bool:
    return SUPABASE_API.delete_meal_category(key)

# ---------------------- Tipos de agenda ----------------------
async def get_task_types() -> List[dict]:
    return SUPABASE_API.get_task_types()

async def add_task_type(label: str, color: str, icon: str, completable: bool) -> bool:
    return SUPABASE_API.add_task_type(label, color, icon, completable)

async def update_task_type(key: str, label: str, color: str, icon: str, completable: bool) -> bool:
    return SUPABASE_API.update_task_type(key, label, color, icon, completable)

async def delete_task_type(key: str) -> bool:
    return SUPABASE_API.delete_task_type(key)

# ---------------------- Supermercados ----------------------
#Catálogo de productos (los ingredientes preestablecidos)
async def get_products() -> List[dict]:
    return SUPABASE_API.get_products()

async def add_product(
    name: str, qty: float = 1, unit: str = "ud", cat: str = "otros", shop: str = "",
    staple: bool = False, note: str = "", pack_qty: float = 0, pack_unit: str = "",
) -> Optional[dict]:
    return SUPABASE_API.add_product(name, qty, unit, cat, shop, staple, note, pack_qty, pack_unit)

async def update_product(
    product_id: int, name: str, qty: float, unit: str, cat: str, shop: str,
    staple: bool, note: str, pack_qty: float = 0, pack_unit: str = "",
) -> Optional[dict]:
    return SUPABASE_API.update_product(
        product_id, name, qty, unit, cat, shop, staple, note,
        pack_qty=pack_qty, pack_unit=pack_unit,
    )

async def delete_product(product_id: int) -> bool:
    return SUPABASE_API.delete_product(product_id)


async def get_supermarkets() -> List[dict]:
    return SUPABASE_API.get_supermarkets()

async def add_supermarket(name: str, color: str) -> bool:
    return SUPABASE_API.add_supermarket(name, color)

async def update_supermarket(old_name: str, new_name: str, color: str) -> bool:
    return SUPABASE_API.update_supermarket(old_name, new_name, color)

async def update_supermarket_color(name: str, color: str) -> bool:
    return SUPABASE_API.update_supermarket_color(name, color)

async def delete_supermarket(name: str) -> bool:
    return SUPABASE_API.delete_supermarket(name)

# ---------------------- Comentarios ----------------------
async def get_day_comments(day_id: int, user_id: int) -> List[Comment]:
    return SUPABASE_API.get_comments_for_day(day_id, user_id) or []

async def add_comment_to_day(day_id: int, user_id: int, content: str) -> Union[Comment, None]:
    comment = SUPABASE_API.add_comment(day_id, user_id, content)
    if comment:
        SUPABASE_API.update_day_comments_flag(day_id)
    return comment

async def delete_comment(comment_id: int, user_id: int) -> bool:
    return SUPABASE_API.delete_comment(comment_id, user_id)

async def update_comments_flag(day_id: int, has_comments: bool) -> bool:
    if has_comments:
        return SUPABASE_API.update_day_comments_flag(day_id)
    return SUPABASE_API.update_day_comments_false(day_id)

async def get_user_by_id(user_id: int) -> Union[User, None]:
    return SUPABASE_API.get_user_by_id(user_id)

async def get_shared_users(calendar_id: int) -> List[User]:
    return SUPABASE_API.load_shared_users(calendar_id)

# Calendario/utils/api.py
async def delete_calendar_and_days(calendar_id: int, user_id: int) -> bool:
    return SUPABASE_API.delete_calendar(calendar_id, user_id)

async def get_today_info(user_id: int) -> Optional[dict]:
    return SUPABASE_API.get_today_info(user_id)

# api.py - Después de los imports

# El resto de funciones para la lista de la compra
async def get_user_shopping_lists(user_id: int):
    return SUPABASE_API.get_shopping_lists(user_id)

async def add_item_to_shopping_list(
    list_id: int, name: str, qty: float, shop: str, user_id: int,
    unit: str = "ud", cat: str = "otros", staple: bool = False, note: str = "",
):
    return SUPABASE_API.add_or_update_item(
        list_id, name, qty, shop, user_id, unit, cat, staple, note
    )

async def update_shopping_item(
    list_id: int, old_name: str, new_name: str, qty: float, unit: str, shop: str,
    user_id: int, cat: Optional[str] = None, staple: Optional[bool] = None,
    note: Optional[str] = None, bought: Optional[bool] = None,
    auto: Optional[bool] = None, source: Optional[str] = None,
) -> bool:
    return SUPABASE_API.update_item_details(
        list_id, old_name, new_name, qty, unit, shop, user_id, cat,
        staple, note, bought, auto, source,
    )

async def clear_bought_shopping_items(list_id: int, user_id: int) -> int:
    return SUPABASE_API.clear_bought_items(list_id, user_id)

async def clear_all_shopping_items(list_id: int, user_id: int) -> int:
    return SUPABASE_API.clear_all_items(list_id, user_id)

async def set_all_shopping_items_bought(list_id: int, user_id: int, bought: bool) -> int:
    return SUPABASE_API.set_all_bought(list_id, user_id, bought)

async def add_recipe_to_shopping_list(
    list_id: int, generated: dict, user_id: int
) -> tuple[bool, int, int, List[str]]:
    """Suma a la lista los ingredientes de una comida suelta (no del menú semanal).

    Devuelve (éxito, añadidos, sumados a lo que ya había, productos que no se
    pudieron sumar por llevar unidades incompatibles).
    """
    return SUPABASE_API.add_recipe_items(list_id, generated, user_id)

async def apply_generated_shopping_items(
    list_id: int, generated: dict, mode: str, user_id: int, week: str = ""
) -> tuple[bool, int]:
    return SUPABASE_API.apply_generated_items(list_id, generated, mode, user_id, week)

async def toggle_shopping_item_status(list_id: int, item_name: str, user_id: int) -> bool:
    return SUPABASE_API.toggle_item_bought(list_id, item_name, user_id)

async def remove_item_from_shopping_list(list_id: int, item_name: str, user_id: int):
    return SUPABASE_API.delete_item(list_id, item_name, user_id)

async def share_shopping_list(list_id: int, friend_username: str, requesting_user_id: int):
    return SUPABASE_API.share_shopping_list(list_id, friend_username, requesting_user_id)

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

async def remove_user_from_list(list_id: int, user_id: int, requesting_user_id: int) -> bool:
    return SUPABASE_API.remove_user_from_shopping_list(list_id, user_id, requesting_user_id)

async def get_user_by_username(username: str):
    return SUPABASE_API.get_user_by_username(username)

async def merge_and_share_shopping_list(user_id: int, friend_username: str) -> tuple[bool, str]:
    return SUPABASE_API.merge_and_share_shopping_list(user_id, friend_username)

# ---------------------- Despensa (el stock de casa) ----------------------
async def get_pantry(user_id: int) -> Optional[dict]:
    """La despensa del usuario, creándola si aún no tenía."""
    return SUPABASE_API.get_or_create_pantry(user_id)


async def get_pantry_stock(user_id: int) -> dict:
    """{nombre: {quantity, unit}} de lo que hay en casa."""
    return SUPABASE_API.get_pantry_stock(user_id)


async def add_pantry_item(
    pantry_id: int, name: str, quantity: float, unit: str, place: str, cat: str,
    shop: str, note: str, min_qty: float, expires: str, user_id: int, sumar: bool = False,
) -> bool:
    return SUPABASE_API.add_or_update_pantry_item(
        pantry_id, name, quantity, unit, place, cat, shop, note, min_qty, expires, user_id, sumar,
    )


async def update_pantry_item(
    pantry_id: int, old_name: str, new_name: str, quantity: float, unit: str, place: str,
    cat: str, shop: str, note: str, min_qty: float, expires: str, user_id: int,
) -> bool:
    return SUPABASE_API.update_pantry_item_details(
        pantry_id, old_name, new_name, quantity, unit, place, cat, shop, note, min_qty, expires, user_id,
    )


async def adjust_pantry_item(pantry_id: int, name: str, delta: float, user_id: int) -> bool:
    return SUPABASE_API.adjust_pantry_item(pantry_id, name, delta, user_id)


async def delete_pantry_item(pantry_id: int, name: str, user_id: int) -> bool:
    return SUPABASE_API.delete_pantry_item(pantry_id, name, user_id)


async def clear_pantry_items(pantry_id: int, user_id: int, solo_agotados: bool = False) -> int:
    return SUPABASE_API.clear_pantry_items(pantry_id, user_id, solo_agotados)


async def set_pantry_auto_stock(pantry_id: int, user_id: int, value: bool) -> bool:
    return SUPABASE_API.set_pantry_auto_stock(pantry_id, user_id, value)


async def get_pantry_users(pantry_id: int) -> List[User]:
    return SUPABASE_API.get_users_in_pantry(pantry_id)


async def merge_and_share_pantry(user_id: int, friend_username: str) -> tuple[bool, str]:
    """Comparte la despensa con otro usuario, fusionando el stock de los dos."""
    return SUPABASE_API.merge_and_share_pantry(user_id, friend_username)


async def remove_user_from_pantry(pantry_id: int, user_id: int, requesting_user_id: int) -> bool:
    return SUPABASE_API.remove_user_from_pantry(pantry_id, user_id, requesting_user_id)


# ---------------------- Cocinar: descontar de la despensa ----------------------
async def consume_from_pantry(pantry_id: int, user_id: int, takes: List[tuple]) -> tuple[bool, int]:
    """Resta de la despensa lo cocinado. `takes` = [(nombre, cantidad, unidad)]."""
    return SUPABASE_API.consume_from_pantry(pantry_id, user_id, takes)


async def get_day_consumption(day_id: int, user_id: int) -> dict:
    return SUPABASE_API.get_day_consumption(day_id, user_id)


async def set_day_consumed(
    day_id: int, slot: str, value: bool, user_id: int,
    username: str = "", items: Optional[List[dict]] = None,
) -> bool:
    return SUPABASE_API.set_day_consumed(day_id, slot, value, user_id, username, items)


async def get_meal_notify_settings(user_id: int) -> dict:
    return SUPABASE_API.get_meal_notify_settings(user_id)


async def set_meal_notify_settings(user_id: int, enabled: bool, meal_time: str, dinner_time: str) -> bool:
    return SUPABASE_API.set_meal_notify_settings(user_id, enabled, meal_time, dinner_time)


# ---------------------- Notificaciones push ----------------------
async def save_push_subscription(user_id: int, endpoint: str, p256dh: str, auth: str, alias: str) -> bool:
    return SUPABASE_API.upsert_push_subscription(user_id, endpoint, p256dh, auth, alias)

async def get_my_push_subscriptions(user_id: int) -> List[dict]:
    return SUPABASE_API.get_push_subscriptions_for_user(user_id)

async def delete_push_subscription(subscription_id: int, requesting_user_id: int) -> bool:
    return SUPABASE_API.delete_push_subscription(subscription_id, requesting_user_id)

# ---------------------- Agenda diaria (tareas / eventos / notas) ----------------------
async def get_day_items(day_id: int, user_id: int) -> List[DayItem]:
    return SUPABASE_API.get_day_items(day_id, user_id)

async def add_day_item(
    day_id: int, owner_id: int, item_type: str, title: str,
    description: str = "", time: Optional[str] = None, end_time: Optional[str] = None,
) -> Optional[DayItem]:
    return SUPABASE_API.add_day_item(day_id, owner_id, item_type, title, description, time, end_time)

async def toggle_day_item_completed(item_id: int, user_id: int) -> bool:
    return SUPABASE_API.toggle_day_item_completed(item_id, user_id)

async def delete_day_item(item_id: int, user_id: int) -> bool:
    return SUPABASE_API.delete_day_item(item_id, user_id)