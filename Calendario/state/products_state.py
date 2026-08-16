# Calendario/state/products_state.py
"""
Catálogo de productos: los ingredientes preestablecidos.

Los ingredientes eran texto libre y eso acababa en "Tomate", "tomates" y
"Tomate " conviviendo en la misma lista de la compra sin sumarse. Ahora se
eligen de este catálogo, que se gestiona desde la app: añadir, editar y borrar.

Cada producto trae valores por defecto (unidad, sección del súper, supermercado,
básico de despensa y nota) que se copian al ingrediente al elegirlo. Cambiar
esos valores en una receta concreta no toca el catálogo.

Si la migración 013 no está aplicada, el catálogo llega vacío y se avisa al
intentar guardar, igual que con unidades y supermercados.
"""

import logging
import re
from typing import List, Optional

import reflex as rx

from Calendario import theme
from Calendario.model.model import Product
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    add_product,
    delete_product,
    get_products,
    update_product,
)
from Calendario.utils.purchase import guess_category

logger = logging.getLogger(__name__)

#Mismo criterio que el nombre de una comida: letras (con tildes y ñ), números
#y la puntuación que aparece de verdad en un producto. Los paréntesis y el «&»
#se añadieron después: sin ellos, cosas tan normales como "Atún claro (lata)"
#se rechazaban con un "caracteres no permitidos" que no explicaba cuál.
NAME_PATTERN = re.compile(r"^[\wÁÉÍÓÚÜÑáéíóúüñ0-9 ,.'%/&+()ºª\-]+$")


