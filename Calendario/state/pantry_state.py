# Calendario/state/pantry_state.py
"""
La despensa: lo que hay en casa.

La app sabía qué hay que comprar y qué se va a cocinar, pero no lo que ya
tienes. Eso se pagaba en el súper ("¿quedaba arroz?") y en casa (tres botes de
pimentón y ni un huevo).

Aquí está el stock, y se llena solo: al marcar un producto como comprado en la
lista, su cantidad entra en la despensa. Desmarcarlo lo saca otra vez, porque
desmarcar es deshacer.

Cada producto sabe **dónde se guarda** (nevera, congelador, despensa), cuándo
caduca y por debajo de qué cantidad hay que reponerlo. Con eso, la despensa
cierra el círculo: lo que se está acabando vuelve a la lista de la compra de un
toque.

Es una lista **independiente** de la de la compra: tiene su propia gente y se
comparte por su cuenta, igual que aquella.

Si la migración 018 no está aplicada, la pantalla lo dice y el resto de la app
sigue funcionando igual (la compra simplemente no suma stock).
"""

import asyncio
import logging
from datetime import date
from typing import Dict, List, Optional

import reflex as rx

from Calendario import theme
from Calendario.model.model import PantryGroup, PantryRow, User
from Calendario.state.products_state import ProductsState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    add_item_to_shopping_list,
    add_pantry_item,
    adjust_pantry_item,
    clear_pantry_items,
    delete_pantry_item,
    get_pantry,
    get_pantry_users,
    get_user_shopping_lists,
    merge_and_share_pantry,
    remove_user_from_pantry,
    set_pantry_auto_stock,
    update_pantry_item,
)
from Calendario.utils.pantry import expiry_status, guess_place, is_low, normalize_entry, since_label
from Calendario.utils.purchase import convert_qty, format_qty

logger = logging.getLogger(__name__)

#Cada cuánto se relee la despensa compartida (segundos). El mismo ritmo que la
#lista de la compra: si tu pareja gasta la leche, tiene que verse aquí.
SYNC_SECONDS = 6


def _numero(valor: float) -> str:
    """'2.0' se ve fatal en un campo de cantidad: se escribe '2'."""
    return str(int(valor)) if float(valor) == int(valor) else str(valor)


