# Calendario/state/consume_state.py
"""
Descontar de la despensa lo que se cocina.

Es la última pieza del circuito: la compra llena la despensa y esto la vacía a
medida que se come. Lo que **no** hace es hacerlo solo. Restar comida sin
preguntar sería lo peor de los dos mundos — un stock que nadie ha confirmado y
en el que, por tanto, nadie confía. Así que el sistema propone y una persona
autoriza: llega el aviso a su hora (15:00 la comida, 23:00 la cena), se abre
esta ventana con las cuentas hechas y se le da a "restar".

Lo que se enseña de cada ingrediente es lo que hace falta para decidir en dos
segundos: cuánto pide la receta, cuánto hay en casa, cuánto se va a restar y
cómo se queda. Y lo que **no está en la despensa** se separa aparte, porque no
es un error del sistema sino información: o se te olvidó guardarlo al comprar, o
hay que comprarlo. Desde ahí mismo se hace cualquiera de las dos cosas.

Las cantidades de la receta y las de casa casi nunca vienen en la misma unidad
("300 ml" contra "2 briks"), así que se traducen con el formato de compra del
producto (migración 019). Cuando no hay forma de traducir, se dice y no se
inventa nada.
"""

import asyncio
import logging
from typing import Dict, List

import reflex as rx

from Calendario import theme
from Calendario.model.model import ConsumeRow
from Calendario.state.calendar_state import CalendarState
from Calendario.state.notification_state import NotificationState
from Calendario.state.products_state import ProductsState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    add_item_to_shopping_list,
    add_pantry_item,
    consume_from_pantry,
    get_day_details,
    get_pantry,
    get_shared_users,
    get_user_shopping_lists,
    set_day_consumed,
)
from Calendario.utils.pantry import convert_with_pack, guess_place, normalize_entry
from Calendario.utils.purchase import format_qty

logger = logging.getLogger(__name__)

#Las cantidades del recetario están escritas para 2 comensales
BASE_SERVINGS = 2

#Cómo se pinta cada estado de un ingrediente
STATUS_STYLE = {
    "ok":     ("Hay de sobra", theme.SUCCESS),
    "justo":  ("Se queda a cero", theme.WARNING),
    "falta":  ("No llega", theme.DANGER),
    "nuevo":  ("No está en la despensa", theme.PANTRY),
    "medida": ("Sin equivalencia", theme.WARNING),
}


def _numero(valor: float) -> str:
    return str(int(valor)) if float(valor) == int(valor) else str(valor)


