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

#Clase Supabase, esta se encargará de todas las gestiones con la base de datos

class SupabaseAPI:

    #Cargamos el archivo de variables de entorno
    dotenv.load_dotenv()

    #Recuperamos la url y la clave de supabase
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    #Conectamos con supabase 
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    #Función que se encarga del registro de usuario
    def register_user(self, username: str, password: str, email: str, birthday: str) -> bool:
        try:
            #Recibe todos los datos del formulario de registro
            #Aplica hash a la contraseña 
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user_data = { #Generamos los datos para el usuario
                "username": username,
                "pasw": hashed_password,
                "email": email,
                "birthday": birthday
            }
            #Insertamos el usuario en la base de datos
            response = self.supabase.table("user").insert(user_data).execute()
            #Devolvemos True + la info de usuario si se registra correctamente
            return bool(response.data)
        #Si ocurre un error, devolvemos el mensaje + False
        except Exception as e:
            print(f"Error registrando usuario: {str(e)}")
            return False
    
    #Función que se encarga de loggear al usuario
    def authenticate_user(self, username: str, password: str) -> Union[dict, None]:
        try:
            #Buscamos coincidencias de usuario con la base de datos
            response = self.supabase.from_("user").select("*").ilike("username", username).execute()
            #Si encontramos respuesta
            if response.data:
                #Guardamos el nombre de usuario
                user = response.data[0]
                #Comprobamos la coincidencia de contraseña
                if bcrypt.checkpw(password.encode('utf-8'), user["pasw"].encode('utf-8')):
                    #Si obtenemos acceso, devolvemos los datos del usuario
                    return user
        #Si existe algún problema devolvemos mensaje de error + None
        except Exception as e:
            print(f"Error autenticando al usuario: {e}")
        return None
    
    #Función que se encarga del cambio de contraseña
    def change_pasw(self, username: str, password: str):

        try:
            #Buscamos coincidencias de usuario con la base de datos
            response = self.supabase.from_("user").select("*").ilike("username", username).execute()
            #Si encontramos respuesta
            if response.data:
                #Guardamos el usuario
                user = response.data[0]
                #Actualizamos la contraseña
                update_response = self.supabase.from_("user").update({"pasw": password}).eq("id", user["id"]).execute()
                #Si tenemos éxito
                if update_response:
                    #Devolvemos True
                    return True
                #Si no, devolvemos False
                else:
                    return False
        #Si existe algún problema devolvemos error + False
        except Exception as e:
            print(f"Error al actualizar la contraseña {e}")
            return False

    #Función que se encarga de encontrar username o email duplicado
    def check_existing_user(self,username: str, email: str) -> dict:
        #Inicializamos controladores para ambos campos a False
        existing_username= False
        existing_email = False

        try:
            #Buscamos coincidencias de usuario en la base de datos
            response_user = self.supabase.from_("user").select("username").ilike("username", username).execute()
            #Guardaremos True si encuentra alguna coincidencia
            existing_username= len(response_user.data) > 0

            #Buscamos coincidencias de email en la base de datos
            response_email= self.supabase.from_("user").select("email").ilike("email",email).execute()
            #Guardaremos True si encuentra alguna coincidencia
            existing_email= len(response_email.data) > 0
            #Devolvemos diccionario con los resultados
            return {'username':existing_username, 'email':existing_email}
        #Si existe algun problema, devolvemos error + Diccionario a false
        except Exception as e:
            print(f"Error verificando existencia de usuario o email: {e}")
            return {'username': False, 'email': False}
    
    #Función que se encarga de verificar si el nombre de usuario se encuentra registrado
    def check_existing_username(self, username):

        try:
            #Buscamos coincidencias de username en la base de datos
            response = self.supabase.from_("user").select("username").ilike("username", username).execute()
            #Devolvemos el resultado en formato booleano
            return len(response.data) > 0
        #Si existe algún error devolvemos mensaje de error + False
        except Exception as e:
            print(f"Error verificando existencia de usuario: {e}")
            return False

    #Función que extrae los calendarios a los que el usuario tiene acceso
    def get_calendars(self, user_id: int) -> Union[List[Calendar], None]:
        try:
            #Creamos la condición, que sea dueño o que se haya compartido con
            condition = f"owner_id.eq.{user_id},shared_with.cs.{{{user_id}}}"

            #Buscamos coincidencias en base de datos pasando la condición
            response = (self.supabase.from_("calendars").select("*").or_(condition).execute())

            #Si encontramos datos
            if response.data:
                #Inicializamos variable para guardar los calendarios
                calendars = []
                #Iteramos sobre la respuesta
                for cal in response.data:
                    #Por cada item, creamos una instancia de calendario y la añadimos a la lista
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
                #Devolvemos la lista de calendarios
                return calendars
        #Si encontramos error, devolvemos mensaje + None
        except Exception as e:
            logging.error(f"Error obteniendo calendarios del usuario: {e}")
        return None

    #Función que se encarga de crear el calendario y los días necesarios para ese mes
    def create_calendar_with_days(self, user_id: int, calendar_name: str, start_date: datetime, end_date: datetime):
        try:
            #Si no se introduce nombre para le calendario
            if not calendar_name.strip(): #Limpiamos el texto
                #Lanzamos ValueError con mensaje de error
                raise ValueError("El nombre del calendario es obligatorio")
            
            #Inicializamos las fechas a las 24:00
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            end_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            )
            
            #Generamos diccionario con la información del calnedario
            calendar_data = {
                "name": calendar_name,
                "owner_id": user_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            #Insertamos la linea de calendario en base de datos
            response = self.supabase.table("calendars").insert(calendar_data).execute()
            
            #Si tenemos éxito al insertar calendario
            if response.data:
                #Inicializamos la lista de dias vacía
                days = []
                #Inicializamos el dia en curso como el primer dia del mes
                current_day = start_date
                #Creamos un bucle para iterar sobre todos los dias
                #Parará cuando el día en curso sea igual a la fecha de fin de mes
                while current_day <= end_date:
                    #Añade cada registro a la lista como diccionario
                    days.append({
                        #Añadimos el ID de calendario
                        "calendar_id": response.data[0]["id"],
                        #Y la fecha del día
                        "date": current_day.isoformat()
                    })
                    #cuando lo añade, añade 1 dia al dia actual
                    current_day += timedelta(days=1)
                #Cuando el bucle finaliza, añadimos los días a la base de datos
                self.supabase.table("days").insert(days).execute()
                
                #Devolvemos la instancia de calendario con sus datos
                return Calendar(
                    id=response.data[0]["id"],
                    name=calendar_name,
                    owner_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    created_at=datetime.fromisoformat(response.data[0]["created_at"])
                )
        #Si obtenemos ValueError, mostramos el mensaje enviado
        except ValueError as ve:
            print(f"Error de validación: {ve}")
        #Si exite algún error al generar el calendario, mostramos el mensaje de error y retornamos None
        except Exception as e:
            print(f"Error al crear calendario: {str(e)}")
        return None
    
    #Función que recupera los días del calendario
    def get_days_for_calendar(self, calendar_id: int) -> List[Day]:
        try:
            #Buscamos coincidencias de dias asociados a la ID del calendario
            response = (
                self.supabase
                .from_("days")
                .select("*")
                .eq("calendar_id", calendar_id)
                .order("date")
                .execute()
            )
            #Si tenemos respuesta
            if response.data:
                #Iteramos sobre la respuesta y devolvemos una instancia de día por cada registro
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
        #Si exsite algún error, devolvemos el mensaje + Lista vacía
        except Exception as e:
            print(f"Error obteniendo dias: {e}")
        return []
    

    #Función que devuelve todos los registros de comidas en base de datos
    def get_all_meals(self) -> list[Meal]:
        try:
            #Buscamos en la tabla de comidas
            response = self.supabase.from_("meals").select("*").execute()
            #Iteramos sobre la respuesta y añadimos una instancia de comida por cada registro
            #Devolvemos la lista de comidas
            return [Meal(**meal) for meal in response.data]
        #Si existe error, devolvemos mensaje + lista vacía
        except Exception as e:
            print(f"Error obteniendo comidas: {e}")
            return []
        
    #Funciónes que actualizan comida/cena para un día en concreto
    async def update_day_meal(self, day_id: int, meal: Optional[str]) -> Optional[Day]:
            try:
                #Actualizamos la información de comida para el dia seleccionado
                response = (
                    self.supabase.table("days")
                    .update({"meal": meal})
                    .eq("id", day_id)
                    .execute()
                )
                #Si tenemos éxito, devolvemos la instancia de día actualizada
                return Day(**response.data[0]) if response.data else None
            #Si existe error, devolvemos mensaje + None
            except Exception as e:
                print(f"Error actualizando comida: {e}")
                return None

    #Realizamos la misma operación con la cena
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

    #Función que recupera todos los comentarios asociados al día
    def get_comments_for_day(self, day_id: int) -> List[Comment]:
        try:
            #Buscamos coincidencias de comentarios para la ID de día
            response = (
                self.supabase.from_("comments")
                .select("*, user:owner_id(username)")
                .eq("day_id", day_id)
                .order("created_at", desc=False)  #Orden ascendente para ver primero los más nuevos
                .execute()
            )
            #Iteramos sobre la respuesta y añadimos instancia de comentario por cada registro a la lista, devolvemos la lista
            return [
                Comment(
                    id=comment['id'],
                    day_id=comment['day_id'],
                    content=comment['content'],
                    owner_id=comment['owner_id'],
                    created_at=datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00')),
                    user=User(
                        id=comment['owner_id'],
                        username=comment['user']['username']
                    )
                ) for comment in response.data
            ]
        #Si existe error, devolvemos mensaje + Lista vacia
        except Exception as e:
            print(f"Error obteniendo comentarios: {e}")
            return []

    #Función que añade comentario al día seleccionado
    def add_comment(self, day_id: int, owner_id: int, content: str) -> Optional[Comment]:
        try:
            #Generamos diccionario con los datos necesarios
            comment_data = {
                "day_id": day_id,
                "owner_id": owner_id,
                "content": content
            }
            #Insertamos el comentario en la base de datos
            response = self.supabase.table("comments").insert(comment_data).execute()
            #Si tenemos éxito
            if response.data:
                #Guardamos el nuevo comentario obteniendo el primer registro de los comentarios
                new_comment = self.get_comments_for_day(day_id)[0]
                #Devolvemos el nuevo comentario
                return new_comment
        #Si existe error, mostramos el mensaje y devolvemos None
        except Exception as e:
            print(f"Error agregando comentario: {e}")
        return None
    
    #Actualiza el estado del día si existen comentarios
    def update_day_comments_flag(self, day_id: int) -> bool:
        try:
            #Actualizamos el estado de comentarios a True
            response = (
                self.supabase.table("days")
                .update({"comments": True})
                .eq("id", day_id)
                .execute()
            )
            #Devolvemos la respuesta en forma de bool
            return len(response.data) > 0
        #Si existe error, devolvemos mensaje + False
        except Exception as e:
            print(f"Error actualizando flag de comentarios: {e}")
            return False
        
    #Función que obtiene un día en concreto
    def get_day(self, day_id: int) -> Optional[Day]:
        try:
            #Buscamos coincidencia de día buscando por ID en base de datos
            response = self.supabase.from_("days").select("*").eq("id", day_id).execute()
            #Si tenemos respuesta            
            if response.data:
                #Devolvemos la instancia de día
                return Day(**response.data[0])
        #Si existe error, mostramos el mensaje y devolvemos None
        except Exception as e:
            print(f"Error obteniendo día: {e}")
        return None
    
    #Función que borra el registro de comentario
    def delete_comment(self, comment_id: int) -> bool:
        try:
            #Buscamos coincidencia de comentario con el ID en base de datos
            comment = self.supabase.table("comments").select("day_id").eq("id", comment_id).execute()
            #Si no encontramos registro, devolvemos False
            if not comment.data:
                return False
            #Guardamos el ID del día asociado al comentario
            day_id = comment.data[0]["day_id"]

            #Eliminamos el comentario en base de datos
            delete_response = self.supabase.table("comments").delete().eq("id", comment_id).execute()
            #Si no tenemos respuesta, devolvemos False
            if not delete_response.data:
                return False

            #Buscamos el número total de comentarios para el día
            count_query = self.supabase.table("comments").select("count", count="exact").eq("day_id", day_id).execute()
            comment_count = count_query.data[0]["count"]

            #Si no quedan comentarios, actualizamos el estado de comments para el día
            if comment_count == 0:
                self.update_day_comments_false(day_id)
            #Devolvemos True si todo sale bien
            return True
        #Si existe error, mostramos mensaje y devolvemos False
        except Exception as e:
            print(f"Error eliminando comentario: {e}")
            return False

    #Actualizamos el estado de comments para el día a False
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
        
    #Función que se encarga de dar acceso al calendario
    def share_with(self, calendar: Calendar, username: str) -> tuple[bool, str]:
        try:
            #Buscamos coincidencias de usuarios
            response_username = self.supabase.from_("user").select("*").ilike("username", username.lower()).execute()
            #Si no tenemos resultados
            if not response_username.data:
                #Devolvemos mensaje de error + False
                return False, "Usuario no encontrado"
            #Si tenemos resultado, guardamos el ID del usuario
            username_id = response_username.data[0]["id"]

            #Buscamos coincidencias de calendario con la ID introducida y sacamos su campo de usuarios compartidos
            response_calendar = self.supabase.from_("calendars").select("shared_with").eq("id", calendar.id).execute()
            #Si no tenemos respuesta, devolvemos mensaje de error + False
            if not response_calendar.data:
                return False, "Calendario no encontrado"
            #Guardamos la linea de compartidos
            shared_with = response_calendar.data[0].get("shared_with", []) or []
            
            #Si el usuario ya se encuentra en la lista, devolvemos mensaje de error + False
            if username_id in shared_with:
                return False, "El usuario ya tiene acceso a este calendario"

            #Si no se encuentra en la lista, actualizamos incluyendo el usuario
            shared_with.append(username_id)
            update_response = self.supabase.from_("calendars").update({"shared_with": shared_with}).eq("id", calendar.id).execute()
            
            #Devolvemos mensaje de éxito + True
            return bool(update_response.data), "Calendario compartido exitosamente"
        #Si existe error, devolvemos mensaje de error + False
        except Exception as e:
            print(f"Error al compartir calendario: {e}")
            return False, "Error interno al compartir el calendario"
        
    #Función que se encarga de obtener el usuario
    def get_user_by_id(self, user_id: int) -> Union[User, None]:
        try:
            #Buscamos coincidencias de usuarios filtrando por ID en base de datos
            response = self.supabase.from_("user").select("*").eq("id", user_id).execute()
            #Si tenemos respuesta devolvemos el usuario, si no, devolvemos None
            return User(**response.data[0]) if response.data else None
        #Si existe error, devolvemos mensaje + None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        

    #Función que devuelve la lista de usuarios con acceso al calendario
    def load_shared_users(self, calendar_id: int) -> list[User]:
        try:
            #Buscamos coincidencias de calendarios con ID y extraemos las lineas de dueño y compartidos
            response = (
                self.supabase
                    .from_("calendars")
                    .select("shared_with, owner_id")
                    .eq("id", calendar_id)
                    .execute()
            )
            #Si no tenemos respuesta, devolvemos lista vacía
            if not response.data:
                return []
            
            #Si tenemos respuesta, guardamos los datos del calendario
            calendar_data = response.data[0]
            #Inicializamos lista de usuarios vacía
            shared_users: list[User] = []
            
            #Guardamos el usuario dueño del calendario
            owner = self.get_user_by_id(calendar_data["owner_id"])
            #Si tenemos éxito, guardamos el dueño a la lista de comaprtidos
            if owner:
                shared_users.append(owner)
            #En caso contrario, devolvemos lista vacia
            else:
                return []
            
            #Obtenemos los ids de los usuarios compartidos, si es None devolvemos lista vacía
            shared_with_ids = calendar_data.get("shared_with") or []
            
            #Si tenemos IDs, iteramos sobre la lista
            for user_id in shared_with_ids:
                #Si el usuario coincide con el dueño, continuamos
                if user_id == owner.id:
                    continue
                #Obtenemos el usuario a partir de su ID
                user = self.get_user_by_id(user_id)
                if user:
                    #Añadimos el usuario a la lista
                    shared_users.append(user)
            #Devolvemos la lista de usuarios compartidos
            return shared_users
        #Si existe error, devolvemos mensaje + Lista vacía
        except Exception as e:
            print(f"Error obteniendo usuarios compartidos: {e}")
            return []

    #Función que elimina el calendario, los días y los registros de comentarios
    def delete_calendar(self, calendar_id: int) -> bool:
        try:
            #Obtenemos todos los días asociados al calendario
            days_resp = (
                self.supabase
                    .table("days")
                    .select("id")
                    .eq("calendar_id", calendar_id)
                    .execute()
            )
            #Guardamos las id's de las lineas obtenidas
            day_ids = [row["id"] for row in (days_resp.data or [])]

            #Si tenemos respuesta, eliminamos los comentarios asociados a esos dias
            if day_ids:
                delete_comments_resp = (
                    self.supabase
                        .table("comments")
                        .delete()
                        .in_("day_id", day_ids)
                        .execute()
                )

            #Eliminamos todos los días asociados al calendario
            delete_days_resp = (
                self.supabase
                    .table("days")
                    .delete()
                    .eq("calendar_id", calendar_id)
                    .execute()
            )

            #Por último eliminamos el calendario
            delete_cal_resp = (
                self.supabase
                    .table("calendars")
                    .delete()
                    .eq("id", calendar_id)
                    .execute()
            )
            #Devolvemos True si ha tenido éxito
            return bool(delete_cal_resp.data)
        #Si existe algún error, devolvemos mensaje + False
        except Exception as e:
            print(f"Error eliminando calendario (id={calendar_id}): {e}")
            return False

    #Función que obtiene la información relacionada al día de hoy de todos los calendarios asociados al usuario
    def get_today_info(self, user_id: int) -> list[dict]:
        try:
            #Obtener fecha actual en Madrid
            madrid_tz = pytz.timezone('Europe/Madrid')
            #Formateamos la fecha a las 24:00
            today = datetime.now(madrid_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            #Formateamos la fecha a cadena
            today_str = today.isoformat()

            #Buscamos los calendarios asociados al usuario
            calendars = self.get_calendars(user_id)
            #Si no encuentra respuesta, devolvemos la info dentro del diccionario
            if not calendars:
                return [{
                    "calendar_name": "Sin calendario activo",
                    "meal": "",
                    "dinner": "",
                    "comments": []
                }]
            
            #Inicializamos variables de almacenamiento y control
            results = []
            active_calendar = False

            #Recorremos los calendarios del usuario y guardamos sus fechas de inicio/fin
            for calendar in calendars:
                start_date = calendar.start_date
                end_date = calendar.end_date

                #Establecemos la zona horaria si no la reconoce
                if start_date.tzinfo is None:
                    start_date = madrid_tz.localize(start_date)
                if end_date.tzinfo is None:
                    end_date = madrid_tz.localize(end_date)

                #Comprobamos si el día de hoy se encuentra en el calendario
                if start_date <= today <= end_date:
                    #Si lo encuentra, marcamos como True e inicializamos variables para recoger los datos
                    active_calendar = True
                    meal = ""
                    dinner = ""
                    comments_formatted = []

                    #Obtenemos la información del día que nos interesa
                    day_response = (
                        self.supabase.from_("days")
                        .select("*")
                        .eq("calendar_id", calendar.id)
                        .eq("date", today_str)
                        .execute()
                    )

                    #Si obtenemos respuesta, creamos instancia de dia con los datos
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

                        #Guardamos comida/cena
                        meal = day.meal
                        dinner = day.dinner

                        #Obtenemos los comentarios
                        comments = self.get_comments_for_day(day.id)
                        #Recorremos todos los comentarios y los formateamos
                        comments_formatted = [{
                            "content": c.content,
                            "username": c.user.username
                        } for c in comments]

                    #Añadimos a la variable de almacenamiento los datos del día
                    results.append({
                        "calendar_name": calendar.name,
                        "meal": meal,
                        "dinner": dinner,
                        "comments": comments_formatted
                    })

            #Si no tenemos calendario que incluya la fecha actual, mostramos la info en la respuesta
            if not active_calendar:
                results.append({
                    "calendar_name": "Sin calendario activo",
                    "meal": "",
                    "dinner": "",
                    "comments": []
                })

            #Devolvemos el "fallo"
            return results

        #Si tenemos algún problema, devolvemos la respuesta con el "fallo"
        except Exception as e:
            return [{
                "calendar_name": "Error al obtener datos",
                "meal": "",
                "dinner": "",
                "comments": []
            }]