class PantryState(rx.State):
    # Datos de la despensa
    items: Dict[str, Dict] = {}
    current_pantry_id: Optional[int] = None
    current_user_id: int = -1
    #Sumar a la despensa lo que se marca como comprado en la lista
    auto_stock: bool = True
    #La migración 018 no está aplicada: se puede ver la pantalla, pero no guardar
    unavailable: bool = False

    # Alta de producto. Mismos campos que un producto de la compra (unidad,
    # sección, supermercado, nota) más los de casa: sitio, mínimo y caducidad.
    new_name: str = ""
    new_qty: str = "1"
    new_unit: str = "ud"
    new_place: str = "despensa"
    new_cat: str = "otros"
    new_shop: str = ""
    new_note: str = ""
    new_min: str = "0"
    new_expires: str = ""
    show_add_form: bool = False

    # Edición
    editing_name: str = ""
    edit_name: str = ""
    edit_qty: str = "1"
    edit_unit: str = "ud"
    edit_place: str = "despensa"
    edit_cat: str = "otros"
    edit_shop: str = ""
    edit_note: str = ""
    edit_min: str = "0"
    edit_expires: str = ""
    show_edit_form: bool = False

    # Filtros
    search: str = ""
    only_low: bool = False
    only_expiring: bool = False
    place_filter: str = ""

    # Con quién se comparte. La despensa es una lista **independiente** de la de
    # la compra: se comparte por su cuenta y con quien tú digas.
    show_users_panel: bool = False
    shared_users: List[User] = []
    new_user_input: str = ""
    add_user_error: str = ""

    #Evita que se solapen varios sondeos si se recarga la página
    _polling: bool = False

    # ------------------------------------------------------------
    # Carga y sincronización
    # ------------------------------------------------------------
    def _normalize_items(self, raw_items: dict) -> dict:
        """Rellena los campos que falten, para que el resto del estado no tenga
        que ir comprobando si existen."""
        return {name: normalize_entry(data) for name, data in (raw_items or {}).items()}

    @rx.event
    async def load_pantry(self):
        """Carga la despensa del usuario (creándola la primera vez)."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        self.current_user_id = user_state.current_user.id

        pantry = await get_pantry(self.current_user_id)
        if not pantry:
            #Sin tabla `pantries` no hay nada que enseñar, pero la pantalla se
            #pinta igual y explica qué falta
            self.unavailable = True
            self.current_pantry_id = None
            self.items = {}
            return
        self.unavailable = False
        self.current_pantry_id = pantry["id"]
        self.auto_stock = bool(pantry.get("auto_stock", True))
        self.items = self._normalize_items(pantry.get("items"))

    @rx.event(background=True)
    async def sync_loop(self):
        """Mantiene el stock al día sin botón de refrescar.

        La despensa es compartida igual que la lista: si tu pareja se acaba la
        leche o marca la compra en el súper, tiene que aparecer aquí sin tocar
        nada. Solo se reasigna el estado si algo ha cambiado de verdad, para no
        repintar mientras estás escribiendo.
        """
        async with self:
            if self._polling:
                return
            self._polling = True
        try:
            while True:
                await asyncio.sleep(SYNC_SECONDS)
                async with self:
                    if self.router.url.path != "/despensa":
                        self._polling = False
                        return
                    if not self.current_pantry_id or self.show_add_form or self.show_edit_form:
                        continue
                    try:
                        pantry = await get_pantry(self.current_user_id)
                    except Exception as e:
                        logger.warning(f"Sondeo de la despensa fallido: {e}")
                        continue
                    if not pantry:
                        continue
                    fresh = self._normalize_items(pantry.get("items"))
                    if fresh != self.items:
                        self.items = fresh
                    self.auto_stock = bool(pantry.get("auto_stock", True))
        finally:
            async with self:
                self._polling = False

    # ------------------------------------------------------------
    # Vistas de los datos
    # ------------------------------------------------------------
    def _row(self, name: str, data: dict) -> PantryRow:
        entry = normalize_entry(data)
        place = entry["place"] if entry["place"] in theme.PANTRY_PLACE_STYLE else "otros"
        label, estado = expiry_status(entry["expires"], date.today())
        color = {
            "expired": theme.DANGER,
            "today": theme.DANGER,
            "soon": theme.WARNING,
            "ok": theme.DIM,
        }.get(estado, "")
        return PantryRow(
            name=name,
            quantity=entry["quantity"],
            qty_label=format_qty(entry["quantity"], entry["unit"]),
            unit=entry["unit"],
            place=place,
            cat=entry["cat"],
            shop=entry["shop"],
            note=entry["note"],
            min_qty=entry["min_qty"],
            min_label=(
                "Mínimo " + format_qty(entry["min_qty"], entry["unit"]) if entry["min_qty"] > 0 else ""
            ),
            low=is_low(entry),
            empty=entry["quantity"] <= 0,
            expires=entry["expires"],
            expiry_label=label,
            expiry_color=color,
            expired=estado == "expired",
            expiring=estado in ("expired", "today", "soon"),
            updated_label=since_label(entry["updated_at"]),
        )

    def _visible_rows(self) -> List[PantryRow]:
        query = self.search.strip().lower()
        rows = []
        for name, data in self.items.items():
            row = self._row(name, data)
            if self.only_low and not row.low:
                continue
            if self.only_expiring and not row.expiring:
                continue
            if self.place_filter and row.place != self.place_filter:
                continue
            if query:
                heno = " ".join([row.note, row.shop, theme.place_label(row.place)]).lower()
                if query not in name.lower() and query not in heno:
                    continue
            rows.append(row)
        return rows

    @rx.var
    def groups(self) -> List[PantryGroup]:
        """El stock agrupado por dónde está guardado.

        Dentro de cada sitio, primero lo que hay que reponer y lo que caduca:
        es a lo que hay que hacer caso, y así no se pierde entre lo demás.
        """
        buckets: Dict[str, List[PantryRow]] = {}
        for row in self._visible_rows():
            buckets.setdefault(row.place, []).append(row)

        groups: List[PantryGroup] = []
        for place in theme.PANTRY_PLACE_ORDER:
            rows = buckets.get(place)
            if not rows:
                continue
            rows.sort(key=lambda r: (not r.low, not r.expiring, r.name.lower()))
            groups.append(
                PantryGroup(
                    place=place,
                    label=theme.place_label(place),
                    color=theme.place_color(place),
                    icon=theme.place_icon(place),
                    items=rows,
                    total=len(rows),
                    low=len([r for r in rows if r.low]),
                )
            )
        return groups

    def _all_rows(self) -> List[PantryRow]:
        return [self._row(name, data) for name, data in self.items.items()]

    @rx.var
    def total_items(self) -> int:
        return len(self.items)

    @rx.var
    def low_count(self) -> int:
        return len([1 for r in self._all_rows() if r.low])

    @rx.var
    def expiring_count(self) -> int:
        return len([1 for r in self._all_rows() if r.expiring and not r.expired])

    @rx.var
    def expired_count(self) -> int:
        return len([1 for r in self._all_rows() if r.expired])

    @rx.var
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @rx.var
    def has_visible_items(self) -> bool:
        return len(self._visible_rows()) > 0

    @rx.var
    def is_filtering(self) -> bool:
        return bool(self.search.strip()) or self.only_low or self.only_expiring or bool(self.place_filter)

    @rx.var
    def has_low(self) -> bool:
        return any(r.low for r in self._all_rows())

    # ------------------------------------------------------------
    # Filtros
    # ------------------------------------------------------------
    @rx.event
    def set_search(self, value: str):
        self.search = value

    @rx.event
    def toggle_only_low(self):
        self.only_low = not self.only_low

    @rx.event
    def toggle_only_expiring(self):
        self.only_expiring = not self.only_expiring

    @rx.event
    def filter_place(self, place: str):
        """Un toque en un sitio lo aísla; otro toque lo suelta."""
        self.place_filter = "" if self.place_filter == place else place

    @rx.event
    def clear_filters(self):
        self.search = ""
        self.only_low = False
        self.only_expiring = False
        self.place_filter = ""

    # ------------------------------------------------------------
    # Alta
    # ------------------------------------------------------------
    @rx.event
    async def open_add_form(self):
        self.show_add_form = True
        self._reset_new()
        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()

    @rx.event
    def close_add_form(self):
        self.show_add_form = False

    def _reset_new(self):
        self.new_name = ""
        self.new_qty = "1"
        self.new_unit = "ud"
        self.new_place = "despensa"
        self.new_cat = "otros"
        self.new_shop = ""
        self.new_note = ""
        self.new_min = "0"
        self.new_expires = ""

    @rx.event
    async def pick_new_product(self, name: str):
        """Elige el producto y rellena el formulario con lo que ya se sabe de él.

        Si ya está en casa, manda lo que tenga puesto en la despensa (dónde se
        guarda, su mínimo, su caducidad): así reponer es teclear la cantidad y
        nada más, sin perder por el camino lo que ya habías configurado.

        Si es nuevo, los valores salen del catálogo de productos y el sitio se
        adivina de su sección del súper: los lácteos a la nevera, los congelados
        al congelador. Todo se puede cambiar.
        """
        clean = (name or "").strip()
        self.new_name = clean
        if not clean:
            return
        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()
        product = products_state.find(clean)

        #Lo que entra en casa es **un envase del súper**, no la cantidad que
        #pide una receta: si el producto tiene puesta su medida de compra
        #(un brik son 1 l), es esa la que se propone aquí.
        if product:
            usa_pack = product.pack_qty > 0 and bool(product.pack_unit)
            self.new_qty = _numero(product.pack_qty if usa_pack else product.qty)
            self.new_unit = product.pack_unit if usa_pack else product.unit
            self.new_cat = product.cat
            self.new_shop = product.shop
            self.new_note = product.note
        else:
            self.new_qty = "1"
        self.new_place = guess_place(product.cat if product else "otros", clean)
        self.new_min = "0"
        self.new_expires = ""

        actual = self.items.get(clean)
        if actual:
            entry = normalize_entry(actual)
            self.new_unit = entry["unit"]
            self.new_place = entry["place"]
            self.new_cat = entry["cat"]
            self.new_shop = entry["shop"] or self.new_shop
            self.new_note = entry["note"] or self.new_note
            self.new_min = _numero(entry["min_qty"])
            self.new_expires = entry["expires"]

    @rx.var
    def new_already_home(self) -> str:
        """'2 briks' de lo que se está guardando, si ya había en casa."""
        actual = self.items.get(self.new_name.strip())
        if not actual:
            return ""
        entry = normalize_entry(actual)
        return format_qty(entry["quantity"], entry["unit"])

    @rx.event
    def set_new_name(self, value: str):
        self.new_name = value

    @rx.event
    def set_new_qty(self, value: str):
        self.new_qty = value

    @rx.event
    def set_new_unit(self, value: str):
        self.new_unit = value

    @rx.event
    def set_new_place(self, value: str):
        self.new_place = value

    @rx.event
    def set_new_cat(self, value: str):
        self.new_cat = value

    @rx.event
    def set_new_shop(self, value: str):
        self.new_shop = value

    @rx.event
    def set_new_note(self, value: str):
        self.new_note = value

    @rx.event
    def set_new_min(self, value: str):
        self.new_min = value

    @rx.event
    def set_new_expires(self, value: str):
        self.new_expires = value

    @staticmethod
    def _to_float(value: str, default: float = 0) -> Optional[float]:
        try:
            return float((value or "").replace(",", "."))
        except (ValueError, AttributeError):
            return None if value else default

    @rx.event
    async def add_item(self):
        if self.unavailable or not self.current_pantry_id:
            return rx.toast.error(
                "La despensa no está disponible. ¿Falta aplicar la migración 018_pantry.sql?",
                position="top-center",
            )
        name = self.new_name.strip()
        if not name:
            return rx.toast.error("Elige un producto", position="top-center")
        if len(name) > 40:
            return rx.toast.error("Máximo 40 caracteres", position="top-center")

        qty = self._to_float(self.new_qty)
        if qty is None or qty < 0:
            return rx.toast.error("La cantidad debe ser un número", position="top-center")
        minimo = self._to_float(self.new_min, 0) or 0

        #Si ya estaba en casa, se suma en vez de sustituir: casi siempre lo que
        #se hace aquí es reponer, no recontar
        ya_estaba = name in self.items
        ok = await add_pantry_item(
            self.current_pantry_id, name, qty, self.new_unit, self.new_place,
            self.new_cat, self.new_shop.strip(), self.new_note.strip()[:60],
            minimo, self.new_expires, self.current_user_id, sumar=ya_estaba,
        )
        if not ok:
            return rx.toast.error("No se pudo guardar en la despensa", position="top-center")

        self.show_add_form = False
        self._reset_new()
        await self.load_pantry()
        if ya_estaba:
            return rx.toast.success(f"{name}: sumado a lo que ya tenías", position="top-center")
        return rx.toast.success(f"{name} está ahora en la despensa", position="top-center")

    # ------------------------------------------------------------
    # Edición
    # ------------------------------------------------------------
    @rx.event
    async def open_editor(self, name: str):
        data = self.items.get(name)
        if not data:
            return
        entry = normalize_entry(data)
        self.editing_name = name
        self.edit_name = name
        self.edit_qty = _numero(entry["quantity"])
        self.edit_unit = entry["unit"]
        self.edit_place = entry["place"]
        self.edit_cat = entry["cat"]
        self.edit_shop = entry["shop"]
        self.edit_note = entry["note"]
        self.edit_min = _numero(entry["min_qty"])
        self.edit_expires = entry["expires"]
        self.show_edit_form = True
        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()

    @rx.event
    def close_editor(self):
        self.show_edit_form = False
        self.editing_name = ""

    @rx.event
    async def pick_edit_product(self, name: str):
        clean = (name or "").strip()
        self.edit_name = clean
        if not clean:
            return
        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()
        product = products_state.find(clean)
        if product:
            self.edit_unit = product.unit
            self.edit_cat = product.cat
            self.edit_shop = product.shop

    @rx.event
    def set_edit_name(self, value: str):
        self.edit_name = value

    @rx.event
    def set_edit_qty(self, value: str):
        self.edit_qty = value

    @rx.event
    def set_edit_unit(self, value: str):
        self.edit_unit = value

    @rx.event
    def set_edit_place(self, value: str):
        self.edit_place = value

    @rx.event
    def set_edit_cat(self, value: str):
        self.edit_cat = value

    @rx.event
    def set_edit_shop(self, value: str):
        self.edit_shop = value

    @rx.event
    def set_edit_note(self, value: str):
        self.edit_note = value

    @rx.event
    def set_edit_min(self, value: str):
        self.edit_min = value

    @rx.event
    def set_edit_expires(self, value: str):
        self.edit_expires = value

    @rx.event
    async def save_edit(self):
        if not self.current_pantry_id or not self.editing_name:
            return
        name = self.edit_name.strip()
        if not name:
            return rx.toast.error("El nombre no puede estar vacío", position="top-center")
        qty = self._to_float(self.edit_qty)
        if qty is None or qty < 0:
            return rx.toast.error("La cantidad debe ser un número", position="top-center")
        minimo = self._to_float(self.edit_min, 0) or 0

        ok = await update_pantry_item(
            self.current_pantry_id, self.editing_name, name, qty, self.edit_unit,
            self.edit_place, self.edit_cat, self.edit_shop.strip(),
            self.edit_note.strip()[:60], minimo, self.edit_expires, self.current_user_id,
        )
        if not ok:
            return rx.toast.error("No se pudo guardar (¿ya tienes otro con ese nombre?)", position="top-center")
        self.show_edit_form = False
        self.editing_name = ""
        await self.load_pantry()
        return rx.toast.success("Despensa actualizada", position="top-center")

    # ------------------------------------------------------------
    # Gastar, reponer y tirar
    # ------------------------------------------------------------
    @rx.event
    async def adjust_qty(self, name: str, delta: float):
        """Sube o baja la cantidad desde la propia fila.

        Se pinta al momento y se guarda después: gastar algo mientras cocinas
        no puede tardar en verse.
        """
        data = self.items.get(name)
        if not data or not self.current_pantry_id:
            return
        actual = normalize_entry(data)
        nueva = max(0.0, round(actual["quantity"] + delta, 3))
        self.items = {
            n: ({**d, "quantity": nueva} if n == name else d)
            for n, d in self.items.items()
        }
        if not await adjust_pantry_item(self.current_pantry_id, name, delta, self.current_user_id):
            self.items = {
                n: ({**d, "quantity": actual["quantity"]} if n == name else d)
                for n, d in self.items.items()
            }
            return rx.toast.error("No se pudo actualizar", position="top-center")

    @rx.event
    async def remove_item(self, name: str):
        if not self.current_pantry_id:
            return
        if not await delete_pantry_item(self.current_pantry_id, name, self.current_user_id):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        await self.load_pantry()

    @rx.event
    async def clear_empty(self):
        """Quita de la despensa todo lo que está a cero."""
        if not self.current_pantry_id:
            return
        borrados = await clear_pantry_items(self.current_pantry_id, self.current_user_id, True)
        await self.load_pantry()
        if borrados:
            return rx.toast.success(f"{borrados} productos agotados eliminados", position="top-center")
        return rx.toast.info("No hay nada agotado", position="top-center")

    @rx.event
    async def clear_all(self):
        """Vacía la despensa entera (con confirmación en la interfaz)."""
        if not self.current_pantry_id:
            return
        borrados = await clear_pantry_items(self.current_pantry_id, self.current_user_id, False)
        await self.load_pantry()
        if borrados:
            return rx.toast.success(f"Despensa vaciada ({borrados} productos)", position="top-center")
        return rx.toast.info("La despensa ya estaba vacía", position="top-center")

    # ------------------------------------------------------------
    # De vuelta a la lista de la compra
    # ------------------------------------------------------------
    async def _send_to_list(self, rows: List[PantryRow]) -> tuple[int, int]:
        """Manda a la compra los productos indicados.

        Se pide **lo que falta hasta el mínimo** (y al menos uno): si te queda
        medio kilo de arroz y quieres tener dos, la lista pide kilo y medio, no
        dos kilos más.

        Lo que ya estuviera pedido no se pisa: solo se sube la cantidad si con
        lo apuntado no llegas al mínimo. Si no, pulsar «reponer» después de
        haber apuntado tres kilos a mano te los dejaría en kilo y medio.

        Devuelve `(añadidos, los que ya estaban bien pedidos)`.
        """
        lists = await get_user_shopping_lists(self.current_user_id)
        if not lists:
            return 0, 0
        list_id = lists[0]["id"]
        pedidos = lists[0].get("items") or {}

        añadidos = ya_estaban = 0
        for row in rows:
            falta = round(row.min_qty - row.quantity, 3) if row.min_qty > 0 else 0
            if falta <= 0:
                falta = 1

            actual = pedidos.get(row.name)
            if actual:
                apuntado = convert_qty(
                    float(actual.get("quantity") or 0), actual.get("unit") or "ud", row.unit
                )
                #Ya hay bastante pedido, o está pedido en una unidad que no se
                #puede comparar: se deja como está y no se toca nada
                if apuntado is None or apuntado >= falta:
                    ya_estaban += 1
                    continue

            if await add_item_to_shopping_list(
                list_id, row.name, falta, row.shop, self.current_user_id,
                row.unit, row.cat, False, row.note,
            ):
                añadidos += 1
        return añadidos, ya_estaban

    @rx.event
    async def to_shopping_list(self, name: str):
        """Manda un producto suelto a la lista de la compra."""
        data = self.items.get(name)
        if not data:
            return
        añadidos, ya_estaban = await self._send_to_list([self._row(name, data)])
        if ya_estaban:
            return rx.toast.info(f"{name} ya estaba en la lista de la compra", position="top-center")
        if not añadidos:
            return rx.toast.error("No se pudo añadir a la lista", position="top-center")
        return rx.toast.success(f"{name} añadido a la lista de la compra", position="top-center")

    @rx.event
    async def restock_all(self):
        """Manda a la compra todo lo que está por debajo del mínimo."""
        faltan = [r for r in self._all_rows() if r.low]
        if not faltan:
            return rx.toast.info("No falta nada por reponer", position="top-center")
        añadidos, ya_estaban = await self._send_to_list(faltan)
        if not añadidos:
            if ya_estaban:
                return rx.toast.info(
                    f"Los {ya_estaban} productos que faltan ya estaban en la lista",
                    position="top-center",
                )
            return rx.toast.error("No se pudo añadir a la lista", position="top-center")
        detalle = f"{añadidos} productos añadidos a la lista de la compra"
        if ya_estaban:
            detalle += f" ({ya_estaban} ya estaban apuntados)"
        return rx.toast.success(detalle, position="top-center", duration=6000)

    # ------------------------------------------------------------
    # Ajustes y quién la comparte
    # ------------------------------------------------------------
    @rx.event
    async def toggle_auto_stock(self, value: bool):
        if not self.current_pantry_id:
            return
        self.auto_stock = value
        if not await set_pantry_auto_stock(self.current_pantry_id, self.current_user_id, value):
            self.auto_stock = not value
            return rx.toast.error("No se pudo cambiar el ajuste", position="top-center")
        if value:
            return rx.toast.success("Lo que compres entrará solo en la despensa", position="top-center")
        return rx.toast.info("La despensa ya no se llena sola al comprar", position="top-center")

    async def load_shared_users(self):
        if not self.current_pantry_id:
            return
        self.shared_users = await get_pantry_users(self.current_pantry_id)

    @rx.event
    async def toggle_users_panel(self):
        self.show_users_panel = not self.show_users_panel
        if self.show_users_panel:
            await self.load_shared_users()
        else:
            self.shared_users = []
            self.new_user_input = ""
            self.add_user_error = ""

    @rx.event
    def set_new_user_input(self, value: str):
        self.new_user_input = value

    @rx.event
    async def add_user_to_pantry(self):
        """Comparte la despensa con otro usuario (fusionando los dos stocks)."""
        self.add_user_error = ""
        username = self.new_user_input.strip().lower()
        if not username:
            self.add_user_error = "Nombre de usuario requerido"
            return
        if self.unavailable:
            return rx.toast.error(
                "La despensa no está disponible. ¿Falta aplicar la migración 018_pantry.sql?",
                position="top-center",
            )

        ok, msg = await merge_and_share_pantry(self.current_user_id, username)
        if not ok:
            self.add_user_error = msg
            return rx.toast.error(msg, position="top-center")

        self.new_user_input = ""
        await self.load_pantry()
        await self.load_shared_users()
        self.show_users_panel = False
        return rx.toast.success(msg, position="top-center", duration=6000)

    @rx.event
    async def remove_user(self, user_id: int, username: str):
        """Saca a alguien de la despensa. Se lleva una copia del stock."""
        if user_id == self.current_user_id:
            return rx.toast.error("No puedes eliminarte a ti mismo", position="top-center")
        if not self.current_pantry_id:
            return
        if not await remove_user_from_pantry(self.current_pantry_id, user_id, self.current_user_id):
            return rx.toast.error("No se pudo eliminar al usuario", position="top-center")
        await self.load_shared_users()
        return rx.toast.success(
            f"{username} ya no comparte la despensa. Se le ha dejado una copia del stock.",
            position="top-center",
            duration=6000,
        )
