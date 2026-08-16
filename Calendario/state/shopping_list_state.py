import asyncio
import logging
import reflex as rx
from typing import Dict, List, Optional

from Calendario import theme
from Calendario.model.model import (
    GeneratedItem,
    ShoppingGroup,
    ShoppingRow,
    Supermarket,
    User,
)
from Calendario.state.calendar_state import CalendarState
from Calendario.state.products_state import ProductsState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    add_item_to_shopping_list,
    add_recipe_to_shopping_list,
    add_user_to_list,
    clear_bought_shopping_items,
    clear_all_shopping_items,
    set_all_shopping_items_bought,
    get_shopping_list_users,
    get_user_by_username,
    get_user_shopping_lists,
    merge_and_share_shopping_list,
    remove_item_from_shopping_list,
    remove_user_from_list,
    toggle_shopping_item_status,
    update_shopping_item,
    get_supermarkets,
    add_supermarket as api_add_supermarket,
    update_supermarket_color as api_update_supermarket_color,
    update_supermarket as api_update_supermarket,
    delete_supermarket as api_delete_supermarket,
    get_pantry_stock,
)
#Mismo formateo y las mismas reglas de compra que el menú semanal: '2 botes',
#'1,5 kg'... Añadir una comida suelta tiene que dar exactamente lo mismo que
#planificarla en la semana, o las cantidades no cuadrarían entre las dos vías.
from Calendario.utils.purchase import format_qty, to_purchase

#Las cantidades del recetario están escritas para 2 comensales
BASE_SERVINGS = 2

logger = logging.getLogger(__name__)


def _numero(valor: float) -> str:
    """'2.0' se ve fatal en un campo de cantidad: se escribe '2'."""
    return str(int(valor)) if float(valor) == int(valor) else str(valor)

#Cada cuánto se relee la lista compartida (segundos)
SYNC_SECONDS = 4

#Paleta para etiquetar supermercados de un vistazo
SHOP_COLORS = [
    "#22c55e", "#38bdf8", "#3b82f6", "#a78bfa",
    "#f472b6", "#ef4444", "#f97316", "#eab308",
]