class ProductsState(rx.State):
    products: List[Product] = []
    loaded: bool = False

    #Gestor del catálogo
    show_manager: bool = False
    manager_search: str = ""
    saving: bool = False

    #Formulario del gestor (alta y edición)
    editing_id: int = 0
    form_name: str = ""
    form_qty: str = "1"
    form_unit: str = "ud"
    #La medida con la que se compra en el súper (un brik son 1 l). Vacía = no se
    #ha dicho, y entonces se usa la cantidad de receta.
    form_pack_qty: str = "0"
    form_pack_unit: str = ""
    form_cat: str = "otros"
    form_shop: str = ""
    form_staple: bool = False
    form_note: str = ""

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    async def _fetch(self):
        rows = await get_products()
        self.products = [self._build(row) for row in rows]
        self.loaded = True

    @rx.event
    async def load_products(self):
        await self._fetch()

    async def ensure_loaded(self):
        """Carga el catálogo si aún no está, sin repetir la consulta."""
        if not self.loaded:
            await self._fetch()

    @staticmethod
    def _build(row: dict) -> Product:
        cat = row.get("cat") or "otros"
        if cat not in theme.SHOP_CATEGORY_STYLE:
            cat = "otros"
        return Product(
            id=row.get("id", 0),
            name=row.get("name", ""),
            qty=float(row.get("qty") or 1),
            unit=row.get("unit") or "ud",
            pack_qty=float(row.get("pack_qty") or 0),
            pack_unit=row.get("pack_unit") or "",
            cat=cat,
            shop=row.get("shop") or "",
            staple=bool(row.get("staple", False)),
            note=row.get("note") or "",
            cat_label=theme.shop_label(cat),
            cat_color=theme.shop_color(cat),
            cat_icon=theme.shop_icon(cat),
        )

    # ------------------------------------------------------------------
    # Lecturas para los desplegables
    # ------------------------------------------------------------------
    @rx.var
    def names(self) -> List[str]:
        return [p.name for p in self.products]

    @rx.var
    def lower_names(self) -> List[str]:
        """Para que el desplegable sepa si lo que escribes existe ya o no."""
        return [p.name.lower() for p in self.products]

    @rx.var
    def product_count(self) -> int:
        return len(self.products)

    @rx.var
    def is_empty(self) -> bool:
        return len(self.products) == 0

    @rx.var
    def filtered(self) -> List[Product]:
        """Catálogo filtrado por el buscador del gestor."""
        query = self.manager_search.strip().lower()
        if not query:
            return self.products
        return [
            p for p in self.products
            if query in p.name.lower() or query in p.shop.lower() or query in p.note.lower()
        ]

    def find(self, name: str) -> Optional[Product]:
        lowered = (name or "").strip().lower()
        return next((p for p in self.products if p.name.lower() == lowered), None)

    # ------------------------------------------------------------------
    # Gestor: apertura y formulario
    # ------------------------------------------------------------------
    @rx.event
    async def open_manager(self):
        self.show_manager = True
        self.manager_search = ""
        self._reset_form()
        await self._fetch()

    @rx.event
    async def open_manager_for(self, product_id: int):
        """Abre el gestor con un producto ya cargado para editarlo.

        Es el lápiz que sale en cada opción del desplegable: se corrige ahí
        mismo sin perder de vista lo que estabas haciendo.
        """
        self.show_manager = True
        self.manager_search = ""
        await self._fetch()
        self._load_into_form(product_id)

    @rx.event
    def close_manager(self):
        self.show_manager = False
        self.manager_search = ""
        self._reset_form()

    def _reset_form(self):
        self.editing_id = 0
        self.form_name = ""
        self.form_qty = "1"
        self.form_unit = "ud"
        self.form_pack_qty = "0"
        self.form_pack_unit = ""
        self.form_cat = "otros"
        self.form_shop = ""
        self.form_staple = False
        self.form_note = ""

    @rx.event
    def cancel_edit(self):
        self._reset_form()

    def _load_into_form(self, product_id: int):
        product = next((p for p in self.products if p.id == product_id), None)
        if not product:
            return
        self.editing_id = product.id
        self.form_name = product.name
        self.form_qty = str(product.qty)
        self.form_unit = product.unit
        self.form_pack_qty = str(product.pack_qty)
        self.form_pack_unit = product.pack_unit
        self.form_cat = product.cat
        self.form_shop = product.shop
        self.form_staple = product.staple
        self.form_note = product.note

    @rx.event
    def edit(self, product_id: int):
        self._load_into_form(product_id)
        #El formulario está arriba del todo y la lista puede ser larga: se sube
        #el foco para que se vea que el producto está en edición
        return rx.set_focus("producto-nombre")

    @rx.var
    def is_editing(self) -> bool:
        return self.editing_id > 0

    @rx.event
    def set_manager_search(self, value: str):
        self.manager_search = value

    @rx.event
    def set_form_name(self, value: str):
        self.form_name = value

    @rx.event
    def set_form_qty(self, value: str):
        self.form_qty = value

    @rx.event
    def set_form_unit(self, value: str):
        self.form_unit = value

    @rx.event
    def set_form_pack_qty(self, value: str):
        self.form_pack_qty = value

    @rx.event
    def set_form_pack_unit(self, value: str):
        self.form_pack_unit = value

    @rx.event
    def set_form_cat(self, value: str):
        self.form_cat = value

    @rx.event
    def set_form_shop(self, value: str):
        self.form_shop = value

    @rx.event
    def set_form_staple(self, value: bool):
        self.form_staple = value

    @rx.event
    def set_form_note(self, value: str):
        self.form_note = value

    # ------------------------------------------------------------------
    # Alta / edición / borrado
    # ------------------------------------------------------------------
    def _validate(self, name: str) -> Optional[str]:
        if not name:
            return "Escribe el nombre del producto"
        if len(name) > 40:
            return "Máximo 40 caracteres"
        if not NAME_PATTERN.match(name):
            #Decir "caracteres no permitidos" y callarse cuáles obligaba a ir
            #probando a quitar letras hasta acertar
            return "El nombre solo admite letras, números y , . ' - / % & ( )"
        return None

    @rx.event
    async def save(self):
        #El catálogo lo ve toda la app: hace falta sesión iniciada
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        name = self.form_name.strip()
        error = self._validate(name)
        if error:
            return rx.toast.error(error, position="top-center")

        try:
            qty = float(self.form_qty.replace(",", "."))
        except (ValueError, AttributeError):
            return rx.toast.error("La cantidad habitual debe ser un número", position="top-center")
        if qty <= 0:
            return rx.toast.error("La cantidad de receta debe ser mayor que 0", position="top-center")

        try:
            pack_qty = float((self.form_pack_qty or "0").replace(",", "."))
        except (ValueError, AttributeError):
            return rx.toast.error("La medida de compra debe ser un número", position="top-center")
        if pack_qty < 0:
            return rx.toast.error("La medida de compra no puede ser negativa", position="top-center")
        pack_unit = (self.form_pack_unit or "").strip()

        self.saving = True
        try:
            if self.editing_id > 0:
                result = await update_product(
                    self.editing_id, name, qty, self.form_unit, self.form_cat,
                    self.form_shop.strip(), self.form_staple, self.form_note.strip()[:60],
                    pack_qty, pack_unit,
                )
                fallo = "No se pudo guardar (¿ya existe otro producto con ese nombre?)"
            else:
                result = await add_product(
                    name, qty, self.form_unit, self.form_cat,
                    self.form_shop.strip(), self.form_staple, self.form_note.strip()[:60],
                    pack_qty, pack_unit,
                )
                fallo = (
                    f"No se pudo guardar '{name}'. ¿Ya existe, o falta la migración "
                    "013_products.sql?"
                )
            if not result:
                return rx.toast.error(fallo, position="top-center")

            self._reset_form()
            await self._fetch()
            return rx.toast.success(f"'{name}' guardado en el catálogo", position="top-center")
        finally:
            self.saving = False

    @rx.event
    async def quick_add(self, name: str):
        """Crea un producto desde el propio desplegable, sin abrir el gestor.

        Es lo que evita que el catálogo se convierta en una jaula: si te falta
        algo, lo escribes en el buscador y lo creas ahí mismo. La sección del
        súper se adivina por el nombre; el resto se afina luego con el lápiz.
        """
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        clean = (name or "").strip()
        error = self._validate(clean)
        if error:
            return rx.toast.error(error, position="top-center")
        if self.find(clean):
            return rx.toast.info(f"'{clean}' ya estaba en el catálogo", position="top-center")

        cat = guess_category(clean)
        if cat not in theme.SHOP_CATEGORY_STYLE:
            cat = "otros"
        if not await add_product(clean, 1, "ud", cat, "", False, ""):
            return rx.toast.error(
                f"No se pudo crear '{clean}'. ¿Está aplicada la migración 013_products.sql?",
                position="top-center",
            )
        await self._fetch()
        return rx.toast.success(f"'{clean}' añadido al catálogo", position="top-center")

    @rx.event
    async def remove(self, product_id: int):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        product = next((p for p in self.products if p.id == product_id), None)
        if not await delete_product(product_id):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        if self.editing_id == product_id:
            self._reset_form()
        await self._fetch()
        nombre = product.name if product else "El producto"
        return rx.toast.success(
            f"'{nombre}' quitado del catálogo (las recetas que lo usaban no cambian)",
            position="top-center",
        )
