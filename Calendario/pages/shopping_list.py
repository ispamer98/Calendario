# shopping_list.py
"""
Lista de la compra.

Rediseñada para que sirva de verdad dentro del súper: agrupada por secciones
(fruta, carnicería, congelados...), con la cantidad y la unidad de cada
producto, marcado rápido de lo que ya está en el carro y distintivo para lo
que ha generado automáticamente el menú semanal.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.ui import (
    empty_state,
    icon_badge,
    info_banner,
    page_header,
    panel,
    pill,
    progress_bar,
    stat_card,
    stats_grid,
)
from Calendario.components.item_fields import (
    bought_switch,
    field,
    field_label,
    note_input,
    pinned_switch,
    qty_input,
    section_select,
    shop_select,
    staple_switch,
    units_select,
)
from Calendario.components.picker import option, picker
from Calendario.components.products_manager import product_picker
from Calendario.model.model import GeneratedItem, ShoppingGroup, ShoppingRow
from Calendario.state.calendar_state import CalendarState
from Calendario.state.products_state import ProductsState
from Calendario.state.shopping_list_state import ShoppingListState
from Calendario.state.units_state import UnitsState
from Calendario.state.user_state import UserState


def _shop_badge(item: rx.Var[ShoppingRow]) -> rx.Component:
    """Círculo con la inicial del supermercado y su color.

    El nombre entero ocupaba demasiado y partía la fila en dos líneas; aquí se
    ve de un vistazo por el color y, al tocarlo, sale el nombre completo.
    """
    return rx.popover.root(
        rx.popover.trigger(
            rx.center(
                rx.text(
                    item.shop_initial,
                    size="1",
                    weight="bold",
                    color=item.shop_color,
                    line_height="1",
                ),
                min_width="20px",
                width="20px",
                height="20px",
                border_radius="50%",
                background=item.shop_color + "26",   # ~15% de opacidad
                border="1px solid " + item.shop_color + "66",
                cursor="pointer",
                flex_shrink="0",
                _hover={"transform": "scale(1.15)"},
                transition="transform 0.15s ease",
            )
        ),
        rx.popover.content(
            rx.hstack(
                rx.box(
                    width="9px", height="9px", border_radius="50%",
                    background=item.shop_color, flex_shrink="0",
                ),
                rx.text(item.supermarket, size="2", weight="medium", color=theme.TEXT),
                spacing="2",
                align="center",
            ),
            side="top",
            style={
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": "10px",
                "padding": "8px 12px",
                "width": "auto",
                "box_shadow": theme.SHADOW,
            },
        ),
    )


# ---------------------------------------------------------------------------
# Fila de producto
# ---------------------------------------------------------------------------
def item_row(item: rx.Var[ShoppingRow]) -> rx.Component:
    return rx.hstack(
        #Marcar como comprado
        rx.icon(
            rx.cond(item.bought, "circle-check-big", "circle"),
            size=20,
            color=rx.cond(item.bought, theme.SUCCESS, theme.MUTED),
            cursor="pointer",
            on_click=ShoppingListState.toggle_bought(item.name),
            flex_shrink="0",
            _hover={"transform": "scale(1.12)"},
            transition="all 0.15s ease",
        ),

        rx.vstack(
            rx.hstack(
                #El nombre se lleva TODO el ancho sobrante: es lo que se lee en
                #el súper. Sin este `flex: 1 1 0` + `min-width: 0` se quedaba
                #con su ancho natural y se cortaba mucho antes de hacer falta.
                rx.box(
                    rx.text(
                        item.name,
                        size="2",
                        weight="medium",
                        text_decoration=rx.cond(item.bought, "line-through", "none"),
                        color=rx.cond(item.bought, theme.DIM, theme.TEXT),
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    flex="1 1 0",
                    min_width="0",
                    overflow="hidden",
                ),
                #Distintivo de "esto lo puso el menú semanal"
                rx.cond(
                    item.auto,
                    rx.icon(
                        "sparkles",
                        size=13,
                        color=theme.PURPLE,
                        flex_shrink="0",
                        title="Añadido por el menú semanal",
                    ),
                ),
                #Solo la inicial y el color: el nombre completo, al tocarlo
                rx.cond(item.supermarket != "", _shop_badge(item)),
                #Básico de despensa: el mismo distintivo que en el recetario
                rx.cond(
                    item.staple,
                    rx.icon(
                        "package",
                        size=12,
                        color=theme.PURPLE,
                        flex_shrink="0",
                        title="Básico de despensa",
                    ),
                ),
                #«Fijado»: vino del menú semanal, pero ya no lo rehace
                rx.cond(
                    ~item.auto & (item.source != ""),
                    rx.icon(
                        "pin",
                        size=12,
                        color=theme.ACCENT,
                        flex_shrink="0",
                        title="Fijado: el menú semanal no lo rehace",
                    ),
                ),
                #Lo que ya tienes de eso en casa. Es media compra de más al mes:
                #en el súper nadie se acuerda de si quedaba leche.
                rx.cond(
                    (item.at_home != "") & ~item.bought,
                    rx.hstack(
                        rx.icon("warehouse", size=11, color=theme.PANTRY, flex_shrink="0"),
                        rx.text(
                            item.at_home,
                            size="1",
                            color=theme.PANTRY,
                            white_space="nowrap",
                            font_family=theme.FONT_MONO,
                        ),
                        spacing="1",
                        align="center",
                        flex_shrink="0",
                        padding="1px 7px",
                        border_radius="999px",
                        background=theme.alpha(theme.PANTRY, 0.12),
                        border=f"1px solid {theme.alpha(theme.PANTRY, 0.28)}",
                        title="Ya tienes esto en la despensa",
                    ),
                ),
                spacing="2",
                align="center",
                width="100%",
                max_width="100%",
                min_width="0",
                overflow="hidden",
            ),
            #La nota, si la hay: lo que apuntaste sobre ese producto
            rx.cond(
                item.note != "",
                rx.hstack(
                    rx.icon("sticky-note", size=11, color=theme.ACCENT, flex_shrink="0"),
                    rx.text(
                        item.note,
                        size="1",
                        color=theme.MUTED,
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    spacing="1",
                    align="center",
                    width="100%",
                    max_width="100%",
                    overflow="hidden",
                ),
            ),
            #De qué recetas viene el producto: recortado, con bocadillo al tocar
            rx.cond(
                item.source != "",
                rx.popover.root(
                    rx.popover.trigger(
                        rx.hstack(
                            rx.icon("chef-hat", size=11, color=theme.DIM, flex_shrink="0"),
                            rx.box(
                                rx.text(
                                    item.source,
                                    size="1",
                                    color=theme.DIM,
                                    overflow="hidden",
                                    text_overflow="ellipsis",
                                    white_space="nowrap",
                                ),
                                flex="1 1 0",
                                min_width="0",
                                overflow="hidden",
                            ),
                            rx.icon("ellipsis", size=11, color=theme.MUTED, flex_shrink="0"),
                            spacing="1",
                            align="center",
                            width="100%",
                            max_width="100%",
                            cursor="pointer",
                            overflow="hidden",
                        )
                    ),
                    rx.popover.content(
                        rx.vstack(
                            rx.text(
                                "RECETAS QUE LO PIDEN",
                                size="1",
                                color=theme.DIM,
                                weight="bold",
                                letter_spacing="0.1em",
                            ),
                            rx.text(item.source, size="2", color=theme.TEXT, line_height="1.5"),
                            spacing="2",
                            align="start",
                        ),
                        side="top",
                        style={
                            "background": theme.BG_WINDOW,
                            "border": f"1px solid {theme.BORDER_STRONG}",
                            "border_radius": theme.RADIUS,
                            "padding": "12px",
                            "max_width": "260px",
                            "width": "auto",
                            "box_shadow": theme.SHADOW_LG,
                        },
                    ),
                ),
            ),
            spacing="0",
            align="start",
            min_width="0",
            max_width="100%",
            overflow="hidden",
            flex="1 1 0",
        ),

        #Sin `rx.spacer()`: era un hijo flexible más y se llevaba la mitad del
        #hueco libre, que es justo el que le falta al nombre del producto

        #Cantidad con ajuste rápido
        rx.hstack(
            rx.icon(
                "minus",
                size=13,
                color=theme.MUTED,
                cursor="pointer",
                on_click=ShoppingListState.adjust_qty(item.name, -1),
                _hover={"color": theme.DANGER},
            ),
            rx.text(
                item.qty_label,
                size="1",
                weight="bold",
                color=rx.cond(item.bought, theme.DIM, theme.TEXT),
                font_family=theme.FONT_MONO,
                white_space="nowrap",
                min_width="46px",
                text_align="center",
            ),
            rx.icon(
                "plus",
                size=13,
                color=theme.MUTED,
                cursor="pointer",
                on_click=ShoppingListState.adjust_qty(item.name, 1),
                _hover={"color": theme.SUCCESS},
            ),
            spacing="1",
            align="center",
            flex_shrink="0",
            padding="3px 6px",
            border_radius="999px",
            background=theme.BG_SUNKEN,
            border=f"1px solid {theme.BORDER}",
        ),

        rx.icon(
            "pencil",
            size=14,
            color=theme.MUTED,
            cursor="pointer",
            on_click=ShoppingListState.open_editor(item.name),
            _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
            flex_shrink="0",
        ),
        rx.icon(
            "trash-2",
            size=14,
            color=theme.MUTED,
            cursor="pointer",
            on_click=ShoppingListState.delete_item(item.name),
            _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
            flex_shrink="0",
        ),

        width="100%",
        align="center",
        #Separación más justa y menos relleno lateral: todo lo que se ahorra
        #aquí se lo queda el nombre del producto
        spacing="2",
        padding="10px 10px",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(item.bought, "transparent", theme.BG_CARD),
        border=f"1px solid {theme.BORDER}",
        opacity=rx.cond(item.bought, "0.6", "1"),
        transition="all 0.15s ease",
        _hover={"background": theme.BG_CARD_HOVER, "border_color": theme.BORDER_STRONG},
    )


def group_block(group: rx.Var[ShoppingGroup]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(group.icon, size=15, color=group.color),
            rx.text(group.label, size="2", weight="bold", color=theme.TEXT),
            rx.text(
                group.bought.to_string() + "/" + group.total.to_string(),
                size="1",
                color=theme.DIM,
                font_family=theme.FONT_MONO,
            ),
            rx.spacer(),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.vstack(
            rx.foreach(group["items"], item_row),
            spacing="2",
            width="100%",
        ),
        spacing="2",
        width="100%",
        align="start",
    )


# ---------------------------------------------------------------------------
# Diálogos
# ---------------------------------------------------------------------------
#Los campos (unidad, sección, supermercado, nota, básico...) son los mismos que
#usa el recetario: viven en `components/item_fields.py`
def _field_label(text: str) -> rx.Component:
    return field_label(text)


def _meal_preview_line(item: rx.Var[GeneratedItem]) -> rx.Component:
    """Un ingrediente de la vista previa, con su casilla para descartarlo.

    La casilla importa: casi siempre hay algo que ya tienes en casa, y sin
    poder quitarlo tocaría añadirlo y borrarlo después de la lista.
    """
    return rx.hstack(
        rx.checkbox(
            checked=item.selected,
            on_change=ShoppingListState.toggle_meal_line(item.key),
            color_scheme="green",
            size="1",
        ),
        rx.text(
            item.name,
            size="2",
            color=rx.cond(item.selected, theme.TEXT, theme.DIM),
            text_decoration=rx.cond(item.selected, "none", "line-through"),
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
            flex="1 1 0",
            min_width="0",
        ),
        rx.cond(
            item.staple,
            rx.icon("package", size=11, color=theme.PURPLE, flex_shrink="0", title="Básico de despensa"),
        ),
        rx.text(item.qty_label, size="1", color=theme.MUTED, flex_shrink="0", white_space="nowrap"),
        width="100%",
        align="center",
        spacing="2",
        padding="6px 8px",
        border_radius="8px",
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
        flex_shrink="0",
    )


def add_meal_dialog() -> rx.Component:
    """Añadir a la lista los ingredientes de una comida del recetario.

    Para lo que se cocina fuera del menú semanal: una tarta para llevar al
    trabajo, una cena para invitados. Se elige la comida, se dice para cuánta
    gente y sus ingredientes caen ya escalados y en unidades de compra.

    Lo que entra por aquí **no** queda marcado como "del menú semanal", así que
    regenerar la semana no se lo lleva por delante.
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("chef-hat", theme.PURPLE, size=19, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Añadir una comida", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Sus ingredientes, escalados para los que seáis",
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(
                        "x", size=18, color=theme.MUTED, cursor="pointer",
                        on_click=ShoppingListState.close_meal_form,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                rx.vstack(
                    _field_label("COMIDA DEL RECETARIO"),
                    picker(
                        display=ShoppingListState.meal_pick,
                        options=[
                            rx.foreach(
                                CalendarState.meals,
                                lambda m: option(
                                    m.name, m.name, ShoppingListState.pick_meal,
                                    selected=m.name == ShoppingListState.meal_pick,
                                ),
                            )
                        ],
                        placeholder="Buscar una comida...",
                        width="300px",
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),

                rx.flex(
                    field(
                        "PARA CUÁNTAS PERSONAS",
                        rx.hstack(
                            rx.icon(
                                "minus", size=14, color=theme.MUTED, cursor="pointer",
                                on_click=ShoppingListState.bump_meal_people(-1),
                                _hover={"color": theme.TEXT},
                            ),
                            rx.input(
                                value=ShoppingListState.meal_people,
                                on_change=ShoppingListState.set_meal_people,
                                type="number",
                                size="2",
                                text_align="center",
                                flex="1 1 0",
                                min_width="0",
                            ),
                            rx.icon(
                                "plus", size=14, color=theme.MUTED, cursor="pointer",
                                on_click=ShoppingListState.bump_meal_people(1),
                                _hover={"color": theme.TEXT},
                            ),
                            spacing="2",
                            align="center",
                            width="100%",
                        ),
                        "170px",
                    ),
                    field(
                        "INCLUIR BÁSICOS",
                        rx.hstack(
                            rx.switch(
                                checked=ShoppingListState.meal_include_staples,
                                on_change=ShoppingListState.toggle_meal_staples,
                                color_scheme="purple",
                            ),
                            rx.text("Sal, aceite, especias...", size="1", color=theme.DIM),
                            spacing="2",
                            align="center",
                            height="32px",
                        ),
                        "190px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),

                rx.cond(
                    ShoppingListState.has_meal_preview,
                    rx.vstack(
                        rx.hstack(
                            _field_label("SE AÑADIRÁ"),
                            pill(
                                ShoppingListState.meal_preview_count.to_string(),
                                theme.PURPLE,
                                "shopping-basket",
                            ),
                            rx.spacer(),
                            rx.text(
                                "Desmarca lo que ya tengas",
                                size="1",
                                color=theme.DIM,
                            ),
                            width="100%",
                            align="center",
                            spacing="2",
                        ),
                        rx.vstack(
                            rx.foreach(ShoppingListState.meal_preview, _meal_preview_line),
                            spacing="1",
                            width="100%",
                            max_height="260px",
                            overflow_y="auto",
                            overflow_x="hidden",
                        ),
                        spacing="2",
                        width="100%",
                        align="start",
                    ),
                    rx.cond(
                        ShoppingListState.meal_pick != "",
                        info_banner(
                            "Esa comida no tiene ingredientes guardados. Edítala en el recetario "
                            "y añádeselos para poder tirar de ella aquí.",
                            icon="triangle-alert",
                            color=theme.WARNING,
                        ),
                        info_banner(
                            "Elige una comida y verás aquí lo que hay que comprar. Si ya tenías "
                            "algo de eso en la lista, se suma en vez de sustituirse.",
                            icon="info",
                            color=theme.ACCENT,
                        ),
                    ),
                ),

                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=ShoppingListState.close_meal_form,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("shopping-basket", size=15),
                        rx.text("Añadir a la lista", size="2"),
                        on_click=ShoppingListState.add_meal_to_list,
                        color_scheme="purple",
                        size="2",
                        type="button",
                        cursor="pointer",
                        loading=ShoppingListState.adding_meal,
                        disabled=~ShoppingListState.has_meal_preview,
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "520px",
                "max_height": "90vh",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=ShoppingListState.show_meal_form,
    )


def add_item_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("package-plus", theme.MEAL, size=19, box="42px"),
                    rx.dialog.title("Añadir producto", margin="0", size="4", weight="bold"),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer", on_click=ShoppingListState.close_add_form),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    _field_label("PRODUCTO"),
                    #Del catálogo: dentro del desplegable se busca, se crea el
                    #que falte y se edita cualquiera
                    product_picker(
                        ShoppingListState.new_item_name,
                        ShoppingListState.pick_new_item,
                        placeholder="Elegir producto del catálogo...",
                    ),
                    rx.cond(
                        ShoppingListState.errors["name"] != "",
                        rx.text(ShoppingListState.errors["name"], color=theme.DANGER, size="1"),
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "CANTIDAD",
                        qty_input(ShoppingListState.new_item_qty, ShoppingListState.change_qty),
                        "88px",
                        grow=False,
                    ),
                    field(
                        "UNIDAD",
                        units_select(ShoppingListState.new_item_unit, ShoppingListState.set_new_item_unit),
                        "140px",
                    ),
                    field(
                        "SECCIÓN DEL SÚPER",
                        section_select(ShoppingListState.new_item_cat, ShoppingListState.set_new_item_cat),
                        "160px",
                    ),
                    field(
                        "SUPERMERCADO",
                        shop_select(ShoppingListState.new_item_shop, ShoppingListState.set_new_item_shop),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    ShoppingListState.errors["quantity"] != "",
                    rx.text(ShoppingListState.errors["quantity"], color=theme.DANGER, size="1"),
                ),
                rx.vstack(
                    _field_label("NOTA (OPCIONAL)"),
                    note_input(ShoppingListState.new_item_note, ShoppingListState.set_new_item_note),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    _field_label("BÁSICO DE DESPENSA"),
                    staple_switch(ShoppingListState.new_item_staple, ShoppingListState.set_new_item_staple),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=ShoppingListState.close_add_form,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("plus", size=15),
                        rx.text("Añadir", size="2"),
                        on_click=ShoppingListState.add_item,
                        color_scheme="green",
                        size="2",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "480px",
                #Con todos los campos, en móvil el diálogo pide scroll propio
                "max_height": "88vh",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=ShoppingListState.show_add_form,
    )


def edit_item_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("pencil", theme.ACCENT, size=18, box="42px"),
                    rx.dialog.title("Editar producto", margin="0", size="4", weight="bold"),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer", on_click=ShoppingListState.close_editor),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    _field_label("PRODUCTO"),
                    product_picker(
                        ShoppingListState.edit_name,
                        ShoppingListState.pick_edit_item,
                        placeholder="Elegir producto del catálogo...",
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "CANTIDAD",
                        qty_input(ShoppingListState.edit_qty, ShoppingListState.set_edit_qty),
                        "88px",
                        grow=False,
                    ),
                    field(
                        "UNIDAD",
                        units_select(ShoppingListState.edit_unit, ShoppingListState.set_edit_unit),
                        "140px",
                    ),
                    field(
                        "SECCIÓN DEL SÚPER",
                        section_select(ShoppingListState.edit_cat, ShoppingListState.set_edit_cat),
                        "160px",
                    ),
                    field(
                        "SUPERMERCADO",
                        shop_select(ShoppingListState.edit_shop, ShoppingListState.set_edit_shop),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    _field_label("NOTA"),
                    note_input(ShoppingListState.edit_note, ShoppingListState.set_edit_note),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    _field_label("DE QUÉ RECETAS VIENE"),
                    rx.input(
                        placeholder="Paella, Arroz con pollo...",
                        value=ShoppingListState.edit_source,
                        on_change=ShoppingListState.set_edit_source,
                        size="2",
                        width="100%",
                        max_length=200,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "BÁSICO DE DESPENSA",
                        staple_switch(ShoppingListState.edit_staple, ShoppingListState.set_edit_staple),
                        "180px",
                    ),
                    field(
                        "EN EL CARRO",
                        bought_switch(ShoppingListState.edit_bought, ShoppingListState.set_edit_bought),
                        "180px",
                    ),
                    field(
                        "FIJADO",
                        pinned_switch(ShoppingListState.edit_pinned, ShoppingListState.set_edit_pinned),
                        "180px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=ShoppingListState.close_editor,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("check", size=15),
                        rx.text("Guardar", size="2"),
                        on_click=ShoppingListState.save_edit,
                        color_scheme="green",
                        size="2",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "480px",
                "max_height": "88vh",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=ShoppingListState.show_edit_form,
    )


def users_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("users", theme.PURPLE, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Lista compartida", margin="0", size="4", weight="bold"),
                        rx.text("Todos veis y editáis la misma lista", size="1", color=theme.MUTED),
                        spacing="0",
                        align="start",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    rx.foreach(
                        ShoppingListState.shared_users,
                        lambda user: rx.hstack(
                            rx.icon("circle-user", size=16, color=theme.ACCENT),
                            rx.text(user.username, size="2", weight="medium", color=theme.TEXT),
                            rx.spacer(),
                            rx.cond(
                                user.id != UserState.current_user.id,
                                rx.icon_button(
                                    rx.icon("user-minus", size=14),
                                    on_click=ShoppingListState.remove_user_from_list(user.id, user.username),
                                    color_scheme="red",
                                    variant="ghost",
                                    size="1",
                                ),
                                rx.text("tú", size="1", color=theme.DIM),
                            ),
                            width="100%",
                            align="center",
                            spacing="2",
                            padding="8px 10px",
                            border_radius=theme.RADIUS_SM,
                            background=theme.BG_SUNKEN,
                            border=f"1px solid {theme.BORDER}",
                        ),
                    ),
                    spacing="2",
                    width="100%",
                    max_height="200px",
                    overflow_y="auto",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    _field_label("AÑADIR POR NOMBRE DE USUARIO"),
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=ShoppingListState.new_user_input,
                        on_change=ShoppingListState.set_new_user_input,
                        size="2",
                        width="100%",
                    ),
                    rx.cond(
                        ShoppingListState.add_user_error != "",
                        rx.text(ShoppingListState.add_user_error, color=theme.DANGER, size="1"),
                    ),
                    rx.text(
                        "Al añadir a alguien, su lista actual se fusiona con la tuya.",
                        size="1",
                        color=theme.DIM,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.hstack(
                    rx.dialog.close(rx.button("Cerrar", variant="soft", color_scheme="gray", size="2")),
                    rx.button(
                        rx.icon("user-plus", size=15),
                        rx.text("Añadir", size="2"),
                        on_click=ShoppingListState.add_user_to_list,
                        color_scheme="green",
                        size="2",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "440px",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=ShoppingListState.show_users_panel,
        on_open_change=lambda opened: rx.cond(
            opened,
            ShoppingListState.toggle_users_panel,
            ShoppingListState.toggle_users_panel,
        ),
    )


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
def _progress_strip() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("En el carro", size="1", color=theme.MUTED),
            rx.spacer(),
            rx.text(
                ShoppingListState.bought_count.to_string()
                + " / "
                + ShoppingListState.total_items.to_string()
                + " productos",
                size="1",
                color=theme.TEXT,
                weight="bold",
                font_family=theme.FONT_MONO,
            ),
            width="100%",
            align="center",
        ),
        progress_bar(ShoppingListState.progress_percent, theme.SUCCESS),
        spacing="2",
        width="100%",
    )


def _toolbar() -> rx.Component:
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon("search", size=15)),
            placeholder="Buscar producto...",
            value=ShoppingListState.search,
            on_change=ShoppingListState.set_search,
            size="2",
            width="100%",
            max_width="280px",
            variant="surface",
            radius="full",
        ),
        rx.button(
            rx.icon(rx.cond(ShoppingListState.hide_bought, "eye-off", "eye"), size=15),
            rx.text(rx.cond(ShoppingListState.hide_bought, "Ver comprados", "Ocultar comprados"), size="2"),
            on_click=ShoppingListState.toggle_hide_bought,
            variant="soft",
            color_scheme="gray",
            size="2",
            radius="full",
            cursor="pointer",
        ),
        rx.cond(
            ShoppingListState.bought_count > 0,
            rx.button(
                rx.icon("brush-cleaning", size=15),
                rx.text("Quitar comprados", size="2"),
                on_click=ShoppingListState.clear_bought,
                variant="soft",
                color_scheme="orange",
                size="2",
                radius="full",
                cursor="pointer",
            ),
        ),
        #Marcar/desmarcar toda la lista de una vez
        rx.cond(
            ShoppingListState.pending_count > 0,
            rx.button(
                rx.icon("circle-check-big", size=15),
                rx.text("Todo comprado", size="2"),
                on_click=ShoppingListState.mark_all(True),
                variant="soft",
                color_scheme="green",
                size="2",
                radius="full",
                cursor="pointer",
            ),
            rx.button(
                rx.icon("circle", size=15),
                rx.text("Desmarcar todo", size="2"),
                on_click=ShoppingListState.mark_all(False),
                variant="soft",
                color_scheme="gray",
                size="2",
                radius="full",
                cursor="pointer",
            ),
        ),
        #Vaciar del todo: borra trabajo, así que pide confirmación
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.icon("trash-2", size=15),
                    rx.text("Vaciar lista", size="2"),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    radius="full",
                    cursor="pointer",
                )
            ),
            rx.dialog.content(
                rx.dialog.title("Vaciar la lista entera"),
                rx.dialog.description(
                    "Se borrarán todos los productos, comprados y pendientes. La lista es compartida: desaparecerán también para el resto.",
                    size="2",
                    color=theme.MUTED,
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                    rx.dialog.close(
                        rx.button("Vaciar", color_scheme="red", on_click=ShoppingListState.clear_all)
                    ),
                    spacing="3",
                    margin_top="1.5em",
                    justify="end",
                ),
                style={
                    "max_width": "430px",
                    "background": theme.BG_WINDOW,
                    "border": f"1px solid {theme.BORDER_STRONG}",
                    "border_radius": theme.RADIUS_LG,
                    "padding": "22px",
                },
            ),
        ),
        rx.spacer(),
        #Sin botón de refrescar: la lista se sincroniza sola cada pocos segundos
        rx.hstack(
            rx.box(
                width="7px", height="7px", border_radius="50%",
                background=theme.SUCCESS,
                box_shadow=f"0 0 8px {theme.SUCCESS}",
            ),
            rx.text("En vivo", size="1", color=theme.DIM),
            spacing="2", align="center", flex_shrink="0",
            title="Los cambios de cualquiera aparecen solos",
        ),
        width="100%",
        align="center",
        spacing="2",
        wrap="wrap",
    )


