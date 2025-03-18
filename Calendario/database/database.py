#database.py

import bcrypt

import os
import dotenv
from typing import Union,List
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar,Day
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
            response = self.supabase.from_("user").select("*").ilike("username", username).execute()
            print(response.data)

            if response.data:
                user = response.data[0]
                if bcrypt.checkpw(password.encode('utf-8'), user["pasw"].encode('utf-8')):
                    logging.info(f"Usuario autenticado: {username}")
                    return user
        except Exception as e:
            logging.error(f"Error autenticando al usuario: {e}")
        return None
    

    def check_existing_user(self,username: str, email: str) -> dict:
        """
        Verifica si el username o email ya existen en la base de datos.

        Args:
            username (str): Nombre de usuario a verificar.
            email (str): Email a verificar.

        Returns:
            dict: Indica si existen el usuario o email.
        """
        existing_username= False
        existing_email = False

        try:

            response_user = self.supabase.from_("user").select("username").ilike("username", username).execute()
            existing_username= len(response_user.data) > 0

            response_email= self.supabase.from_("user").select("email").ilike("email",email).execute()
            existing_email= len(response_email.data) > 0

            return {'username':existing_username, 'email':existing_email}
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario o email: {e}")
            return {'username': False, 'email': False}
        
    def check_existing_username(self, username):
        try:
            response = self.supabase.from_("user").select("username").ilike("username", username).execute()
            return len(response.data) > 0  # Devuelve directamente el booleano
        
        except Exception as e:
            logging.error(f"Error verificando existencia de usuario: {e}")
            return False

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
                        start_date=cal['start_date'],
                        end_date=cal['end_date'],
                        shared_with=cal.get('shared_with', []),
                        created_at=datetime.fromisoformat(
                            cal['created_at'].replace('Z', '+00:00')
                        ) if cal.get('created_at') else datetime.now(),
                        
                    )
                    for cal in response.data
                ]
                return calendars
                
        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None


    def create_calendar_with_days(self, user_id: int, calendar_name: str, start_date: datetime, end_date: datetime):
        try:
            # Calcular fechas de inicio y fin del mes actual
            if not calendar_name.strip():
                raise ValueError("El nombre del calendario es obligatorio")
            # Insertar calendario con las fechas calculadas
            calendar_data = {
                "name": calendar_name,
                "owner_id": user_id,
                "start_date": start_date.isoformat(),  # Usa el start_date del parámetro
                "end_date": end_date.isoformat(),      # Usa el end_date del parámetro
                "created_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table("calendars").insert(calendar_data).execute()
            
            if response.data:
                # Crear días del mes
                days = []
                current_day = start_date
                while current_day <= end_date:
                    days.append({
                        "calendar_id": response.data[0]["id"],
                        "date": current_day.isoformat()
                    })
                    current_day += timedelta(days=1)
                
                # Insertar días en lote
                self.supabase.table("days").insert(days).execute()
                
                return Calendar(
                    id=response.data[0]["id"],
                    name=calendar_name,
                    owner_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    created_at=datetime.fromisoformat(response.data[0]["created_at"])
                )
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise 
        except Exception as e:
            print(f"Error creating calendar: {str(e)}")
        return None
    

    def get_days_for_calendar(self, calendar_id: int) -> List[Day]:
        try:
            response = (
                self.supabase
                .from_("days")
                .select("*")
                .eq("calendar_id", calendar_id)
                .execute()
            )
            
            if response.data:
                return [
                    Day(
                        id=day['id'],
                        calendar_id=day['calendar_id'],
                        date=datetime.fromisoformat(day['date']),
                        # ... otros campos
                    )
                    for day in response.data
                ]
        except Exception as e:
            print(f"Error getting days: {e}")
        return []