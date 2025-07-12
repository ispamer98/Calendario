#database.py

import bcrypt

import os
import dotenv
from typing import Union,List,Optional
import pytz
from supabase import create_client, Client
import logging
from Calendario.model.model import Calendar,Day,Meal,Comment,User
from datetime import datetime, timedelta



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
                    return user
        except Exception as e:
            logging.error(f"Error autenticando al usuario: {e}")
        return None
    
    def change_pasw(self,username: str, password: str):
        response = self.supabase.from_("user").select("*").ilike("username", username).execute()
        if response.data:
            user = response.data[0]
            update_response = self.supabase.from_("user").update({"pasw": password}).eq("id", user["id"]).execute()

            if update_response:
                return True
            else:
                return False


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
            # 1) Creamos la condición combinada: owner_id o array shared_with contiene user_id
            condition = f"owner_id.eq.{user_id},shared_with.cs.{{{user_id}}}"

            # 2) Ejecutamos un único query con .or_()
            response = (
                self.supabase
                    .from_("calendars")
                    .select("*")
                    .or_(condition)
                    .execute()
            )

            # 3) Si hay datos, mapeamos al modelo Calendar
            if response.data:
                calendars = []
                for cal in response.data:
                    calendars.append(
                        Calendar(
                            id=cal['id'],
                            name=cal['name'],
                            owner_id=cal['owner_id'],
                            start_date=cal['start_date'],
                            end_date=cal['end_date'],
                            shared_with=cal.get('shared_with', []),
                            created_at=(
                                datetime.fromisoformat(cal['created_at'].replace('Z', '+00:00'))
                                if cal.get('created_at') else datetime.now()
                            )
                        )
                    )
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
        

