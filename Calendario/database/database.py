#database.py

import bcrypt

import os
import dotenv
from typing import Union,List,Optional
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar,Day,Meal,Comment,User
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
            if not calendar_name.strip():
                raise ValueError("El nombre del calendario es obligatorio")
            
            # Normalizar fechas a UTC medianoche
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            end_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            
            calendar_data = {
                "name": calendar_name,
                "owner_id": user_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("calendars").insert(calendar_data).execute()
            
            if response.data:
                days = []
                current_day = start_date
                while current_day <= end_date:
                    days.append({
                        "calendar_id": response.data[0]["id"],
                        "date": current_day.isoformat()
                    })
                    current_day += timedelta(days=1)
                
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
                .order("date")
                .execute()
            )
            
            if response.data:
                return [
                    Day(
                        id=day['id'],
                        calendar_id=day['calendar_id'],
                        date=datetime.fromisoformat(
                            day['date'].replace('Z', '+00:00')
                        ).replace(tzinfo=None),
                        meal=day['meal'],
                        dinner=day['dinner'],
                        comments=day['comments'],
                    )
                    for day in response.data
                ]
        except Exception as e:
            print(f"Error getting days: {e}")
        return []
    


    def get_all_meals(self) -> list[Meal]:
        try:
            response = self.supabase.from_("meals").select("*").execute()
            print("COMIDAS TOTALES! EN DATABASE!",response.data)
            return [Meal(**meal) for meal in response.data]
        except Exception as e:
            print(f"Error obteniendo comidas: {e}")
            return []
        

    async def update_day_meal(self, day_id: int, meal: Optional[str]) -> Optional[Day]:
            try:
                response = (
                    self.supabase.table("days")
                    .update({"meal": meal})
                    .eq("id", day_id)
                    .execute()
                )
                return Day(**response.data[0]) if response.data else None
            except Exception as e:
                print(f"Error actualizando comida: {e}")
                return None

    async def update_day_dinner(self, day_id: int, dinner: Optional[str]) -> Optional[Day]:
        try:
            response = (
                self.supabase.table("days")
                .update({"dinner": dinner})
                .eq("id", day_id)
                .execute()
            )
            return Day(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error actualizando cena: {e}")
            return None


    def get_comments_for_day(self, day_id: int) -> List[Comment]:
        try:
            print(f"Buscando comentarios para day_id: {day_id}")  # Debug
            response = (
                self.supabase.from_("comments")
                .select("*, user:owner_id(username)")
                .eq("day_id", day_id)
                .order("created_at", desc=False)  # Cambiar a ascendente para ver nuevos primero
                .execute()
            )
            print("Respuesta de Supabase:", response.data)  # Debug
            return [
                Comment(
                    id=comment['id'],
                    day_id=comment['day_id'],
                    content=comment['content'],
                    owner_id=comment['owner_id'],  # <- aquí estaba el error
                    created_at=datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00')),
                    user=User(
                        id=comment['owner_id'],  # <- aquí también
                        username=comment['user']['username']
                    )
                ) for comment in response.data
            ]
        except Exception as e:
            print(f"Error obteniendo comentarios: {e}")
            return []

    def add_comment(self, day_id: int, owner_id: int, content: str) -> Optional[Comment]:
        try:
            comment_data = {
                "day_id": day_id,
                "owner_id": owner_id,
                "content": content
            }
            
            response = self.supabase.table("comments").insert(comment_data).execute()
            
            if response.data:
                # Obtener el comentario recién creado con datos del usuario
                new_comment = self.get_comments_for_day(day_id)[0]
                return new_comment
        except Exception as e:
            print(f"Error agregando comentario: {e}")
        return None
    
    def update_day_comments_flag(self, day_id: int) -> bool:
        try:
            response = (
                self.supabase.table("days")
                .update({"comments": True})
                .eq("id", day_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error actualizando flag de comentarios: {e}")
            return False
        

    def get_day(self, day_id: int) -> Optional[Day]:
        try:
            response = self.supabase.from_("days").select("*").eq("id", day_id).execute()
            if response.data:
                return Day(**response.data[0])
        except Exception as e:
            print(f"Error obteniendo día: {e}")
        return None
    

    def delete_comment(self, comment_id: int) -> bool:
        try:
            # Obtener day_id del comentario antes de eliminarlo
            comment = self.supabase.table("comments").select("day_id").eq("id", comment_id).execute()
            if not comment.data:
                return False
            day_id = comment.data[0]["day_id"]

            # Eliminar el comentario
            delete_response = self.supabase.table("comments").delete().eq("id", comment_id).execute()
            if not delete_response.data:
                return False

            # Contar comentarios restantes para el día
            count_query = self.supabase.table("comments").select("count", count="exact").eq("day_id", day_id).execute()
            comment_count = count_query.data[0]["count"]

            # Actualizar flag si no hay comentarios
            if comment_count == 0:
                self.update_day_comments_false(day_id)
                
            return True
        except Exception as e:
            print(f"Error eliminando comentario: {e}")
            return False

    def update_day_comments_false(self, day_id: int) -> bool:
        try:
            response = (
                self.supabase.table("days")
                .update({"comments": False})
                .eq("id", day_id)
                .execute()
            )
            return len(response.data) > 0
        except Exception as e:
            print(f"Error actualizando flag a False: {e}")
            return False