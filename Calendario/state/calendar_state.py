#calendar_state.py

import asyncio
import logging
import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment, Calendar, User, CalendarOption, MealGroup, CatalogEntry, MealCard, CalendarMember
from Calendario.state.user_state import UserState
from Calendario.utils.api import get_today_info,delete_calendar_and_days,get_shared_users,fetch_and_transform_calendars, get_all_meals, get_days_for_calendar, get_user_by_id, share_calendar_with_user, get_calendars_summary, get_meal_categories, save_meal_category, delete_meal_category, get_calendar_role, get_calendar_members, set_member_role, remove_calendar_member
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from Calendario import theme
from Calendario.state.notification_state import NotificationState

#Estado que maneja la lógica del calendario
logger = logging.getLogger(__name__)

#Cada cuánto se relee el calendario compartido (segundos)
SYNC_SECONDS = 6


def pick_calendar_for_today(
    calendars: List[Calendar], user_id: int, today: Optional[datetime] = None
) -> Optional[Calendar]:
    """Elige el calendario que debe salir seleccionado al entrar en la app.

    Prioridad:
    1. El que cubre el día de hoy (si hay varios, antes el propio que el compartido).
    2. El más próximo en el futuro.
    3. El más reciente del pasado.

    Función aparte (y sin estado) a propósito: es la regla de negocio del
    "sale el mes en curso" y así se puede comprobar sin levantar la app.
    """
    if not calendars:
        return None

    today = (today or datetime.today()).replace(hour=0, minute=0, second=0, microsecond=0)

    current = [c for c in calendars if c.start_date <= today <= c.end_date]
    if current:
        current.sort(key=lambda c: (c.owner_id != user_id, c.start_date))
        return current[0]

    future = sorted([c for c in calendars if c.start_date > today], key=lambda c: c.start_date)
    if future:
        return future[0]

    past = sorted([c for c in calendars if c.end_date < today], key=lambda c: c.end_date, reverse=True)
    return past[0] if past else calendars[0]