# Calendario/database/database.py
    def share_with(self, calendar: Calendar, username: str) -> tuple[bool, str]:
        try:
            # Buscar usuario ignorando mayúsculas/minúsculas
            response_username = self.supabase.from_("user").select("*").ilike("username", username.lower()).execute()
            if not response_username.data:
                return False, "Usuario no encontrado"
            username_id = response_username.data[0]["id"]

            # 2. Obtener calendario actual
            response_calendar = self.supabase.from_("calendars").select("shared_with").eq("id", calendar.id).execute()
            if not response_calendar.data:
                return False, "Calendario no encontrado"
                
            shared_with = response_calendar.data[0].get("shared_with", []) or []
            
            # 3. Verificar si ya tiene acceso
            if username_id in shared_with:
                return False, "El usuario ya tiene acceso a este calendario"

            # 4. Actualizar shared_with
            shared_with.append(username_id)
            update_response = self.supabase.from_("calendars").update({"shared_with": shared_with}).eq("id", calendar.id).execute()
            
            return bool(update_response.data), "Calendario compartido exitosamente"
            
        except Exception as e:
            print(f"Error al compartir calendario: {e}")
            return False, "Error interno al compartir el calendario"
        
    def get_user_by_id(self, user_id: int) -> Union[User, None]:
        try:
            response = self.supabase.from_("user").select("*").eq("id", user_id).execute()
            return User(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        

    # Calendario/database/database.py
    def load_shared_users(self, calendar_id: int) -> list[User]:
        try:
            response = (
                self.supabase
                    .from_("calendars")
                    .select("shared_with, owner_id")
                    .eq("id", calendar_id)
                    .execute()
            )
            
            if not response.data:
                return []
                
            calendar_data = response.data[0]
            shared_users: list[User] = []
            
            # 1) Obtener owner
            owner = self.get_user_by_id(calendar_data["owner_id"])
            if owner:
                shared_users.append(owner)
            else:
                return []  # si ni siquiera hay owner, devolvemos vacío
            
            # 2) Normalizar shared_with: si es None, lo convertimos en lista vacía
            shared_with_ids = calendar_data.get("shared_with") or []
            
            # 3) Iterar solo si hay IDs
            for user_id in shared_with_ids:
                # evitamos volver a agregar al owner por si acaso
                if user_id == owner.id:
                    continue

                user = self.get_user_by_id(user_id)
                if user:
                    shared_users.append(user)
                        
            return shared_users

        except Exception as e:
            print(f"Error obteniendo usuarios compartidos: {e}")
            return []

    
    def delete_calendar(self, calendar_id: int) -> bool:
        try:
            # 1) Recuperar todos los IDs de días vinculados al calendario
            days_resp = (
                self.supabase
                    .table("days")
                    .select("id")
                    .eq("calendar_id", calendar_id)
                    .execute()
            )
            day_ids = [row["id"] for row in (days_resp.data or [])]

            # 2) Si hay días, eliminar sus comentarios asociados
            if day_ids:
                delete_comments_resp = (
                    self.supabase
                        .table("comments")
                        .delete()
                        .in_("day_id", day_ids)
                        .execute()
                )
                # Opcional: informar si no se encontraron comentarios
                if delete_comments_resp.count == 0:
                    print(f"No se encontraron comentarios para los días del calendario {calendar_id}")

            # 3) Eliminar todos los días del calendario
            delete_days_resp = (
                self.supabase
                    .table("days")
                    .delete()
                    .eq("calendar_id", calendar_id)
                    .execute()
            )
            if delete_days_resp.count == 0:
                print(f"No se encontraron días para el calendario {calendar_id}")

            # 4) Eliminar el propio calendario
            delete_cal_resp = (
                self.supabase
                    .table("calendars")
                    .delete()
                    .eq("id", calendar_id)
                    .execute()
            )
            # Si data trae al menos un elemento, la eliminación fue exitosa
            return bool(delete_cal_resp.data)

        except Exception as e:
            print(f"Error eliminando calendario (id={calendar_id}): {e}")
            return False


    def get_today_info(self, user_id: int) -> list[dict]:
        try:
            # Obtener fecha actual en Madrid
            madrid_tz = pytz.timezone('Europe/Madrid')
            today = datetime.now(madrid_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            today_str = today.isoformat()

            # Obtener calendarios del usuario
            calendars = self.get_calendars(user_id)
            if not calendars:
                return []

            results = []

            # Buscar en todos los calendarios
            for calendar in calendars:
                # Verificar si la fecha está dentro del rango
                start_date = calendar.start_date
                end_date = calendar.end_date

                if start_date.tzinfo is None:
                    start_date = madrid_tz.localize(start_date)
                if end_date.tzinfo is None:
                    end_date = madrid_tz.localize(end_date)

                if start_date <= today <= end_date:
                    # Buscar el día correspondiente
                    day_response = (
                        self.supabase.from_("days")
                        .select("*")
                        .eq("calendar_id", calendar.id)
                        .eq("date", today_str)
                        .execute()
                    )

                    # Si hay datos, construir objeto día con comida, cena y comentarios
                    if day_response.data:
                        day_data = day_response.data[0]
                        day = Day(
                            id=day_data['id'],
                            calendar_id=day_data['calendar_id'],
                            date=datetime.fromisoformat(day_data['date'].replace('Z', '+00:00')),
                            meal=day_data['meal'],
                            dinner=day_data['dinner'],
                            comments=day_data['comments']
                        )

                        comments = self.get_comments_for_day(day.id)

                        comments_formatted = [{
                            "content": c.content,
                            "username": c.user.username
                        } for c in comments]

                        meal = day.meal
                        dinner = day.dinner
                    else:
                        # Si no hay datos, usar valores vacíos por defecto
                        comments_formatted = []
                        meal = ""
                        dinner = ""

                    # Agregar resultado para este calendario, con o sin datos
                    results.append({
                        "calendar_name": calendar.name,
                        "meal": meal,
                        "dinner": dinner,
                        "comments": comments_formatted
                    })

            return results

        except Exception as e:
            print(f"Error obteniendo información del día actual: {e}")
            return []