class ConsumeState(rx.State):
    """La ventana de "restar de la despensa" de una comida concreta."""

    show: bool = False
    day_id: int = 0
    slot: str = "meal"              # meal | dinner
    meal_name: str = ""
    date_label: str = ""
    calendar_id: int = 0
    calendar_name: str = ""

    people: str = str(BASE_SERVINGS)
    include_staples: bool = False

    rows: List[ConsumeRow] = []
    loading: bool = False
    applying: bool = False

    #Estado del día: si esa comida ya se descontó, y por quién
    already: bool = False
    already_label: str = ""
    already_items: List[str] = []

    #Sin despensa (falta la migración 018) no hay nada que restar
    pantry_id: int = 0
    unavailable: bool = False

    current_user_id: int = -1
    username: str = ""

    # ------------------------------------------------------------------
    # Apertura
    # ------------------------------------------------------------------
    @rx.event
    async def open_for(self, day_id: int, slot: str):
        """Abre la ventana para la comida o la cena de un día.

        Se entra por aquí desde los tres sitios: el aviso del móvil, el editor
        del día en el calendario y la propia despensa.
        """
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        self.current_user_id = user_state.current_user.id
        self.username = user_state.current_user.username

        self.show = True
        self.loading = True
        self.day_id = int(day_id)
        self.slot = "dinner" if slot == "dinner" else "meal"
        self.rows = []
        self.people = str(BASE_SERVINGS)
        self.include_staples = False
        try:
            await self._load()
        finally:
            self.loading = False

    @rx.event
    async def open_from_url(self):
        """Abre la ventana si se ha llegado desde el aviso del móvil.

        El aviso lleva a `/despensa?dia=123&slot=meal`: se toca la notificación
        y sale directamente lo que hay que restar, sin buscar el día a mano.
        """
        params = self.router.url.query_parameters
        dia = params.get("dia", "")
        if not dia:
            return
        slot = params.get("slot", "meal")
        try:
            day_id = int(dia)
        except (TypeError, ValueError):
            return
        return ConsumeState.open_for(day_id, slot)

    @rx.event
    def close(self):
        self.show = False
        self.rows = []
        self.meal_name = ""

    async def _load(self):
        """Trae el día, la receta, la despensa y el catálogo, y monta las filas."""
        day = await get_day_details(self.day_id, self.current_user_id)
        if not day:
            self.show = False
            return rx.toast.error("No se encontró ese día", position="top-center")

        self.meal_name = (day.meal if self.slot == "meal" else day.dinner) or ""
        self.calendar_id = day.calendar_id
        self.date_label = day.date.strftime("%d/%m/%Y")
        self.already = day.meal_consumed if self.slot == "meal" else day.dinner_consumed
        self.already_label = (
            day.meal_consumed_label if self.slot == "meal" else day.dinner_consumed_label
        )
        self.already_items = (
            day.meal_consumed_items if self.slot == "meal" else day.dinner_consumed_items
        )

        calendar_state = await self.get_state(CalendarState)
        if not calendar_state.meals:
            await calendar_state.load_meals()
        calendario = next((c for c in calendar_state.calendars if c.id == day.calendar_id), None)
        self.calendar_name = calendario.name if calendario else ""

        pantry = await get_pantry(self.current_user_id)
        self.unavailable = pantry is None
        self.pantry_id = pantry["id"] if pantry else 0
        self._stock = {n: normalize_entry(d) for n, d in ((pantry or {}).get("items") or {}).items()}

        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()
        self._packs = {
            p.name.strip().lower(): (p.pack_qty, p.pack_unit, p.cat, p.shop, p.note)
            for p in products_state.products
        }
        self._build_rows(calendar_state)

    #Datos auxiliares que no hacen falta en el navegador
    _stock: Dict[str, Dict] = {}
    _packs: Dict[str, tuple] = {}

    # ------------------------------------------------------------------
    # Las cuentas
    # ------------------------------------------------------------------
    @rx.var
    def people_int(self) -> int:
        try:
            return max(1, min(50, int(self.people)))
        except (ValueError, TypeError):
            return BASE_SERVINGS

    def _build_rows(self, calendar_state: CalendarState):
        receta = next((m for m in calendar_state.meals if m.name == self.meal_name), None)
        if not receta:
            self.rows = []
            return

        factor = self.people_int / BASE_SERVINGS
        #Una receta puede repetir el mismo ingrediente en dos pasos: se agrupa
        necesario: Dict[tuple, dict] = {}
        for ing in receta.ingredients:
            if ing.staple and not self.include_staples:
                continue
            clave = (ing.name, ing.unit)
            entrada = necesario.setdefault(
                clave, {"qty": 0.0, "staple": ing.staple, "cat": ing.cat, "shop": ing.shop, "note": ing.note}
            )
            entrada["qty"] += ing.qty * factor

        filas: List[ConsumeRow] = []
        for (nombre, unidad), datos in necesario.items():
            filas.append(self._row(nombre, round(datos["qty"], 3), unidad, datos))
        #Primero lo que pide atención: lo que falta y lo que no está en casa
        orden = {"falta": 0, "nuevo": 1, "medida": 2, "justo": 3, "ok": 4}
        filas.sort(key=lambda r: (orden.get(r.status, 9), r.name.lower()))
        self.rows = filas

    def _row(self, nombre: str, need_qty: float, need_unit: str, datos: dict) -> ConsumeRow:
        pack_qty, pack_unit, cat, shop, note = self._packs.get(
            nombre.strip().lower(), (0, "", datos.get("cat", "otros"), datos.get("shop", ""), datos.get("note", ""))
        )
        entry = self._stock.get(nombre)
        base = dict(
            name=nombre,
            need_qty=need_qty,
            need_unit=need_unit,
            need_label=format_qty(need_qty, need_unit),
            staple=bool(datos.get("staple", False)),
            cat=datos.get("cat") or cat or "otros",
            shop=datos.get("shop") or shop or "",
            note=datos.get("note") or note or "",
            key=f"{nombre}|{need_unit}",
        )

        #No está en casa: no se resta nada, se ofrece guardarlo o comprarlo
        if entry is None:
            etiqueta, color = STATUS_STYLE["nuevo"]
            return ConsumeRow(
                **base, in_pantry=False, selected=False, status="nuevo",
                status_label=etiqueta, status_color=color,
                take_qty=need_qty, take_label=format_qty(need_qty, need_unit),
                have_label="—", after_label="—",
            )

        have_qty, have_unit = entry["quantity"], entry["unit"]
        take = convert_with_pack(need_qty, need_unit, have_unit, pack_qty, pack_unit)

        #Se sabe que está, pero no en qué se mide: mejor decirlo que restar mal
        if take is None:
            etiqueta, color = STATUS_STYLE["medida"]
            return ConsumeRow(
                **base, in_pantry=True, selected=False, status="medida",
                status_label=etiqueta, status_color=color,
                have_qty=have_qty, have_unit=have_unit,
                have_label=format_qty(have_qty, have_unit),
                take_qty=0, take_label=format_qty(0, have_unit), after_label=format_qty(have_qty, have_unit),
            )

        take = round(take, 3)
        falta = take > have_qty + 0.0001
        #No se puede restar más de lo que hay: se resta lo que queda y se avisa
        real = min(take, have_qty)
        after = round(have_qty - real, 3)
        estado = "falta" if falta else ("justo" if after <= 0.0001 else "ok")
        etiqueta, color = STATUS_STYLE[estado]
        if estado == "falta":
            etiqueta = f"No llega: faltan {format_qty(round(take - have_qty, 3), have_unit)}"
        return ConsumeRow(
            **base, in_pantry=True, selected=True, status=estado,
            status_label=etiqueta, status_color=color,
            have_qty=have_qty, have_unit=have_unit,
            have_label=format_qty(have_qty, have_unit),
            take_qty=real, take_label=format_qty(real, have_unit),
            after_label=format_qty(after, have_unit),
        )

    async def _rebuild(self):
        calendar_state = await self.get_state(CalendarState)
        self._build_rows(calendar_state)

    # ------------------------------------------------------------------
    # Ajustes de la ventana
    # ------------------------------------------------------------------
    @rx.event
    async def set_people(self, value: str):
        self.people = value
        await self._rebuild()

    @rx.event
    async def bump_people(self, delta: int):
        self.people = str(max(1, min(50, self.people_int + delta)))
        await self._rebuild()

    @rx.event
    async def toggle_staples(self, value: bool):
        self.include_staples = value
        await self._rebuild()

    @rx.event
    def toggle_row(self, key: str):
        """Quitar de la resta algo que no has usado (o has usado de otro sitio)."""
        self.rows = [
            r.copy(update={"selected": not r.selected}) if r.key == key else r
            for r in self.rows
        ]

    @rx.event
    def adjust_take(self, key: str, delta: float):
        """Afina a mano cuánto se resta: la receta es una guía, no una báscula."""
        nuevas = []
        for r in self.rows:
            if r.key != key:
                nuevas.append(r)
                continue
            #El paso se adapta a la escala: no tiene sentido subir de 1 en 1 en kg
            paso = delta if r.have_qty >= 10 or r.take_qty >= 10 else delta * 0.1
            nuevo = max(0.0, round(r.take_qty + paso, 3))
            if r.in_pantry:
                nuevo = min(nuevo, r.have_qty)
                after = round(r.have_qty - nuevo, 3)
                nuevas.append(r.copy(update={
                    "take_qty": nuevo,
                    "take_label": format_qty(nuevo, r.have_unit),
                    "after_label": format_qty(after, r.have_unit),
                }))
            else:
                nuevas.append(r.copy(update={
                    "take_qty": nuevo,
                    "take_label": format_qty(nuevo, r.need_unit),
                }))
        self.rows = nuevas

    # ------------------------------------------------------------------
    # Lecturas para la interfaz
    # ------------------------------------------------------------------
    @rx.var
    def has_rows(self) -> bool:
        return len(self.rows) > 0

    @rx.var
    def slot_label(self) -> str:
        return "Comida" if self.slot == "meal" else "Cena"

    @rx.var
    def slot_icon(self) -> str:
        return "sun" if self.slot == "meal" else "moon"

    @rx.var
    def to_take_count(self) -> int:
        return len([r for r in self.rows if r.selected and r.in_pantry and r.take_qty > 0])

    @rx.var
    def missing_rows(self) -> List[ConsumeRow]:
        return [r for r in self.rows if not r.in_pantry]

    @rx.var
    def missing_count(self) -> int:
        return len(self.missing_rows)

    @rx.var
    def short_count(self) -> int:
        return len([r for r in self.rows if r.status == "falta"])

    @rx.var
    def can_apply(self) -> bool:
        return (not self.unavailable) and self.to_take_count > 0

    # ------------------------------------------------------------------
    # Aplicar (la autorización)
    # ------------------------------------------------------------------
    @rx.event
    async def apply(self):
        """Resta de la despensa lo marcado y deja constancia de quién y qué."""
        if self.unavailable or not self.pantry_id:
            return rx.toast.error(
                "La despensa no está disponible. ¿Falta la migración 018_pantry.sql?",
                position="top-center",
            )
        marcadas = [r for r in self.rows if r.selected and r.in_pantry and r.take_qty > 0]
        if not marcadas:
            return rx.toast.error("No hay nada marcado que restar", position="top-center")

        self.applying = True
        try:
            takes = [(r.name, r.take_qty, r.have_unit) for r in marcadas]
            ok, tocados = await consume_from_pantry(self.pantry_id, self.current_user_id, takes)
            if not ok:
                return rx.toast.error("No se pudo descontar de la despensa", position="top-center")

            detalle = [{"name": r.name, "qty": r.take_qty, "unit": r.have_unit} for r in marcadas]
            await set_day_consumed(
                self.day_id, self.slot, True, self.current_user_id, self.username, detalle,
            )

            comida = self.meal_name
            fecha = self.date_label
            await self._notify_others(comida, fecha, len(marcadas))

            #El calendario tiene que enseñar ya el tick de "descontado"
            calendar_state = await self.get_state(CalendarState)
            await calendar_state.refresh_page()

            self.show = False
            avisos = [rx.toast.success(
                f"{tocados} ingredientes descontados de la despensa",
                position="top-center",
                duration=6000,
            )]
            if self.missing_count:
                avisos.append(rx.toast.warning(
                    f"{self.missing_count} ingredientes no estaban en la despensa: revísalos",
                    position="top-center",
                    duration=8000,
                ))
            return avisos
        finally:
            self.applying = False

    async def _notify_others(self, comida: str, fecha: str, cuantos: int):
        """Avisa al resto de la casa de que ya se ha restado.

        Es lo que evita que dos personas descuenten la misma cena: en cuanto uno
        lo hace, a los demás les llega y ven el tick.
        """
        if not self.calendar_id:
            return
        try:
            usuarios = await get_shared_users(self.calendar_id)
        except Exception as e:
            logger.warning(f"No se pudo avisar del descuento: {e}")
            return
        momento = "la comida" if self.slot == "meal" else "la cena"
        for user in usuarios:
            if user.username == self.username:
                continue
            await asyncio.to_thread(
                NotificationState.enviar_aviso_despensa,
                titulo="📦 Despensa actualizada",
                mensaje=(
                    f"{self.username} ha restado {cuantos} ingredientes de {momento} "
                    f"({comida}) del {fecha}"
                ),
                destino=user.username,
                url=f"/despensa?dia={self.day_id}&slot={self.slot}",
                tag=f"stock-{self.day_id}-{self.slot}",
            )

    @rx.event
    async def undo(self):
        """Deshace el descuento: devuelve a la despensa lo que se restó.

        Se puede porque queda guardado **qué** se restó exactamente, así que
        devolverlo es exacto y no una estimación.
        """
        if not self.already_items and not self.pantry_id:
            return
        day = await get_day_details(self.day_id, self.current_user_id)
        if not day:
            return
        detalle = day.meal_consumed_items if self.slot == "meal" else day.dinner_consumed_items
        if not detalle:
            #Sin detalle guardado (descuento antiguo) solo se quita la marca
            await set_day_consumed(self.day_id, self.slot, False, self.current_user_id)
            await self._load()
            return rx.toast.info("Marca quitada (no había detalle que devolver)", position="top-center")

        #`detalle` viene ya formateado para leer; el crudo está en la base, así
        #que se rehace desde ahí para devolver las cantidades exactas
        crudo = await self._raw_consumed()
        devueltos = 0
        for item in crudo:
            if await add_pantry_item(
                self.pantry_id, item["name"], float(item.get("qty") or 0), item.get("unit") or "ud",
                guess_place("otros", item["name"]), "otros", "", "", 0, "",
                self.current_user_id, sumar=True,
            ):
                devueltos += 1
        await set_day_consumed(self.day_id, self.slot, False, self.current_user_id)
        calendar_state = await self.get_state(CalendarState)
        await calendar_state.refresh_page()
        await self._load()
        return rx.toast.success(
            f"Devueltos {devueltos} ingredientes a la despensa", position="top-center", duration=6000
        )

    async def _raw_consumed(self) -> List[dict]:
        """El detalle sin formatear de lo que se descontó, desde la base."""
        from Calendario.utils.api import SUPABASE_API

        try:
            columna = "meal_consumed_items" if self.slot == "meal" else "dinner_consumed_items"
            res = SUPABASE_API.supabase.from_("days").select(columna).eq("id", self.day_id).execute()
            crudo = (res.data or [{}])[0].get(columna) or []
            return [i for i in crudo if isinstance(i, dict) and i.get("name")]
        except Exception as e:
            logger.warning(f"No se pudo leer el detalle del descuento: {e}")
            return []

    # ------------------------------------------------------------------
    # Lo que no está en la despensa
    # ------------------------------------------------------------------
    @rx.event
    async def stock_missing(self, key: str):
        """Guarda en la despensa un ingrediente que no estaba."""
        row = next((r for r in self.rows if r.key == key), None)
        if not row or not self.pantry_id:
            return
        ok = await add_pantry_item(
            self.pantry_id, row.name, row.take_qty or row.need_qty, row.need_unit,
            guess_place(row.cat, row.name), row.cat, row.shop, row.note, 0, "",
            self.current_user_id, sumar=True,
        )
        if not ok:
            return rx.toast.error("No se pudo guardar en la despensa", position="top-center")
        await self._load()
        return rx.toast.success(f"{row.name} guardado en la despensa", position="top-center")

    @rx.event
    async def buy_missing(self, key: str):
        """Manda a la lista de la compra un ingrediente que no estaba en casa."""
        row = next((r for r in self.rows if r.key == key), None)
        if not row:
            return
        lists = await get_user_shopping_lists(self.current_user_id)
        if not lists:
            return rx.toast.error("No tienes lista de la compra activa", position="top-center")
        ok = await add_item_to_shopping_list(
            lists[0]["id"], row.name, row.need_qty, row.shop, self.current_user_id,
            row.need_unit, row.cat, row.staple, row.note,
        )
        if not ok:
            return rx.toast.error("No se pudo añadir a la lista", position="top-center")
        return rx.toast.success(f"{row.name} añadido a la lista de la compra", position="top-center")

    @rx.event
    async def buy_all_missing(self):
        """Manda a la compra todo lo que faltaba en casa, de una vez."""
        faltan = [r for r in self.rows if not r.in_pantry]
        if not faltan:
            return rx.toast.info("No falta nada", position="top-center")
        lists = await get_user_shopping_lists(self.current_user_id)
        if not lists:
            return rx.toast.error("No tienes lista de la compra activa", position="top-center")
        añadidos = 0
        for row in faltan:
            if await add_item_to_shopping_list(
                lists[0]["id"], row.name, row.need_qty, row.shop, self.current_user_id,
                row.need_unit, row.cat, row.staple, row.note,
            ):
                añadidos += 1
        return rx.toast.success(
            f"{añadidos} ingredientes añadidos a la lista de la compra",
            position="top-center", duration=6000,
        )
