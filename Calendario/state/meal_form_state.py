# Calendario/state/meal_form_state.py
"""
Alta y edición de comidas del recetario, con sus ingredientes.

Los ingredientes son lo que hace posible que el menú semanal genere la lista
de la compra, así que el formulario los trata como ciudadanos de primera: cada
uno lleva **los mismos campos que un producto de la compra** (cantidad, unidad,
sección del súper, supermercado, básico de despensa y nota), la sección se
adivina sola a partir del nombre, y cualquiera de ellos se puede editar después
sin tener que borrar el ingrediente y volver a escribirlo.
"""

import logging
import re
from typing import List, Optional

import reflex as rx

from Calendario import theme
from Calendario.model.model import Ingredient
from Calendario.state.calendar_state import CalendarState
from Calendario.state.products_state import ProductsState
from Calendario.state.shopping_list_state import ShoppingListState
from Calendario.state.user_state import UserState
from Calendario.utils.api import add_new_meal, update_meal
#La sección del súper se adivina en un único sitio, compartido con el catálogo
from Calendario.utils.purchase import guess_category

logger = logging.getLogger(__name__)


def _numero(valor: float) -> str:
    """'500.0' se ve fatal en un campo: se escribe '500'."""
    return str(int(valor)) if float(valor) == int(valor) else str(valor)

