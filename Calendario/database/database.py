#database.py

import bcrypt
import os
import logging
import time
import dotenv
from typing import Dict,Union,List,Optional
import pytz
from supabase import create_client, Client
from Calendario.model.model import Calendar,Day,Meal,Comment,User,DayItem
#Sumar cantidades exige saber si dos unidades son mezclables
from Calendario.utils.purchase import convert_qty
#Las reglas de la despensa (qué entra al stock y cómo se deshace) son puras y
#viven aparte: aquí solo se leen y se escriben filas
from Calendario.utils.pantry import (
    add_to_stock,
    is_low,
    new_entry,
    normalize_entry,
    now_iso,
    stock_key,
    take_from_stock,
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def time_range_label(start: Optional[str], end: Optional[str]) -> str:
    """'09:00 – 09:30', '09:00' o '' — como se pinta una franja en la agenda."""
    if not start:
        return ""
    if end and end != start:
        return f"{start} – {end}"
    return start


def _generated_share(row: dict) -> dict:
    """Lo que el menú semanal ha puesto en esta fila, semana a semana.

    `{"2026-08-03": 15.0}` = "de la semana del 3 de agosto salieron 15". Es lo
    que permite **rehacer** una semana sin tocar las demás ni lo que pusiste tú.
    """
    aportes = row.get("gen")
    if not isinstance(aportes, dict):
        return {}
    limpio = {}
    for semana, cantidad in aportes.items():
        try:
            limpio[str(semana)] = float(cantidad)
        except (TypeError, ValueError):
            continue
    return limpio


def _manual_share(row: dict) -> float:
    """Lo que hay en la fila que **no** puso el menú semanal.

    Se deduce en vez de guardarse, y por eso aguanta que edites la cantidad a
    mano: si el menú puso 15 y la fila marca 20, tuyos son 5 y así se quedan
    cuando la semana se recalcule.
    """
    aportes = _generated_share(row)
    cantidad = float(row.get("quantity", 0) or 0)
    if not aportes:
        #Filas de antes de que se guardara el reparto: si la puso el menú es
        #entera suya; si la escribiste tú, entera tuya
        return 0.0 if row.get("auto") else cantidad
    return max(0.0, round(cantidad - sum(aportes.values()), 2))


def merge_generated_items(items: dict, generated: dict, mode: str, week: str = "") -> dict:
    """Mezcla los productos calculados por el menú semanal con la lista actual.

    Se mantiene aparte de la clase (sin tocar la base de datos) porque es la
    regla delicada: qué se suma, qué se rehace y qué no se toca nunca.

    La clave está en que cada fila recuerda **cuánto puso el menú y de qué
    semana** (`gen`). Sin eso, generar era siempre "sumar a ciegas" y volver a
    generar la misma semana multiplicaba la compra: 5 alitas se convertían en
    105 a base de pasadas. Ahora regenerar una semana **sustituye** su aporte en
    lugar de acumularlo, así que darle dos veces al botón deja la lista igual.

    - mode="merge" («Sumar»): pone al día lo de esta semana y no quita nada. Lo
      generado para otras semanas sigue sumando, que es comida distinta.
    - mode="replace" («Rehacer»): además retira de esta semana lo que ya no está
      en el menú (o desmarcaste en la vista previa). Lo que añadiste a mano o
      dejaste fijado no se toca.

    Un mismo producto con **otra unidad** va a una fila aparte ("Leche (l)"),
    porque sumar 500 ml con 2 l daría un número sin sentido.

    El supermercado, la sección, el básico de despensa y la nota llegan desde el
    ingrediente de la receta, pero **no pisan** lo que ya hubiera: si moviste el
    producto de pasillo o le pusiste el súper a mano, manda lo tuyo.
    """
    semana = week or "?"
    result = {n: dict(d) for n, d in (items or {}).items()}

    #Dónde acabó cada producto la última vez que se generó ESTA semana. Se mira
    #`gen_of` y no la clave porque la fila puede llamarse "Arroz (kg)".
    previas: dict[str, str] = {}
    for clave, fila in result.items():
        aportes = _generated_share(fila)
        if semana in aportes:
            previas.setdefault(fila.get("gen_of") or clave, clave)
        elif fila.get("auto") and not aportes:
            #Filas antiguas, sin reparto guardado: se dan por de esta semana,
            #que es justo lo que hay que recalcular
            previas.setdefault(clave, clave)

    def _asentar(clave: str, fila: dict, data: dict, aportes: dict) -> dict:
        """Reescribe una fila con el nuevo reparto, respetando lo tuyo."""
        anterior = float(fila.get("quantity", 0) or 0)
        cantidad = round(_manual_share(fila) + sum(aportes.values()), 2)
        #Solo se destacha si de verdad hay que comprar más de lo que había; y al
        #destacharse deja de contar como "ya está en la despensa": lo que se
        #compró se queda en casa y la próxima compra volverá a sumar
        comprado = bool(fila.get("bought", False)) and cantidad <= anterior
        return {
            **fila,
            "quantity": cantidad,
            "unit": data["unit"],
            "cat": fila.get("cat") or data.get("cat", "otros"),
            "supermarket": fila.get("supermarket") or data.get("shop", ""),
            "staple": bool(fila.get("staple", False) or data.get("staple", False)),
            "note": fila.get("note") or data.get("note", ""),
            #Una fila fijada (o tuya) no se convierte en borrable por «Rehacer»
            #solo porque el menú le haya sumado cantidad
            "auto": bool(fila.get("auto", False)) if fila else True,
            "source": data.get("source", ""),
            "bought": comprado,
            "stocked": bool(fila.get("stocked", False)) and comprado,
            "gen": aportes,
            "gen_of": data["_name"],
        }

    tocadas: set[str] = set()

    for name, data in generated.items():
        data = {**data, "_name": name}

        #1) ¿Ya hay una fila de esta misma semana para este producto? Entonces
        #   esto es un recálculo: se sustituye su aporte, no se suma otro.
        clave = previas.get(name)
        if clave is not None and clave in result:
            fila = result[clave]
            #Fila que salió del menú y luego fijaste: «fijado» quiere decir
            #justo esto, que no se recalcula sola nunca más
            if not fila.get("auto", False):
                tocadas.add(clave)
                continue
            aportes = {**_generated_share(fila), semana: data["quantity"]}
            result[clave] = _asentar(clave, fila, data, aportes)
            tocadas.add(clave)
            continue

        #2) Si no, va sobre la fila que se llame igual (tuya o de otra semana)
        clave = name
        fila = result.get(clave)
        if fila and fila.get("unit", "ud") != data["unit"]:
            clave = f"{name} ({data['unit']})"
            fila = result.get(clave)

        #Rehaciendo la lista, lo que añadiste a mano es tuyo: no se toca
        if fila and mode == "replace" and not fila.get("auto", False):
            continue

        if fila:
            aportes = {**_generated_share(fila), semana: data["quantity"]}
            result[clave] = _asentar(clave, fila, data, aportes)
        else:
            result[clave] = _asentar(clave, {}, data, {semana: data["quantity"]})
            result[clave]["auto"] = True
        tocadas.add(clave)

    if mode == "replace":
        #Lo que esta semana ya no pide: se le quita **su** aporte, y la fila solo
        #desaparece si no queda nada tuyo dentro
        for clave in list(result.keys()):
            if clave in tocadas:
                continue
            fila = result[clave]
            if not fila.get("auto", False):
                continue
            aportes = _generated_share(fila)
            if semana not in aportes and aportes:
                continue
            propio = _manual_share(fila)
            aportes.pop(semana, None)
            restante = round(propio + sum(aportes.values()), 2)
            if restante <= 0:
                del result[clave]
            else:
                result[clave] = {**fila, "quantity": restante, "gen": aportes}

    return result


#Clase Supabase, esta se encargará de todas las gestiones con la base de datos

class SupabaseAPI:

    #Cargamos el archivo de variables de entorno
    dotenv.load_dotenv()

    #Recuperamos la url y la clave de supabase
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    #Conectamos con supabase 
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def register_user(self, username: str, password: str, email: str, birthday: str) -> bool:
        try:
            logger.debug("🔵 [DB] register_user iniciado")
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user_data = {
                "username": username.lower(),
                "pasw": hashed_password,
                "email": email,
                "birthday": birthday
            }
            response = self.supabase.table("user").insert(user_data).execute()
            logger.debug(f"🔵 [DB] Respuesta insert user: {response.data}")
            if response.data:
                new_user_id = response.data[0]["id"]
                logger.info(f"✅ [DB] Usuario creado con ID: {new_user_id}")
                # 🔥 Crear la lista de la compra para este usuario
                list_data = {
                    "user_ids": [new_user_id],
                    "items": {}
                }
                list_response = self.supabase.table("shopping_lists").insert(list_data).execute()
                logger.debug(f"🔵 [DB] Respuesta insert shopping_list: {list_response.data}")
                if list_response.data:
                    logger.info("✅ [DB] Lista de compra creada exitosamente")
                else:
                    logger.warning("⚠️ [DB] La lista NO se creó (list_response.data vacío)")
                return True
            else:
                logger.error("❌ [DB] No se pudo insertar el usuario")
                return False
        except Exception as e:
            logger.error(f"💥 [DB] Error en register_user: {str(e)}")
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
            logger.error(f"Error autenticando al usuario: {e}")
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
            logger.error(f"Error al actualizar la contraseña {e}")
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
            logger.error(f"Error verificando existencia de usuario o email: {e}")
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
            logger.error(f"Error verificando existencia de usuario: {e}")
            return False

    # ---------------------- Comprobaciones de acceso ----------------------
    # Como usamos la service_role key de Supabase (sin RLS), estas comprobaciones
    # son la única barrera real entre un usuario y los datos de otro.

    def _get_calendar_access(self, calendar_id: int) -> Optional[dict]:
        """Devuelve owner_id y shared_with de un calendario, o None si no existe."""
        try:
            response = (
                self.supabase.from_("calendars")
                .select("owner_id, shared_with")
                .eq("id", calendar_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error obteniendo acceso de calendario: {e}")
            return None

    def user_has_calendar_access(self, calendar_id: int, user_id: int) -> bool:
        """True si el usuario es dueño o tiene acceso compartido al calendario."""
        data = self._get_calendar_access(calendar_id)
        if not data:
            return False
        if data["owner_id"] == user_id:
            return True
        if user_id in (data.get("shared_with") or []):
            return True
        #También vale tener fila de rol, por si el array se quedó atrás
        try:
            response = (
                self.supabase.from_("calendar_members")
                .select("id").eq("calendar_id", calendar_id).eq("user_id", user_id).execute()
            )
            return bool(response.data)
        except Exception:
            return False

    def user_is_calendar_owner(self, calendar_id: int, user_id: int) -> bool:
        """True si el usuario es el propietario del calendario."""
        data = self._get_calendar_access(calendar_id)
        return bool(data) and data["owner_id"] == user_id

    def get_calendar_id_for_day(self, day_id: int) -> Optional[int]:
        try:
            response = self.supabase.from_("days").select("calendar_id").eq("id", day_id).execute()
            return response.data[0]["calendar_id"] if response.data else None
        except Exception as e:
            logger.error(f"Error obteniendo calendario del día: {e}")
            return None

    def user_has_day_access(self, day_id: int, user_id: int) -> bool:
        """True si el usuario tiene acceso al calendario al que pertenece el día."""
        calendar_id = self.get_calendar_id_for_day(day_id)
        if calendar_id is None:
            return False
        return self.user_has_calendar_access(calendar_id, user_id)

    def user_in_shopping_list(self, list_id: int, user_id: int) -> bool:
        """True si el usuario forma parte de la lista de la compra."""
        try:
            response = self.supabase.from_("shopping_lists").select("user_ids").eq("id", list_id).execute()
            if not response.data:
                return False
            return user_id in (response.data[0].get("user_ids") or [])
        except Exception as e:
            logger.error(f"Error comprobando acceso a lista de la compra: {e}")
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
            logger.error(f"Error obteniendo calendarios del usuario: {e}")
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
            logger.error(f"Error de validación: {ve}")
        #Si exite algún error al generar el calendario, mostramos el mensaje de error y retornamos None
        except Exception as e:
            logger.error(f"Error al crear calendario: {str(e)}")
        return None
    
    @staticmethod
    def _consumed_label(username: Optional[str], momento: Optional[str]) -> str:
        """'Ruben · 12/08 15:34' — quién descontó la comida de la despensa."""
        quien = (username or "").strip()
        if not quien:
            return ""
        if not momento:
            return quien
        try:
            fecha = datetime.fromisoformat(str(momento).replace("Z", "+00:00"))
            local = fecha.astimezone(pytz.timezone("Europe/Madrid"))
            return f"{quien} · {local.strftime('%d/%m %H:%M')}"
        except (ValueError, TypeError):
            return quien

    @staticmethod
    def _consumed_items(raw) -> List[str]:
        """['Arroz — 300 g', ...] a partir del detalle guardado."""
        from Calendario.utils.purchase import format_qty

        if not isinstance(raw, list):
            return []
        lineas = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            nombre = (item.get("name") or "").strip()
            if not nombre:
                continue
            lineas.append(f"{nombre} — {format_qty(float(item.get('qty') or 0), item.get('unit') or 'ud')}")
        return lineas

    def _day_from_row(self, row: dict, agenda_total: int = 0, pending_tasks: int = 0) -> Day:
        """Una fila de `days` -> `Day`, con el descuento de despensa ya resuelto."""
        return Day(
            id=row["id"],
            calendar_id=row["calendar_id"],
            date=datetime.fromisoformat(str(row["date"]).replace("Z", "+00:00")).replace(tzinfo=None),
            meal=row.get("meal"),
            dinner=row.get("dinner"),
            comments=bool(row.get("comments", False)),
            agenda_total=agenda_total,
            pending_tasks=pending_tasks,
            meal_consumed=bool(row.get("meal_consumed", False)),
            dinner_consumed=bool(row.get("dinner_consumed", False)),
            meal_consumed_by=row.get("meal_consumed_by") or "",
            dinner_consumed_by=row.get("dinner_consumed_by") or "",
            meal_consumed_label=self._consumed_label(
                row.get("meal_consumed_by"), row.get("meal_consumed_at")
            ),
            dinner_consumed_label=self._consumed_label(
                row.get("dinner_consumed_by"), row.get("dinner_consumed_at")
            ),
            meal_consumed_items=self._consumed_items(row.get("meal_consumed_items")),
            dinner_consumed_items=self._consumed_items(row.get("dinner_consumed_items")),
        )

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
                #Cargamos en una sola consulta el resumen de agenda (tareas/eventos/notas)
                #de todo el calendario, para no hacer una consulta por día
                agenda_by_day: dict[int, dict] = {}
                try:
                    items_resp = (
                        self.supabase.from_("day_items")
                        .select("day_id, item_type, completed")
                        .eq("calendar_id", calendar_id)
                        .execute()
                    )
                    for row in (items_resp.data or []):
                        summary = agenda_by_day.setdefault(row["day_id"], {"total": 0, "pending_tasks": 0})
                        summary["total"] += 1
                        if row["item_type"] == "task" and not row["completed"]:
                            summary["pending_tasks"] += 1
                except Exception as e:
                    logger.error(f"Error obteniendo resumen de agenda: {e}")

                #Iteramos sobre la respuesta y devolvemos una instancia de día por cada registro.
                #El descuento de despensa (migración 019) llega en la misma fila:
                #con `select("*")` no hay que pedir las columnas por nombre, así
                #que si aún no existen no se pinta ningún tick y ya está.
                return [
                    self._day_from_row(
                        day,
                        agenda_by_day.get(day['id'], {}).get("total", 0),
                        agenda_by_day.get(day['id'], {}).get("pending_tasks", 0),
                    )
                    for day in response.data
                ]
        #Si exsite algún error, devolvemos el mensaje + Lista vacía
        except Exception as e:
            logger.error(f"Error obteniendo dias: {e}")
        return []
    

    def get_calendars_summary(self, calendar_ids: List[int]) -> dict:
        """{calendar_id: {"total": n, "planned": n}} en una sola consulta.

        Lo usa el selector de calendarios para enseñar cuánto tienes
        planificado cada mes sin cargar los días de todos los calendarios.
        """
        try:
            if not calendar_ids:
                return {}
            response = (
                self.supabase.from_("days")
                .select("calendar_id, meal, dinner")
                .in_("calendar_id", calendar_ids)
                .execute()
            )
            summary: dict[int, dict] = {cid: {"total": 0, "planned": 0} for cid in calendar_ids}
            for row in (response.data or []):
                entry = summary.setdefault(row["calendar_id"], {"total": 0, "planned": 0})
                entry["total"] += 1
                if row.get("meal") or row.get("dinner"):
                    entry["planned"] += 1
            return summary
        except Exception as e:
            logger.error(f"Error obteniendo resumen de calendarios: {e}")
            return {}

    def get_days_in_range(
        self, user_id: int, start: datetime, end: datetime, preferred_calendar_id: Optional[int] = None
    ) -> List[Day]:
        """Días entre dos fechas (inclusive) de los calendarios a los que el
        usuario tiene acceso.

        Lo usa el menú semanal: una semana puede caer a caballo entre dos meses
        y por tanto entre dos calendarios distintos. Si dos calendarios cubren
        la misma fecha se prioriza `preferred_calendar_id` (el que el usuario
        tiene seleccionado) para que la semana sea coherente con lo que ve.
        """
        try:
            calendars = self.get_calendars(user_id) or []
            if not calendars:
                return []
            calendar_ids = [c.id for c in calendars]

            response = (
                self.supabase.from_("days")
                .select("*")
                .in_("calendar_id", calendar_ids)
                .gte("date", start.replace(hour=0, minute=0, second=0, microsecond=0).isoformat())
                .lte("date", end.replace(hour=0, minute=0, second=0, microsecond=0).isoformat())
                .order("date")
                .execute()
            )

            #Nos quedamos con un único día por fecha, prefiriendo el calendario activo
            best: dict[str, dict] = {}
            for row in (response.data or []):
                key = row["date"][:10]
                current = best.get(key)
                if current is None:
                    best[key] = row
                elif row["calendar_id"] == preferred_calendar_id and current["calendar_id"] != preferred_calendar_id:
                    best[key] = row

            return [
                Day(
                    id=row["id"],
                    calendar_id=row["calendar_id"],
                    date=datetime.fromisoformat(row["date"].replace("Z", "+00:00")).replace(tzinfo=None),
                    meal=row["meal"],
                    dinner=row["dinner"],
                    comments=row["comments"],
                )
                for row in sorted(best.values(), key=lambda r: r["date"])
            ]
        except Exception as e:
            logger.error(f"Error obteniendo días por rango: {e}")
            return []

    # ---------------------- Recetarios (meals + recipe_books) ----------------
    # El recetario ya no es común a toda la app: cada usuario tiene el suyo y,
    # al compartirlo, los dos se fusionan en uno que ambos ven y editan. Es el
    # mismo modelo que la lista de la compra (`shopping_lists.user_ids`).

    def get_recipe_book(self, user_id: int) -> Optional[dict]:
        """Recetario en el que está el usuario, o None si aún no tiene."""
        try:
            response = (
                self.supabase.table("recipe_books")
                .select("*")
                .filter("user_ids", "cs", f"{{{user_id}}}")
                .order("id")
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.warning(f"No se pudo leer el recetario ({e}); ¿falta la migración 014?")
            return None

    def get_or_create_recipe_book(self, user_id: int) -> Optional[dict]:
        """Recetario del usuario, creándolo vacío la primera vez.

        Quien se da de alta no hereda las comidas de nadie: empieza con su
        recetario en blanco hasta que alguien lo comparta con él.
        """
        book = self.get_recipe_book(user_id)
        if book:
            return book
        try:
            response = (
                self.supabase.table("recipe_books").insert({"user_ids": [user_id]}).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creando el recetario de user_id={user_id}: {e}")
            return None

    def user_in_recipe_book(self, book_id: int, user_id: int) -> bool:
        try:
            response = (
                self.supabase.table("recipe_books").select("user_ids").eq("id", book_id).execute()
            )
            if not response.data:
                return False
            return user_id in (response.data[0].get("user_ids") or [])
        except Exception as e:
            logger.error(f"Error comprobando el acceso al recetario: {e}")
            return False

    def _meal_book_id(self, meal_id: int) -> Optional[int]:
        try:
            response = self.supabase.from_("meals").select("book_id").eq("id", meal_id).execute()
            return response.data[0].get("book_id") if response.data else None
        except Exception as e:
            logger.error(f"Error leyendo el recetario de la comida {meal_id}: {e}")
            return None

    def user_can_edit_meal(self, meal_id: int, user_id: int) -> bool:
        """Solo se toca una comida del recetario propio (o compartido contigo)."""
        book_id = self._meal_book_id(meal_id)
        if book_id is None:
            return False
        return self.user_in_recipe_book(book_id, user_id)

    #Función que devuelve las comidas del recetario del usuario
    def get_all_meals(self, user_id: int) -> list[Meal]:
        try:
            book = self.get_or_create_recipe_book(user_id)
            if not book:
                return []
            #Buscamos en la tabla de comidas, solo las de ese recetario
            response = self.supabase.from_("meals").select("*").eq("book_id", book["id"]).execute()
            #Iteramos sobre la respuesta y añadimos una instancia de comida por cada registro
            #Devolvemos la lista de comidas
            return [Meal(**meal) for meal in response.data]
        #Si existe error, devolvemos mensaje + lista vacía
        except Exception as e:
            logger.error(f"Error obteniendo comidas: {e}")
            return []
        

    def add_meal(
        self,
        meal: str,
        description: str,
        ingredients: Optional[list] = None,
        category: str = "otros",
        prep_minutes: int = 20,
        user_id: Optional[int] = None,
    ) -> Optional[Meal]:
        try:
            book = self.get_or_create_recipe_book(user_id) if user_id else None
            if not book:
                logger.warning(f"Sin recetario para user_id={user_id}: no se puede añadir la comida")
                return None

            # 1️⃣ Comprobamos si ya existe en ESE recetario (case-insensitive)
            existing = (
                self.supabase
                .from_("meals")
                .select("id")
                .eq("book_id", book["id"])
                .ilike("name", meal)
                .execute()
            )

            if existing.data:
                return None  # ⬅️ Nombre en uso

            # 2️⃣Insertamos si no existe
            meal_data = {
                "name": meal,
                "description": description,
                "ingredients": ingredients or [],
                "category": category,
                "prep_minutes": prep_minutes,
                "book_id": book["id"],
            }

            response = self._insert_meal_row(meal_data)

            if response and response.data:
                return Meal(**response.data[0])

        except Exception as e:
            logger.error(f"Error agregando comida: {e}")
        return None

    def _insert_meal_row(self, meal_data: dict):
        """Inserta en `meals` tolerando que la migración 004 aún no esté aplicada.

        Si las columnas ingredients/category/prep_minutes no existen todavía,
        PostgREST responde PGRST204 y reintentamos con las columnas de siempre,
        para que dar de alta una comida nunca falle por una migración pendiente.
        """
        try:
            return self.supabase.from_("meals").insert(meal_data).execute()
        except Exception as e:
            if "schema cache" not in str(e):
                raise
            logger.warning("Columnas de ingredientes no disponibles; insertando comida sin ellas")
            legacy = {"name": meal_data["name"], "description": meal_data.get("description", "")}
            return self.supabase.from_("meals").insert(legacy).execute()

    def update_meal(
        self,
        meal_id: int,
        name: str,
        description: str,
        ingredients: Optional[list] = None,
        category: str = "otros",
        prep_minutes: int = 20,
        user_id: Optional[int] = None,
    ) -> Optional[Meal]:
        """Actualiza una comida de tu recetario.

        Si cambia el nombre, arrastra el cambio a los días que la tenían
        asignada (days.meal / days.dinner guardan el nombre, no el id, así que
        sin esto los días quedarían apuntando a un plato que ya no existe).
        """
        try:
            current = (
                self.supabase.from_("meals").select("name, book_id").eq("id", meal_id).execute()
            )
            if not current.data:
                return None
            old_name = current.data[0]["name"]
            book_id = current.data[0].get("book_id")

            #Solo se edita lo que está en tu recetario (o en uno compartido contigo)
            if user_id is None or book_id is None or not self.user_in_recipe_book(book_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no puede editar la comida {meal_id}")
                return None

            # Nombre en uso por OTRA comida DEL MISMO recetario
            clash = (
                self.supabase.from_("meals")
                .select("id").eq("book_id", book_id).ilike("name", name).execute()
            )
            if any(row["id"] != meal_id for row in (clash.data or [])):
                return None

            payload = {
                "name": name,
                "description": description,
                "ingredients": ingredients or [],
                "category": category,
                "prep_minutes": prep_minutes,
            }
            try:
                response = self.supabase.from_("meals").update(payload).eq("id", meal_id).execute()
            except Exception as e:
                if "schema cache" not in str(e):
                    raise
                response = (
                    self.supabase.from_("meals")
                    .update({"name": name, "description": description})
                    .eq("id", meal_id)
                    .execute()
                )

            if old_name != name:
                self._rename_meal_in_days(old_name, name, user_id)

            return Meal(**response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Error actualizando comida (id={meal_id}): {e}")
            return None

    def _accessible_calendar_ids(self, user_id: int) -> List[int]:
        """Calendarios que el usuario puede tocar (suyos o compartidos con él)."""
        try:
            condition = f"owner_id.eq.{user_id},shared_with.cs.{{{user_id}}}"
            response = self.supabase.from_("calendars").select("id").or_(condition).execute()
            return [row["id"] for row in (response.data or [])]
        except Exception as e:
            logger.error(f"Error obteniendo los calendarios accesibles: {e}")
            return []

    def _rename_meal_in_days(self, old_name: str, new_name: str, user_id: Optional[int]) -> None:
        """Arrastra el cambio de nombre a los días planificados.

        Solo a los calendarios del usuario: ahora que cada recetario es de
        alguien, dos personas distintas pueden tener una "Paella" que no es la
        misma, y renombrar la tuya no puede tocar los días de la suya.
        """
        if user_id is None:
            return
        calendar_ids = self._accessible_calendar_ids(user_id)
        if not calendar_ids:
            return
        try:
            (self.supabase.table("days").update({"meal": new_name})
             .eq("meal", old_name).in_("calendar_id", calendar_ids).execute())
            (self.supabase.table("days").update({"dinner": new_name})
             .eq("dinner", old_name).in_("calendar_id", calendar_ids).execute())
        except Exception as e:
            logger.warning(f"No se pudo renombrar el plato en los días: {e}")

    

    #Funciónes que actualizan comida/cena para un día en concreto
    async def update_day_meal(self, day_id: int, meal: Optional[str], user_id: int) -> Optional[Day]:
            try:
                #Comprobamos que el usuario tenga acceso al calendario de este día
                if not self.user_has_day_access(day_id, user_id):
                    logger.warning(f"⛔ Acceso denegado: user_id={user_id} no tiene acceso al día {day_id}")
                    return None
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
                logger.error(f"Error actualizando comida: {e}")
                return None

    #Realizamos la misma operación con la cena
    async def update_day_dinner(self, day_id: int, dinner: Optional[str], user_id: int) -> Optional[Day]:
        try:
            #Comprobamos que el usuario tenga acceso al calendario de este día
            if not self.user_has_day_access(day_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no tiene acceso al día {day_id}")
                return None
            response = (
                self.supabase.table("days")
                .update({"dinner": dinner})
                .eq("id", day_id)
                .execute()
            )
            return Day(**response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Error actualizando cena: {e}")
            return None

    #Función que recupera todos los comentarios asociados al día
    def get_comments_for_day(self, day_id: int, user_id: int) -> List[Comment]:
        try:
            if not self.user_has_day_access(day_id, user_id):
                return []
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
            logger.error(f"Error obteniendo comentarios: {e}")
            return []

    #Función que añade comentario al día seleccionado
    def add_comment(self, day_id: int, owner_id: int, content: str) -> Optional[Comment]:
        try:
            #Comprobamos que el usuario tenga acceso al calendario de este día
            if not self.user_has_day_access(day_id, owner_id):
                logger.warning(f"⛔ Acceso denegado: user_id={owner_id} no tiene acceso al día {day_id}")
                return None
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
                new_comment = self.get_comments_for_day(day_id, owner_id)[0]
                #Devolvemos el nuevo comentario
                return new_comment
        #Si existe error, mostramos el mensaje y devolvemos None
        except Exception as e:
            logger.error(f"Error agregando comentario: {e}")
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
            logger.error(f"Error actualizando flag de comentarios: {e}")
            return False
        
    #Función que obtiene un día en concreto
    def get_day(self, day_id: int, user_id: int) -> Optional[Day]:
        try:
            if not self.user_has_day_access(day_id, user_id):
                return None
            #Buscamos coincidencia de día buscando por ID en base de datos
            response = self.supabase.from_("days").select("*").eq("id", day_id).execute()
            #Si tenemos respuesta
            if response.data:
                #Se monta a mano y no con `Day(**fila)`: desde la migración 019 la
                #fila trae columnas que el modelo no lleva tal cual (el detalle de
                #lo descontado se guarda como JSON y se pinta ya formateado)
                return self._day_from_row(response.data[0])
        #Si existe error, mostramos el mensaje y devolvemos None
        except Exception as e:
            logger.error(f"Error obteniendo día: {e}")
        return None
    
    #Función que borra el registro de comentario
    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        try:
            #Buscamos coincidencia de comentario con el ID en base de datos
            comment = self.supabase.table("comments").select("day_id, owner_id").eq("id", comment_id).execute()
            #Si no encontramos registro, devolvemos False
            if not comment.data:
                return False
            #Guardamos el ID del día asociado al comentario
            day_id = comment.data[0]["day_id"]

            #Cada uno borra solo lo que ha escrito él, propietario incluido
            if comment.data[0]["owner_id"] != user_id:
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no escribió el comentario {comment_id}")
                return False

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
            logger.error(f"Error eliminando comentario: {e}")
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
            logger.error(f"Error actualizando flag a False: {e}")
            return False
        
    #Función que se encarga de dar acceso al calendario
    def share_with(self, calendar: Calendar, username: str, requesting_user_id: int) -> tuple[bool, str]:
        try:
            #Comparten el propietario y los administradores que él nombre
            if not self.user_can_share_calendar(calendar.id, requesting_user_id):
                return False, "Solo el propietario o un administrador pueden compartir"

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
            #Entra como invitado; el propietario puede ascenderlo después
            try:
                self.supabase.table("calendar_members").insert(
                    {"calendar_id": calendar.id, "user_id": username_id, "role": "member"}
                ).execute()
            except Exception:
                pass
            
            #Devolvemos mensaje de éxito + True
            return bool(update_response.data), "Calendario compartido exitosamente"
        #Si existe error, devolvemos mensaje de error + False
        except Exception as e:
            logger.error(f"Error al compartir calendario: {e}")
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
            logger.error(f"Error obteniendo usuario: {e}")
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
            logger.error(f"Error obteniendo usuarios compartidos: {e}")
            return []

    #Función que elimina el calendario, los días y los registros de comentarios
    def delete_calendar(self, calendar_id: int, user_id: int) -> bool:
        try:
            #Solo el propietario puede eliminar el calendario
            if not self.user_is_calendar_owner(calendar_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no es propietario del calendario {calendar_id}")
                return False

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
            logger.error(f"Error eliminando calendario (id={calendar_id}): {e}")
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
                    "comments": [],
                    #"tasks" debe ir siempre: el frontend lo lee sin comprobar
                    "tasks": [],
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
                    tasks_formatted = []

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
                        comments = self.get_comments_for_day(day.id, user_id)
                        #Recorremos todos los comentarios y los formateamos
                        comments_formatted = [{
                            "content": c.content,
                            "username": c.user.username
                        } for c in comments]

                        #Obtenemos los elementos de agenda (tareas/eventos/notas) de hoy
                        #Icono y color del tipo, para que Hoy pinte igual que la agenda
                        tipos = {t["key"]: t for t in self.get_task_types()}
                        tasks_formatted = []
                        for item in self.get_day_items(day.id, user_id):
                            t = tipos.get(item.item_type)
                            tasks_formatted.append({
                                "id": item.id,
                                "title": item.title,
                                "item_type": item.item_type,
                                "completed": item.completed,
                                "time": item.time or "",
                                "time_label": item.time_label,
                                "type_icon": t["icon"] if t else "circle-dot",
                                "type_color": t["color"] if t else "#94a3b8",
                                "completable": bool(t["completable"]) if t else item.item_type == "task",
                            })

                    #Añadimos a la variable de almacenamiento los datos del día
                    results.append({
                        "calendar_name": calendar.name,
                        "meal": meal,
                        "dinner": dinner,
                        "comments": comments_formatted,
                        "tasks": tasks_formatted,
                    })

            #Si no tenemos calendario que incluya la fecha actual, mostramos la info en la respuesta
            if not active_calendar:
                results.append({
                    "calendar_name": "Sin calendario activo",
                    "meal": "",
                    "dinner": "",
                    "comments": [],
                    "tasks": [],
                })

            #Devolvemos el "fallo"
            return results

        #Si tenemos algún problema, devolvemos la respuesta con el "fallo"
        except Exception as e:
            return [{
                "calendar_name": "Error al obtener datos",
                "meal": "",
                "dinner": "",
                "comments": [],
                "tasks": [],
            }]


    def delete_meal_by_id(self, meal_id: int, user_id: Optional[int] = None) -> bool:
        """Elimina una comida de tu recetario y limpia days.meal / days.dinner"""
        try:
            # 1. Obtener el nombre de la comida
            meal_resp = (
                self.supabase
                .table("meals")
                .select("name, book_id")
                .eq("id", meal_id)
                .execute()
            )

            if not meal_resp.data:
                return False

            meal_name = meal_resp.data[0]["name"]
            book_id = meal_resp.data[0].get("book_id")

            #Solo se borra lo que está en tu recetario
            if user_id is None or book_id is None or not self.user_in_recipe_book(book_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no puede borrar la comida {meal_id}")
                return False

            # 2. Limpiar referencias en los días de SUS calendarios
            calendar_ids = self._accessible_calendar_ids(user_id)
            if calendar_ids:
                (self.supabase.table("days").update({"meal": None})
                 .eq("meal", meal_name).in_("calendar_id", calendar_ids).execute())
                (self.supabase.table("days").update({"dinner": None})
                 .eq("dinner", meal_name).in_("calendar_id", calendar_ids).execute())

            # 4. Eliminar la comida
            delete_resp = (
                self.supabase
                .table("meals")
                .delete()
                .eq("id", meal_id)
                .execute()
            )

            return bool(delete_resp.data)

        except Exception as e:
            logger.error(f"Error eliminando comida (id={meal_id}): {e}")
            return False

    # ---------------------- Compartir el recetario ----------------------
    # Mismo trato que la lista de la compra: al compartir, los dos recetarios se
    # fusionan en uno solo y a partir de ahí ambos ven y editan exactamente las
    # mismas recetas.

    def get_users_in_recipe_book(self, book_id: int) -> List[User]:
        try:
            book = self.supabase.table("recipe_books").select("user_ids").eq("id", book_id).execute()
            if not book.data:
                return []
            user_ids = book.data[0].get("user_ids") or []
            if not user_ids:
                return []
            response = self.supabase.table("user").select("*").in_("id", user_ids).execute()
            return [User(**row) for row in (response.data or [])]
        except Exception as e:
            logger.error(f"Error obteniendo los usuarios del recetario: {e}")
            return []

    def merge_and_share_recipe_book(self, user_id: int, friend_username: str) -> tuple[bool, str]:
        """Comparte tu recetario con otro usuario, fusionando el suyo con el tuyo.

        Las recetas del otro se mueven al tuyo. Si las dos tienen un plato con
        el mismo nombre, se queda el tuyo (no se puede saber cuál de los dos es
        "el bueno", y perder el tuyo sin avisar sería peor).
        """
        try:
            friend = self.get_user_by_username(friend_username)
            if not friend:
                return False, "Usuario no encontrado"
            friend_id = friend["id"]
            if friend_id == user_id:
                return False, "Ese eres tú"

            book = self.get_or_create_recipe_book(user_id)
            if not book:
                return False, "No tienes recetario activo. ¿Falta la migración 014_recipe_books.sql?"
            book_id = book["id"]

            if friend_id in (book.get("user_ids") or []):
                return False, f"{friend['username']} ya comparte tu recetario"

            friend_book = self.get_recipe_book(friend_id)
            movidas, repetidas = 0, 0

            if friend_book and friend_book["id"] != book_id:
                mine = self.supabase.from_("meals").select("name").eq("book_id", book_id).execute()
                existing = {row["name"].strip().lower() for row in (mine.data or [])}

                theirs = self.supabase.from_("meals").select("id, name").eq("book_id", friend_book["id"]).execute()
                for row in (theirs.data or []):
                    if row["name"].strip().lower() in existing:
                        #Duplicada por nombre: se descarta la suya
                        self.supabase.table("meals").delete().eq("id", row["id"]).execute()
                        repetidas += 1
                    else:
                        self.supabase.table("meals").update({"book_id": book_id}).eq("id", row["id"]).execute()
                        existing.add(row["name"].strip().lower())
                        movidas += 1

                #El recetario viejo del amigo se queda vacío: se elimina
                self.supabase.table("recipe_books").delete().eq("id", friend_book["id"]).execute()

            user_ids = list(book.get("user_ids") or [])
            if friend_id not in user_ids:
                user_ids.append(friend_id)
            self.supabase.table("recipe_books").update({"user_ids": user_ids}).eq("id", book_id).execute()

            detalle = f"{movidas} recetas suyas añadidas"
            if repetidas:
                detalle += f" ({repetidas} ya las tenías)"
            return True, f"Recetario compartido con {friend['username']}: {detalle}"
        except Exception as e:
            logger.error(f"Error compartiendo el recetario: {e}")
            return False, "No se pudo compartir el recetario"

    def remove_user_from_recipe_book(
        self, book_id: int, user_id: int, requesting_user_id: int
    ) -> bool:
        """Saca a alguien del recetario compartido y le deja una copia propia.

        Se le copian las recetas en vez de dejarle a cero: al contrario que una
        lista de la compra, un recetario es trabajo acumulado de meses y
        quitárselo de golpe sería destructivo.
        """
        try:
            if not self.user_in_recipe_book(book_id, requesting_user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={requesting_user_id} no está en el recetario {book_id}")
                return False
            if user_id == requesting_user_id:
                return False

            book = self.supabase.table("recipe_books").select("user_ids").eq("id", book_id).execute()
            if not book.data:
                return False
            user_ids = [uid for uid in (book.data[0].get("user_ids") or []) if uid != user_id]
            self.supabase.table("recipe_books").update({"user_ids": user_ids}).eq("id", book_id).execute()

            #Recetario nuevo para el que sale, con una copia de las recetas
            new_book = self.supabase.table("recipe_books").insert({"user_ids": [user_id]}).execute()
            if not new_book.data:
                return False
            new_book_id = new_book.data[0]["id"]

            meals = self.supabase.from_("meals").select("*").eq("book_id", book_id).execute()
            copias = []
            for row in (meals.data or []):
                copia = {k: v for k, v in row.items() if k not in ("id", "created_at")}
                copia["book_id"] = new_book_id
                copias.append(copia)
            if copias:
                self.supabase.table("meals").insert(copias).execute()
            return True
        except Exception as e:
            logger.error(f"Error sacando a un usuario del recetario: {e}")
            return False


    # ---------------------- Unidades de medida ----------------------
    # Configurables por el usuario (tabla `units`, migración 006). Si la tabla
    # todavía no existe, se devuelve la lista de reserva y la app sigue igual.

    #Lista de reserva mientras no esté aplicada la migración 006
    DEFAULT_UNITS = ["ud", "g", "kg", "ml", "l", "lata", "paquete", "cda", "diente", "sobre", "manojo", "pizca"]

    def _find_unit_by_name(self, name: str) -> Optional[dict]:
        """Busca una unidad por nombre exacto (ignorando mayúsculas).

        Igual que con los productos, `ilike` no vale: `_` es un comodín y `\\w`
        lo admite en el nombre de una unidad. Son menos de veinte filas.
        """
        try:
            rows = self.supabase.from_("units").select("id, name").execute().data or []
        except Exception as e:
            logger.warning(f"No se pudo comprobar si la unidad ya existe: {e}")
            return None
        return next((r for r in rows if self._mismo_nombre(r.get("name"), name)), None)

    def get_units(self) -> List[str]:
        try:
            response = (
                self.supabase.from_("units")
                .select("name, position")
                .order("position")
                .order("name")
                .execute()
            )
            units = [row["name"] for row in (response.data or [])]
            return units or list(self.DEFAULT_UNITS)
        except Exception as e:
            logger.warning(f"No se pudieron leer las unidades ({e}); usando las de reserva")
            return list(self.DEFAULT_UNITS)

    def add_unit(self, name: str) -> bool:
        """Añade una unidad. False si ya existe (comparando sin mayúsculas)."""
        try:
            if self._find_unit_by_name(name):
                return False
            #Se coloca al final: `position` ordena, y las semillas van de 10 en 10
            last = self.supabase.from_("units").select("position").order("position", desc=True).limit(1).execute()
            position = (last.data[0]["position"] + 10) if last.data else 10
            response = self.supabase.table("units").insert({"name": name, "position": position}).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error añadiendo unidad: {e}")
            return False

    def update_unit(self, old_name: str, new_name: str) -> bool:
        """Renombra una unidad y la arrastra allí donde estaba escrita.

        La unidad es texto en los ingredientes, en los productos de la compra y
        en el catálogo: sin arrastrarla, cambiar "ud" por "unidad" dejaría las
        cantidades antiguas con la unidad vieja.
        """
        try:
            old_name = (old_name or "").strip()
            new_name = (new_name or "").strip()
            if not old_name or not new_name:
                return False
            if old_name.lower() != new_name.lower() and self._find_unit_by_name(new_name):
                return False

            actual = self._find_unit_by_name(old_name)
            if not actual:
                return False
            response = (
                self.supabase.table("units")
                .update({"name": new_name})
                .eq("id", actual["id"])
                .execute()
            )
            if not response.data:
                return False
            if old_name.lower() != new_name.lower():
                self._rename_unit_usages(old_name, new_name)
            return True
        except Exception as e:
            logger.error(f"Error renombrando la unidad: {e}")
            return False

    def _rename_unit_usages(self, old_name: str, new_name: str) -> int:
        """Reescribe la unidad allí donde está guardada como texto.

        Devuelve cuántas cosas ha tocado (productos + ingredientes + líneas de
        la compra), que es lo que se le enseña al usuario al convertir.
        """
        objetivo = old_name.strip().lower()
        tocados = 0

        def es_la_vieja(valor) -> bool:
            return (valor or "").strip().lower() == objetivo

        try:
            #Por `id` y no por `ilike("unit", ...)`: el comodín de `ilike` podría
            #arrastrar unidades que no eran (ver `_find_product_by_name`)
            afectados = [
                row["id"]
                for row in (self.supabase.from_("products").select("id, unit").execute().data or [])
                if es_la_vieja(row.get("unit"))
            ]
            if afectados:
                response = (
                    self.supabase.table("products")
                    .update({"unit": new_name})
                    .in_("id", afectados)
                    .execute()
                )
                tocados += len(response.data or [])
        except Exception as e:
            logger.warning(f"No se pudo renombrar la unidad en el catálogo: {e}")

        try:
            meals = self.supabase.from_("meals").select("id, ingredients").execute()
            for row in (meals.data or []):
                ingredients = row.get("ingredients") or []
                afectados = sum(1 for i in ingredients if es_la_vieja((i or {}).get("unit")))
                if not afectados:
                    continue
                updated = [
                    {**i, "unit": new_name} if es_la_vieja((i or {}).get("unit")) else i
                    for i in ingredients
                ]
                self.supabase.table("meals").update({"ingredients": updated}).eq("id", row["id"]).execute()
                tocados += afectados
        except Exception as e:
            logger.warning(f"No se pudo renombrar la unidad en las recetas: {e}")

        try:
            lists = self.supabase.from_("shopping_lists").select("id, items").execute()
            for row in (lists.data or []):
                items = row.get("items") or {}
                afectados = 0
                for data in items.values():
                    if es_la_vieja(data.get("unit")):
                        data["unit"] = new_name
                        afectados += 1
                if afectados:
                    self.supabase.table("shopping_lists").update({"items": items}).eq("id", row["id"]).execute()
                    tocados += afectados
        except Exception as e:
            logger.warning(f"No se pudo renombrar la unidad en las listas: {e}")

        return tocados

    def get_unit_usage(self) -> Dict[str, int]:
        """Cuántas veces está escrita cada unidad, mire donde mire la app.

        La unidad se guarda como **texto** en tres sitios (catálogo, recetas y
        listas de la compra), no como referencia a la tabla `units`. Por eso
        borrar una unidad no rompe nada... pero deja huérfano todo lo que la
        usaba: se sigue viendo, y ya no se puede volver a elegir. Este recuento
        es lo que permite avisar antes de borrar y encontrar las huérfanas
        después.

        La clave es la unidad **en minúsculas**: "G" y "g" son la misma cosa.
        """
        uso: Dict[str, int] = {}

        def anota(valor) -> None:
            nombre = (valor or "").strip()
            if nombre:
                uso[nombre.lower()] = uso.get(nombre.lower(), 0) + 1

        try:
            for row in (self.supabase.from_("products").select("unit").execute().data or []):
                anota(row.get("unit"))
        except Exception as e:
            logger.warning(f"No se pudo contar el uso de unidades en el catálogo: {e}")

        try:
            for row in (self.supabase.from_("meals").select("ingredients").execute().data or []):
                for ingrediente in (row.get("ingredients") or []):
                    anota((ingrediente or {}).get("unit"))
        except Exception as e:
            logger.warning(f"No se pudo contar el uso de unidades en las recetas: {e}")

        try:
            for row in (self.supabase.from_("shopping_lists").select("items").execute().data or []):
                for data in (row.get("items") or {}).values():
                    anota((data or {}).get("unit"))
        except Exception as e:
            logger.warning(f"No se pudo contar el uso de unidades en las listas: {e}")

        return uso

    def convert_unit(self, old_name: str, new_name: str) -> int:
        """Pasa todo lo que usa `old_name` a `new_name`, sin tocar la tabla.

        Es lo que arregla una unidad huérfana (la que se borró del desplegable
        pero seguía escrita en las recetas): en vez de resucitarla, se convierte
        a una de las que sí existen. Devuelve cuántas cosas ha cambiado, o -1 si
        los nombres no valen.
        """
        old_name = (old_name or "").strip()
        new_name = (new_name or "").strip()
        if not old_name or not new_name or old_name.lower() == new_name.lower():
            return -1
        try:
            return self._rename_unit_usages(old_name, new_name)
        except Exception as e:
            logger.error(f"Error convirtiendo la unidad: {e}")
            return -1

    def delete_unit(self, name: str) -> bool:
        """Quita una unidad del desplegable.

        No toca los ingredientes ni los productos que ya la usaban: ahí la
        unidad es solo texto y se sigue mostrando igual. Quien llama a esto es
        responsable de avisar (o de convertir antes) si la unidad está en uso;
        para eso está `get_unit_usage`.
        """
        try:
            actual = self._find_unit_by_name(name)
            if not actual:
                return False
            response = self.supabase.table("units").delete().eq("id", actual["id"]).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error eliminando unidad: {e}")
            return False

    # ---------------------- Roles de calendario ----------------------
    # propietario = calendars.owner_id; el resto vive en calendar_members.
    # Si la tabla no existe todavía, todo el mundo es "invitado", que es
    # exactamente como se comportaba la app antes.

    def get_calendar_role(self, calendar_id: int, user_id: int) -> Optional[str]:
        """'owner' | 'admin' | 'member' | None."""
        data = self._get_calendar_access(calendar_id)
        if not data:
            return None
        if data["owner_id"] == user_id:
            return "owner"
        try:
            response = (
                self.supabase.from_("calendar_members")
                .select("role").eq("calendar_id", calendar_id).eq("user_id", user_id).execute()
            )
            if response.data:
                return response.data[0]["role"]
        except Exception as e:
            logger.warning(f"calendar_members no disponible ({e}); se asume invitado")
        #Sin fila de rol, basta con estar en el array de siempre
        if user_id in (data.get("shared_with") or []):
            return "member"
        return None

    def user_can_share_calendar(self, calendar_id: int, user_id: int) -> bool:
        return self.get_calendar_role(calendar_id, user_id) in ("owner", "admin")

    def get_calendar_members(self, calendar_id: int) -> List[dict]:
        """Todos los que tienen acceso, con su rol y su nombre."""
        data = self._get_calendar_access(calendar_id)
        if not data:
            return []

        roles: dict[int, str] = {}
        try:
            response = (
                self.supabase.from_("calendar_members")
                .select("user_id, role").eq("calendar_id", calendar_id).execute()
            )
            roles = {r["user_id"]: r["role"] for r in (response.data or [])}
        except Exception:
            roles = {}

        ids = [data["owner_id"]] + [
            uid for uid in (data.get("shared_with") or []) if uid != data["owner_id"]
        ]
        for uid in roles:
            if uid not in ids:
                ids.append(uid)

        salida = []
        for uid in ids:
            user = self.get_user_by_id(uid)
            if not user:
                continue
            rol = "owner" if uid == data["owner_id"] else roles.get(uid, "member")
            salida.append({"user_id": uid, "username": user.username, "role": rol})
        #Propietario primero, luego admins, luego invitados
        orden = {"owner": 0, "admin": 1, "member": 2}
        salida.sort(key=lambda m: (orden.get(m["role"], 3), m["username"].lower()))
        return salida

    def set_member_role(self, calendar_id: int, target_user_id: int, role: str, requesting_user_id: int) -> bool:
        """Cambiar roles es cosa exclusiva del propietario."""
        try:
            if role not in ("admin", "member"):
                return False
            if self.get_calendar_role(calendar_id, requesting_user_id) != "owner":
                logger.warning(f"⛔ user_id={requesting_user_id} no es propietario del calendario {calendar_id}")
                return False
            if target_user_id == requesting_user_id:
                return False
            existing = (
                self.supabase.from_("calendar_members")
                .select("id").eq("calendar_id", calendar_id).eq("user_id", target_user_id).execute()
            )
            if existing.data:
                self.supabase.table("calendar_members").update({"role": role}).eq("id", existing.data[0]["id"]).execute()
            else:
                self.supabase.table("calendar_members").insert(
                    {"calendar_id": calendar_id, "user_id": target_user_id, "role": role}
                ).execute()
            return True
        except Exception as e:
            logger.error(f"Error cambiando el rol: {e}")
            return False

    def remove_calendar_member(self, calendar_id: int, target_user_id: int, requesting_user_id: int) -> bool:
        """Expulsar a alguien: propietario o admin. Al propietario no se le toca."""
        try:
            rol_solicitante = self.get_calendar_role(calendar_id, requesting_user_id)
            if rol_solicitante not in ("owner", "admin"):
                return False
            data = self._get_calendar_access(calendar_id)
            if not data or data["owner_id"] == target_user_id:
                return False
            #Un admin no puede expulsar a otro admin; solo el propietario
            if rol_solicitante == "admin" and self.get_calendar_role(calendar_id, target_user_id) == "admin":
                return False

            compartidos = [uid for uid in (data.get("shared_with") or []) if uid != target_user_id]
            self.supabase.table("calendars").update({"shared_with": compartidos}).eq("id", calendar_id).execute()
            try:
                (
                    self.supabase.table("calendar_members").delete()
                    .eq("calendar_id", calendar_id).eq("user_id", target_user_id).execute()
                )
            except Exception:
                pass
            return True
        except Exception as e:
            logger.error(f"Error expulsando del calendario: {e}")
            return False

    # ---------------------- Amigos ----------------------

    def get_friendships(self, user_id: int) -> dict:
        """Amigos aceptados, solicitudes recibidas y enviadas.

        Si la tabla no existe todavía (migración 011 sin aplicar) devuelve todo
        vacío en vez de reventar: la pestaña sale sin contenido y ya está.
        """
        vacio = {"friends": [], "incoming": [], "outgoing": []}
        try:
            response = (
                self.supabase.from_("friendships")
                .select("id, requester_id, addressee_id, status")
                .or_(f"requester_id.eq.{user_id},addressee_id.eq.{user_id}")
                .execute()
            )
            rows = response.data or []
            if not rows:
                return vacio

            #Un solo viaje para resolver todos los nombres
            otros = {r["requester_id"] if r["addressee_id"] == user_id else r["addressee_id"] for r in rows}
            nombres = {}
            if otros:
                users = self.supabase.from_("user").select("id, username").in_("id", list(otros)).execute()
                nombres = {u["id"]: u["username"] for u in (users.data or [])}

            salida = {"friends": [], "incoming": [], "outgoing": []}
            for r in rows:
                soy_yo_el_que_pide = r["requester_id"] == user_id
                otro_id = r["addressee_id"] if soy_yo_el_que_pide else r["requester_id"]
                entrada = {
                    "id": r["id"],
                    "user_id": otro_id,
                    "username": nombres.get(otro_id, "?"),
                }
                if r["status"] == "accepted":
                    salida["friends"].append(entrada)
                elif soy_yo_el_que_pide:
                    salida["outgoing"].append(entrada)
                else:
                    salida["incoming"].append(entrada)
            return salida
        except Exception as e:
            logger.warning(f"No se pudieron leer las amistades ({e})")
            return vacio

    def send_friend_request(self, user_id: int, username: str) -> tuple[bool, str]:
        try:
            destino = self.get_user_by_username(username)
            if not destino:
                return False, "No existe ese usuario"
            if destino["id"] == user_id:
                return False, "No puedes enviarte una solicitud a ti mismo"

            a, b = min(user_id, destino["id"]), max(user_id, destino["id"])
            existe = (
                self.supabase.from_("friendships")
                .select("id, status")
                .or_(f"requester_id.eq.{a},requester_id.eq.{b}")
                .execute()
            )
            for r in (existe.data or []):
                pass  # el índice único hace el trabajo fino; aquí solo evitamos lo evidente

            data = {"requester_id": user_id, "addressee_id": destino["id"], "status": "pending"}
            response = self.supabase.table("friendships").insert(data).execute()
            if response.data:
                return True, f"Solicitud enviada a {destino['username']}"
            return False, "No se pudo enviar la solicitud"
        except Exception as e:
            if "duplicate" in str(e).lower() or "23505" in str(e):
                return False, "Ya hay una solicitud o amistad con esa persona"
            logger.error(f"Error enviando solicitud: {e}")
            return False, "No se pudo enviar. ¿Está aplicada la migración 011_friends.sql?"

    def respond_friend_request(self, friendship_id: int, user_id: int, accept: bool) -> bool:
        """Solo el destinatario puede aceptar o rechazar."""
        try:
            row = (
                self.supabase.from_("friendships")
                .select("addressee_id").eq("id", friendship_id).execute()
            )
            if not row.data or row.data[0]["addressee_id"] != user_id:
                logger.warning(f"⛔ user_id={user_id} no puede responder a la solicitud {friendship_id}")
                return False
            if accept:
                resp = self.supabase.table("friendships").update({"status": "accepted"}).eq("id", friendship_id).execute()
            else:
                resp = self.supabase.table("friendships").delete().eq("id", friendship_id).execute()
            return bool(resp.data)
        except Exception as e:
            logger.error(f"Error respondiendo solicitud: {e}")
            return False

    def remove_friendship(self, friendship_id: int, user_id: int) -> bool:
        """Cualquiera de los dos puede deshacer la amistad."""
        try:
            row = (
                self.supabase.from_("friendships")
                .select("requester_id, addressee_id").eq("id", friendship_id).execute()
            )
            if not row.data:
                return False
            r = row.data[0]
            if user_id not in (r["requester_id"], r["addressee_id"]):
                logger.warning(f"⛔ user_id={user_id} no pertenece a la amistad {friendship_id}")
                return False
            return bool(self.supabase.table("friendships").delete().eq("id", friendship_id).execute().data)
        except Exception as e:
            logger.error(f"Error eliminando amistad: {e}")
            return False

    def are_friends(self, user_id: int, other_id: int) -> bool:
        try:
            response = (
                self.supabase.from_("friendships")
                .select("id").eq("status", "accepted")
                .or_(
                    f"and(requester_id.eq.{user_id},addressee_id.eq.{other_id}),"
                    f"and(requester_id.eq.{other_id},addressee_id.eq.{user_id})"
                )
                .execute()
            )
            return bool(response.data)
        except Exception:
            return False

    def get_notify_preference(self, user_id: int) -> bool:
        try:
            response = self.supabase.from_("user").select("notify_calendar_changes").eq("id", user_id).execute()
            if not response.data:
                return True
            return bool(response.data[0].get("notify_calendar_changes", True))
        except Exception:
            return True   #Sin la columna, se avisa como siempre

    def set_notify_preference(self, user_id: int, value: bool) -> bool:
        try:
            resp = (
                self.supabase.table("user")
                .update({"notify_calendar_changes": value}).eq("id", user_id).execute()
            )
            return bool(resp.data)
        except Exception as e:
            logger.warning(f"No se pudo guardar la preferencia de avisos: {e}")
            return False

    # ---------------------- Chat entre amigos ----------------------

    MESSAGE_MAX_LEN = 1000
    #Cuántos mensajes se traen de una conversación. Es un chat de andar por
    #casa: con el último centenar sobra para no perder el hilo.
    CONVERSATION_LIMIT = 120
    #Mensajes que se miran para armar la lista de conversaciones (el "quién te
    #ha escrito lo último"). Con pocos amigos, esto los cubre a todos.
    OVERVIEW_LIMIT = 300

    def _local(self, iso: Optional[str]) -> Optional[datetime]:
        """timestamptz de Postgres → hora de Madrid, que es la que ve el usuario."""
        if not iso:
            return None
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            return dt.astimezone(pytz.timezone("Europe/Madrid"))
        except Exception:
            return None

    def _day_label(self, dt: Optional[datetime]) -> str:
        """'Hoy', 'Ayer' o '3 mar' — el separador entre días de la conversación."""
        if not dt:
            return ""
        hoy = datetime.now(pytz.timezone("Europe/Madrid")).date()
        dias = (hoy - dt.date()).days
        if dias <= 0:
            return "Hoy"
        if dias == 1:
            return "Ayer"
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        etiqueta = f"{dt.day} {meses[dt.month - 1]}"
        return etiqueta if dias < 365 else f"{etiqueta} {dt.year}"

    def send_message(self, sender_id: int, recipient_id: int, body: str) -> tuple[bool, str, bool]:
        """Guarda un mensaje. Devuelve (ok, error, avisar_al_movil).

        Lo de `avisar` es para no convertir el push en una ametralladora: si el
        otro **ya tiene sin leer** algo mío, la notificación anterior sigue en su
        pantalla y no hace falta otra. El aviso salta cuando la conversación
        pasa de "todo leído" a "tienes algo nuevo", que es cuando aporta.
        """
        cuerpo = (body or "").strip()
        if not cuerpo:
            return False, "El mensaje está vacío", False
        if len(cuerpo) > self.MESSAGE_MAX_LEN:
            return False, f"Máximo {self.MESSAGE_MAX_LEN} caracteres", False
        if sender_id == recipient_id:
            return False, "No puedes escribirte a ti mismo", False
        #Escribir a alguien que no es amigo tuyo, ni con la petición a mano
        if not self.are_friends(sender_id, recipient_id):
            return False, "Solo puedes escribir a tus amigos", False
        try:
            pendientes = (
                self.supabase.from_("messages")
                .select("id")
                .eq("sender_id", sender_id).eq("recipient_id", recipient_id)
                .is_("read_at", None).limit(1).execute()
            )
            avisar = not (pendientes.data or [])
            resp = (
                self.supabase.table("messages")
                .insert({"sender_id": sender_id, "recipient_id": recipient_id, "body": cuerpo})
                .execute()
            )
            if not resp.data:
                return False, "No se pudo enviar el mensaje", False
            return True, "", avisar
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return False, "No se pudo enviar. ¿Está aplicada la migración 016_chat.sql?", False

    def get_conversation(self, user_id: int, other_id: int) -> List[dict]:
        """La conversación entre dos personas, ya masticada para pintarla.

        Sin la tabla (migración 016 sin aplicar) devuelve vacío en vez de
        reventar, igual que hacen los amigos con la 011.
        """
        try:
            response = (
                self.supabase.from_("messages")
                .select("id, sender_id, recipient_id, body, created_at, read_at")
                .or_(
                    f"and(sender_id.eq.{user_id},recipient_id.eq.{other_id}),"
                    f"and(sender_id.eq.{other_id},recipient_id.eq.{user_id})"
                )
                #Los últimos N: se piden del revés y se le da la vuelta aquí
                .order("id", desc=True).limit(self.CONVERSATION_LIMIT).execute()
            )
            filas = list(reversed(response.data or []))
        except Exception as e:
            logger.warning(f"No se pudo leer la conversación ({e})")
            return []

        salida: List[dict] = []
        dia_anterior = ""
        for fila in filas:
            momento = self._local(fila.get("created_at"))
            dia = self._day_label(momento)
            salida.append({
                "id": fila["id"],
                "mine": fila["sender_id"] == user_id,
                "body": fila.get("body", ""),
                "time_label": momento.strftime("%H:%M") if momento else "",
                "day_label": dia,
                #Solo el primer mensaje de cada día lleva separador
                "show_day": dia != dia_anterior,
                "read": bool(fila.get("read_at")),
            })
            dia_anterior = dia
        return salida

    def mark_messages_read(self, user_id: int, other_id: int) -> bool:
        """Marca como leído lo que `other_id` me ha escrito. Solo el destinatario."""
        try:
            self.supabase.table("messages").update(
                {"read_at": datetime.now(pytz.utc).isoformat()}
            ).eq("recipient_id", user_id).eq("sender_id", other_id).is_("read_at", None).execute()
            return True
        except Exception as e:
            logger.warning(f"No se pudieron marcar los mensajes como leídos ({e})")
            return False

    def get_chat_overview(self, user_id: int) -> dict:
        """Último mensaje y sin-leer con cada persona, para la lista de chats.

        Devuelve `{"last": {otro_id: {...}}, "unread": {otro_id: n}, "total": n}`.
        `available` dice si la tabla existe: sin la migración 016 el chat se ve
        pero no puede guardar nada, y la pestaña lo avisa en vez de callarse.
        """
        vacio = {"last": {}, "unread": {}, "total": 0, "available": False}
        try:
            recientes = (
                self.supabase.from_("messages")
                .select("id, sender_id, recipient_id, body, created_at")
                .or_(f"sender_id.eq.{user_id},recipient_id.eq.{user_id}")
                .order("id", desc=True).limit(self.OVERVIEW_LIMIT).execute()
            )
            sin_leer = (
                self.supabase.from_("messages")
                .select("sender_id")
                .eq("recipient_id", user_id).is_("read_at", None).execute()
            )
        except Exception as e:
            logger.warning(f"No se pudo leer el resumen del chat ({e})")
            return vacio

        ultimos: dict = {}
        #Vienen del más nuevo al más viejo: el primero que aparece de cada
        #interlocutor es justo el último mensaje con esa persona
        for fila in (recientes.data or []):
            mio = fila["sender_id"] == user_id
            otro = fila["recipient_id"] if mio else fila["sender_id"]
            if otro in ultimos:
                continue
            momento = self._local(fila.get("created_at"))
            ultimos[otro] = {
                "id": fila["id"],
                "body": fila.get("body", ""),
                "mine": mio,
                "day_label": self._day_label(momento),
                "time_label": momento.strftime("%H:%M") if momento else "",
            }

        pendientes: dict = {}
        for fila in (sin_leer.data or []):
            pendientes[fila["sender_id"]] = pendientes.get(fila["sender_id"], 0) + 1

        return {
            "last": ultimos,
            "unread": pendientes,
            "total": sum(pendientes.values()),
            "available": True,
        }

    def get_unread_count(self, user_id: int) -> int:
        """Solo el número, para la chincheta de la barra de navegación."""
        try:
            response = (
                self.supabase.from_("messages")
                .select("id", count="exact")
                .eq("recipient_id", user_id).is_("read_at", None).limit(1).execute()
            )
            if response.count is not None:
                return int(response.count)
            return len(response.data or [])
        except Exception:
            return 0

    # ---------------------- Categorías de plato ----------------------

    DEFAULT_MEAL_CATEGORIES = [
        {"key": k, "label": v["label"], "color": v["color"], "icon": v["icon"]}
        for k, v in {
            "arroz": {"label": "Arroz", "color": "#f59e0b", "icon": "wheat"},
            "pasta": {"label": "Pasta", "color": "#fbbf24", "icon": "wheat"},
            "patata": {"label": "Patata", "color": "#d97706", "icon": "cookie"},
            "legumbre": {"label": "Legumbre", "color": "#a16207", "icon": "bean"},
            "carne": {"label": "Carne", "color": "#ef4444", "icon": "beef"},
            "pescado": {"label": "Pescado", "color": "#38bdf8", "icon": "fish"},
            "huevo": {"label": "Huevo", "color": "#eab308", "icon": "egg"},
            "verdura": {"label": "Verdura", "color": "#22c55e", "icon": "carrot"},
            "ensalada": {"label": "Ensalada", "color": "#34d399", "icon": "salad"},
            "sandwich": {"label": "Bocadillo", "color": "#f472b6", "icon": "sandwich"},
            "otros": {"label": "Otros", "color": "#94a3b8", "icon": "utensils"},
        }.items()
    ]

    def get_meal_categories(self) -> List[dict]:
        try:
            response = (
                self.supabase.from_("meal_categories")
                .select("key, label, color, icon, position")
                .order("position").order("label").execute()
            )
            rows = response.data or []
            return [
                {"key": r["key"], "label": r["label"], "color": r["color"], "icon": r["icon"]}
                for r in rows
            ] or list(self.DEFAULT_MEAL_CATEGORIES)
        except Exception as e:
            logger.warning(f"No se pudieron leer las categorías ({e}); usando las de reserva")
            return list(self.DEFAULT_MEAL_CATEGORIES)

    def save_meal_category(self, key: str, label: str, color: str, icon: str) -> bool:
        """Crea o actualiza una categoría. `key` vacía = se deriva de la etiqueta."""
        try:
            key = (key or "").strip().lower()
            if not key:
                key = "".join(c for c in label.lower().replace(" ", "_") if c.isalnum() or c == "_")[:24]
            if not key:
                return False
            existing = self.supabase.from_("meal_categories").select("id").ilike("key", key).execute()
            data = {"key": key, "label": label, "color": color, "icon": icon}
            if existing.data:
                self.supabase.table("meal_categories").update(data).eq("id", existing.data[0]["id"]).execute()
                return True
            last = self.supabase.from_("meal_categories").select("position").order("position", desc=True).limit(1).execute()
            data["position"] = (last.data[0]["position"] + 10) if last.data else 10
            return bool(self.supabase.table("meal_categories").insert(data).execute().data)
        except Exception as e:
            logger.error(f"Error guardando categoría: {e}")
            return False

    def delete_meal_category(self, key: str) -> bool:
        """Borra la categoría y manda sus platos a 'otros'."""
        try:
            if key == "otros":
                return False
            self.supabase.table("meals").update({"category": "otros"}).eq("category", key).execute()
            response = self.supabase.table("meal_categories").delete().ilike("key", key).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error eliminando categoría: {e}")
            return False

    # ---------------------- Tipos de entrada de agenda ----------------------

    DEFAULT_TASK_TYPES = [
        {"key": "task", "label": "Tarea", "color": "#eab308", "icon": "square-check", "completable": True},
        {"key": "event", "label": "Evento", "color": "#38bdf8", "icon": "calendar-clock", "completable": False},
        {"key": "note", "label": "Nota", "color": "#a78bfa", "icon": "sticky-note", "completable": False},
    ]

    def get_task_types(self) -> List[dict]:
        try:
            response = (
                self.supabase.from_("task_types")
                .select("key, label, color, icon, completable, position")
                .order("position").order("label").execute()
            )
            rows = response.data or []
            return [
                {"key": r["key"], "label": r["label"], "color": r["color"],
                 "icon": r["icon"], "completable": bool(r["completable"])}
                for r in rows
            ] or list(self.DEFAULT_TASK_TYPES)
        except Exception as e:
            logger.warning(f"No se pudieron leer los tipos de agenda ({e}); usando los de reserva")
            return list(self.DEFAULT_TASK_TYPES)

    def add_task_type(self, label: str, color: str, icon: str, completable: bool) -> bool:
        try:
            #La clave se deriva de la etiqueta: es lo que se guarda en day_items
            key = "".join(c for c in label.lower().replace(" ", "_") if c.isalnum() or c == "_")[:24]
            if not key:
                return False
            existing = self.supabase.from_("task_types").select("id").ilike("key", key).execute()
            if existing.data:
                return False
            last = self.supabase.from_("task_types").select("position").order("position", desc=True).limit(1).execute()
            position = (last.data[0]["position"] + 10) if last.data else 10
            response = self.supabase.table("task_types").insert({
                "key": key, "label": label, "color": color,
                "icon": icon, "completable": completable, "position": position,
            }).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error añadiendo tipo de agenda: {e}")
            return False

    def update_task_type(self, key: str, label: str, color: str, icon: str, completable: bool) -> bool:
        """Edita un tipo de agenda sin tocar su clave.

        La clave es lo que guardan las entradas ya creadas (`day_items.item_type`),
        así que se deja como está: se cambia solo lo que se ve (nombre, color,
        icono y si se puede marcar como hecho).
        """
        try:
            response = (
                self.supabase.table("task_types")
                .update({"label": label, "color": color, "icon": icon, "completable": completable})
                .ilike("key", key)
                .execute()
            )
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error actualizando el tipo de agenda: {e}")
            return False

    def delete_task_type(self, key: str) -> bool:
        """Quita el tipo del desplegable; las entradas que lo usaban no se tocan."""
        try:
            response = self.supabase.table("task_types").delete().ilike("key", key).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error eliminando tipo de agenda: {e}")
            return False

    # ---------------------- Supermercados ----------------------

    #Colores por defecto si la migración 007 no está aplicada
    DEFAULT_SUPERMARKETS = [
        {"name": "Mercadona", "color": "#22c55e"},
        {"name": "Lidl", "color": "#38bdf8"},
        {"name": "Carrefour", "color": "#3b82f6"},
        {"name": "Dia", "color": "#ef4444"},
    ]

    def get_supermarkets(self) -> List[dict]:
        try:
            response = (
                self.supabase.from_("supermarkets")
                .select("name, color, position")
                .order("position")
                .order("name")
                .execute()
            )
            rows = response.data or []
            return [{"name": r["name"], "color": r["color"]} for r in rows] or list(self.DEFAULT_SUPERMARKETS)
        except Exception as e:
            logger.warning(f"No se pudieron leer los supermercados ({e}); usando los de reserva")
            return list(self.DEFAULT_SUPERMARKETS)

    def add_supermarket(self, name: str, color: str) -> bool:
        try:
            existing = self.supabase.from_("supermarkets").select("id").ilike("name", name).execute()
            if existing.data:
                return False
            last = (
                self.supabase.from_("supermarkets")
                .select("position").order("position", desc=True).limit(1).execute()
            )
            position = (last.data[0]["position"] + 10) if last.data else 10
            response = (
                self.supabase.table("supermarkets")
                .insert({"name": name, "color": color, "position": position})
                .execute()
            )
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error añadiendo supermercado: {e}")
            return False

    def update_supermarket(self, old_name: str, new_name: str, color: str) -> bool:
        """Edita un supermercado: nombre y color.

        El nombre se guarda como texto en los productos de la lista de la compra
        y en el catálogo, así que al renombrarlo hay que arrastrarlo allí: si no,
        corregir "Mercadna" dejaría huérfanos todos los productos que lo tenían.
        """
        try:
            old_name = (old_name or "").strip()
            new_name = (new_name or "").strip()
            if not old_name or not new_name:
                return False

            #Que no choque con otro supermercado distinto
            if old_name.lower() != new_name.lower():
                clash = self.supabase.from_("supermarkets").select("id").ilike("name", new_name).execute()
                if clash.data:
                    return False

            response = (
                self.supabase.table("supermarkets")
                .update({"name": new_name, "color": color})
                .ilike("name", old_name)
                .execute()
            )
            if not response.data:
                return False

            if old_name.lower() != new_name.lower():
                self._rename_supermarket_usages(old_name, new_name)
            return True
        except Exception as e:
            logger.error(f"Error actualizando el supermercado: {e}")
            return False

    def _rename_supermarket_usages(self, old_name: str, new_name: str) -> None:
        """Cambia el nombre del súper allí donde estaba escrito."""
        try:
            lists = self.supabase.from_("shopping_lists").select("id, items").execute()
            for row in (lists.data or []):
                items = row.get("items") or {}
                tocado = False
                for data in items.values():
                    if (data.get("supermarket") or "").strip().lower() == old_name.lower():
                        data["supermarket"] = new_name
                        tocado = True
                if tocado:
                    self.supabase.table("shopping_lists").update({"items": items}).eq("id", row["id"]).execute()
        except Exception as e:
            logger.warning(f"No se pudo renombrar el súper en las listas: {e}")

        try:
            self.supabase.table("products").update({"shop": new_name}).ilike("shop", old_name).execute()
        except Exception as e:
            logger.warning(f"No se pudo renombrar el súper en el catálogo: {e}")

        #Y en los ingredientes de las recetas, que también lo llevan
        try:
            meals = self.supabase.from_("meals").select("id, ingredients").execute()
            for row in (meals.data or []):
                ingredients = row.get("ingredients") or []
                if not any((i or {}).get("shop", "").strip().lower() == old_name.lower() for i in ingredients):
                    continue
                updated = [
                    {**i, "shop": new_name}
                    if (i or {}).get("shop", "").strip().lower() == old_name.lower() else i
                    for i in ingredients
                ]
                self.supabase.table("meals").update({"ingredients": updated}).eq("id", row["id"]).execute()
        except Exception as e:
            logger.warning(f"No se pudo renombrar el súper en las recetas: {e}")

    def update_supermarket_color(self, name: str, color: str) -> bool:
        try:
            response = (
                self.supabase.table("supermarkets").update({"color": color}).ilike("name", name).execute()
            )
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error cambiando el color del supermercado: {e}")
            return False

    # ---------------------- Catálogo de productos ----------------------
    # Los ingredientes ya no son texto libre: salen de aquí. Si la migración
    # 013 no está aplicada, se devuelve una lista vacía y la app avisa al
    # intentar guardar, igual que con unidades y supermercados.

    #Con el formato de compra (migración 019)
    PRODUCT_FIELDS = "id, name, qty, pack_qty, pack_unit, unit, cat, shop, staple, note"

    #Sin él: los que había entre la 015 y la 019
    PRODUCT_FIELDS_SIN_PACK = "id, name, qty, unit, cat, shop, staple, note"

    #Campos sin `qty`: los que había antes de la migración 015
    PRODUCT_FIELDS_SIN_QTY = "id, name, unit, cat, shop, staple, note"

    @staticmethod
    def _falta_columna(error: Exception, *columnas: str) -> bool:
        """¿El fallo es porque a la tabla le falta alguna de esas columnas?"""
        texto = str(error)
        if "does not exist" not in texto and "schema cache" not in texto:
            return False
        return any(col in texto for col in columnas)

    @classmethod
    def _falta_qty(cls, error: Exception) -> bool:
        """¿El fallo es porque la columna `qty` (migración 015) no está aún?"""
        return cls._falta_columna(error, "qty")

    @classmethod
    def _falta_pack(cls, error: Exception) -> bool:
        """¿Falta el formato de compra (migración 019)?"""
        return cls._falta_columna(error, "pack_qty", "pack_unit")

    @staticmethod
    def _mismo_nombre(a: Optional[str], b: Optional[str]) -> bool:
        """¿Son el mismo nombre? Sin mayúsculas y sin espacios de sobra."""
        return (a or "").strip().lower() == (b or "").strip().lower()

    def _find_product_by_name(self, name: str) -> Optional[dict]:
        """Busca un producto por nombre exacto (ignorando mayúsculas).

        A propósito **no** usa `ilike`: en PostgREST, `%` y `_` dentro del valor
        son comodines. Un producto llamado "Leche 1,5%" hacía que `ilike` casara
        con cualquier "Leche 1,5..." y el alta se rechazaba con un "ya existe"
        que no era verdad. El catálogo son un par de cientos de filas: comparar
        aquí es exacto y no cuesta nada.
        """
        try:
            rows = self.supabase.from_("products").select("id, name").execute().data or []
        except Exception as e:
            logger.warning(f"No se pudo comprobar si el producto ya existe: {e}")
            return None
        return next((r for r in rows if self._mismo_nombre(r.get("name"), name)), None)

    def get_products(self) -> List[dict]:
        #El catálogo tiene que funcionar con las migraciones a medio aplicar: se
        #pide lo mejor y se va bajando de campos si la tabla aún no los tiene
        for campos in (self.PRODUCT_FIELDS, self.PRODUCT_FIELDS_SIN_PACK, self.PRODUCT_FIELDS_SIN_QTY):
            try:
                response = self.supabase.from_("products").select(campos).order("name").execute()
                return response.data or []
            except Exception as e:
                if self._falta_pack(e) or self._falta_qty(e):
                    continue
                logger.warning(f"No se pudo leer el catálogo de productos ({e}); ¿falta la migración 013?")
                return []
        logger.warning("No se pudo leer el catálogo de productos con ningún juego de campos")
        return []

    @staticmethod
    def _sin_columnas(datos: dict, *columnas: str) -> dict:
        """Copia de los datos sin las columnas que la tabla todavía no tiene."""
        return {k: v for k, v in datos.items() if k not in columnas}

    def _write_product(self, datos: dict, product_id: Optional[int] = None):
        """Escribe un producto quitando lo que la tabla aún no admita.

        Con la 019 sin aplicar no hay `pack_qty`/`pack_unit`, y con la 015 sin
        aplicar tampoco `qty`: en vez de fallar, se guarda lo que sí cabe.
        """
        intentos = (
            datos,
            self._sin_columnas(datos, "pack_qty", "pack_unit"),
            self._sin_columnas(datos, "pack_qty", "pack_unit", "qty"),
        )
        ultimo = None
        for intento in intentos:
            try:
                tabla = self.supabase.table("products")
                if product_id is None:
                    return tabla.insert(intento).execute()
                return tabla.update(intento).eq("id", product_id).execute()
            except Exception as e:
                ultimo = e
                if self._falta_pack(e) or self._falta_qty(e):
                    continue
                raise
        raise ultimo

    def add_product(
        self,
        name: str,
        qty: float = 1,
        unit: str = "ud",
        cat: str = "otros",
        shop: str = "",
        staple: bool = False,
        note: str = "",
        pack_qty: float = 0,
        pack_unit: str = "",
    ) -> Optional[dict]:
        """Da de alta un producto. `None` si ya existe o si falla la escritura."""
        try:
            if self._find_product_by_name(name):
                return None
            datos = {
                "name": name, "qty": qty, "unit": unit, "cat": cat,
                "shop": shop, "staple": staple, "note": note,
                "pack_qty": pack_qty, "pack_unit": pack_unit,
            }
            response = self._write_product(datos)
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error añadiendo producto: {e}")
            return None

    def update_product(
        self,
        product_id: int,
        name: str,
        qty: float,
        unit: str,
        cat: str,
        shop: str,
        staple: bool,
        note: str,
        rename_usages: bool = True,
        pack_qty: float = 0,
        pack_unit: str = "",
    ) -> Optional[dict]:
        """Edita un producto del catálogo.

        Si cambia el nombre, arrastra el cambio a las recetas y a las listas de
        la compra que lo usaban: si no, corregir una falta de ortografía dejaría
        huérfanos los ingredientes que ya estaban escritos con el nombre viejo.
        """
        try:
            current = self.supabase.from_("products").select("name").eq("id", product_id).execute()
            if not current.data:
                return None
            old_name = current.data[0]["name"]

            clash = self._find_product_by_name(name)
            if clash and clash["id"] != product_id:
                return None

            datos = {
                "name": name, "qty": qty, "unit": unit, "cat": cat,
                "shop": shop, "staple": staple, "note": note,
                "pack_qty": pack_qty, "pack_unit": pack_unit,
            }
            response = self._write_product(datos, product_id)
            if rename_usages and old_name != name:
                self._rename_product_usages(old_name, name)
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error actualizando producto (id={product_id}): {e}")
            return None

    def _rename_product_usages(self, old_name: str, new_name: str) -> None:
        """Cambia el nombre del ingrediente allí donde ya estaba escrito."""
        try:
            meals = self.supabase.from_("meals").select("id, ingredients").execute()
            for row in (meals.data or []):
                ingredients = row.get("ingredients") or []
                if not any((i or {}).get("name") == old_name for i in ingredients):
                    continue
                updated = [
                    {**i, "name": new_name} if (i or {}).get("name") == old_name else i
                    for i in ingredients
                ]
                self.supabase.table("meals").update({"ingredients": updated}).eq("id", row["id"]).execute()
        except Exception as e:
            logger.warning(f"No se pudo renombrar el ingrediente en las recetas: {e}")

        try:
            lists = self.supabase.from_("shopping_lists").select("id, items").execute()
            for row in (lists.data or []):
                items = row.get("items") or {}
                if old_name not in items:
                    continue
                #Si ya existía un producto con el nombre nuevo, se suman
                entry = dict(items.pop(old_name))
                if new_name in items:
                    entry["quantity"] = round(
                        float(items[new_name].get("quantity", 0)) + float(entry.get("quantity", 0)), 2
                    )
                items[new_name] = entry
                self.supabase.table("shopping_lists").update({"items": items}).eq("id", row["id"]).execute()
        except Exception as e:
            logger.warning(f"No se pudo renombrar el producto en las listas de la compra: {e}")

    def delete_product(self, product_id: int) -> bool:
        """Quita el producto del catálogo.

        Las recetas y listas que ya lo usaban no se tocan: allí el nombre es
        texto y se sigue viendo igual, solo deja de poder elegirse de nuevo.
        """
        try:
            response = self.supabase.table("products").delete().eq("id", product_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error eliminando producto: {e}")
            return False

    def delete_supermarket(self, name: str) -> bool:
        """Quita el supermercado del desplegable.

        Los productos que lo tuvieran asignado conservan el texto: solo dejan
        de tener color asociado.
        """
        try:
            response = self.supabase.table("supermarkets").delete().ilike("name", name).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error eliminando supermercado: {e}")
            return False

    # ---------------------- MÉTODOS PARA LISTA DE LA COMPRA ----------------------

    def get_shopping_lists(self, user_id: int) -> list:
        """Devuelve todas las listas donde aparece el user_id."""
        try:
            response = self.supabase.table("shopping_lists")\
                .select("*")\
                .filter("user_ids", "cs", f"{{{user_id}}}")\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error get_shopping_lists: {e}")
            return []

    def add_or_update_item(
        self,
        list_id: int,
        item_name: str,
        quantity: float,
        supermarket: str,
        user_id: int,
        unit: str = "ud",
        cat: str = "otros",
        staple: bool = False,
        note: str = "",
    ) -> bool:
        """Añade o actualiza un producto dentro del JSON 'items'."""
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False
            # 1. Obtener los items actuales
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return False
            items = res.data[0]["items"]
            # 2. Modificar el diccionario. Si el producto ya existía y lo puso el
            #    menú semanal, se conserva de dónde venía: reescribirlo a mano no
            #    debería borrar esa información.
            previous = items.get(item_name) or {}
            items[item_name] = {
                "quantity": quantity,
                "supermarket": supermarket,
                "bought": False,
                "unit": unit,
                "cat": cat,
                "staple": staple,
                "note": note,
                "auto": False,
                "source": previous.get("source", ""),
                #Vuelve a estar pendiente: lo que ya se llevó a la despensa se
                #queda allí, y esta nueva compra volverá a sumar cuando se marque
                "stocked": False,
            }
            # 3. Guardar
            update_res = self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            return len(update_res.data) > 0
        except Exception as e:
            logger.error(f"Error add_or_update_item: {e}")
            return False

    def add_recipe_items(
        self, list_id: int, generated: dict, user_id: int
    ) -> tuple[bool, int, int, List[str]]:
        """Suma a la lista los ingredientes de UNA receta suelta.

        Es lo que hace falta cuando cocinas algo fuera del menú semanal (una
        tarta para llevar al trabajo, una cena para invitados): eliges la
        comida, dices para cuánta gente y sus ingredientes caen en la lista.

        Dos diferencias importantes con el volcado del menú semanal:

        - **No se marcan como `auto`.** Un producto `auto` es de la semana
          planificada y el generador lo rehace o lo quita al regenerar; esto es
          un añadido puntual y tiene que sobrevivir a eso, igual que lo que
          añades a mano.
        - **Se suma, no se sustituye.** Si ya tenías 300 gr de harina, pedir
          una receta que lleva 200 más te deja 500, no 200.

        Cuando las unidades no se pueden mezclar (2 latas + 300 gr), no se
        inventa nada: se deja el producto como estaba y se devuelve su nombre
        para poder avisar.

        Devuelve `(éxito, añadidos, sumados, conflictos)`.
        """
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False, 0, 0, []
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return False, 0, 0, []

            items = res.data[0]["items"] or {}
            añadidos = sumados = 0
            conflictos: List[str] = []

            for name, data in generated.items():
                nueva_qty = float(data.get("quantity") or 0)
                nueva_unidad = data.get("unit") or "ud"
                origen = data.get("source") or ""
                actual = items.get(name)

                if not actual:
                    items[name] = {
                        "quantity": nueva_qty,
                        "supermarket": data.get("shop") or "",
                        "bought": False,
                        "unit": nueva_unidad,
                        "cat": data.get("cat") or "otros",
                        "staple": bool(data.get("staple", False)),
                        "note": data.get("note") or "",
                        "auto": False,
                        "source": origen,
                        "stocked": False,
                    }
                    añadidos += 1
                    continue

                convertida = convert_qty(nueva_qty, nueva_unidad, actual.get("unit") or "ud")
                if convertida is None:
                    conflictos.append(name)
                    continue

                actual["quantity"] = round(float(actual.get("quantity") or 0) + convertida, 3)
                #Si ya estaba comprado y ahora hace falta más, vuelve a pendiente
                actual["bought"] = False
                #Lo ya comprado se queda en la despensa; esta compra suma aparte
                actual["stocked"] = False
                #Deja de ser "de la semana": que el menú semanal no se lo lleve
                actual["auto"] = False
                previo = actual.get("source") or ""
                if origen and origen not in previo:
                    actual["source"] = f"{previo}, {origen}" if previo else origen
                sumados += 1

            update_res = (
                self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            )
            if not update_res.data:
                return False, 0, 0, []
            return True, añadidos, sumados, conflictos
        except Exception as e:
            logger.error(f"Error añadiendo los ingredientes de una receta: {e}")
            return False, 0, 0, []

    def update_item_details(
        self,
        list_id: int,
        old_name: str,
        new_name: str,
        quantity: float,
        unit: str,
        supermarket: str,
        user_id: int,
        cat: Optional[str] = None,
        staple: Optional[bool] = None,
        note: Optional[str] = None,
        bought: Optional[bool] = None,
        auto: Optional[bool] = None,
        source: Optional[str] = None,
    ) -> bool:
        """Edita un producto ya existente.

        Se puede tocar **cualquiera** de sus campos: nombre, cantidad, unidad,
        supermercado, sección, básico de despensa, nota, si ya está en el carro,
        de qué recetas viene y si el menú semanal puede rehacerlo. Lo que llegue
        como `None` se deja como estaba.
        """
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return False
            items = res.data[0]["items"]
            if old_name not in items:
                return False
            #Renombrar a un producto que ya existe fusionaría dos filas sin avisar
            if new_name != old_name and new_name in items:
                return False

            entry = dict(items.pop(old_name))
            #Copia de cómo estaba: es lo que la despensa tiene sumado ahora
            original = dict(entry)
            entry.update({"quantity": quantity, "unit": unit, "supermarket": supermarket})
            #Al renombrarlo deja de ser "el producto que puso el menú": se olvida
            #de qué semana venía, o la próxima generación lo recalcularía con el
            #nombre viejo y aparecería la fila duplicada
            if new_name != old_name:
                entry.pop("gen", None)
                entry.pop("gen_of", None)
            if cat:
                entry["cat"] = cat
            #Los booleanos y los textos se comparan contra `None` a propósito:
            #`False` y `""` son valores válidos que hay que poder guardar
            if staple is not None:
                entry["staple"] = bool(staple)
            if note is not None:
                entry["note"] = note
            if bought is not None:
                entry["bought"] = bool(bought)
            if auto is not None:
                entry["auto"] = bool(auto)
            if source is not None:
                entry["source"] = source

            #La despensa tiene que cuadrar con lo que se marcó como comprado: si
            #aquí cambia el "en el carro", la cantidad, la unidad o el nombre, se
            #retira del stock lo que había entrado y se vuelve a meter lo nuevo.
            estaba = bool(original.get("stocked", False))
            ahora = bool(entry.get("bought", False))
            cambia = (
                estaba != ahora
                or old_name != new_name
                or float(original.get("quantity", 0) or 0) != float(quantity)
                or (original.get("unit") or "ud") != unit
            )
            if cambia and (estaba or ahora):
                quitar = [self._stock_payload(old_name, original)] if estaba else []
                poner = [self._stock_payload(new_name, entry)] if ahora else []
                if self._apply_stock(user_id, poner, quitar):
                    entry["stocked"] = ahora

            items[new_name] = entry
            update_res = self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            return len(update_res.data) > 0
        except Exception as e:
            logger.error(f"Error update_item_details: {e}")
            return False

    def clear_bought_items(self, list_id: int, user_id: int) -> int:
        """Elimina de la lista todo lo que ya esté marcado como comprado."""
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return 0
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return 0
            items = res.data[0]["items"]
            remaining = {n: d for n, d in items.items() if not d.get("bought", False)}
            removed = len(items) - len(remaining)
            if removed:
                self.supabase.table("shopping_lists").update({"items": remaining}).eq("id", list_id).execute()
            return removed
        except Exception as e:
            logger.error(f"Error clear_bought_items: {e}")
            return 0

    def clear_all_items(self, list_id: int, user_id: int) -> int:
        """Vacía la lista entera. Devuelve cuántos productos había."""
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return 0
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return 0
            count = len(res.data[0]["items"] or {})
            if count:
                self.supabase.table("shopping_lists").update({"items": {}}).eq("id", list_id).execute()
            return count
        except Exception as e:
            logger.error(f"Error clear_all_items: {e}")
            return 0

    def set_all_bought(self, list_id: int, user_id: int, bought: bool) -> int:
        """Marca (o desmarca) todos los productos de golpe."""
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return 0
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return 0
            items = res.data[0]["items"] or {}
            changed = len([1 for d in items.values() if d.get("bought", False) != bought])

            #Todo lo que cambia de estado entra o sale de la despensa de una vez:
            #una sola escritura en vez de una por producto
            mueve = [
                self._stock_payload(n, d)
                for n, d in items.items()
                if d.get("bought", False) != bought and bool(d.get("stocked", False)) != bought
            ]
            movido = self._apply_stock(
                user_id, mueve if bought else [], [] if bought else mueve
            )

            for name, data in items.items():
                if movido and data.get("bought", False) != bought and bool(data.get("stocked", False)) != bought:
                    data["stocked"] = bought
                data["bought"] = bought
            if changed:
                self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            return changed
        except Exception as e:
            logger.error(f"Error set_all_bought: {e}")
            return 0

    def apply_generated_items(
        self, list_id: int, generated: dict, mode: str, user_id: int, week: str = ""
    ) -> tuple[bool, int]:
        """Vuelca en la lista los productos calculados por el menú semanal.

        `generated` es {nombre: {quantity, unit, cat, source}}. `week` es el
        lunes de la semana planificada en ISO: es lo que hace que volver a
        generarla sustituya su aporte en vez de sumarlo otra vez.

        - mode="replace": deja esta semana exactamente como la vista previa.
        - mode="merge": pone al día esta semana sin quitar nada de la lista.

        Devuelve (éxito, nº de productos escritos).
        """
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False, 0
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                return False, 0
            items = merge_generated_items(res.data[0]["items"] or {}, generated, mode, week)
            update_res = self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            return bool(update_res.data), len(generated)
        except Exception as e:
            logger.error(f"Error apply_generated_items: {e}")
            return False, 0

# database.py - Dentro de la clase SupabaseAPI

    def toggle_item_bought(self, list_id: int, item_name: str, user_id: int) -> bool:
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            if not res.data:
                logger.warning("Lista no encontrada")
                return False
            items = res.data[0]["items"]
            if item_name not in items:
                logger.warning("Item no existe")
                return False
            # Invertir
            entry = items[item_name]
            comprado = not entry.get("bought", False)
            entry["bought"] = comprado
            # Y llevarlo (o traerlo de vuelta) de la despensa. `stocked` recuerda
            # si esta línea ya está sumada al stock: sin esa marca, marcar y
            # desmarcar dos veces acabaría duplicando la leche en casa.
            if comprado and not entry.get("stocked", False):
                if self._apply_stock(user_id, [self._stock_payload(item_name, entry)], []):
                    entry["stocked"] = True
            elif not comprado and entry.get("stocked", False):
                if self._apply_stock(user_id, [], [self._stock_payload(item_name, entry)]):
                    entry["stocked"] = False
            # Actualizar
            update_res = self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
            if update_res.data:
                logger.info(f"✅ {item_name} ahora está {items[item_name]['bought']}")
                return True
            return False
        except Exception as e:
            logger.error(e)
            return False
        
    def delete_item(self, list_id: int, item_name: str, user_id: int) -> bool:
        """Elimina un producto del JSON."""
        try:
            if not self.user_in_shopping_list(list_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la lista {list_id}")
                return False
            res = self.supabase.table("shopping_lists").select("items").eq("id", list_id).execute()
            items = res.data[0]["items"]
            if item_name in items:
                del items[item_name]
                self.supabase.table("shopping_lists").update({"items": items}).eq("id", list_id).execute()
                return True
            return False
        except Exception:
            return False

    def get_user_by_username(self, username: str):
        """Busca un usuario por su nombre (para compartir)."""
        try:
            res = self.supabase.table("user").select("*").ilike("username", username).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error get_user_by_username: {e}")
            return None

    def share_shopping_list(self, list_id: int, friend_username: str, requesting_user_id: int) -> tuple[bool, str]:
        try:
            if not self.user_in_shopping_list(list_id, requesting_user_id):
                return False, "No perteneces a esta lista de la compra"

            friend = self.get_user_by_username(friend_username)
            if not friend:
                return False, "Usuario no encontrado"

            res = self.supabase.table("shopping_lists").select("user_ids").eq("id", list_id).execute()
            if not res.data:
                return False, "Lista no encontrada"
            current_ids = res.data[0]["user_ids"]
            if friend["id"] in current_ids:
                return False, f"{friend_username} ya tiene acceso a esta lista"

            current_ids.append(friend["id"])
            self.supabase.table("shopping_lists").update({"user_ids": current_ids}).eq("id", list_id).execute()
            return True, f"Lista compartida con {friend_username}"
        except Exception as e:
            return False, str(e)
        


    def create_shopping_list(self, user_ids: list[int]) -> Optional[dict]:
        data = {"user_ids": user_ids, "items": {}}
        response = self.supabase.table("shopping_lists").insert(data).execute()
        return response.data[0] if response.data else None
    

    def get_users_in_shopping_list(self, list_id: int) -> List[User]:
        """Devuelve lista de objetos User que tienen acceso a la lista."""
        try:
            # Obtener la lista
            res = self.supabase.table("shopping_lists").select("user_ids").eq("id", list_id).execute()
            if not res.data:
                return []
            user_ids = res.data[0]["user_ids"]
            users = []
            for uid in user_ids:
                # Usar get_user_by_id existente (devuelve User o None)
                user = self.get_user_by_id(uid)
                if user:
                    users.append(user)
            return users
        except Exception as e:
            logger.error(f"Error get_users_in_shopping_list: {e}")
            return []

    def add_user_to_shopping_list(self, list_id: int, user_id: int) -> bool:
        """Añade un user_id al array user_ids de la lista."""
        try:
            res = self.supabase.table("shopping_lists").select("user_ids").eq("id", list_id).execute()
            if not res.data:
                return False
            current = res.data[0]["user_ids"]
            if user_id in current:
                return False  # ya existe
            current.append(user_id)
            self.supabase.table("shopping_lists").update({"user_ids": current}).eq("id", list_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error add_user_to_shopping_list: {e}")
            return False

    def remove_user_from_shopping_list(self, list_id: int, user_id: int, requesting_user_id: int) -> bool:
        """Elimina user_id del array y crea una nueva lista para ese usuario con los mismos items."""
        try:
            if not self.user_in_shopping_list(list_id, requesting_user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={requesting_user_id} no pertenece a la lista {list_id}")
                return False
            # Obtener datos de la lista original
            res = self.supabase.table("shopping_lists").select("*").eq("id", list_id).execute()
            if not res.data:
                return False
            orig = res.data[0]
            user_ids = orig["user_ids"]
            items = orig["items"]
            if user_id not in user_ids:
                return False
            # 1. Crear nueva lista para el usuario eliminado (con sus mismos items)
            new_list_data = {
                "user_ids": [user_id],
                "items": items
            }
            self.supabase.table("shopping_lists").insert(new_list_data).execute()
            # 2. Eliminar user_id de la lista original
            new_user_ids = [uid for uid in user_ids if uid != user_id]
            self.supabase.table("shopping_lists").update({"user_ids": new_user_ids}).eq("id", list_id).execute()
            # La despensa se queda como esté: se comparte y se deja de compartir
            # desde su propia pantalla
            return True
        except Exception as e:
            logger.error(f"Error remove_user_from_shopping_list: {e}")
            return False
        

    # database.py - dentro de la clase SupabaseAPI

    def merge_and_share_shopping_list(self, user_id: int, friend_username: str) -> tuple[bool, str]:
        """
        1. Obtener la lista del usuario actual (user_id)
        2. Obtener la lista del amigo por nombre
        3. Fusionar los items (los del amigo se añaden a la lista actual)
        4. Añadir el ID del amigo al array user_ids de la lista actual
        5. Eliminar la lista antigua del amigo (para que solo tenga la compartida)
        6. Devolver éxito/mensaje
        """
        try:
            # 1. Buscar al amigo por nombre
            friend = self.get_user_by_username(friend_username)
            if not friend:
                return False, "Usuario no encontrado"
            friend_id = friend["id"]

            # 2. Obtener la lista actual del usuario (asumimos que tiene al menos una)
            current_lists = self.get_shopping_lists(user_id)
            if not current_lists:
                return False, "No tienes una lista activa"
            current_list = current_lists[0]  # primera lista
            current_list_id = current_list["id"]
            current_items = current_list["items"]

            # 3. Obtener la lista del amigo (si existe)
            friend_lists = self.get_shopping_lists(friend_id)
            if friend_lists:
                friend_list = friend_lists[0]
                friend_items = friend_list["items"]

                # 4. Fusionar items: los del amigo se añaden a current_items
                #    Si un item ya existe, se suma la cantidad (o se puede mantener el del dueño)
                for name, data in friend_items.items():
                    if name in current_items:
                        # Sumar cantidades (por ejemplo)
                        current_items[name]["quantity"] = current_items[name].get("quantity", 1) + data.get("quantity", 1)
                        # El supermercado se mantiene del dueño (opcional)
                        # El estado 'bought' se mantiene como False si alguno está sin comprar
                        current_items[name]["bought"] = current_items[name].get("bought", False) and data.get("bought", False)
                    else:
                        # Añadir nuevo item
                        current_items[name] = {
                            "quantity": data.get("quantity", 1),
                            "supermarket": data.get("supermarket", ""),
                            "bought": data.get("bought", False)
                        }

                # 5. Actualizar la lista actual con los items fusionados
                self.supabase.table("shopping_lists").update({"items": current_items}).eq("id", current_list_id).execute()

                # 6. Eliminar la lista antigua del amigo
                self.supabase.table("shopping_lists").delete().eq("id", friend_list["id"]).execute()
            else:
                # El amigo no tiene lista propia (caso raro), solo le añadimos a la actual
                pass

            # 7. Añadir el ID del amigo al array user_ids de la lista actual
            res = self.supabase.table("shopping_lists").select("user_ids").eq("id", current_list_id).execute()
            user_ids = res.data[0]["user_ids"]
            if friend_id not in user_ids:
                user_ids.append(friend_id)
                self.supabase.table("shopping_lists").update({"user_ids": user_ids}).eq("id", current_list_id).execute()

            #La despensa NO se toca aquí: es una lista aparte y se comparte por
            #su cuenta, desde su propia pantalla

            return True, f"Lista fusionada y compartida con {friend_username}"
        except Exception as e:
            logger.error(f"Error en merge_and_share: {e}")
            return False, str(e)

    # ---------------------- Despensa (el stock de casa) ----------------------
    # Tiene la misma forma que la lista de la compra —`user_ids` + un JSON de
    # productos— y por el mismo motivo: una casa, una despensa. Los miembros se
    # mantienen emparejados con los de la lista, así que compartir la compra es
    # compartir el stock.
    #
    # Si la migración 018 no está aplicada, todo esto devuelve vacío y la app
    # sigue funcionando: la despensa avisa de que falta y la lista de la compra
    # deja de sumar stock, pero nada se rompe.

    #Sin la migración 018 aplicada, cada intento son viajes a Supabase que
    #siempre van a fallar — y uno de ellos está en medio de marcar un producto
    #como comprado, que tiene que ser instantáneo en mitad del súper. Al primer
    #"esa tabla no existe" se deja de preguntar durante un rato, y pasado ese
    #rato se vuelve a probar: así se entera solo de que ya está aplicada, sin
    #tener que reiniciar la app.
    _pantry_off_until: float = 0.0
    PANTRY_RETRY_SECONDS = 300

    @staticmethod
    def _falta_despensa(error: Exception) -> bool:
        texto = str(error).lower()
        return "pantries" in texto and ("does not exist" in texto or "schema cache" in texto)

    def _pantry_ready(self) -> bool:
        return time.monotonic() >= type(self)._pantry_off_until

    def _pantry_missing(self, error: Exception) -> None:
        """Apunta que la tabla no está, para no volver a preguntar en un rato."""
        if self._falta_despensa(error):
            type(self)._pantry_off_until = time.monotonic() + self.PANTRY_RETRY_SECONDS
            logger.warning("La despensa no está disponible: falta la migración 018_pantry.sql")
        else:
            logger.warning(f"No se pudo usar la despensa: {error}")

    def get_pantry(self, user_id: int) -> Optional[dict]:
        """La despensa del usuario. `None` si no tiene (no la crea)."""
        if not self._pantry_ready():
            return None
        try:
            res = (
                self.supabase.table("pantries")
                .select("*")
                .filter("user_ids", "cs", f"{{{user_id}}}")
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            self._pantry_missing(e)
            return None

    def get_or_create_pantry(self, user_id: int) -> Optional[dict]:
        """La despensa del usuario, creándola si hace falta.

        Nace **solo suya**: la despensa es una lista independiente de la de la
        compra y se comparte aparte, con quien tú digas (`merge_and_share_pantry`).
        """
        if not self._pantry_ready():
            return None
        try:
            mine = self.get_pantry(user_id)
            if mine:
                return mine
            res = self.supabase.table("pantries").insert({"user_ids": [user_id], "items": {}}).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            self._pantry_missing(e)
            return None

    def user_in_pantry(self, pantry_id: int, user_id: int) -> bool:
        """True si el usuario forma parte de la despensa."""
        try:
            res = self.supabase.from_("pantries").select("user_ids").eq("id", pantry_id).execute()
            if not res.data:
                return False
            return user_id in (res.data[0].get("user_ids") or [])
        except Exception as e:
            logger.error(f"Error comprobando acceso a la despensa: {e}")
            return False

    def _read_pantry_items(self, pantry_id: int, user_id: int) -> Optional[dict]:
        """Los productos de la despensa, comprobando antes que sea tuya."""
        if not self.user_in_pantry(pantry_id, user_id):
            logger.warning(f"⛔ Acceso denegado: user_id={user_id} no pertenece a la despensa {pantry_id}")
            return None
        res = self.supabase.table("pantries").select("items").eq("id", pantry_id).execute()
        if not res.data:
            return None
        return res.data[0].get("items") or {}

    def _write_pantry_items(self, pantry_id: int, items: dict) -> bool:
        res = self.supabase.table("pantries").update({"items": items}).eq("id", pantry_id).execute()
        return bool(res.data)

    def get_pantry_stock(self, user_id: int) -> dict:
        """{nombre: {quantity, unit}} de lo que hay en casa.

        Lo usa la lista de la compra para poder decir "de esto ya tienes 2 en
        casa" antes de que lo eches al carro otra vez.
        """
        pantry = self.get_pantry(user_id)
        if not pantry:
            return {}
        stock = {}
        for name, data in (pantry.get("items") or {}).items():
            entry = normalize_entry(data)
            if entry["quantity"] > 0:
                stock[name] = {"quantity": entry["quantity"], "unit": entry["unit"]}
        return stock

    def add_or_update_pantry_item(
        self,
        pantry_id: int,
        name: str,
        quantity: float,
        unit: str,
        place: str,
        cat: str,
        shop: str,
        note: str,
        min_qty: float,
        expires: str,
        user_id: int,
        sumar: bool = False,
    ) -> bool:
        """Mete un producto en la despensa (o corrige el que ya estaba).

        Con `sumar=True` se **añade** a lo que ya había, que es lo que se quiere
        al reponer: acabas de traer dos briks más, no de contarlos todos otra vez.
        El resto de campos (dónde se guarda, mínimo, caducidad...) son siempre
        los del formulario: lo que se ve en el diálogo es lo que se guarda.
        """
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None:
                return False
            anterior = items.get(name)
            if sumar and anterior:
                clave = stock_key(items, name, unit)
                items = add_to_stock(items, name, quantity, unit, {"cat": cat, "shop": shop, "note": note})
                entrada = items.get(clave)
                if entrada is not None:
                    entrada.update({
                        "place": place, "cat": cat, "shop": shop, "note": note,
                        "min_qty": round(float(min_qty or 0), 3), "expires": expires or "",
                    })
            else:
                entrada = new_entry(quantity, unit, place, cat, shop, note, min_qty, expires)
                #Corrigiendo una fila que ya existía, se conserva desde cuándo
                #está en casa salvo que cambie la cantidad
                if anterior and float(anterior.get("quantity", 0) or 0) == float(quantity):
                    entrada["updated_at"] = anterior.get("updated_at") or entrada["updated_at"]
                items[name] = entrada
            return self._write_pantry_items(pantry_id, items)
        except Exception as e:
            logger.error(f"Error añadiendo a la despensa: {e}")
            return False

    def update_pantry_item_details(
        self,
        pantry_id: int,
        old_name: str,
        new_name: str,
        quantity: float,
        unit: str,
        place: str,
        cat: str,
        shop: str,
        note: str,
        min_qty: float,
        expires: str,
        user_id: int,
    ) -> bool:
        """Edita un producto de la despensa. `False` si el nombre nuevo ya existe."""
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None or old_name not in items:
                return False
            if new_name != old_name and new_name in items:
                return False

            anterior = normalize_entry(items.pop(old_name))
            entrada = new_entry(quantity, unit, place, cat, shop, note, min_qty, expires)
            if anterior["quantity"] == float(quantity):
                entrada["updated_at"] = anterior["updated_at"] or entrada["updated_at"]
            items[new_name] = entrada
            return self._write_pantry_items(pantry_id, items)
        except Exception as e:
            logger.error(f"Error actualizando la despensa: {e}")
            return False

    def adjust_pantry_item(self, pantry_id: int, name: str, delta: float, user_id: int) -> bool:
        """Sube o baja la cantidad desde la propia fila (gastar o reponer)."""
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None or name not in items:
                return False
            entry = normalize_entry(items[name])
            nueva = round(entry["quantity"] + float(delta), 3)
            if nueva < 0:
                nueva = 0.0
            entry["quantity"] = nueva
            entry["updated_at"] = now_iso()
            items[name] = entry
            return self._write_pantry_items(pantry_id, items)
        except Exception as e:
            logger.error(f"Error ajustando la despensa: {e}")
            return False

    def delete_pantry_item(self, pantry_id: int, name: str, user_id: int) -> bool:
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None or name not in items:
                return False
            del items[name]
            return self._write_pantry_items(pantry_id, items)
        except Exception as e:
            logger.error(f"Error eliminando de la despensa: {e}")
            return False

    def clear_pantry_items(self, pantry_id: int, user_id: int, solo_agotados: bool = False) -> int:
        """Vacía la despensa entera, o solo lo que se ha acabado."""
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None:
                return 0
            if solo_agotados:
                quedan = {
                    n: d for n, d in items.items()
                    if normalize_entry(d)["quantity"] > 0
                }
            else:
                quedan = {}
            borrados = len(items) - len(quedan)
            if borrados:
                self._write_pantry_items(pantry_id, quedan)
            return borrados
        except Exception as e:
            logger.error(f"Error vaciando la despensa: {e}")
            return 0

    def set_pantry_auto_stock(self, pantry_id: int, user_id: int, value: bool) -> bool:
        """Enciende o apaga el "sumar a la despensa al comprar"."""
        try:
            if not self.user_in_pantry(pantry_id, user_id):
                return False
            res = (
                self.supabase.table("pantries")
                .update({"auto_stock": value})
                .eq("id", pantry_id)
                .execute()
            )
            return bool(res.data)
        except Exception as e:
            logger.error(f"Error cambiando el automático de la despensa: {e}")
            return False

    def get_users_in_pantry(self, pantry_id: int) -> List[User]:
        try:
            res = self.supabase.table("pantries").select("user_ids").eq("id", pantry_id).execute()
            if not res.data:
                return []
            usuarios = []
            for uid in (res.data[0].get("user_ids") or []):
                user = self.get_user_by_id(uid)
                if user:
                    usuarios.append(user)
            return usuarios
        except Exception as e:
            logger.error(f"Error get_users_in_pantry: {e}")
            return []

    def pantry_low_items(self, user_id: int) -> List[dict]:
        """Lo que hay que reponer: por debajo del mínimo o agotado."""
        pantry = self.get_pantry(user_id)
        if not pantry:
            return []
        faltan = []
        for name, data in (pantry.get("items") or {}).items():
            entry = normalize_entry(data)
            if is_low(entry):
                faltan.append({"name": name, **entry})
        return faltan

    # --- Compartir la despensa ------------------------------------------------
    # Es una lista independiente de la de la compra y se comparte igual que
    # ella: por nombre de usuario, fusionando el stock del otro en la tuya y
    # dejando una sola despensa para los dos.

    def merge_and_share_pantry(self, user_id: int, friend_username: str) -> tuple[bool, str]:
        """Comparte tu despensa con otro usuario, sumando lo que él tuviera.

        Mismo trato que la lista de la compra: no se elige "la tuya o la suya",
        se fusionan. Lo que estuviera repetido se suma (convirtiendo unidades
        cuando se puede), y la despensa vieja del otro desaparece para que no le
        queden dos.
        """
        if not self._pantry_ready():
            return False, "La despensa no está disponible. ¿Falta la migración 018_pantry.sql?"
        try:
            friend = self.get_user_by_username(friend_username)
            if not friend:
                return False, "Usuario no encontrado"
            friend_id = friend["id"]
            if friend_id == user_id:
                return False, "Esa es tu propia despensa"

            mine = self.get_or_create_pantry(user_id)
            if not mine:
                return False, "No tienes una despensa activa"

            theirs = self.get_pantry(friend_id)
            if theirs and theirs["id"] == mine["id"]:
                return False, f"{friend_username} ya comparte tu despensa"

            items = mine.get("items") or {}
            if theirs:
                for name, data in (theirs.get("items") or {}).items():
                    entry = normalize_entry(data)
                    if name not in items:
                        items[name] = entry
                        continue
                    items = add_to_stock(
                        items, name, entry["quantity"], entry["unit"],
                        {"cat": entry["cat"], "shop": entry["shop"], "note": entry["note"]},
                    )
                self.supabase.table("pantries").delete().eq("id", theirs["id"]).execute()
                self._write_pantry_items(mine["id"], items)

            ids = list(mine.get("user_ids") or [])
            if friend_id not in ids:
                ids.append(friend_id)
                self.supabase.table("pantries").update({"user_ids": ids}).eq("id", mine["id"]).execute()
            return True, f"Despensa fusionada y compartida con {friend_username}"
        except Exception as e:
            logger.error(f"Error compartiendo la despensa: {e}")
            return False, str(e)

    def remove_user_from_pantry(self, pantry_id: int, user_id: int, requesting_user_id: int) -> bool:
        """Saca a alguien de la despensa compartida y le deja una copia del stock.

        Copia y no reparto, igual que en la lista de la compra: nadie sabe de
        quién es cada bote, y quedarse sin despensa al salir sería peor.
        """
        try:
            if not self.user_in_pantry(pantry_id, requesting_user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={requesting_user_id} no pertenece a la despensa {pantry_id}")
                return False
            res = self.supabase.table("pantries").select("*").eq("id", pantry_id).execute()
            if not res.data:
                return False
            pantry = res.data[0]
            user_ids = pantry.get("user_ids") or []
            if user_id not in user_ids:
                return False

            self.supabase.table("pantries").insert(
                {"user_ids": [user_id], "items": pantry.get("items") or {}}
            ).execute()
            quedan = [uid for uid in user_ids if uid != user_id]
            self.supabase.table("pantries").update({"user_ids": quedan}).eq("id", pantry_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error sacando a un usuario de la despensa: {e}")
            return False

    # --- El automático: lo que compras entra en casa --------------------------

    def _apply_stock(self, user_id: int, adds: list, removes: list) -> bool:
        """Suma (o resta) en la despensa lo que se acaba de marcar en la compra.

        Cada elemento es `(nombre, cantidad, unidad, datos del producto)`.
        Devuelve si se ha escrito de verdad: es lo que decide si el producto de
        la lista queda marcado como «ya está en casa» (`stocked`), y por tanto
        si desmarcarlo tiene que restarlo. Con el automático apagado, o sin la
        migración 018, devuelve `False` y la lista se comporta como siempre.
        """
        if not adds and not removes:
            return False
        try:
            pantry = self.get_or_create_pantry(user_id)
            if not pantry or not pantry.get("auto_stock", True):
                return False
            items = pantry.get("items") or {}
            for name, qty, unit, defaults in adds:
                items = add_to_stock(items, name, qty, unit, defaults)
            for name, qty, unit, _ in removes:
                items = take_from_stock(items, name, qty, unit)
            return self._write_pantry_items(pantry["id"], items)
        except Exception as e:
            logger.warning(f"No se pudo actualizar la despensa desde la compra: {e}")
            return False

    @staticmethod
    def _stock_payload(name: str, entry: dict) -> tuple:
        """Lo que hace falta para llevar un producto de la lista a la despensa."""
        return (
            name,
            float(entry.get("quantity", 0) or 0),
            entry.get("unit") or "ud",
            {
                "cat": entry.get("cat") or "otros",
                "shop": entry.get("supermarket") or "",
                "note": entry.get("note") or "",
            },
        )

    # ---------------------- Cocinar: descontar de la despensa ----------------------
    # Lo que cierra el circuito. La compra llena la despensa; esto la vacía a
    # medida que se cocina, pero **nunca solo**: se propone y lo autoriza una
    # persona. Todo lo de aquí necesita la migración 019.

    def consume_from_pantry(self, pantry_id: int, user_id: int, takes: List[tuple]) -> tuple[bool, int]:
        """Resta de la despensa lo que se ha cocinado.

        `takes` es una lista de `(nombre, cantidad, unidad)` **ya en la unidad
        de la despensa** (quien llama es el que sabe convertir, y quien enseña
        al usuario lo que va a pasar antes de que lo autorice).

        Devuelve `(éxito, cuántos productos se tocaron)`.
        """
        try:
            items = self._read_pantry_items(pantry_id, user_id)
            if items is None:
                return False, 0
            tocados = 0
            for name, qty, unit in takes:
                if float(qty or 0) <= 0:
                    continue
                antes = dict(items)
                items = take_from_stock(items, name, float(qty), unit)
                if items != antes:
                    tocados += 1
            if not tocados:
                return True, 0
            return self._write_pantry_items(pantry_id, items), tocados
        except Exception as e:
            logger.error(f"Error descontando de la despensa: {e}")
            return False, 0

    def get_day_consumption(self, day_id: int, user_id: int) -> dict:
        """`{"meal": bool, "dinner": bool}`: qué comidas del día ya se descontaron."""
        try:
            if not self.user_has_day_access(day_id, user_id):
                return {"meal": False, "dinner": False}
            res = (
                self.supabase.from_("days")
                .select("meal_consumed, dinner_consumed")
                .eq("id", day_id)
                .execute()
            )
            if not res.data:
                return {"meal": False, "dinner": False}
            row = res.data[0]
            return {
                "meal": bool(row.get("meal_consumed", False)),
                "dinner": bool(row.get("dinner_consumed", False)),
            }
        except Exception as e:
            #Sin la migración 019 no existen las columnas: se responde "no
            #descontado" y la app sigue funcionando (solo que no lo recuerda)
            logger.warning(f"No se pudo leer si el día estaba descontado ({e}); ¿falta la 019?")
            return {"meal": False, "dinner": False}

    def set_day_consumed(
        self,
        day_id: int,
        slot: str,
        value: bool,
        user_id: int,
        username: str = "",
        items: Optional[List[dict]] = None,
    ) -> bool:
        """Deja constancia de que esa comida ya se descontó: quién, cuándo y qué.

        El detalle (`items`) es lo que permite comprobarlo después: un tick que
        no dice qué se restó no se puede auditar. Si la migración 019 aún no
        está, se intenta guardar al menos la marca.
        """
        prefijo = "meal" if slot == "meal" else "dinner"
        try:
            if not self.user_has_day_access(day_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no puede tocar el día {day_id}")
                return False

            completo = {
                f"{prefijo}_consumed": value,
                f"{prefijo}_consumed_by": username if value else "",
                f"{prefijo}_consumed_at": datetime.now(pytz.timezone("Europe/Madrid")).isoformat() if value else None,
                f"{prefijo}_consumed_items": (items or []) if value else [],
            }
            for datos in (completo, {f"{prefijo}_consumed": value}):
                try:
                    res = self.supabase.table("days").update(datos).eq("id", day_id).execute()
                    return bool(res.data)
                except Exception as e:
                    if self._falta_columna(e, f"{prefijo}_consumed_by", f"{prefijo}_consumed_at", f"{prefijo}_consumed_items"):
                        continue
                    raise
            return False
        except Exception as e:
            logger.warning(f"No se pudo marcar el día como descontado ({e}); ¿falta la 019?")
            return False

    # --- Ajustes de aviso por usuario ---------------------------------------
    #Valores por defecto: la comida a las 15:00 y la cena a las 23:00

    MEAL_NOTIFY_DEFAULTS = {"notify_meal_stock": True, "meal_notify_time": "15:00", "dinner_notify_time": "23:00"}

    def get_meal_notify_settings(self, user_id: int) -> dict:
        try:
            res = (
                self.supabase.from_("user")
                .select("notify_meal_stock, meal_notify_time, dinner_notify_time")
                .eq("id", user_id)
                .execute()
            )
            if not res.data:
                return dict(self.MEAL_NOTIFY_DEFAULTS)
            row = res.data[0]
            return {
                "notify_meal_stock": bool(row.get("notify_meal_stock", True)),
                "meal_notify_time": (row.get("meal_notify_time") or "15:00")[:5],
                "dinner_notify_time": (row.get("dinner_notify_time") or "23:00")[:5],
            }
        except Exception as e:
            logger.warning(f"No se pudieron leer los ajustes de aviso ({e}); ¿falta la 019?")
            return dict(self.MEAL_NOTIFY_DEFAULTS)

    def set_meal_notify_settings(
        self, user_id: int, enabled: bool, meal_time: str, dinner_time: str
    ) -> bool:
        try:
            res = (
                self.supabase.table("user")
                .update({
                    "notify_meal_stock": enabled,
                    "meal_notify_time": meal_time,
                    "dinner_notify_time": dinner_time,
                })
                .eq("id", user_id)
                .execute()
            )
            return bool(res.data)
        except Exception as e:
            logger.warning(f"No se pudieron guardar los ajustes de aviso ({e}); ¿falta la 019?")
            return False

    def get_users_wanting_meal_reminders(self) -> List[dict]:
        """Quién quiere el recordatorio de descontar, y a qué hora."""
        try:
            res = (
                self.supabase.from_("user")
                .select("id, username, notify_meal_stock, meal_notify_time, dinner_notify_time")
                .execute()
            )
            usuarios = []
            for row in (res.data or []):
                if not bool(row.get("notify_meal_stock", True)):
                    continue
                usuarios.append({
                    "id": row["id"],
                    "username": row.get("username", ""),
                    "meal_notify_time": (row.get("meal_notify_time") or "15:00")[:5],
                    "dinner_notify_time": (row.get("dinner_notify_time") or "23:00")[:5],
                })
            return usuarios
        except Exception as e:
            logger.warning(f"No se pudo leer quién quiere recordatorios ({e}); ¿falta la 019?")
            return []

    def claim_meal_reminder(self, user_id: int, day_id: int, slot: str) -> bool:
        """Reserva el envío de un recordatorio. `True` si te toca mandarlo a ti.

        Es el seguro contra los avisos repetidos: el índice único de
        `meal_reminders` hace que solo la primera inserción pase. Si el servidor
        corre con varios procesos, o se reinicia justo a esa hora, el aviso sale
        **una vez**.
        """
        try:
            res = (
                self.supabase.table("meal_reminders")
                .insert({"user_id": user_id, "day_id": day_id, "slot": slot})
                .execute()
            )
            return bool(res.data)
        except Exception as e:
            texto = str(e).lower()
            if "duplicate" in texto or "23505" in texto or "unique" in texto:
                return False   # ya lo mandó otro proceso: normal, no es un fallo
            logger.warning(f"No se pudo registrar el recordatorio ({e}); ¿falta la 019?")
            return False

    def get_todays_meals_for_user(self, user_id: int, today: datetime) -> List[dict]:
        """Las comidas de hoy del usuario, con lo que hace falta para avisar.

        Devuelve una fila por día accesible con comida o cena puesta:
        `{day_id, calendar_id, calendar_name, meal, dinner, meal_consumed,
        dinner_consumed}`.
        """
        try:
            calendar_ids = self._accessible_calendar_ids(user_id)
            if not calendar_ids:
                return []
            inicio = today.replace(hour=0, minute=0, second=0, microsecond=0)
            fin = inicio + timedelta(days=1)
            res = (
                self.supabase.from_("days")
                .select("id, calendar_id, date, meal, dinner, meal_consumed, dinner_consumed")
                .in_("calendar_id", calendar_ids)
                .gte("date", inicio.isoformat())
                .lt("date", fin.isoformat())
                .execute()
            )
            filas = []
            for row in (res.data or []):
                if not (row.get("meal") or row.get("dinner")):
                    continue
                filas.append({
                    "day_id": row["id"],
                    "calendar_id": row["calendar_id"],
                    "meal": row.get("meal") or "",
                    "dinner": row.get("dinner") or "",
                    "meal_consumed": bool(row.get("meal_consumed", False)),
                    "dinner_consumed": bool(row.get("dinner_consumed", False)),
                })
            return filas
        except Exception as e:
            logger.warning(f"No se pudieron leer las comidas de hoy ({e}); ¿falta la 019?")
            return []

    # ---------------------- Suscripciones a notificaciones push ----------------------

    def upsert_push_subscription(self, user_id: int, endpoint: str, p256dh: str, auth: str, alias: str) -> bool:
        """Crea o actualiza (por endpoint) la suscripción push de un usuario."""
        try:
            existing = (
                self.supabase.table("push_subscriptions")
                .select("id")
                .eq("endpoint", endpoint)
                .execute()
            )
            data = {
                "user_id": user_id,
                "endpoint": endpoint,
                "p256dh": p256dh,
                "auth": auth,
                "alias": alias,
            }
            try:
                if existing.data:
                    self.supabase.table("push_subscriptions").update(data).eq("endpoint", endpoint).execute()
                else:
                    self.supabase.table("push_subscriptions").insert(data).execute()
            except Exception as e:
                #La tabla en producción se creó sin la columna `alias` (ver
                #migración 003): sin este reintento, suscribir un dispositivo
                #falla siempre con PGRST204 y el usuario solo ve "error al
                #guardar la suscripción".
                if "schema cache" not in str(e) or "alias" not in str(e):
                    raise
                logger.warning("push_subscriptions no tiene columna 'alias' (falta migración 003); guardando sin alias")
                data.pop("alias")
                if existing.data:
                    self.supabase.table("push_subscriptions").update(data).eq("endpoint", endpoint).execute()
                else:
                    self.supabase.table("push_subscriptions").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error guardando suscripción push: {e}")
            return False

    def get_push_subscriptions_for_user(self, user_id: int) -> list[dict]:
        try:
            response = (
                self.supabase.table("push_subscriptions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at")
                .execute()
            )
            #Sin la migración 003 no hay columna `alias`: damos un nombre
            #legible para que /profile no muestre filas en blanco
            return [
                {**row, "alias": (row.get("alias") or "").strip() or "Dispositivo sin nombre"}
                for row in (response.data or [])
            ]
        except Exception as e:
            logger.error(f"Error obteniendo suscripciones push: {e}")
            return []

    def get_push_subscriptions_for_username(self, username: str, respect_pref: bool = True) -> list[dict]:
        try:
            user = self.get_user_by_username(username)
            if not user:
                return []
            #Los avisos automáticos (cambios de calendario) respetan la
            #preferencia del destinatario; los mensajes que le manda un amigo
            #a propósito, no.
            if respect_pref and not bool(user.get("notify_calendar_changes", True)):
                return []
            return self.get_push_subscriptions_for_user(user["id"])
        except Exception as e:
            logger.error(f"Error obteniendo suscripciones push por username: {e}")
            return []

    def get_all_push_subscriptions(self) -> list[dict]:
        try:
            response = self.supabase.table("push_subscriptions").select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error obteniendo todas las suscripciones push: {e}")
            return []

    def delete_push_subscription(self, subscription_id: int, requesting_user_id: int) -> bool:
        """Solo el dueño del dispositivo puede eliminar su propia suscripción."""
        try:
            response = (
                self.supabase.table("push_subscriptions")
                .select("user_id")
                .eq("id", subscription_id)
                .execute()
            )
            if not response.data:
                return False
            if response.data[0]["user_id"] != requesting_user_id:
                logger.warning(
                    f"⛔ Acceso denegado: user_id={requesting_user_id} no puede borrar la suscripción {subscription_id}"
                )
                return False
            delete_resp = (
                self.supabase.table("push_subscriptions")
                .delete()
                .eq("id", subscription_id)
                .execute()
            )
            return bool(delete_resp.data)
        except Exception as e:
            logger.error(f"Error eliminando suscripción push: {e}")
            return False

    # ---------------------- Agenda diaria (tareas / eventos / notas) ----------------------

    def get_day_items(self, day_id: int, user_id: int) -> List[DayItem]:
        """Devuelve los elementos de agenda de un día, si el usuario tiene acceso."""
        try:
            if not self.user_has_day_access(day_id, user_id):
                return []
            response = (
                self.supabase.from_("day_items")
                .select("*")
                .eq("day_id", day_id)
                .order("time")
                .order("created_at")
                .execute()
            )
            items = []
            for row in (response.data or []):
                item = DayItem(**row)
                item.time_label = time_range_label(item.time, item.end_time)
                items.append(item)
            #Primero lo que tiene hora (en orden), después lo que no
            items.sort(key=lambda i: (i.time is None or i.time == "", i.time or ""))
            return items
        except Exception as e:
            logger.error(f"Error obteniendo agenda del día: {e}")
            return []

    def add_day_item(
        self, day_id: int, owner_id: int, item_type: str, title: str,
        description: str = "", time: Optional[str] = None, end_time: Optional[str] = None,
    ) -> Optional[DayItem]:
        """Añade un elemento a la agenda del día, si el usuario tiene acceso al calendario."""
        try:
            calendar_id = self.get_calendar_id_for_day(day_id)
            if calendar_id is None or not self.user_has_calendar_access(calendar_id, owner_id):
                logger.warning(f"⛔ Acceso denegado: user_id={owner_id} no tiene acceso al día {day_id}")
                return None
            #Los tipos son configurables (tabla task_types): basta con validar
            #que sea una clave razonable
            item_type = (item_type or "task").strip()[:24] or "task"
            data = {
                "day_id": day_id,
                "calendar_id": calendar_id,
                "owner_id": owner_id,
                "item_type": item_type,
                "title": title,
                "description": description or "",
                "time": time or None,
                "end_time": end_time or None,
            }
            try:
                response = self.supabase.table("day_items").insert(data).execute()
            except Exception as e:
                #Sin la migración 008 no existe `end_time`: se guarda igual,
                #solo que sin hora de fin
                if "schema cache" not in str(e):
                    raise
                logger.warning("day_items sin columna 'end_time' (falta migración 008)")
                data.pop("end_time")
                response = self.supabase.table("day_items").insert(data).execute()

            if not response.data:
                return None
            item = DayItem(**response.data[0])
            item.time_label = time_range_label(item.time, item.end_time)
            return item
        except Exception as e:
            logger.error(f"Error añadiendo elemento de agenda: {e}")
            return None

    def toggle_day_item_completed(self, item_id: int, user_id: int) -> bool:
        """Alterna el estado 'completado' de un elemento de agenda (solo tareas tienen sentido, pero no se restringe el tipo)."""
        try:
            existing = (
                self.supabase.table("day_items")
                .select("day_id, completed")
                .eq("id", item_id)
                .execute()
            )
            if not existing.data:
                return False
            day_id = existing.data[0]["day_id"]
            if not self.user_has_day_access(day_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no puede modificar el elemento {item_id}")
                return False
            new_value = not existing.data[0]["completed"]
            update_resp = (
                self.supabase.table("day_items")
                .update({"completed": new_value})
                .eq("id", item_id)
                .execute()
            )
            return bool(update_resp.data)
        except Exception as e:
            logger.error(f"Error actualizando elemento de agenda: {e}")
            return False

    def delete_day_item(self, item_id: int, user_id: int) -> bool:
        """Elimina un elemento de agenda, si el usuario tiene acceso al calendario del día."""
        try:
            existing = (
                self.supabase.table("day_items")
                .select("day_id")
                .eq("id", item_id)
                .execute()
            )
            if not existing.data:
                return False
            day_id = existing.data[0]["day_id"]
            if not self.user_has_day_access(day_id, user_id):
                logger.warning(f"⛔ Acceso denegado: user_id={user_id} no puede eliminar el elemento {item_id}")
                return False
            delete_resp = self.supabase.table("day_items").delete().eq("id", item_id).execute()
            return bool(delete_resp.data)
        except Exception as e:
            logger.error(f"Error eliminando elemento de agenda: {e}")
            return False