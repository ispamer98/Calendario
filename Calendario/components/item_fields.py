# Calendario/components/item_fields.py
"""
Campos compartidos por un "producto", venga de donde venga.

Un ingrediente del recetario y un producto de la lista de la compra son la
misma cosa vista en dos momentos distintos, así que se editan con los mismos
campos: cantidad, unidad, sección del súper, supermercado, básico de despensa
y una nota. Estaban duplicados (y desparejados) entre `meal_form.py` y
`shopping_list.py`; aquí hay una sola versión de cada uno.

Todos los campos se pintan **etiquetados y con ancho mínimo**: antes, la fila
de alta de ingredientes metía cinco controles en una línea de 520 px y la
sección del súper acababa siendo un desplegable de 40 px que no se veía.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.picker import (
    clear_option,
    manage_option,
    option,
    picker,
    static_options,
)
from Calendario.state.shopping_list_state import ShoppingListState
from Calendario.state.units_state import UnitsState


def field_label(text: str) -> rx.Component:
    return rx.text(text, size="1", color=theme.MUTED, weight="medium", letter_spacing="0.02em")


def field(label: str, control: rx.Component, min_width: str = "150px", grow: bool = True) -> rx.Component:
    """Etiqueta + control, como bloque que sabe encogerse y saltar de línea."""
    return rx.vstack(
        field_label(label),
        control,
        spacing="1",
        align="start",
        flex=("1 1 " + min_width) if grow else "0 0 " + min_width,
        min_width=min_width,
    )


def qty_input(value, on_change) -> rx.Component:
    return rx.input(
        value=value,
        on_change=on_change,
        type="number",
        size="2",
        width="100%",
    )


def units_select(value, on_change) -> rx.Component:
    """Unidad: buscador, «+» para añadir la que falte y gestor."""
    return picker(
        display=value,
        options=[rx.foreach(UnitsState.units, lambda u: option(u, u, on_change, selected=u == value))],
        placeholder="Unidad",
        search_placeholder="Buscar unidad...",
        footer=manage_option(UnitsState.open_manager, "Gestionar unidades"),
        width="220px",
        on_add=UnitsState.open_manager,
        add_title="Añadir una unidad nueva",
    )


def section_select(value, on_change) -> rx.Component:
    """Sección del súper: es lo que agrupa la lista por pasillos."""
    return picker(
        display=SECTION_LABEL(value),
        options=static_options(
            [
                (key, style["label"], style["color"], style["icon"])
                for key, style in theme.SHOP_CATEGORY_STYLE.items()
            ],
            on_change,
        ),
        placeholder="Sección",
        search_placeholder="Buscar sección...",
        width="240px",
    )


def SECTION_LABEL(value):
    """Clave de sección -> etiqueta legible ('verduras' -> 'Frutas y verduras')."""
    return rx.match(
        value,
        *[(key, style["label"]) for key, style in theme.SHOP_CATEGORY_STYLE.items()],
        "",
    )


def shop_select(value, on_change) -> rx.Component:
    """Supermercado (opcional): buscador, aspa para vaciarlo y gestor."""
    return picker(
        display=value,
        options=[
            rx.foreach(
                ShoppingListState.supermarkets,
                lambda shop: option(
                    shop.name, shop.name, on_change,
                    color=shop.color, selected=shop.name == value,
                ),
            )
        ],
        placeholder="Ninguno",
        search_placeholder="Buscar supermercado...",
        footer=rx.vstack(
            rx.cond(value != "", clear_option(on_change, "Sin supermercado")),
            manage_option(ShoppingListState.open_shops_panel, "Gestionar supermercados"),
            spacing="1",
            width="100%",
        ),
        width="240px",
        on_add=ShoppingListState.open_shops_panel,
        add_title="Añadir un supermercado nuevo",
    )


def place_select(value, on_change) -> rx.Component:
    """Dónde se guarda en casa: es lo que agrupa la despensa."""
    return picker(
        display=PLACE_LABEL(value),
        options=static_options(
            [
                (key, style["label"], style["color"], style["icon"])
                for key, style in theme.PANTRY_PLACE_STYLE.items()
            ],
            on_change,
        ),
        placeholder="Dónde se guarda",
        search_placeholder="Buscar sitio...",
        width="240px",
    )


def PLACE_LABEL(value):
    """Clave de sitio -> etiqueta legible ('nevera' -> 'Nevera')."""
    return rx.match(
        value,
        *[(key, style["label"]) for key, style in theme.PANTRY_PLACE_STYLE.items()],
        "",
    )


def expiry_input(value, on_change) -> rx.Component:
    """Caducidad (opcional). Campo de fecha del navegador: en el móvil abre su
    propio calendario, que es mucho menos trabajo que teclear la fecha."""
    return rx.input(
        value=value,
        on_change=on_change,
        type="date",
        size="2",
        width="100%",
    )


def min_qty_input(value, on_change) -> rx.Component:
    """Mínimo por debajo del cual avisar de que hay que reponer."""
    return rx.input(
        value=value,
        on_change=on_change,
        type="number",
        size="2",
        width="100%",
        placeholder="0",
    )


def note_input(value, on_change, placeholder: str = "Nota: marca, tamaño, pasillo...") -> rx.Component:
    return rx.input(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        size="2",
        width="100%",
        max_length=60,
    )


def staple_switch(checked, on_change) -> rx.Component:
    """Básico de despensa: el menú semanal lo salta salvo que lo pidas."""
    return rx.hstack(
        rx.switch(checked=checked, on_change=on_change, color_scheme="green"),
        rx.text("Aceite, sal, especias...", size="1", color=theme.DIM),
        spacing="2",
        align="center",
        height="32px",
    )


def bought_switch(checked, on_change) -> rx.Component:
    return rx.hstack(
        rx.switch(checked=checked, on_change=on_change, color_scheme="green"),
        rx.text("Ya está en el carro", size="1", color=theme.DIM),
        spacing="2",
        align="center",
        height="32px",
    )


def pinned_switch(checked, on_change) -> rx.Component:
    """«Fijado» = el menú semanal no lo rehace ni lo borra al regenerar."""
    return rx.hstack(
        rx.switch(checked=checked, on_change=on_change, color_scheme="purple"),
        rx.text("Lo respeta al rehacer la lista", size="1", color=theme.DIM),
        spacing="2",
        align="center",
        height="32px",
    )