class MealFormState(rx.State):
    show: bool = False
    editing_id: Optional[int] = None

    name: str = ""
    description: str = ""
    category: str = "otros"
    #Etiqueta legible de la categoría, para pintarla en el desplegable
    category_label: str = "Otros"
    prep_minutes: str = "20"
    ingredients: List[Ingredient] = []

    #Formulario del ingrediente: sirve tanto para dar de alta uno nuevo como
    #para editar uno ya añadido (entonces `ing_index` apunta a su posición)
    ing_name: str = ""
    ing_qty: str = "1"
    ing_unit: str = "ud"
    ing_cat: str = "otros"
    ing_shop: str = ""
    ing_staple: bool = False
    ing_note: str = ""
    #-1 = estamos dando de alta uno nuevo
    ing_index: int = -1
    #El formulario del ingrediente va plegado por defecto: lo que interesa ver
    #al abrir una receta es la lista de lo que lleva, no ocho campos en blanco.
    #Se despliega al pulsar «Añadir ingrediente» o el lápiz de uno de la lista.
    show_ing_form: bool = False

    saving: bool = False

    # ------------------------------------------------------------------
    # Apertura / cierre
    # ------------------------------------------------------------------
    @rx.event
    async def open_new(self):
        self._reset()
        await self._load_catalogs()
        await self._refresh_category_label()
        self.show = True

    @rx.event
    async def open_edit(self, meal_id: int):
        calendar_state = await self.get_state(CalendarState)
        meal = next((m for m in calendar_state.meals if m.id == meal_id), None)
        if not meal:
            return rx.toast.error("No se encontró la comida", position="top-center")
        self._reset()
        await self._load_catalogs()
        self.editing_id = meal.id
        self.name = meal.name
        self.description = meal.description or ""
        self.category = meal.category or "otros"
        self.prep_minutes = str(meal.prep_minutes or 20)
        self.ingredients = list(meal.ingredients)
        await self._refresh_category_label()
        self.show = True

    async def _load_catalogs(self):
        """Trae productos y supermercados aunque no hayas pasado por la compra.

        Los desplegables del ingrediente leen el catálogo de productos
        (`ProductsState`) y la lista de supermercados (`ShoppingListState`); si
        entras directo al recetario, ambas están todavía vacías.
        """
        try:
            products_state = await self.get_state(ProductsState)
            await products_state.ensure_loaded()
        except Exception as e:
            logger.warning(f"No se pudo cargar el catálogo de productos: {e}")
        try:
            shopping_state = await self.get_state(ShoppingListState)
            if not shopping_state.supermarkets:
                await shopping_state.load_supermarkets()
        except Exception as e:
            logger.warning(f"No se pudieron cargar los supermercados: {e}")

    async def _refresh_category_label(self):
        """La categoría del plato es configurable, así que su etiqueta hay que
        buscarla en `CalendarState` (un `rx.match` estático no vale)."""
        try:
            calendar_state = await self.get_state(CalendarState)
            self.category_label = next(
                (c.label for c in calendar_state.categories if c.key == self.category),
                self.category,
            )
        except Exception:
            self.category_label = self.category

    @rx.event
    def close(self):
        self.show = False
        self._reset()

    def _reset(self):
        self.editing_id = None
        self.name = ""
        self.description = ""
        self.category = "otros"
        self.prep_minutes = "20"
        self.ingredients = []
        self._reset_ingredient_form()
        #Plegado al abrir cualquier receta: primero se ve lo que lleva
        self.show_ing_form = False
        self.saving = False

    def _reset_ingredient_form(self):
        self.ing_name = ""
        self.ing_qty = "1"
        self.ing_unit = "ud"
        self.ing_cat = "otros"
        self.ing_shop = ""
        self.ing_staple = False
        self.ing_note = ""
        self.ing_index = -1

    @rx.event
    def open_ingredient_form(self):
        """Despliega el formulario en blanco para añadir uno nuevo."""
        self._reset_ingredient_form()
        self.show_ing_form = True

    @rx.event
    def close_ingredient_form(self):
        """Lo pliega y tira lo que hubiera a medias."""
        self._reset_ingredient_form()
        self.show_ing_form = False

    @rx.var
    def is_editing(self) -> bool:
        return self.editing_id is not None

    @rx.var
    def dialog_title(self) -> str:
        return "Editar comida" if self.editing_id is not None else "Nueva comida"

    #Las categorías de plato salen de `CalendarState` (son configurables) y las
    #secciones del súper, de `theme`: los desplegables las leen de allí

    @rx.var
    def ingredient_count(self) -> int:
        return len(self.ingredients)

    @rx.var
    def has_ingredients(self) -> bool:
        return len(self.ingredients) > 0

    @rx.var
    def is_editing_ingredient(self) -> bool:
        return self.ing_index >= 0

    @rx.var
    def ingredient_form_title(self) -> str:
        if self.ing_index < 0:
            return "AÑADIR INGREDIENTE"
        return "EDITANDO INGREDIENTE"

    # ------------------------------------------------------------------
    # Campos
    # ------------------------------------------------------------------
    @rx.event
    def set_name(self, value: str):
        self.name = value

    @rx.event
    def set_description(self, value: str):
        self.description = value

    @rx.event
    async def set_category(self, value: str):
        self.category = value
        await self._refresh_category_label()

    @rx.event
    def set_prep_minutes(self, value: str):
        self.prep_minutes = value

    @rx.event
    async def pick_ingredient(self, name: str):
        """Elige un producto del catálogo y trae sus valores por defecto.

        Es lo que sustituye a escribir el ingrediente a mano: la unidad, la
        sección, el supermercado, el básico y la nota vienen ya puestos del
        catálogo, y luego se pueden cambiar **solo para esta receta**.
        """
        clean = (name or "").strip()
        self.ing_name = clean
        if not clean:
            return

        #Si ese producto ya está en la receta, se abre el que hay en vez de
        #dejarte rellenar un alta que iba a chocar al pulsar «Añadir». Antes
        #esto era el camino directo al "ya está en la lista" que no se veía.
        repetido = self._duplicate_index(clean)
        if repetido >= 0:
            existente = self.ingredients[repetido]
            self.edit_ingredient(repetido)
            return [
                rx.scroll_to(f"ingrediente-{repetido}"),
                rx.set_focus("ingrediente-cantidad"),
                rx.toast.info(
                    f"'{existente.name}' ya estaba en esta receta: te lo he abierto para editarlo",
                    position="top-center",
                ),
            ]

        products_state = await self.get_state(ProductsState)
        await products_state.ensure_loaded()
        product = products_state.find(clean)
        if product:
            #Todo lo que el catálogo sepa del producto se trae puesto, incluida
            #la cantidad habitual; luego se cambia lo que haga falta
            self.ing_qty = _numero(product.qty)
            self.ing_unit = product.unit
            self.ing_cat = product.cat
            self.ing_shop = product.shop
            self.ing_staple = product.staple
            self.ing_note = product.note
        else:
            #Recién creado desde el propio desplegable: al menos acertamos la sección
            self.ing_cat = guess_category(clean)

    @rx.event
    def set_ing_qty(self, value: str):
        self.ing_qty = value

    @rx.event
    def set_ing_unit(self, value: str):
        self.ing_unit = value

    @rx.event
    def set_ing_cat(self, value: str):
        self.ing_cat = value

    @rx.event
    def set_ing_shop(self, value: str):
        self.ing_shop = value

    @rx.event
    def set_ing_staple(self, value: bool):
        self.ing_staple = value

    @rx.event
    def set_ing_note(self, value: str):
        self.ing_note = value

    # ------------------------------------------------------------------
    # Ingredientes
    # ------------------------------------------------------------------
    @rx.event
    def edit_ingredient(self, index: int):
        """Carga un ingrediente ya añadido en el formulario para retocarlo."""
        if index < 0 or index >= len(self.ingredients):
            return
        item = self.ingredients[index]
        #El lápiz de un ingrediente tiene que desplegar el formulario, o el
        #clic no haría nada visible
        self.show_ing_form = True
        self.ing_index = index
        self.ing_name = item.name
        #`str(500.0)` en un campo numérico se lee fatal: "500" es lo que se puso
        self.ing_qty = _numero(item.qty)
        self.ing_unit = item.unit
        self.ing_cat = item.cat
        self.ing_shop = item.shop
        self.ing_staple = item.staple
        self.ing_note = item.note
        #El formulario está encima de la lista: se sube el foco para que se vea
        #que ese ingrediente está en edición
        return rx.set_focus("ingrediente-cantidad")

    @rx.event
    def cancel_ingredient_edit(self):
        """Cancelar deja de editar y vuelve a plegar el formulario."""
        self._reset_ingredient_form()
        self.show_ing_form = False

    def _duplicate_index(self, name: str) -> int:
        """Posición del ingrediente que ya se llama así, o -1.

        No cuenta el que se está editando: chocar consigo mismo no es duplicado.
        Se compara sin mayúsculas y sin espacios de sobra, que es como llegan
        los nombres del catálogo.
        """
        buscado = name.strip().lower()
        return next(
            (
                pos
                for pos, i in enumerate(self.ingredients)
                if i.name.strip().lower() == buscado and pos != self.ing_index
            ),
            -1,
        )

    def _commit_ingredient(self) -> tuple[Optional[str], int, bool]:
        """Vuelca el formulario del ingrediente en la lista.

        Devuelve `(error, posición, era_edición)`. El error es `None` si ha ido
        bien. Lo usan tanto el botón de añadir/guardar como el guardado de la
        comida, para que un ingrediente escrito y no añadido no se pierda al
        pulsar «Guardar».
        """
        name = self.ing_name.strip()
        if not name:
            return "Escribe el nombre del ingrediente", -1, False
        if len(name) > 40:
            return "Nombre de ingrediente demasiado largo", -1, False
        try:
            qty = float(self.ing_qty.replace(",", "."))
        except (ValueError, AttributeError):
            return "La cantidad debe ser un número", -1, False
        if qty <= 0:
            return "La cantidad debe ser mayor que 0", -1, False

        item = Ingredient(
            name=name,
            qty=qty,
            unit=self.ing_unit,
            cat=self.ing_cat,
            shop=self.ing_shop.strip(),
            staple=self.ing_staple,
            note=self.ing_note.strip()[:60],
        )
        era_edicion = 0 <= self.ing_index < len(self.ingredients)
        if era_edicion:
            posicion = self.ing_index
            updated = list(self.ingredients)
            updated[posicion] = item
            self.ingredients = updated
        else:
            posicion = len(self.ingredients)
            self.ingredients = self.ingredients + [item]
        self._reset_ingredient_form()
        return None, posicion, era_edicion

    @rx.event
    def save_ingredient(self):
        """Da de alta el ingrediente, o guarda los cambios si se está editando.

        Aquí había dos agujeros que hacían que pareciera que el botón no
        funcionaba:

        1. **No decía nada al acertar.** El ingrediente se añadía al final de
           una lista con altura limitada que estaba por debajo del formulario,
           así que muchas veces no se veía nada moverse. Ahora avisa y lleva la
           vista hasta él.
        2. **"Ese ingrediente ya está en la lista" era un callejón sin salida**,
           y encima ni decía cuál. Ahora, si ya está, se abre el que ya había
           (con lo que acabas de escribir puesto) para que lo cambies y lo
           guardes: la lista no se toca sin que lo veas.
        """
        repetido = self._duplicate_index(self.ing_name)
        if repetido >= 0:
            existente = self.ingredients[repetido]
            #Se pasa a editar el que ya estaba, PERO conservando lo tecleado:
            #lo normal es que quisieras corregir su cantidad
            self.ing_index = repetido
            self.show_ing_form = True
            return [
                rx.scroll_to(f"ingrediente-{repetido}"),
                rx.set_focus("ingrediente-cantidad"),
                rx.toast.info(
                    f"'{existente.name}' ya estaba en la lista "
                    f"({_numero(existente.qty)} {existente.unit}). Lo tienes abierto arriba: "
                    "cambia lo que quieras y pulsa «Guardar cambios».",
                    position="top-center",
                    duration=6000,
                ),
            ]

        nombre = self.ing_name.strip()
        error, posicion, era_edicion = self._commit_ingredient()
        if error:
            return rx.toast.error(error, position="top-center")
        return [
            rx.scroll_to(f"ingrediente-{posicion}"),
            rx.toast.success(
                f"'{nombre}' actualizado" if era_edicion else f"'{nombre}' añadido a la receta",
                position="top-center",
            ),
        ]

    @rx.event
    def remove_ingredient(self, index: int):
        if index < 0 or index >= len(self.ingredients):
            return
        self.ingredients = [i for pos, i in enumerate(self.ingredients) if pos != index]
        #Si borras justo el que estabas editando, el formulario vuelve a "nuevo"
        if self.ing_index == index:
            self._reset_ingredient_form()
        elif self.ing_index > index:
            self.ing_index -= 1

    # ------------------------------------------------------------------
    # Guardado
    # ------------------------------------------------------------------
    @rx.event
    async def save(self):
        #El recetario es común a toda la app, pero solo lo tocan usuarios con
        #sesión: los manejadores de estado son invocables por cualquier cliente
        #conectado, así que la comprobación tiene que estar aquí
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        #Si hay un ingrediente escrito y sin añadir, se añade en vez de perderlo
        if self.ing_name.strip():
            repetido = self._duplicate_index(self.ing_name)
            if repetido >= 0:
                existente = self.ingredients[repetido]
                self.ing_index = repetido
                self.show_ing_form = True
                return [
                    rx.scroll_to(f"ingrediente-{repetido}"),
                    rx.toast.warning(
                        f"Tienes '{existente.name}' a medias y ya estaba en la receta "
                        f"({_numero(existente.qty)} {existente.unit}). Guárdalo o cancélalo "
                        "antes de guardar la comida.",
                        position="top-center",
                        duration=6000,
                    ),
                ]
            error, _, _ = self._commit_ingredient()
            if error:
                return rx.toast.error(f"Ingrediente sin añadir: {error}", position="top-center")

        name = self.name.strip()
        description = self.description.strip()

        if not name:
            return rx.toast.error("El nombre es obligatorio", position="top-center")
        if len(name) > 40:
            return rx.toast.error("El nombre no puede tener más de 40 caracteres", position="top-center")
        #Se permiten tildes y ñ (antes solo A-Z0-9, que dejaba fuera media cocina
        #española) y la puntuación que sale en un nombre de plato de verdad:
        #"Arroz a la cubana (2 raciones)", "Pasta c/tomate", "Sal & pimienta"
        if not re.match(r"^[\wÁÉÍÓÚÜÑáéíóúüñ0-9 ,.'%/&+()ºª\-]+$", name):
            return rx.toast.error(
                "El nombre solo admite letras, números y , . ' - / % & ( )",
                position="top-center",
            )
        if len(description) > 300:
            return rx.toast.error("La descripción es demasiado larga (máx. 300)", position="top-center")

        try:
            prep = int(self.prep_minutes)
        except (ValueError, TypeError):
            prep = 20
        prep = max(1, min(600, prep))

        payload = [i.dict() for i in self.ingredients]

        self.saving = True
        try:
            if self.editing_id is not None:
                result = await update_meal(
                    self.editing_id, name, description, payload, self.category, prep,
                    user_state.current_user.id,
                )
                error_message = "No se pudo actualizar (¿ya existe otra comida con ese nombre en tu recetario?)"
            else:
                result = await add_new_meal(
                    name, description, payload, self.category, prep,
                    user_state.current_user.id,
                )
                error_message = "Ya existe una comida con ese nombre en tu recetario"

            if result is None:
                return rx.toast.error(error_message, position="top-center")

            calendar_state = await self.get_state(CalendarState)
            await calendar_state.load_meals()
            self.show = False
            saved_name = name
            self._reset()
            return rx.toast.success(f"'{saved_name}' guardada", position="top-center")
        except Exception as e:
            logger.error(f"Error guardando comida: {e}")
            return rx.toast.error("Error al guardar la comida", position="top-center")
        finally:
            self.saving = False
