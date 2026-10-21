# Calendario/state/menu_state.py
"""
Estado del planificador semanal.

Es la pieza que une las tres cosas que ya existían por separado: los días del
calendario, el recetario con ingredientes y la lista de la compra. Se rellena
la semana (comida y cena de lunes a domingo) y de ahí sale directamente la
compra, sumando los ingredientes de todos los platos.

No escribe días "nuevos": trabaja siempre sobre los `days` que ya creó el
calendario del mes, así que una semana a caballo entre dos meses solo se puede
planificar si existen los dos calendarios (se avisa en la interfaz).
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional

import reflex as rx

from Calendario import theme
from Calendario.model.model import Day, GeneratedItem, Meal, WeekDay
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    apply_generated_shopping_items,
    get_days_in_range,
    get_user_shopping_lists,
    update_day_dinner,
    update_day_meal,
)
from Calendario.utils.purchase import format_qty, to_purchase

logger = logging.getLogger(__name__)

#Cantidades del recetario pensadas para 2 comensales
BASE_SERVINGS = 2


class MenuState(rx.State):
    #Semana mostrada, en desplazamientos respecto a la semana actual (0 = esta)
    week_offset: int = 0
    week_days: List[WeekDay] = []
    loading: bool = False
    #Fechas de la semana sin días de calendario detrás (mes sin calendario creado)
    missing_dates: List[str] = []

    #Generador de la lista de la compra
    show_generator: bool = False
    people: str = "2"
    include_staples: bool = False
    generating: bool = False

    # ------------------------------------------------------------------
    # Navegación por semanas
    # ------------------------------------------------------------------
    def _monday(self) -> datetime:
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        monday = today - timedelta(days=today.weekday())
        return monday + timedelta(weeks=self.week_offset)

    #Etiquetas de la semana. Se calculan en `load_week` en lugar de con
    #`rx.var` para no depender de que Reflex deduzca la dependencia a través
    #de `_monday()`; cualquier cambio de semana pasa por `load_week`.
    week_label: str = ""
    week_year: str = ""
    week_subtitle: str = ""

    def _refresh_labels(self):
        start = self._monday()
        end = start + timedelta(days=6)
        if start.month == end.month:
            self.week_label = f"{start.day} – {end.day} de {theme.MESES[start.month - 1]}"
        else:
            self.week_label = (
                f"{start.day} {theme.MESES[start.month - 1][:3].lower()} – "
                f"{end.day} {theme.MESES[end.month - 1][:3].lower()}"
            )
        self.week_year = str(start.year)
        if self.week_offset == 0:
            self.week_subtitle = "Esta semana"
        elif self.week_offset == 1:
            self.week_subtitle = "La semana que viene"
        elif self.week_offset == -1:
            self.week_subtitle = "La semana pasada"
        elif self.week_offset > 1:
            self.week_subtitle = f"Dentro de {self.week_offset} semanas"
        else:
            self.week_subtitle = f"Hace {abs(self.week_offset)} semanas"

    @rx.var
    def is_current_week(self) -> bool:
        return self.week_offset == 0

    @rx.event
    async def next_week(self):
        self.week_offset += 1
        return MenuState.load_week

    @rx.event
    async def previous_week(self):
        self.week_offset -= 1
        return MenuState.load_week

    @rx.event
    async def this_week(self):
        self.week_offset = 0
        return MenuState.load_week

    # ------------------------------------------------------------------
    # Carga de la semana
    # ------------------------------------------------------------------
    @rx.event
    async def load_week(self):
        """Trae los días de la semana desde los calendarios accesibles."""
        self.loading = True
        self._refresh_labels()
        try:
            user_state = await self.get_state(UserState)
            if not user_state.current_user:
                self.week_days = []
                return

            calendar_state = await self.get_state(CalendarState)
            #El menú necesita el recetario cargado para pintar categorías
            if not calendar_state.meals:
                await calendar_state.load_meals()
            if not calendar_state.calendars:
                await calendar_state.load_calendars()

            preferred = calendar_state.current_calendar.id if calendar_state.current_calendar else None
            monday = self._monday()
            sunday = monday + timedelta(days=6)

            days = await get_days_in_range(user_state.current_user.id, monday, sunday, preferred)
            by_date = {d.date.date(): d for d in days}
            calendar_names = {c.id: c.name for c in calendar_state.calendars}
            categories = {m.name: (m.category or "otros") for m in calendar_state.meals}

            today = datetime.today().date()
            week: List[WeekDay] = []
            missing: List[str] = []

            for offset in range(7):
                current = (monday + timedelta(days=offset)).date()
                day: Optional[Day] = by_date.get(current)
                if day is None:
                    missing.append(f"{current.day} de {theme.MESES[current.month - 1]}")
                    continue
                week.append(
                    WeekDay(
                        day_id=day.id,
                        date_iso=current.isoformat(),
                        day_name=theme.DIAS_SEMANA[offset],
                        date_label=f"{current.day} {theme.MESES[current.month - 1][:3].lower()}",
                        meal=day.meal or "",
                        dinner=day.dinner or "",
                        meal_category=categories.get(day.meal or "", "otros"),
                        dinner_category=categories.get(day.dinner or "", "otros"),
                        is_today=current == today,
                        is_past=current < today,
                        is_weekend=offset >= 5,
                        calendar_name=calendar_names.get(day.calendar_id, ""),
                    )
                )

            self.week_days = week
            self.missing_dates = missing
        except Exception as e:
            logger.error(f"Error cargando la semana: {e}")
            return rx.toast.error("No se pudo cargar la semana", position="top-center")
        finally:
            self.loading = False

    @rx.var
    def has_missing_days(self) -> bool:
        return len(self.missing_dates) > 0

    @rx.var
    def missing_label(self) -> str:
        return ", ".join(self.missing_dates)

    # ------------------------------------------------------------------
    # Edición de la semana
    # ------------------------------------------------------------------
    def _day_ids(self) -> set:
        """Días que forman la semana cargada.

        Cualquier escritura se contrasta contra este conjunto: así un cliente
        no puede pedir que se escriba en un día que no está viendo (además de
        la comprobación de acceso que hace la base de datos).
        """
        return {d.day_id for d in self.week_days}

    @rx.event
    async def set_slot(self, day_id: int, slot: str, value: str):
        """Asigna comida o cena a un día concreto y lo guarda al momento."""
        if day_id not in self._day_ids():
            return rx.toast.error("Ese día no pertenece a la semana", position="top-center")

        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return

        meal_value = value or None
        #`update_day_*` vuelve a comprobar en base de datos que el usuario
        #tenga acceso al calendario del día antes de escribir nada
        if slot == "dinner":
            updated = await update_day_dinner(day_id, meal_value, user_state.current_user.id)
        else:
            updated = await update_day_meal(day_id, meal_value, user_state.current_user.id)

        if updated is None:
            return rx.toast.error("No tienes permiso para modificar este día", position="top-center")

        #Actualizamos la tarjeta en memoria en vez de recargar la semana entera:
        #elegir un plato en un desplegable no debería costar tres viajes a la
        #base de datos. El calendario del mes se refresca al volver a él.
        calendar_state = await self.get_state(CalendarState)
        category = next(
            (m.category or "otros" for m in calendar_state.meals if m.name == value), "otros"
        )
        self.week_days = [
            day.copy(update={slot: value, f"{slot}_category": category})
            if day.day_id == day_id
            else day
            for day in self.week_days
        ]

    @rx.event
    async def clear_slot(self, day_id: int, slot: str):
        return MenuState.set_slot(day_id, slot, "")

    @rx.event
    async def clear_week(self):
        """Vacía comida y cena de toda la semana (con confirmación en la UI)."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        user_id = user_state.current_user.id
        for day in list(self.week_days):
            if day.meal:
                await update_day_meal(day.day_id, None, user_id)
            if day.dinner:
                await update_day_dinner(day.day_id, None, user_id)
        await self._refresh_after_edit()
        return rx.toast.success("Semana vaciada", position="top-center")

    @rx.event
    async def surprise_me(self):
        """Rellena los huecos vacíos con platos al azar del recetario.

        Para los sábados de poca inspiración: no toca lo que ya has puesto y
        evita repetir el mismo plato dos veces en la misma semana.
        """
        calendar_state = await self.get_state(CalendarState)
        meals: List[Meal] = list(calendar_state.meals)
        if not meals:
            return rx.toast.error("Añade comidas al recetario primero", position="top-center")

        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        user_id = user_state.current_user.id

        used = {d.meal for d in self.week_days if d.meal} | {d.dinner for d in self.week_days if d.dinner}
        pool = [m.name for m in meals if m.name not in used]
        random.shuffle(pool)

        filled = 0
        for day in list(self.week_days):
            for slot, value in (("meal", day.meal), ("dinner", day.dinner)):
                if value:
                    continue
                if not pool:
                    #Si nos quedamos sin platos sin usar, reciclamos el recetario entero
                    pool = [m.name for m in meals]
                    random.shuffle(pool)
                choice = pool.pop()
                if slot == "dinner":
                    await update_day_dinner(day.day_id, choice, user_id)
                else:
                    await update_day_meal(day.day_id, choice, user_id)
                filled += 1

        await self._refresh_after_edit()
        if filled == 0:
            return rx.toast.info("La semana ya estaba completa", position="top-center")
        return rx.toast.success(f"{filled} huecos rellenados al azar", position="top-center")

    @rx.event
    async def copy_previous_week(self):
        """Repite el menú de la semana anterior en la que estás viendo."""
        user_state = await self.get_state(UserState)
        calendar_state = await self.get_state(CalendarState)
        if not user_state.current_user:
            return

        monday = self._monday()
        previous_monday = monday - timedelta(weeks=1)
        preferred = calendar_state.current_calendar.id if calendar_state.current_calendar else None
        previous = await get_days_in_range(
            user_state.current_user.id, previous_monday, previous_monday + timedelta(days=6), preferred
        )
        if not previous:
            return rx.toast.error("No hay datos de la semana anterior", position="top-center")

        by_weekday = {d.date.weekday(): d for d in previous}
        user_id = user_state.current_user.id
        copied = 0
        for day in list(self.week_days):
            source = by_weekday.get(datetime.fromisoformat(day.date_iso).weekday())
            if not source or not (source.meal or source.dinner):
                continue
            if source.meal:
                await update_day_meal(day.day_id, source.meal, user_id)
            if source.dinner:
                await update_day_dinner(day.day_id, source.dinner, user_id)
            copied += 1

        await self._refresh_after_edit()
        if copied == 0:
            return rx.toast.info("La semana anterior estaba vacía", position="top-center")
        return rx.toast.success(f"Copiados {copied} días de la semana anterior", position="top-center")

    async def _refresh_after_edit(self):
        """Recarga la semana y el calendario del mes para que todo cuadre."""
        await self.load_week()
        calendar_state = await self.get_state(CalendarState)
        if calendar_state.current_calendar:
            await calendar_state.set_current_calendar(calendar_state.current_calendar.id)
            await calendar_state.load_calendar_summaries()

    # ------------------------------------------------------------------
    # Métricas de la semana
    # ------------------------------------------------------------------
    @rx.var
    def total_slots(self) -> int:
        return len(self.week_days) * 2

    @rx.var
    def filled_slots(self) -> int:
        return len([1 for d in self.week_days if d.meal]) + len([1 for d in self.week_days if d.dinner])

    @rx.var
    def empty_slots(self) -> int:
        return self.total_slots - self.filled_slots

    @rx.var
    def week_percent(self) -> int:
        if not self.total_slots:
            return 0
        return min(100, int(self.filled_slots * 100 / self.total_slots))

    @rx.var
    def is_week_empty(self) -> bool:
        return self.filled_slots == 0

    # ------------------------------------------------------------------
    # Generación de la lista de la compra
    # ------------------------------------------------------------------
    @rx.event
    async def open_generator(self):
        self.show_generator = True
        #Se abre con todo marcado: descartar es la excepción, no la norma
        self.excluded_keys = []
        #Calculamos ya la vista previa: el diálogo debe abrirse con la lista hecha
        self.preview_items = await self._aggregate()

    @rx.event
    def close_generator(self):
        self.show_generator = False

    @rx.event
    def set_people(self, value: str):
        self.people = value

    @rx.event
    def toggle_staples(self, value: bool):
        self.include_staples = value

    @rx.var
    def people_int(self) -> int:
        try:
            return max(1, min(20, int(self.people)))
        except (ValueError, TypeError):
            return BASE_SERVINGS

    async def _aggregate(self) -> List[GeneratedItem]:
        """Suma los ingredientes de todos los platos de la semana.

        Se agrega por (producto, unidad): 400 g de arroz de un plato y 160 g de
        otro acaban en una sola línea de 560 g.
        """
        calendar_state = await self.get_state(CalendarState)
        recipes = {m.name: m for m in calendar_state.meals}
        factor = self.people_int / BASE_SERVINGS

        totals: dict[tuple, dict] = {}
        for day in self.week_days:
            for name in (day.meal, day.dinner):
                if not name:
                    continue
                recipe = recipes.get(name)
                if not recipe:
                    continue
                for item in recipe.ingredients:
                    if item.staple and not self.include_staples:
                        continue
                    key = (item.name, item.unit)
                    entry = totals.setdefault(
                        key,
                        {
                            "qty": 0.0,
                            "cat": item.cat,
                            "sources": [],
                            "staple": item.staple,
                            "shop": item.shop,
                            "note": item.note,
                        },
                    )
                    entry["qty"] += item.qty * factor
                    #Si el mismo producto aparece en dos recetas y solo una dice
                    #dónde comprarlo, ese dato no se pierde
                    if not entry.get("shop") and item.shop:
                        entry["shop"] = item.shop
                    if not entry.get("note") and item.note:
                        entry["note"] = item.note
                    if name not in entry["sources"]:
                        entry["sources"].append(name)

        #Ahora se pasa de unidades de cocina a unidades de compra: en el súper
        #no compras "5 pizcas de sal", compras un bote. Puede que dos entradas
        #distintas acaben en la misma unidad de compra, así que se vuelven a
        #agrupar después de convertir.
        purchased: dict[tuple, dict] = {}
        for (name, unit), data in totals.items():
            qty, shop_unit = to_purchase(name, data["qty"], unit)
            key = (name, shop_unit)
            entry = purchased.setdefault(
                key,
                {
                    "qty": 0.0,
                    "cat": data["cat"],
                    "sources": [],
                    "staple": data["staple"],
                    "shop": data.get("shop", ""),
                    "note": data.get("note", ""),
                },
            )
            entry["qty"] += qty
            if not entry.get("shop") and data.get("shop"):
                entry["shop"] = data["shop"]
            if not entry.get("note") and data.get("note"):
                entry["note"] = data["note"]
            for src in data["sources"]:
                if src not in entry["sources"]:
                    entry["sources"].append(src)

        order = {c: i for i, c in enumerate(theme.SHOP_CATEGORY_ORDER)}
        generated = [
            GeneratedItem(
                name=name,
                qty=round(data["qty"], 2),
                unit=unit,
                cat=data["cat"],
                shop=data.get("shop", ""),
                note=data.get("note", ""),
                source=", ".join(data["sources"]),
                qty_label=format_qty(data["qty"], unit),
                staple=data["staple"],
                key=f"{name}|{unit}",
                #Lo desmarcado se recuerda aunque cambien comensales o básicos
                selected=f"{name}|{unit}" not in self.excluded_keys,
            )
            for (name, unit), data in purchased.items()
        ]
        generated.sort(key=lambda g: (order.get(g.cat, 99), g.name))
        return generated

    #Vista previa de lo que se va a añadir a la compra
    preview_items: List[GeneratedItem] = []
    #Productos que el usuario ha descartado en la vista previa ("nombre|unidad")
    excluded_keys: List[str] = []

    @rx.event
    async def refresh_preview(self):
        self.preview_items = await self._aggregate()

    @rx.event
    async def toggle_item(self, key: str):
        """Marca o desmarca un producto de la vista previa."""
        if key in self.excluded_keys:
            self.excluded_keys = [k for k in self.excluded_keys if k != key]
        else:
            self.excluded_keys = self.excluded_keys + [key]
        self.preview_items = await self._aggregate()

    @rx.event
    async def select_all(self):
        self.excluded_keys = []
        self.preview_items = await self._aggregate()

    @rx.event
    async def select_none(self):
        self.excluded_keys = [item.key for item in self.preview_items]
        self.preview_items = await self._aggregate()

    @rx.var
    def preview_count(self) -> int:
        return len(self.preview_items)

    @rx.var
    def selected_count(self) -> int:
        return len([i for i in self.preview_items if i.selected])

    @rx.var
    def has_selection(self) -> bool:
        return self.selected_count > 0

    @rx.var
    def planned_meals_count(self) -> int:
        return self.filled_slots

    @rx.event
    async def generate(self, mode: str):
        """Vuelca los ingredientes agregados en la lista de la compra.

        `mode` = "merge" (pone al día esta semana sin quitar nada) | "replace"
        (deja esta semana igual que la vista previa, respetando lo añadido a
        mano). Las dos son repetibles: volver a generar la misma semana
        sustituye su aporte en lugar de sumarlo otra vez.
        """
        if mode not in ("merge", "replace"):
            return rx.toast.error("Modo de generación no válido", position="top-center")

        self.generating = True
        try:
            user_state = await self.get_state(UserState)
            if not user_state.current_user:
                return rx.redirect("/")

            #Solo lo que quede marcado en la vista previa
            items = [item for item in await self._aggregate() if item.selected]
            if not items:
                return rx.toast.error(
                    "No has dejado ningún producto marcado",
                    position="top-center",
                )

            lists = await get_user_shopping_lists(user_state.current_user.id)
            if not lists:
                return rx.toast.error("No tienes lista de la compra activa", position="top-center")

            payload = {
                item.name: {
                    "quantity": item.qty,
                    "unit": item.unit,
                    "cat": item.cat,
                    #Todo lo que se escribió en el ingrediente viaja con él
                    "shop": item.shop,
                    "staple": item.staple,
                    "note": item.note,
                    "source": item.source,
                }
                for item in items
            }
            success, count = await apply_generated_shopping_items(
                lists[0]["id"], payload, mode, user_state.current_user.id,
                #La semana que se está planificando: es lo que permite volver a
                #generarla sin que las cantidades se multipliquen
                self._monday().date().isoformat(),
            )
            if not success:
                return rx.toast.error("No se pudo actualizar la lista", position="top-center")

            self.show_generator = False
            return [
                rx.toast.success(
                    f"{count} productos en la lista de la compra para {self.people_int} personas",
                    position="top-center",
                ),
                rx.redirect("/shopping_list"),
            ]
        except Exception as e:
            logger.error(f"Error generando la lista: {e}")
            return rx.toast.error("Error generando la lista de la compra", position="top-center")
        finally:
            self.generating = False