class ShoppingListState(rx.State):
    # Datos de la lista
    items: Dict[str, Dict] = {}
    current_list_id: Optional[int] = None
    current_user_id: int = -1

    # Formulario de añadir producto. Lleva los mismos campos que un ingrediente
    # del recetario: lo que se escribe en un sitio se entiende en el otro.
    new_item_name: str = ""
    new_item_qty: str = "1"
    new_item_unit: str = "ud"
    new_item_shop: str = ""
    new_item_cat: str = "otros"
    new_item_staple: bool = False
    new_item_note: str = ""
    show_add_form: bool = False
    errors: Dict[str, str] = {"name": "", "quantity": "", "supermarket": ""}

    # Añadir una comida entera. Cocinar algo fuera del menú semanal (una tarta
    # para llevar al trabajo, una cena para invitados) obligaba a ir mirando la
    # receta y copiar sus ingredientes a mano uno a uno. Aquí se elige la
    # comida, se dice para cuánta gente y sus ingredientes caen ya escalados.
    show_meal_form: bool = False
    meal_pick: str = ""
    meal_people: str = str(BASE_SERVINGS)
    meal_include_staples: bool = False
    #Lo que se va a añadir, ya escalado y en unidades de compra
    meal_preview: List[GeneratedItem] = []
    adding_meal: bool = False

    # Edición de un producto ya existente: TODOS sus campos, incluidos los que
    # antes solo escribía el menú semanal (origen, generado automáticamente...)
    editing_name: str = ""
    edit_name: str = ""
    edit_qty: str = "1"
    edit_unit: str = "ud"
    edit_shop: str = ""
    edit_cat: str = "otros"
    edit_staple: bool = False
    edit_note: str = ""
    edit_bought: bool = False
    edit_source: str = ""
    #«Fijado» = el menú semanal no lo rehace al regenerar (auto=False)
    edit_pinned: bool = False
    show_edit_form: bool = False

    # Filtros de la vista
    search: str = ""
    hide_bought: bool = False

    # Gestión de usuarios
    show_users_panel: bool = False
    shared_users: List[User] = []
    new_user_input: str = ""
    add_user_error: str = ""

    # Lo que ya hay en casa, para avisar en la propia fila antes de volver a
    # echarlo al carro. Es {nombre en minúsculas: "2 briks"}; llega de la
    # despensa y se queda vacío si aún no está aplicada la migración 018.
    pantry_stock: Dict[str, str] = {}

    # Supermercados (nombre + color). Viven aquí y no en un estado aparte
    # porque solo se usan en esta pantalla.
    supermarkets: List[Supermarket] = []
    show_shops_panel: bool = False
    new_shop_name: str = ""
    new_shop_color: str = SHOP_COLORS[0]
    #Supermercado en edición (su nombre original). Vacío = estamos dando de alta
    editing_shop: str = ""

    # ------------------------------------------------------------
    # Supermercados
    # ------------------------------------------------------------
    async def load_supermarkets(self):
        rows = await get_supermarkets()
        self.supermarkets = [
            Supermarket(
                name=r["name"],
                color=r.get("color") or "#38bdf8",
                initial=(r["name"].strip()[:1] or "?").upper(),
            )
            for r in rows
        ]

    async def load_pantry_stock(self):
        """Lee lo que hay en casa para poder decirlo en cada fila de la lista."""
        try:
            stock = await get_pantry_stock(self.current_user_id)
        except Exception as e:
            logger.warning(f"No se pudo leer la despensa: {e}")
            return
        fresco = {
            name.strip().lower(): format_qty(data["quantity"], data["unit"])
            for name, data in (stock or {}).items()
        }
        #Solo se reasigna si ha cambiado: esto se relee en el sondeo y no puede
        #repintar la lista entera cada pocos segundos
        if fresco != self.pantry_stock:
            self.pantry_stock = fresco

    def _shop_style(self, name: str) -> tuple[str, str]:
        """(color, inicial) de un supermercado. Gris si ya no está en la lista."""
        if not name:
            return "", ""
        for shop in self.supermarkets:
            if shop.name.lower() == name.lower():
                return shop.color, shop.initial
        return theme.MUTED, (name.strip()[:1] or "?").upper()

    @rx.var
    def shop_names(self) -> List[str]:
        return [s.name for s in self.supermarkets]

    @rx.var
    def palette(self) -> List[str]:
        return SHOP_COLORS

    @rx.event
    async def open_shops_panel(self):
        self.show_shops_panel = True
        self._reset_shop_form()
        await self.load_supermarkets()

    @rx.event
    def close_shops_panel(self):
        self.show_shops_panel = False
        self._reset_shop_form()

    def _reset_shop_form(self):
        self.new_shop_name = ""
        self.new_shop_color = SHOP_COLORS[0]
        self.editing_shop = ""

    @rx.var
    def is_editing_shop(self) -> bool:
        return self.editing_shop != ""

    @rx.event
    def edit_supermarket(self, name: str):
        """Carga un supermercado en el formulario para cambiarle nombre y color."""
        shop = next((s for s in self.supermarkets if s.name == name), None)
        if not shop:
            return
        self.editing_shop = shop.name
        self.new_shop_name = shop.name
        self.new_shop_color = shop.color
        return rx.set_focus("supermercado-nombre")

    @rx.event
    def cancel_shop_edit(self):
        self._reset_shop_form()

    @rx.event
    def set_new_shop_name(self, value: str):
        self.new_shop_name = value

    @rx.event
    def set_new_shop_color(self, value: str):
        self.new_shop_color = value

    @rx.event
    async def add_supermarket(self):
        """Da de alta un supermercado, o guarda los cambios si se está editando."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        name = self.new_shop_name.strip()
        if not name:
            return rx.toast.error("Escribe el nombre del supermercado", position="top-center")
        if len(name) > 20:
            return rx.toast.error("Máximo 20 caracteres", position="top-center")

        #Editando: se permite conservar el mismo nombre (solo cambiar el color)
        if self.editing_shop:
            if any(
                s.name.lower() == name.lower() and s.name.lower() != self.editing_shop.lower()
                for s in self.supermarkets
            ):
                return rx.toast.error(f"'{name}' ya está en la lista", position="top-center")
            if not await api_update_supermarket(self.editing_shop, name, self.new_shop_color):
                return rx.toast.error("No se pudo guardar el cambio", position="top-center")
            anterior = self.editing_shop
            self._reset_shop_form()
            await self.load_supermarkets()
            await self.load_shopping_list()
            if anterior != name:
                return rx.toast.success(
                    f"'{anterior}' ahora es '{name}' (cambiado también en productos y recetas)",
                    position="top-center",
                )
            return rx.toast.success(f"{name} actualizado", position="top-center")

        if any(s.name.lower() == name.lower() for s in self.supermarkets):
            return rx.toast.error(f"'{name}' ya está en la lista", position="top-center")
        if not await api_add_supermarket(name, self.new_shop_color):
            return rx.toast.error(
                "No se pudo guardar. ¿Está aplicada la migración 007_supermarkets.sql?",
                position="top-center",
            )
        self.new_shop_name = ""
        await self.load_supermarkets()
        return rx.toast.success(f"{name} añadido", position="top-center")

    @rx.event
    async def recolor_supermarket(self, name: str, color: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if await api_update_supermarket_color(name, color):
            await self.load_supermarkets()

    @rx.event
    async def remove_supermarket(self, name: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if not await api_delete_supermarket(name):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        if self.editing_shop.lower() == name.lower():
            self._reset_shop_form()
        await self.load_supermarkets()
        return rx.toast.success(f"{name} eliminado", position="top-center")

    # ------------------------------------------------------------
    # Sincronización automática
    # ------------------------------------------------------------
    #Evita que se solapen varios sondeos si se recarga la página
    _polling: bool = False

    @rx.event(background=True)
    async def sync_loop(self):
        """Mantiene la lista al día sin botón de refrescar.

        La lista es compartida: si tu pareja tacha algo en el súper, tiene que
        aparecerte tachado sin tocar nada. Se relee cada pocos segundos y solo
        se reasigna el estado si algo ha cambiado de verdad, para no repintar
        la pantalla mientras estás escribiendo.
        """
        async with self:
            if self._polling:
                return
            self._polling = True
        try:
            while True:
                await asyncio.sleep(SYNC_SECONDS)
                async with self:
                    #Si el usuario ya no está en la lista, el bucle se apaga solo
                    if self.router.url.path != "/shopping_list":
                        self._polling = False
                        return
                    if not self.current_list_id or self.show_add_form or self.show_edit_form:
                        continue
                    try:
                        lists = await get_user_shopping_lists(self.current_user_id)
                    except Exception as e:
                        logger.warning(f"Sondeo de la lista fallido: {e}")
                        continue
                    if not lists:
                        continue
                    fresh = self._normalize_items(lists[0]["items"])
                    if fresh != self.items:
                        self.items = fresh
                        self.current_list_id = lists[0]["id"]
                    #Y lo que hay en casa, que cambia solo al marcar la compra
                    await self.load_pantry_stock()
        finally:
            async with self:
                self._polling = False

    # ------------------------------------------------------------
    # Normalización de datos
    # ------------------------------------------------------------
    def _normalize_items(self, raw_items: dict) -> dict:
        """Rellena los campos que las listas antiguas no tenían (unidad,
        categoría, origen, básico, nota), para que el resto del estado no tenga
        que ir comprobando si existen."""
        normalized = {}
        for name, details in (raw_items or {}).items():
            normalized[name] = {
                "quantity": details.get("quantity", 1),
                "supermarket": details.get("supermarket", ""),
                "bought": details.get("bought", False),
                "unit": details.get("unit", "ud"),
                "cat": details.get("cat", "otros"),
                "staple": details.get("staple", False),
                "note": details.get("note", ""),
                "auto": details.get("auto", False),
                "source": details.get("source", ""),
            }
        return normalized

    # ------------------------------------------------------------
    # Vistas de los datos
    # ------------------------------------------------------------
    @rx.var
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def _visible_items(self) -> list:
        query = self.search.strip().lower()
        rows = []
        for name, data in self.items.items():
            if self.hide_bought and data.get("bought", False):
                continue
            #Se busca por todo lo que se ve en la fila: nombre, receta de
            #origen, supermercado y nota
            if query:
                haystack = " ".join(
                    str(data.get(field, "") or "")
                    for field in ("source", "supermarket", "note")
                )
                if query not in name.lower() and query not in haystack.lower():
                    continue
            rows.append((name, data))
        return rows

    @rx.var
    def groups(self) -> List[ShoppingGroup]:
        """Lista agrupada por sección del súper, en orden de recorrido de la
        tienda. Dentro de cada sección, lo pendiente antes que lo comprado."""
        buckets: dict[str, list] = {}
        for name, data in self._visible_items():
            cat = data.get("cat", "otros")
            if cat not in theme.SHOP_CATEGORY_STYLE:
                cat = "otros"
            buckets.setdefault(cat, []).append(
                ShoppingRow(
                    name=name,
                    quantity=float(data.get("quantity", 1) or 0),
                    qty_label=format_qty(data.get("quantity", 1) or 0, data.get("unit", "ud")),
                    unit=data.get("unit", "ud"),
                    supermarket=data.get("supermarket", ""),
                    shop_color=self._shop_style(data.get("supermarket", ""))[0],
                    shop_initial=self._shop_style(data.get("supermarket", ""))[1],
                    bought=bool(data.get("bought", False)),
                    auto=bool(data.get("auto", False)),
                    source=data.get("source", ""),
                    staple=bool(data.get("staple", False)),
                    note=data.get("note", "") or "",
                    cat=cat,
                    at_home=self.pantry_stock.get(name.strip().lower(), ""),
                )
            )

        groups: List[ShoppingGroup] = []
        for cat in theme.SHOP_CATEGORY_ORDER:
            rows = buckets.get(cat)
            if not rows:
                continue
            rows.sort(key=lambda r: (r.bought, r.name.lower()))
            groups.append(
                ShoppingGroup(
                    cat=cat,
                    label=theme.shop_label(cat),
                    color=theme.shop_color(cat),
                    icon=theme.shop_icon(cat),
                    items=rows,
                    total=len(rows),
                    bought=len([r for r in rows if r.bought]),
                )
            )
        return groups

    @rx.var
    def total_items(self) -> int:
        return len(self.items)

    @rx.var
    def bought_count(self) -> int:
        return len([1 for d in self.items.values() if d.get("bought", False)])

    @rx.var
    def pending_count(self) -> int:
        return self.total_items - self.bought_count

    @rx.var
    def progress_percent(self) -> int:
        if not self.items:
            return 0
        return min(100, int(self.bought_count * 100 / self.total_items))

    @rx.var
    def auto_count(self) -> int:
        return len([1 for d in self.items.values() if d.get("auto", False)])

    @rx.var
    def section_count(self) -> int:
        return len({d.get("cat", "otros") for d in self.items.values()})

    @rx.var
    def has_visible_items(self) -> bool:
        return len(self._visible_items()) > 0

    @rx.var
    def is_filtering(self) -> bool:
        return bool(self.search.strip()) or self.hide_bought

    @rx.event
    def set_search(self, value: str):
        self.search = value

    @rx.event
    def toggle_hide_bought(self):
        self.hide_bought = not self.hide_bought

    @rx.event
    def clear_filters(self):
        self.search = ""
        self.hide_bought = False

    # ------------------------------------------------------------
    # Carga inicial
    # ------------------------------------------------------------
    async def load_shopping_list(self):
        """Carga la lista del usuario actual desde la base de datos."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        self.current_user_id = user_state.current_user.id
        user_id = self.current_user_id
        await self.load_supermarkets()
        await self.load_pantry_stock()
        lists = await get_user_shopping_lists(user_id)
        if lists:
            self.current_list_id = lists[0]["id"]
            self.items = self._normalize_items(lists[0]["items"])
        else:
            from Calendario.utils.api import SUPABASE_API
            new_list = SUPABASE_API.create_shopping_list([user_id])
            if new_list:
                self.current_list_id = new_list["id"]
                self.items = {}

    async def refresh_page(self):
        """Recarga manualmente los datos de la lista de la compra."""
        logger.debug("🔄 Recargando lista de la compra...")
        await self.load_shopping_list()
        # Si el panel de usuarios está abierto, también lo recargamos
        if self.show_users_panel:
            await self.load_shared_users()

    # ------------------------------------------------------------
    # Añadir productos
    # ------------------------------------------------------------
    def validate_item(self) -> bool:
        self.errors = {"name": "", "quantity": "", "supermarket": ""}
        has_error = False
        if not self.new_item_name.strip():
            self.errors["name"] = "El nombre es obligatorio"
            has_error = True
        elif len(self.new_item_name) > 40:
            self.errors["name"] = "Máximo 40 caracteres"
            has_error = True

        if not self.new_item_qty.strip():
            self.errors["quantity"] = "Cantidad obligatoria"
            has_error = True
        else:
            try:
                qty = float(self.new_item_qty.replace(",", "."))
                if qty <= 0:
                    self.errors["quantity"] = "Debe ser >0"
                    has_error = True
                elif qty > 9999:
                    self.errors["quantity"] = "Máximo 9999"
                    has_error = True
            except ValueError:
                self.errors["quantity"] = "Escribe un número"
                has_error = True

        if len(self.new_item_shop) > 20:
            self.errors["supermarket"] = "Máximo 20 caracteres"
            has_error = True
        return has_error

    @rx.event
    def change_qty(self, val: str):
        self.new_item_qty = val

    async def _product_defaults(self, name: str):
        """Producto del catálogo por su nombre, ya cargado el catálogo."""
        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()
        return products_state.find(name)

    @rx.event
    async def pick_new_item(self, name: str):
        """Elige el producto del catálogo y trae sus valores por defecto."""
        clean = (name or "").strip()
        self.new_item_name = clean
        if not clean:
            return
        product = await self._product_defaults(clean)
        if product:
            #En el súper se compra por envases: si el producto tiene puesta su
            #medida de compra (un brik son 1 l), es la que se propone. La `qty`
            #es la de cocinar, y esa manda en las recetas, no aquí.
            usa_pack = product.pack_qty > 0 and bool(product.pack_unit)
            self.new_item_qty = _numero(product.pack_qty if usa_pack else product.qty)
            self.new_item_unit = product.pack_unit if usa_pack else product.unit
            self.new_item_cat = product.cat
            self.new_item_shop = product.shop
            self.new_item_staple = product.staple
            self.new_item_note = product.note

    @rx.event
    async def pick_edit_item(self, name: str):
        """Cambia el producto de una línea ya existente (misma cantidad)."""
        clean = (name or "").strip()
        self.edit_name = clean
        if not clean:
            return
        product = await self._product_defaults(clean)
        if product:
            self.edit_qty = _numero(product.qty)
            self.edit_unit = product.unit
            self.edit_cat = product.cat
            self.edit_shop = product.shop
            self.edit_staple = product.staple
            self.edit_note = product.note

    @rx.event
    def set_new_item_name(self, val: str):
        self.new_item_name = val

    @rx.event
    def set_new_item_unit(self, val: str):
        self.new_item_unit = val

    @rx.event
    def set_new_item_shop(self, val: str):
        self.new_item_shop = val

    @rx.event
    def set_new_item_cat(self, val: str):
        self.new_item_cat = val

    @rx.event
    def set_new_item_staple(self, val: bool):
        self.new_item_staple = val

    @rx.event
    def set_new_item_note(self, val: str):
        self.new_item_note = val

    @rx.event
    def set_edit_cat(self, val: str):
        self.edit_cat = val

    @rx.event
    def set_edit_staple(self, val: bool):
        self.edit_staple = val

    @rx.event
    def set_edit_note(self, val: str):
        self.edit_note = val

    @rx.event
    def set_edit_bought(self, val: bool):
        self.edit_bought = val

    @rx.event
    def set_edit_source(self, val: str):
        self.edit_source = val

    @rx.event
    def set_edit_pinned(self, val: bool):
        self.edit_pinned = val

    @rx.var
    def shop_sections(self) -> List[str]:
        return theme.SHOP_CATEGORY_ORDER

    @rx.event
    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form
        if not self.show_add_form:
            self.errors = {"name": "", "quantity": "", "supermarket": ""}

    @rx.event
    def close_add_form(self):
        self.show_add_form = False
        self.errors = {"name": "", "quantity": "", "supermarket": ""}

    # ------------------------------------------------------------
    # Añadir una comida entera a la lista
    # ------------------------------------------------------------
    @rx.event
    async def open_meal_form(self):
        """Abre el panel de «añadir comida» con el recetario cargado."""
        self.show_meal_form = True
        self.meal_pick = ""
        self.meal_people = str(BASE_SERVINGS)
        self.meal_include_staples = False
        self.meal_preview = []
        #Se puede entrar a la compra sin pasar por el recetario: si no se cargan
        #aquí, el desplegable de comidas sale vacío
        calendar_state = await self.get_state(CalendarState)
        if not calendar_state.meals:
            await calendar_state.load_meals()

    @rx.event
    def close_meal_form(self):
        self.show_meal_form = False
        self.meal_pick = ""
        self.meal_preview = []

    @rx.var
    def meal_people_int(self) -> int:
        try:
            return max(1, min(50, int(self.meal_people)))
        except (ValueError, TypeError):
            return BASE_SERVINGS

    @rx.var
    def has_meal_preview(self) -> bool:
        return len(self.meal_preview) > 0

    @rx.var
    def meal_preview_count(self) -> int:
        return len(self.meal_preview)

    @rx.event
    def set_meal_people(self, value: str):
        self.meal_people = value
        return ShoppingListState.refresh_meal_preview

    @rx.event
    def bump_meal_people(self, delta: int):
        self.meal_people = str(max(1, min(50, self.meal_people_int + delta)))
        return ShoppingListState.refresh_meal_preview

    @rx.event
    def toggle_meal_staples(self, value: bool):
        self.meal_include_staples = value
        return ShoppingListState.refresh_meal_preview

    @rx.event
    async def pick_meal(self, name: str):
        self.meal_pick = (name or "").strip()
        return ShoppingListState.refresh_meal_preview

    @rx.event
    async def refresh_meal_preview(self):
        """Recalcula lo que se va a añadir: escalado y en unidades de compra.

        Se hace igual que el menú semanal (`to_purchase`) para que dé lo mismo
        pedir una tarta por aquí que planificarla en la semana: si no, la misma
        receta dejaría "5 pizcas de sal" por un lado y "1 bote" por el otro.
        """
        if not self.meal_pick:
            self.meal_preview = []
            return

        calendar_state = await self.get_state(CalendarState)
        receta = next((m for m in calendar_state.meals if m.name == self.meal_pick), None)
        if not receta:
            self.meal_preview = []
            return

        factor = self.meal_people_int / BASE_SERVINGS
        #Se agrupa por (producto, unidad de compra): una receta puede repetir el
        #mismo ingrediente en dos pasos y en la lista tiene que salir una vez
        totales: Dict[tuple, dict] = {}
        for ing in receta.ingredients:
            if ing.staple and not self.meal_include_staples:
                continue
            qty, unidad = to_purchase(ing.name, ing.qty * factor, ing.unit)
            clave = (ing.name, unidad)
            entrada = totales.setdefault(
                clave,
                {"qty": 0.0, "cat": ing.cat, "shop": ing.shop, "note": ing.note, "staple": ing.staple},
            )
            entrada["qty"] += qty
            if not entrada["shop"] and ing.shop:
                entrada["shop"] = ing.shop
            if not entrada["note"] and ing.note:
                entrada["note"] = ing.note

        self.meal_preview = [
            GeneratedItem(
                name=nombre,
                qty=round(datos["qty"], 2),
                unit=unidad,
                cat=datos["cat"],
                shop=datos["shop"],
                note=datos["note"],
                staple=datos["staple"],
                source=receta.name,
                qty_label=format_qty(datos["qty"], unidad),
                key=f"{nombre}|{unidad}",
                selected=True,
            )
            for (nombre, unidad), datos in totales.items()
        ]

    @rx.event
    def toggle_meal_line(self, key: str):
        """Quitar de la lista algo que ya tienes en casa, antes de añadirla."""
        self.meal_preview = [
            item.copy(update={"selected": not item.selected}) if item.key == key else item
            for item in self.meal_preview
        ]

    @rx.event
    async def add_meal_to_list(self):
        """Vuelca los ingredientes marcados de la comida elegida en la lista."""
        if not self.current_list_id:
            return rx.toast.error("Lista no identificada", position="top-center")
        if not self.meal_pick:
            return rx.toast.error("Elige una comida", position="top-center")

        marcados = [item for item in self.meal_preview if item.selected]
        if not marcados:
            return rx.toast.error("No has dejado ningún ingrediente marcado", position="top-center")

        self.adding_meal = True
        try:
            payload = {
                item.name: {
                    "quantity": item.qty,
                    "unit": item.unit,
                    "cat": item.cat,
                    "shop": item.shop,
                    "staple": item.staple,
                    "note": item.note,
                    "source": item.source,
                }
                for item in marcados
            }
            ok, añadidos, sumados, conflictos = await add_recipe_to_shopping_list(
                self.current_list_id, payload, self.current_user_id
            )
            if not ok:
                return rx.toast.error("No se pudo añadir a la lista", position="top-center")

            comida = self.meal_pick
            personas = self.meal_people_int
            self.close_meal_form()
            await self.load_shopping_list()

            detalle = f"{añadidos} productos nuevos"
            if sumados:
                detalle += f" y {sumados} sumados a los que ya tenías"
            avisos = [
                rx.toast.success(
                    f"'{comida}' para {personas} personas: {detalle}",
                    position="top-center",
                    duration=6000,
                )
            ]
            if conflictos:
                #No se inventa una suma entre unidades que no se pueden mezclar
                avisos.append(
                    rx.toast.warning(
                        "Sin sumar por llevar otra unidad en la lista: "
                        + ", ".join(conflictos[:4])
                        + ("..." if len(conflictos) > 4 else ""),
                        position="top-center",
                        duration=8000,
                    )
                )
            return avisos
        finally:
            self.adding_meal = False

    async def add_item(self):
        if self.validate_item():
            return
        if not self.current_list_id:
            return rx.toast.error("Lista no identificada", position="top-center")
        qty = float(self.new_item_qty.replace(",", ".")) if self.new_item_qty else 1
        success = await add_item_to_shopping_list(
            self.current_list_id,
            self.new_item_name.strip(),
            qty,
            self.new_item_shop.strip(),
            self.current_user_id,
            self.new_item_unit,
            self.new_item_cat,
            self.new_item_staple,
            self.new_item_note.strip()[:60],
        )
        if success:
            name = self.new_item_name.strip()
            self.new_item_name = ""
            self.new_item_qty = "1"
            self.new_item_unit = "ud"
            self.new_item_shop = ""
            self.new_item_cat = "otros"
            self.new_item_staple = False
            self.new_item_note = ""
            self.show_add_form = False
            await self.load_shopping_list()
            return rx.toast.success(f"{name} añadido a la lista", position="top-center")
        return rx.toast.error("Error al añadir", position="top-center")

    # ------------------------------------------------------------
    # Editar / marcar / borrar
    # ------------------------------------------------------------
    @rx.event
    def open_editor(self, name: str):
        data = self.items.get(name)
        if not data:
            return
        self.editing_name = name
        self.edit_name = name
        self.edit_qty = str(data.get("quantity", 1))
        self.edit_unit = data.get("unit", "ud")
        self.edit_shop = data.get("supermarket", "")
        self.edit_cat = data.get("cat", "otros")
        self.edit_staple = bool(data.get("staple", False))
        self.edit_note = data.get("note", "") or ""
        self.edit_bought = bool(data.get("bought", False))
        self.edit_source = data.get("source", "") or ""
        #En la interfaz se pregunta al revés («fijado»), que es lo que se entiende
        self.edit_pinned = not bool(data.get("auto", False))
        self.show_edit_form = True

    @rx.event
    def close_editor(self):
        self.show_edit_form = False
        self.editing_name = ""

    @rx.event
    def set_edit_name(self, val: str):
        self.edit_name = val

    @rx.event
    def set_edit_qty(self, val: str):
        self.edit_qty = val

    @rx.event
    def set_edit_unit(self, val: str):
        self.edit_unit = val

    @rx.event
    def set_edit_shop(self, val: str):
        self.edit_shop = val

    @rx.event
    async def save_edit(self):
        if not self.current_list_id or not self.editing_name:
            return
        name = self.edit_name.strip()
        if not name:
            return rx.toast.error("El nombre no puede estar vacío", position="top-center")
        try:
            qty = float(self.edit_qty.replace(",", "."))
        except ValueError:
            return rx.toast.error("La cantidad debe ser un número", position="top-center")
        if qty <= 0:
            return rx.toast.error("La cantidad debe ser mayor que 0", position="top-center")

        success = await update_shopping_item(
            self.current_list_id, self.editing_name, name, qty,
            self.edit_unit, self.edit_shop.strip(), self.current_user_id, self.edit_cat,
            staple=self.edit_staple,
            note=self.edit_note.strip()[:60],
            bought=self.edit_bought,
            #«Fijado» es lo contrario de «lo puso el menú semanal»
            auto=not self.edit_pinned,
            source=self.edit_source.strip()[:200],
        )
        if not success:
            return rx.toast.error("No se pudo guardar (¿ese producto ya existe?)", position="top-center")
        self.show_edit_form = False
        self.editing_name = ""
        await self.load_shopping_list()
        return rx.toast.success("Producto actualizado", position="top-center")

    @rx.event
    async def adjust_qty(self, name: str, delta: float):
        """Sube o baja la cantidad de un producto desde la propia fila."""
        data = self.items.get(name)
        if not data or not self.current_list_id:
            return
        new_qty = round(float(data.get("quantity", 1)) + delta, 2)
        if new_qty <= 0:
            return
        success = await update_shopping_item(
            self.current_list_id, name, name, new_qty,
            data.get("unit", "ud"), data.get("supermarket", ""), self.current_user_id,
        )
        if success:
            await self.load_shopping_list()

    async def toggle_bought(self, item_name: str):
        """Marca/desmarca al instante y guarda después.

        Antes esperaba a Supabase y encima recargaba la lista entera, así que
        tachar un producto en el súper tardaba un mundo. Ahora se pinta ya y
        solo se revierte si la escritura falla.

        Marcar es además lo que llena la despensa: la escritura suma el producto
        al stock de casa (y desmarcar lo resta, porque desmarcar es deshacer).
        """
        data = self.items.get(item_name)
        if not data or not self.current_list_id:
            return
        nuevo = not data.get("bought", False)
        self.items = {
            n: ({**d, "bought": nuevo} if n == item_name else d)
            for n, d in self.items.items()
        }
        if not await toggle_shopping_item_status(self.current_list_id, item_name, self.current_user_id):
            self.items = {
                n: ({**d, "bought": not nuevo} if n == item_name else d)
                for n, d in self.items.items()
            }
            return rx.toast.error("Error al actualizar", position="top-center")

    async def delete_item(self, item_name: str):
        if await remove_item_from_shopping_list(self.current_list_id, item_name, self.current_user_id):
            await self.load_shopping_list()
        else:
            return rx.toast.error("Error al eliminar", position="top-center")

    @rx.event
    async def clear_bought(self):
        """Quita de la lista todo lo que ya está en el carro."""
        if not self.current_list_id:
            return
        removed = await clear_bought_shopping_items(self.current_list_id, self.current_user_id)
        await self.load_shopping_list()
        if removed:
            return rx.toast.success(f"{removed} productos comprados eliminados", position="top-center")
        return rx.toast.info("No hay productos marcados como comprados", position="top-center")

    @rx.event
    async def clear_all(self):
        """Vacía la lista entera (con confirmación en la interfaz)."""
        if not self.current_list_id:
            return
        removed = await clear_all_shopping_items(self.current_list_id, self.current_user_id)
        await self.load_shopping_list()
        if removed:
            return rx.toast.success(f"Lista vaciada ({removed} productos)", position="top-center")
        return rx.toast.info("La lista ya estaba vacía", position="top-center")

    @rx.event
    async def mark_all(self, bought: bool):
        """Marca o desmarca toda la lista de una vez."""
        if not self.current_list_id:
            return
        changed = await set_all_shopping_items_bought(self.current_list_id, self.current_user_id, bought)
        await self.load_shopping_list()
        if not changed:
            return rx.toast.info("No había nada que cambiar", position="top-center")
        if bought:
            return rx.toast.success(
                f"{changed} productos marcados como comprados y guardados en la despensa",
                position="top-center",
                duration=6000,
            )
        return rx.toast.success(f"{changed} productos desmarcados", position="top-center")

    # ------------------------------------------------------------
    # Métodos para usuarios (compartir, añadir, eliminar)
    # ------------------------------------------------------------
    async def load_shared_users(self):
        if not self.current_list_id:
            return
        users = await get_shopping_list_users(self.current_list_id)
        self.shared_users = users

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
    def set_new_user_input(self, val: str):
        self.new_user_input = val

    async def add_user_to_list(self):
        self.add_user_error = ""
        username = self.new_user_input.strip().lower()
        if not username:
            self.add_user_error = "Nombre de usuario requerido"
            return

        user_state = await self.get_state(UserState)
        current_user_id = user_state.current_user.id
        success, msg = await merge_and_share_shopping_list(current_user_id, username)

        if success:
            self.new_user_input = ""
            await self.load_shared_users()
            await self.load_shopping_list()
            self.show_users_panel = False
            return rx.toast.success(msg, position="top-center")
        self.add_user_error = msg
        return rx.toast.error(msg, position="top-center")

    async def remove_user_from_list(self, user_id: int, username: str):
        if user_id == self.current_user_id:
            return rx.toast.error("No puedes eliminarte a ti mismo", position="top-center")
        success = await remove_user_from_list(self.current_list_id, user_id, self.current_user_id)
        if success:
            await self.load_shared_users()
            return rx.toast.success(
                f"Usuario {username} eliminado. Se le ha creado su propia lista.",
                position="top-center",
            )
        return rx.toast.error("Error al eliminar usuario", position="top-center")
