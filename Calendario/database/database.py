#database.py


import os
import dotenv
from typing import Union,List
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class SupabaseAPI:

    dotenv.load_dotenv()

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def authenticate_user(self, username: str, password: str) -> Union[dict, None]:
        """
        Autentica a un usuario verificando su nombre y contraseña.

        Args:
            username (str): Nombre de usuario a buscar.
            password (str): Contraseña del nnnnnnn.

        Returns:
            dict | None: Datos del usuario si la autenticación es exitosa, o None si falla.
        """
        try:
            response = self.supabase.from_("user").select("*").eq("username", username).execute()
            print(response.data)

            if response.data:
                user = response.data[0]
                if user["pasw"] == password:
                    logging.info(f"Usuario autenticado: {username}")
                    return user
        except Exception as e:
            logging.error(f"Error autenticando al usuario: {e}")
        return None
    

    def register_user(self, username: str, password: str, email: str, birth_date: str):
        try:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').isoformat()
            response = self.supabase.from_("user").insert({
                "username": username,
                "pasw": password,
                "email": email,
                "birth_date": birth_date
            }).execute()

        except Exception as e:
            print(e)

    def get_calendars(self, user_id: int) -> Union[List[Calendar], None]:
        try:
            response = (
                self.supabase
                .from_("calendars")
                .select("*")
                .eq("owner_id", user_id)
                .execute()
            )

            if response.data:
                calendars = [
                    Calendar(
                        id=cal['id'],
                        name=cal['name'],
                        owner_id=cal['owner_id'],
                        shared_with=cal.get('shared_with', []),
                        created_at=datetime.fromisoformat(
                            cal['created_at'].replace('Z', '+00:00')
                        ) if cal.get('created_at') else datetime.now()
                    )
                    for cal in response.data
                ]
                return calendars
                
        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None