@rx.page(
    route="/shopping_list",
    title="Lista de Compras | CalendPy",
    on_load=[
        UserState.on_load,
        UserState.check_autenticated,
        ShoppingListState.load_shopping_list,
        ShoppingListState.sync_loop,
        UnitsState.load_units,
        ProductsState.load_products,
    ],
)
def shopping_list() -> rx.Component:
    return app_shell(
        add_item_dialog(),
        add_meal_dialog(),
        edit_item_dialog(),
        users_dialog(),
        #El gestor de supermercados lo monta ahora `app_shell`, porque también
        #se abre desde el recetario
        rx.vstack(
            page_header(
                icon="shopping-cart",
                title="Lista de la compra",
                subtitle="Ordenada por secciones del súper, para no dar vueltas",
                accent=theme.MEAL,
                actions=[
                    rx.button(
                        rx.icon("users", size=16),
                        rx.text("Compartir", size="2"),
                        on_click=ShoppingListState.toggle_users_panel,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        radius="full",
                        cursor="pointer",
                    ),
                    #Para lo que se cocina fuera del menú semanal: elige la
                    #comida, di para cuánta gente y entran sus ingredientes
                    rx.button(
                        rx.icon("chef-hat", size=16),
                        rx.text("Añadir comida", size="2"),
                        on_click=ShoppingListState.open_meal_form,
                        color_scheme="purple",
                        size="2",
                        radius="full",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("plus", size=16),
                        rx.text("Añadir producto", size="2"),
                        on_click=ShoppingListState.toggle_add_form,
                        color_scheme="green",
                        size="2",
                        radius="full",
                        cursor="pointer",
                    ),
                ],
                extra=_progress_strip(),
            ),

            stats_grid(
                stat_card(
                    icon="shopping-basket",
                    label="Productos",
                    value=ShoppingListState.total_items,
                    color=theme.ACCENT,
                ),
                stat_card(
                    icon="circle-dashed",
                    label="Por comprar",
                    value=ShoppingListState.pending_count,
                    color=theme.WARNING,
                ),
                stat_card(
                    icon="circle-check-big",
                    label="En el carro",
                    value=ShoppingListState.bought_count,
                    color=theme.SUCCESS,
                ),
                stat_card(
                    icon="sparkles",
                    label="Del menú semanal",
                    value=ShoppingListState.auto_count,
                    color=theme.PURPLE,
                ),
            ),

            rx.cond(~ShoppingListState.is_empty, _toolbar()),

            rx.cond(
                ShoppingListState.is_empty,
                empty_state(
                    icon="shopping-basket",
                    title="La lista está vacía",
                    description="Puedes añadir productos a mano, volcar de golpe los ingredientes de una comida del recetario, o dejar que el menú semanal la rellene con lo que planifiquéis.",
                    action=rx.hstack(
                        rx.link(
                            rx.button(
                                rx.icon("clipboard-list", size=15),
                                rx.text("Planificar la semana", size="2"),
                                color_scheme="blue",
                                size="3",
                                radius="full",
                                cursor="pointer",
                            ),
                            href="/menu_semanal",
                            underline="none",
                        ),
                        rx.button(
                            rx.icon("chef-hat", size=15),
                            rx.text("Añadir una comida", size="2"),
                            on_click=ShoppingListState.open_meal_form,
                            color_scheme="purple",
                            size="3",
                            radius="full",
                            cursor="pointer",
                        ),
                        rx.button(
                            rx.icon("plus", size=15),
                            rx.text("Añadir a mano", size="2"),
                            on_click=ShoppingListState.toggle_add_form,
                            variant="soft",
                            color_scheme="green",
                            size="3",
                            radius="full",
                            cursor="pointer",
                        ),
                        spacing="2",
                        wrap="wrap",
                        justify="center",
                    ),
                    color=theme.MEAL,
                ),
                rx.cond(
                    ShoppingListState.has_visible_items,
                    rx.vstack(
                        rx.foreach(ShoppingListState.groups, group_block),
                        spacing="5",
                        width="100%",
                    ),
                    empty_state(
                        icon="search-x",
                        title="Nada que mostrar",
                        description="Ningún producto coincide con el filtro actual.",
                        action=rx.button(
                            rx.icon("rotate-ccw", size=15),
                            "Quitar filtros",
                            on_click=ShoppingListState.clear_filters,
                            variant="soft",
                            color_scheme="gray",
                            size="2",
                            cursor="pointer",
                        ),
                        color=theme.MUTED,
                    ),
                ),
            ),

            rx.cond(
                ShoppingListState.auto_count > 0,
                info_banner(
                    "Los productos con ✨ los ha calculado el menú semanal a partir de los ingredientes. Puedes editarlos o borrarlos: al volver a generar, solo se recalculan esos.",
                    icon="sparkles",
                    color=theme.PURPLE,
                ),
            ),

            spacing="5",
            width="100%",
            max_width="1000px",
            margin="0 auto",
            align="center",
        ),
    )
