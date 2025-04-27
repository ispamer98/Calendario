# api.py
import bcrypt
from datetime import datetime
from typing import Union, List, Optional, Dict
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import User, Calendar, Day, Meal, Comment

SUPABASE_API = SupabaseAPI()

# ---------------------- Autenticación de usuario ----------------------
async def authenticate_user(username: str, password: str) -> Union[User, None]:
    user_data = SUPABASE_API.authenticate_user(username, password)
    return User(**user_data) if user_data else None

async def check_existing_user(username: str, email: str) -> Dict[str, bool]:
    return SUPABASE_API.check_existing_user(username, email)

async def check_existing_username(username: str) -> bool:
    return SUPABASE_API.check_existing_username(username)

async def register_user(username: str, password: str, email: str, birthday: str) -> bool:
    try:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_data = {
            "username": username,
            "pasw": hashed_password,
            "email": email,
            "birthday": birthday
        }
        response = SUPABASE_API.supabase.table("user").insert(user_data).execute()
        return bool(response.data)
    except Exception as e:
        print(f"Error registrando usuario: {str(e)}")
        return False

# ---------------------- Calendarios ----------------------
async def fetch_and_transform_calendars(user_id: int) -> List[Calendar]:
    return SUPABASE_API.get_calendars(user_id) or []

async def create_calendar(
    user_id: int, 
    name: str, 
    start_date: datetime, 
    end_date: datetime
) -> Union[Calendar, None]:
    return SUPABASE_API.create_calendar_with_days(user_id, name, start_date, end_date)

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

# ---------------------- Comentarios ----------------------
async def get_day_comments(day_id: int) -> List[Comment]:
    return SUPABASE_API.get_comments_for_day(day_id) or []

async def add_comment_to_day(
    day_id: int, 
    user_id: int, 
    content: str
) -> Union[Comment, None]:
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