class CalendarState(rx.State):
    meals: List[Meal] = []  #Lista de comidas en bd
    comments: List[Comment] = []  #Lista de comentarios para el día seleccionado
    calendars: List[Calendar] = []  # Lista de los calendarios del usuario
    toast_info: Optional[str] = None #Mensaje de información
    new_calendar_name : str = "" #Nombre para nuevo calendario
    new_calendar_month: str = datetime.today().strftime("%Y-%m") #Mes/año del nuevo calendario
    loading : bool = False #Manejador de carga
    show_calendar_creator: bool = False #Manejador para mostrar el creador de calendario
    error_message : Optional[str] = None #Mensaje de error para inputs
    current_calendar: Optional[Calendar] = None #Calendario actual
    days : List[Day] = [] #Lista de días del calendario seleccionado
    hovered_day: Optional[int] = None #Día seleccionado
    display_days: list[Optional[Day]] = [] #Días para mostrar en el calendario
    current_date_str: str #Fecha del día actual
    username_to_share: str = ""  #Nombre de usuario con quien compartir
    show_calendar_sharer: bool = False  #Manejador para mostrar compartir calendario
    shared_users: list[User] = [] #Lista de usuarios con acceso al calendario
    owner_username: str = "" #Nombre del dueño del calendario
    meal_search: str = "" #Texto de búsqueda en /meal_list
    meal_category: str = "todas" #Filtro de categoría en /meal_list
    #Resumen {calendar_id: {"total": n, "planned": n}} para el selector de calendarios
    calendar_summaries: dict[int, dict] = {}

    #Rol del usuario en el calendario activo y gente con acceso
    current_role: str = "member"
    members: List[CalendarMember] = []

    # ---------------------- Roles y miembros ----------------------

    @rx.event
    async def load_members(self):
        """Carga quién tiene acceso al calendario activo y con qué rol."""
        if not self.current_calendar:
            self.members = []
            self.current_role = "member"
            return
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        yo = user_state.current_user.id

        self.current_role = await get_calendar_role(self.current_calendar.id, yo) or "member"
        etiquetas = {"owner": "Propietario", "admin": "Administrador", "member": "Invitado"}
        filas = await get_calendar_members(self.current_calendar.id)
        self.members = [
            CalendarMember(
                user_id=m["user_id"],
                username=m["username"],
                role=m["role"],
                role_label=etiquetas.get(m["role"], "Invitado"),
                is_owner=m["role"] == "owner",
                is_admin=m["role"] == "admin",
                is_me=m["user_id"] == yo,
            )
            for m in filas
        ]
        #`owner_username` lo sigue usando el diálogo de compartir
        propietario = next((m for m in self.members if m.is_owner), None)
        if propietario:
            self.owner_username = propietario.username
        self.shared_users = [
            User(id=m.user_id, username=m.username) for m in self.members if not m.is_owner
        ]

    @rx.var
    def can_share(self) -> bool:
        """Compartir es cosa del propietario y de los administradores."""
        return self.current_role in ("owner", "admin")

    @rx.var
    def is_owner(self) -> bool:
        return self.current_role == "owner"

    @rx.event
    async def change_role(self, target_user_id: int, role: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user or not self.current_calendar:
            return
        ok = await set_member_role(
            self.current_calendar.id, target_user_id, role, user_state.current_user.id
        )
        if not ok:
            return rx.toast.error("Solo el propietario puede cambiar roles", position="top-center")
        await self.load_members()
        return rx.toast.success(
            "Ahora es administrador" if role == "admin" else "Vuelve a ser invitado",
            position="top-center",
        )

    @rx.event
    async def kick_member(self, target_user_id: int, username: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user or not self.current_calendar:
            return
        ok = await remove_calendar_member(
            self.current_calendar.id, target_user_id, user_state.current_user.id
        )
        if not ok:
            return rx.toast.error("No tienes permiso para expulsar a esa persona", position="top-center")
        await self.load_members()
        return rx.toast.success(f"{username} ya no tiene acceso", position="top-center")

    #Catálogo de categorías de plato (configurable, tabla meal_categories)
    categories: List[CatalogEntry] = []
    show_category_manager: bool = False
    cat_key: str = ""
    cat_label: str = ""
    cat_color: str = "#94a3b8"
    cat_icon: str = "utensils"

    #Buscador de los selectores de plato (editor del día y menú semanal)
    picker_search: str = ""

    @rx.event
    def set_picker_search(self, value: str):
        self.picker_search = value

    @rx.event
    def clear_picker_search(self):
        self.picker_search = ""

    @rx.var
    def picker_results(self) -> List[MealCard]:
        """Platos que casan con lo escrito en el buscador del desplegable.

        Con 125 platos, una lista plana no vale: aquí se filtra por nombre,
        descripción o ingrediente, igual que en el recetario.
        """
        query = self.picker_search.strip().lower()
        cats = self._category_map()
        salida = []
        for m in self.meals:
            if query and not (
                query in m.name.lower()
                or query in (m.description or "").lower()
                or any(query in i.name.lower() for i in m.ingredients)
            ):
                continue
            key = m.category or "otros"
            entry = cats.get(key)
            salida.append(
                MealCard(
                    id=m.id, name=m.name, prep_minutes=m.prep_minutes or 20,
                    ingredient_count=len(m.ingredients), cat_key=key,
                    cat_label=entry.label if entry else theme.category_label(key),
                    cat_color=entry.color if entry else theme.category_color(key),
                    cat_icon=entry.icon if entry else theme.category_icon(key),
                )
            )
        salida.sort(key=lambda c: c.name.lower())
        return salida

    @rx.var
    def picker_empty(self) -> bool:
        return len(self.picker_results) == 0

    # ---------------------- Gestor de categorías ----------------------

    @rx.event
    async def load_categories(self):
        rows = await get_meal_categories()
        self.categories = [
            CatalogEntry(key=r["key"], label=r["label"], color=r["color"], icon=r["icon"])
            for r in rows
        ]

    @rx.event
    async def open_category_manager(self):
        self.show_category_manager = True
        self._reset_category_form()
        await self.load_categories()

    @rx.event
    def close_category_manager(self):
        self.show_category_manager = False
        self._reset_category_form()

    def _reset_category_form(self):
        self.cat_key = ""
        self.cat_label = ""
        self.cat_color = "#94a3b8"
        self.cat_icon = "utensils"

    @rx.event
    def set_cat_label(self, value: str):
        self.cat_label = value

    @rx.event
    def set_cat_color(self, value: str):
        self.cat_color = value

    @rx.event
    def set_cat_icon(self, value: str):
        self.cat_icon = value

    @rx.event
    def edit_category(self, key: str):
        """Carga una categoría en el formulario para modificarla."""
        entry = next((c for c in self.categories if c.key == key), None)
        if not entry:
            return
        self.cat_key = entry.key
        self.cat_label = entry.label
        self.cat_color = entry.color
        self.cat_icon = entry.icon

    @rx.event
    async def save_category(self):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        label = self.cat_label.strip()
        if not label:
            return rx.toast.error("Escribe el nombre de la categoría", position="top-center")
        if len(label) > 24:
            return rx.toast.error("Máximo 24 caracteres", position="top-center")
        if not await save_meal_category(self.cat_key, label, self.cat_color, self.cat_icon):
            return rx.toast.error(
                "No se pudo guardar. ¿Está aplicada la migración 010_meal_categories.sql?",
                position="top-center",
            )
        self._reset_category_form()
        await self.load_categories()
        await self.load_meals()
        return rx.toast.success(f"Categoría '{label}' guardada", position="top-center")

    @rx.event
    async def remove_category(self, key: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if key == "otros":
            return rx.toast.error("'Otros' no se puede borrar: es la categoría de reserva", position="top-center")
        if not await delete_meal_category(key):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        await self.load_categories()
        await self.load_meals()
        return rx.toast.success("Categoría eliminada; sus platos pasan a 'Otros'", position="top-center")

    def _category_map(self) -> dict:
        return {c.key: c for c in self.categories}

    @rx.var
    def palette(self) -> List[str]:
        return ["#22c55e", "#38bdf8", "#3b82f6", "#a78bfa", "#f472b6",
                "#ef4444", "#f97316", "#eab308", "#34d399", "#94a3b8"]

    @rx.var
    def icon_choices(self) -> List[str]:
        return ["utensils", "wheat", "beef", "fish", "egg", "carrot",
                "salad", "sandwich", "cookie", "bean", "soup", "pizza"]

    #Platos con su categoría ya resuelta, para pintar la cuadrícula
    @rx.var
    def meal_cards(self) -> List[MealCard]:
        cats = self._category_map()
        cards = []
        for m in self.filtered_meals:
            key = m.category or "otros"
            entry = cats.get(key)
            cards.append(
                MealCard(
                    id=m.id,
                    name=m.name,
                    description=m.description or "",
                    prep_minutes=m.prep_minutes or 20,
                    ingredient_count=len(m.ingredients),
                    cat_key=key,
                    cat_label=entry.label if entry else theme.category_label(key),
                    cat_color=entry.color if entry else theme.category_color(key),
                    cat_icon=entry.icon if entry else theme.category_icon(key),
                )
            )
        return cards

    #Chips de filtro, con su recuento
    @rx.var
    def category_chips(self) -> List[MealCard]:
        counts = self.meals_by_category
        chips = []
        for c in self.categories:
            n = counts.get(c.key, 0)
            if not n:
                continue
            chips.append(
                MealCard(
                    id=0, name=c.label, ingredient_count=n,
                    cat_key=c.key, cat_label=c.label, cat_color=c.color, cat_icon=c.icon,
                )
            )
        return chips

    @rx.event
    def set_meal_search(self, value: str):
        self.meal_search = value

    @rx.event
    def set_meal_category(self, value: str):
        self.meal_category = value

    @rx.event
    def clear_meal_filters(self):
        self.meal_search = ""
        self.meal_category = "todas"

    #Comidas filtradas por búsqueda (nombre o ingrediente) y por categoría
    @rx.var
    def filtered_meals(self) -> List[Meal]:
        meals = self.meals
        if self.meal_category != "todas":
            meals = [m for m in meals if (m.category or "otros") == self.meal_category]
        query = self.meal_search.strip().lower()
        if query:
            meals = [
                m for m in meals
                if query in m.name.lower()
                or query in (m.description or "").lower()
                or any(query in i.name.lower() for i in m.ingredients)
            ]
        return meals

    @rx.var
    def meal_count_label(self) -> str:
        total = len(self.meals)
        shown = len(self.filtered_meals)
        if shown == total:
            return f"{total} comidas en el recetario"
        return f"{shown} de {total} comidas"

    #Nº de comidas por categoría, para los chips de filtro
    @rx.var
    def meals_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for m in self.meals:
            key = m.category or "otros"
            counts[key] = counts.get(key, 0) + 1
        return counts

    @rx.var
    def meals_with_ingredients(self) -> int:
        return len([m for m in self.meals if m.ingredients])

    @rx.var
    def category_count(self) -> int:
        return len({(m.category or "otros") for m in self.meals})

    #Comidas agrupadas por categoría, para los desplegables del menú semanal
    #y del editor del día
    @rx.var
    def meal_groups(self) -> List[MealGroup]:
        buckets: dict[str, List[Meal]] = {}
        for m in self.meals:
            buckets.setdefault(m.category or "otros", []).append(m)
        cats = self._category_map()
        orden = [c.key for c in self.categories] or theme.MEAL_CATEGORY_ORDER
        #Cualquier categoría suelta que no esté en el catálogo va al final
        orden += [k for k in buckets if k not in orden]
        groups: List[MealGroup] = []
        for key in orden:
            items = buckets.get(key)
            if not items:
                continue
            entry = cats.get(key)
            groups.append(
                MealGroup(
                    key=key,
                    label=entry.label if entry else theme.category_label(key),
                    meals=sorted(items, key=lambda m: m.name.lower()),
                )
            )
        return groups

    # ---------------------- Selector de calendarios ----------------------

    @rx.var
    def calendar_options(self) -> List[CalendarOption]:
        """Los calendarios del usuario, ya preparados para pintarlos.

        Se ordenan por fecha descendente (el más reciente arriba), que es el
        orden en el que uno los busca.
        """
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        options: List[CalendarOption] = []
        owner_id = self._owner_id_hint
        for cal in sorted(self.calendars, key=lambda c: c.start_date, reverse=True):
            summary = self.calendar_summaries.get(cal.id, {})
            total = summary.get("total", 0)
            planned = summary.get("planned", 0)
            options.append(
                CalendarOption(
                    id=cal.id,
                    name=cal.name,
                    month_label=f"{theme.MESES[cal.start_date.month - 1]} {cal.start_date.year}",
                    month_abbr=theme.MESES[cal.start_date.month - 1][:3].upper(),
                    year_abbr=str(cal.start_date.year)[2:],
                    is_owner=cal.owner_id == owner_id,
                    is_current_month=cal.start_date <= today <= cal.end_date,
                    is_past=cal.end_date < today,
                    days_total=total,
                    days_planned=planned,
                    percent=int(planned * 100 / total) if total else 0,
                )
            )
        return options

    #Id del usuario en sesión, cacheado al cargar calendarios: `calendar_options`
    #es un rx.var síncrono y no puede hacer await get_state(UserState)
    _owner_id_hint: int = -1

    @rx.var
    def has_calendars(self) -> bool:
        return len(self.calendars) > 0

    #Id del calendario activo como escalar (-1 si no hay ninguno). Evita tener
    #que acceder a `current_calendar.id` en el frontend, que revienta cuando
    #el calendario es None fuera de un rx.cond.
    @rx.var
    def current_calendar_id(self) -> int:
        return self.current_calendar.id if self.current_calendar else -1

    @rx.var
    def current_calendar_is_owner(self) -> bool:
        return bool(self.current_calendar) and self.current_calendar.owner_id == self._owner_id_hint

    #Nº de personas con acceso al calendario activo (dueño incluido)
    @rx.var
    def current_shared_count(self) -> int:
        if not self.current_calendar:
            return 0
        return 1 + len(self.current_calendar.shared_with or [])

    @rx.var
    def current_is_shared(self) -> bool:
        return self.current_shared_count > 1

    # ---------------------- Estadísticas del calendario activo ----------------------

    @rx.var
    def days_with_meal(self) -> int:
        return len([d for d in self.days if d.meal])

    @rx.var
    def days_with_dinner(self) -> int:
        return len([d for d in self.days if d.dinner])

    @rx.var
    def days_planned(self) -> int:
        return len([d for d in self.days if d.meal or d.dinner])

    @rx.var
    def days_pending(self) -> int:
        return len(self.days) - self.days_planned

    @rx.var
    def planned_percent(self) -> int:
        if not self.days:
            return 0
        return min(100, int(self.days_planned * 100 / len(self.days)))

    @rx.var
    def agenda_pending(self) -> int:
        return sum(d.pending_tasks for d in self.days)

    @rx.var
    def days_with_comments(self) -> int:
        return len([d for d in self.days if d.comments])


    #Recarga los datos de la página
    @rx.event
    async def refresh_page(self):
        #Recargamos primero la lista de calendarios (puede haber cambiado si
        #alguien nos ha compartido uno nuevo o hemos borrado el activo)
        await self.load_calendars()
        if self.current_calendar and any(c.id == self.current_calendar.id for c in self.calendars):
            #Recarga los días del calendario activo
            await self.set_current_calendar(self.current_calendar.id)
        else:
            #Sin calendario válido, seleccionamos el del mes en curso
            await self.auto_select_calendar(force=True)
        #Devuelve la información del día en curso
        return UserState.today_info()

            
    #Elimina el calendario actual
    @rx.event
    #Pasamnos la id del calendario como parámetro
    async def delete_calendar(self, calendar_id: int):
        try:
            #Solo el propietario puede eliminar el calendario (comprobado también en base de datos)
            user_state = await self.get_state(UserState)
            #Eliminamos registros de calendario en base de datos
            success = await delete_calendar_and_days(calendar_id, user_state.current_user.id)
            
            #Si la acción se completa
            if success:
                #Creamos una lista de calendarios vacios
                current_calendars = []
                #Iteramos sobre los calendarios del usuario
                for cal in self.calendars:
                    #Comprobamos la id con la del calendario del parámetro
                    if cal.id != calendar_id:
                        #Si la id es distinta, añadimos el calendario a la lista
                        current_calendars.append(cal)
                #Reemplazamos la lista de calendarios por la nueva
                self.calendars = current_calendars

                #Resetea la visión del calendario y salta al siguiente disponible
                self.current_calendar = None
                self.days = []
                self.display_days = []
                await self.load_calendar_summaries()
                await self.auto_select_calendar(force=True)

                #Devuelve un mensaje de información y actualiza la info de hoy por si ha sufrido cambios
                return [rx.toast.success("Calendario eliminado exitosamente", position="top-center"),
                        UserState.today_info()]
            else:
                #Si existe algún error, devuelve un mensaje con el error
                return rx.toast.error("Error eliminando el calendario", position="top-center")
                
        except Exception as e:
            #Si falla la base de datos, devuelve error
            return rx.toast.error(f"Error: {str(e)}", position="top-center")

    #Abrir compartir calendario
    @rx.event
    def open_calendar_sharer(self):
        self.show_calendar_sharer = True
        self.error_message = None
        self.username_to_share = ""
        
    #Cerrar compartir calendario
    @rx.event
    def close_calendar_sharer(self):
        self.show_calendar_sharer = False

    #Compartir calendario
    async def share_calendar(self):
        try:
            #Resetea mensajes de error previos
            self.error_message = None
            
            #Si no existe calendario, muestra error
            if not self.current_calendar:
                return rx.toast.error("Selecciona un calendario primero", position="top-center")
            
            #Si no se ha introducido nombre de usuario para compartir
            if not self.username_to_share.strip():
                self.username_to_share = "" #Resetea el campo
                #Devuelve mensaje de error
                return rx.toast.error("Escribe un nombre de usuario", position="top-center")

            #Si intentas compartir con el usuario loggeado
            #Obtenemos el estado de usuario
            user_state = await self.get_state(UserState)
            #Comparamos los nombres de usuario, si coincide
            if self.username_to_share.lower() == user_state.current_user.username.lower():
                #Resetea el campo
                self.username_to_share = ""
                #Devuelve error
                return rx.toast.error("No puedes compartir contigo mismo", position="top-center")

            #Intentamos llamar a la función que comparte el calendario
            success, message = await share_calendar_with_user(
                self.current_calendar, self.username_to_share, user_state.current_user.id
            )
            
            #Si tiene éxito
            if success:
                # Guardamos el nombre del destinatario antes de limpiar
                destinatario = self.username_to_share
                self.username_to_share = ""
                self.close_calendar_sharer()

                # Enviar notificación al destinatario
                NotificationState.enviar_notificacion(
                    titulo="📅 Nuevo calendario compartido",
                    mensaje=f"{user_state.current_user.username} te ha añadido al calendario '{self.current_calendar.name}'",
                    destino=destinatario
                )

                return rx.toast.success(message, position="top-center")
            
            #Si se genera error
            else:
                #Limpiamos el campo y devolvemos el mensaje de error
                self.username_to_share = ""
                return rx.toast.error(message, position="top-center")
        
        #Si se produce error de bd
        except Exception as e:
            #Mostramos mensaje de error
            return rx.toast.error(f"Error inesperado: {str(e)}", position="top-center")
        
    #Carga los usuarios con acceso al calendario (con sus roles)
    @rx.event
    async def load_shared_users(self):
        await self.load_members()
        return

    #Obtenemos el nombre del més del calendario
    @rx.var
    def calendar_title(self) -> str:
        #Si hay calendario seleccionado y tiene fecha de inicio
        if self.current_calendar and self.current_calendar.start_date:
            #Identificamos el mes y el año a partir de la fecha de inicio
            mes = theme.MESES[self.current_calendar.start_date.month - 1]
            año = self.current_calendar.start_date.year
            #Retornamos la fecha del calendario
            return f"{mes} {año}"
        return "" #Si no hay calendario retorna cadena vacía

    #Nombre del calendario activo (o un texto neutro si no hay ninguno)
    @rx.var
    def current_calendar_name(self) -> str:
        return self.current_calendar.name if self.current_calendar else "Sin calendario"

    #Etiqueta corta del mes activo, para el selector plegado
    @rx.var
    def current_short_label(self) -> str:
        if not self.current_calendar:
            return ""
        start = self.current_calendar.start_date
        return f"{theme.MESES[start.month - 1][:3].upper()} {str(start.year)[2:]}"

    #True si el calendario activo es el del mes en curso
    @rx.var
    def current_is_this_month(self) -> bool:
        if not self.current_calendar:
            return False
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.current_calendar.start_date <= today <= self.current_calendar.end_date
    
    #Actualizamos la fecha actual
    def update_current_date(self):
        #Establecemos zona horaria
        madrid_tz = pytz.timezone('Europe/Madrid')
        #Sacamos la hora actual para la zona horaria
        madrid_time = datetime.now(madrid_tz)
        #Guardamos la fecha actual formateada
        self.current_date_str = madrid_time.strftime("%Y-%m-%d 00:00:00")

    #Guardamos el día sobre el que se situa el ratón
    @rx.event
    def set_hovered_day(self, day_id: int):
        self.hovered_day = day_id

    @rx.event
    def set_new_calendar_name(self, value: str):
        self.new_calendar_name = value

    @rx.event
    def set_new_calendar_month(self, value: str):
        self.new_calendar_month = value

    @rx.event
    def set_username_to_share(self, value: str):
        self.username_to_share = value
    
    #Limpiamos el día sobre el que se situa el ratón
    @rx.event
    def clear_hovered_day(self):
        self.hovered_day = None

    #Controla la apertura del creador de calendario
    @rx.event
    def open_calendar_creator(self):
        self.show_calendar_creator = True
    
    #Controla el cierre del creador de calendario
    @rx.event
    def close_calendar_creator(self):
        self.show_calendar_creator = False

    #Cargamos las comidas del recetario del usuario
    @rx.event
    async def load_meals(self):
        """Trae SU recetario: el suyo, o el que comparta con quien se lo haya
        compartido. Antes `meals` era una tabla global y todo el mundo veía las
        comidas de todos."""
        try:
            user_state = await self.get_state(UserState)
            if not user_state.current_user:
                self.meals = []
                return
            #Guardamos los registros que nos aporta la base de datos
            total_meals = await get_all_meals(user_state.current_user.id)
            self.meals = sorted(total_meals, key=lambda meal: meal.name.lower())
        except Exception as e:
            logger.error(f"Error loading meals: {e}")

    #Guardamos el calendario que selecciona el usuario
    @rx.event
    async def set_current_calendar(self, value: str):
        try:
            #Guardamos la id
            calendar_id = int(value)
            #Iteramos sobre los calendarios del usuario. Solo se puede
            #seleccionar algo que esté en `self.calendars`, que son los
            #calendarios que la base de datos ya validó como accesibles: un
            #cliente no puede colar aquí el id de un calendario ajeno.
            for calendar in self.calendars:
                #Comparamos la id con la del calendario del usuario
                if calendar.id == calendar_id:
                    #Cuando coincide, guardamos el calendario actual
                    self.current_calendar = calendar
                    #Guardamos los dias que nos da la base de datos
                    self.days = await get_days_for_calendar(self.current_calendar.id)
                    start_date = self.current_calendar.start_date
                    #Calculamos el indice en la semana del primer día del més
                    first_weekday = start_date.weekday()

                    #Creamos la lista de días incluyendo días vacios al principio
                    self.display_days = [None] * first_weekday + self.days
                    self.update_current_date()
                    await self.load_members()
                    return
        except (ValueError, TypeError):
            logger.error(f"Error convirtiendo el valor: {value}")

    #Selección desde el selector visual de la barra superior
    @rx.event
    async def select_calendar(self, calendar_id: int):
        await self.set_current_calendar(calendar_id)

    #Función para crear el calendario
    @rx.event
    async def create_calendar(self):
        try:
            self.loading = True
            #Si no encuentra usuario, lanza excepción
            if UserState.current_user is None:
                raise Exception("Usuario no autenticado")

            #Calcula el rango máximo que permite el input
            today = datetime.today()
            #Mínimo el més actual
            min_month = today.strftime("%Y-%m")
            #Máximo, diciembre del año siguiente
            max_month = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

            if not (min_month <= self.new_calendar_month <= max_month):
                return rx.toast.error(
                    f"Mes fuera de rango: debe ser entre {min_month} y {max_month}",
                    position="top-center"
                )

            #Convierte la fecha de inicio del calendario en un objeto datetime
            start_date = datetime.strptime(self.new_calendar_month, "%Y-%m")
            #Convertimos le fecha de fin en un objeto datetime, sumando 1 mes y restando 1 dia
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

            #Creamos el calendario en base de datos
            db = SupabaseAPI()
            #Obtenemos el estado de usuario para obtener los datos del mismo
            user_state = await self.get_state(UserState)
            #Creamos el calendario con los parametros calculados
            new_calendar = db.create_calendar_with_days(
                user_id=user_state.current_user.id,
                calendar_name=self.new_calendar_name,
                start_date=start_date,
                end_date=end_date
            )
            #Si tenemos éxito
            if new_calendar:
                #Añadimos el calendario a la lista de calendarios del usuario
                self.calendars.append(new_calendar)
                #Establecemos el nuevo calendario como actual
                self.current_calendar = new_calendar
                #Guardamos los dias del calendario
                self.days = await get_days_for_calendar(new_calendar.id)
                #Obtenemos la posicion del primer día
                first_weekday = start_date.weekday()
                self.display_days = [None] * first_weekday + self.days
                #Cerramos el creador de calendario
                self.close_calendar_creator()
                #Limpiamos el nombre de nuevo calendario
                self.new_calendar_name = ""
                #Establecemos el nuevo mes por defecto en el mes actual
                self.new_calendar_month = today.strftime("%Y-%m")
                #Refrescamos el resumen para que el selector muestre el nuevo mes
                await self.load_calendar_summaries()
                return rx.toast.success(
                    f"Calendario '{self.current_calendar.name}' creado con éxito!",
                    position="top-center"
                )

        except ValueError as ve:
            return rx.toast.error(str(ve), position="top-center")
        except Exception as e:
            return rx.toast.error(str(e), position="top-center")
        finally:
            self.loading = False

    #Cargamos lo calendarios del usuario
    @rx.event
    async def load_calendars(self):
        self.loading = True
        try:
            #Obtenemos el id del usuario
            user_state = await self.get_state(UserState)

            #Si no existe usuario loggeado, retornamos error
            if user_state.current_user is None:
                return rx.toast.error(
                    position="top-center",
                    title="Debes iniciar sesión para ver tus calendarios."
                )

            user_id = user_state.current_user.id
            self._owner_id_hint = user_id

            #Obtenemos los calendarios desde la base de datos para el usuario loggeado
            calendars = await fetch_and_transform_calendars(user_id)
            #Se asigna siempre (aunque venga vacío): si el usuario borró el
            #último calendario, quedarse con la lista antigua mostraría
            #calendarios que ya no existen
            self.calendars = calendars
            await self.load_calendar_summaries()

        except Exception as e:
            return rx.toast.error(str(e), position="top-center")
        finally:
            self.loading = False

    #Resumen de días planificados por calendario, para el selector
    async def load_calendar_summaries(self):
        if not self.calendars:
            self.calendar_summaries = {}
            return
        self.calendar_summaries = await get_calendars_summary([c.id for c in self.calendars])

    #Selecciona automáticamente el calendario del mes en curso
    @rx.event
    async def auto_select_calendar(self, force: bool = False):
        """Deja seleccionado el calendario que cubre el día de hoy.

        Es lo que uno espera al entrar: ver el mes actual, sea un calendario
        propio o uno al que le han invitado. Si ninguno cubre hoy, se elige el
        más cercano en el futuro y, en su defecto, el más reciente del pasado.
        """
        if not self.calendars:
            self.current_calendar = None
            self.days = []
            self.display_days = []
            return

        #Sin `force`, respetamos la elección manual del usuario mientras siga siendo válida
        if not force and self.current_calendar:
            if any(c.id == self.current_calendar.id for c in self.calendars):
                return

        target = pick_calendar_for_today(self.calendars, self._owner_id_hint)
        if target:
            await self.set_current_calendar(target.id)

    #Actualiza los días por si sufren cambios
    @rx.event
    async def update_day_in_state(self, updated_day: Day):
        #Iteramos sobre los días del calendario actual, si encuentra coincidencias, actualiza el día
        self.days = [
            updated_day if day.id == updated_day.id else day
            for day in self.days
        ]
        
        start_date = self.current_calendar.start_date
        first_weekday = start_date.weekday()
        self.display_days = [None] * first_weekday + self.days

    # ---------------------- Sincronización automática ----------------------
    #Evita que se solapen varios sondeos si se recarga la página
    _polling: bool = False

    @rx.event(background=True)
    async def sync_loop(self):
        """Mantiene el mes al día sin botón de refrescar.

        Un calendario compartido lo tocan varias personas: lo que cambie tu
        pareja tiene que aparecerte solo. Se relee cada pocos segundos y solo
        se reasigna el estado si algo cambió, para no repintar sin motivo.
        """
        async with self:
            if self._polling:
                return
            self._polling = True
        try:
            while True:
                await asyncio.sleep(SYNC_SECONDS)
                async with self:
                    #El bucle se apaga solo al salir de la pantalla
                    if self.router.url.path != "/calendar":
                        self._polling = False
                        return
                    if not self.current_calendar:
                        continue
                    try:
                        fresh = await get_days_for_calendar(self.current_calendar.id)
                    except Exception as e:
                        logger.warning(f"Sondeo del calendario fallido: {e}")
                        continue
                    if fresh and fresh != self.days:
                        self.days = fresh
                        first_weekday = self.current_calendar.start_date.weekday()
                        self.display_days = [None] * first_weekday + self.days
        finally:
            async with self:
                self._polling = False

    #Limpia todos los datos asociados al calendario ( Cuando el usuario cierra sesión )
    @rx.event
    def clean(self):
        self.meals = []
        self.comments = []
        self.days = []
        self.display_days = []
        #Sin esto, los calendarios del usuario anterior seguían en memoria tras
        #cerrar sesión en la misma pestaña
        self.calendars = []
        self.current_calendar = None
        self.calendar_summaries = {}
        self._owner_id_hint = -1
        self.toast_info = None
        self.new_calendar_name = ""
        self.new_calendar_month = datetime.today().strftime("%Y-%m")
        self.loading = False
        self.show_calendar_creator = False
        self.error_message = None
        self.meal_search = ""
        self.meal_category = "todas"


