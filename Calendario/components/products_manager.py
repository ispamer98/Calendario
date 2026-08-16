# Calendario/components/products_manager.py
"""
Catálogo de productos: el selector y su gestor.

La idea es que haya **un solo botón**: el de elegir producto. Dentro del
desplegable está todo lo demás — buscar, crear el que falte sin salir de ahí
(«Crear "X"») y corregir cualquiera con el lápiz, que abre el gestor con ese
producto ya cargado.

Así los ingredientes dejan de ser texto libre (que acababa en "Tomate",
"tomates" y "Tomate " como tres productos distintos) sin convertirse en una
jaula: lo que falte se añade en el momento.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.item_fields import (
    field,
    field_label,
    note_input,
    section_select,
    shop_select,
    staple_switch,
    units_select,
)
from Calendario.components.picker import PickerState, picker
from Calendario.components.ui import icon_badge, info_banner
from Calendario.state.products_state import ProductsState


def manage_products_button(title: str = "Gestionar el catálogo de productos") -> rx.Component:
    return rx.icon(
        "settings-2",
        size=15,
        color=theme.MUTED,
        cursor="pointer",
        on_click=ProductsState.open_manager,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease",
        flex_shrink="0",
        title=title,
    )


# ---------------------------------------------------------------------------
# Selector de producto
# ---------------------------------------------------------------------------
def _product_option(product, on_pick) -> rx.Component:
    """Una fila del desplegable: elegir con un toque, corregir con el lápiz.

    Elegir y editar van en **dos zonas separadas**, cada una dentro de su
    `popover.close`: si el lápiz fuese un hijo de la zona de elegir, tocarlo
    haría las dos cosas a la vez.
    """
    row = rx.hstack(
        rx.popover.close(
            rx.hstack(
                rx.icon(product.cat_icon, size=13, color=product.cat_color, flex_shrink="0"),
                rx.box(
                    rx.text(
                        product.name,
                        size="2",
                        color=theme.TEXT,
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    flex="1 1 0",
                    min_width="0",
                    overflow="hidden",
                ),
                rx.cond(
                    product.shop != "",
                    rx.icon("store", size=11, color=theme.WARNING, flex_shrink="0"),
                ),
                rx.cond(
                    product.staple,
                    rx.icon("package", size=11, color=theme.PURPLE, flex_shrink="0"),
                ),
                rx.text(product.qty.to_string() + " " + product.unit, size="1", color=theme.DIM,
                        flex_shrink="0", white_space="nowrap"),
                flex="1 1 0",
                min_width="0",
                align="center",
                spacing="2",
                cursor="pointer",
                on_mouse_down=rx.noop().prevent_default,
                on_click=[on_pick(product.name), PickerState.finish],
                overflow="hidden",
            )
        ),
        rx.popover.close(
            rx.icon(
                "pencil",
                size=12,
                color=theme.MUTED,
                flex_shrink="0",
                cursor="pointer",
                title="Editar este producto",
                on_mouse_down=rx.noop().prevent_default,
                on_click=ProductsState.open_manager_for(product.id),
                _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
            )
        ),
        width="100%",
        align="center",
        spacing="2",
        padding="7px 9px",
        border_radius="8px",
        _hover={"background": theme.BG_CARD_HOVER},
        overflow="hidden",
    )
    return rx.cond(product.name.lower().contains(PickerState.query.lower()), row)


def _create_option(on_pick) -> rx.Component:
    """«Crear "lo que has escrito"» — solo si no existe ya en el catálogo."""
    typed = PickerState.query.strip()
    return rx.cond(
        (typed != "") & ~ProductsState.lower_names.contains(typed.lower()),
        rx.popover.close(
            rx.hstack(
                rx.icon("plus", size=13, color=theme.MEAL, flex_shrink="0"),
                rx.box(
                    rx.text(
                        'Crear "' + typed + '"',
                        size="1",
                        color=theme.MEAL,
                        weight="medium",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    flex="1 1 0",
                    min_width="0",
                    overflow="hidden",
                ),
                spacing="2",
                align="center",
                width="100%",
                padding="7px 9px",
                border_radius="8px",
                cursor="pointer",
                on_mouse_down=rx.noop().prevent_default,
                #Se crea en el catálogo y se elige en el mismo gesto
                on_click=[ProductsState.quick_add(typed), on_pick(typed), PickerState.finish],
                _hover={"background": theme.alpha(theme.MEAL, 0.12)},
                border=f"1px dashed {theme.alpha(theme.MEAL, 0.4)}",
            )
        ),
    )


def product_picker(value, on_pick, placeholder: str = "Elegir producto...") -> rx.Component:
    """Desplegable de producto: buscar, elegir, crear y editar, todo dentro.

    `on_pick` recibe el **nombre**; quien lo reciba resuelve el resto de datos
    (unidad, sección, súper...) contra el catálogo.
    """
    return picker(
        display=value,
        options=[
            rx.foreach(ProductsState.products, lambda p: _product_option(p, on_pick)),
        ],
        placeholder=placeholder,
        search_placeholder="Buscar o escribir uno nuevo...",
        footer=rx.vstack(
            _create_option(on_pick),
            rx.cond(
                ProductsState.is_empty,
                info_banner(
                    "El catálogo está vacío. ¿Falta aplicar la migración 013_products.sql?",
                    icon="triangle-alert",
                    color=theme.WARNING,
                ),
            ),
            rx.hstack(
                rx.icon("settings-2", size=13, color=theme.ACCENT, flex_shrink="0"),
                rx.text("Gestionar catálogo", size="1", color=theme.ACCENT),
                rx.spacer(),
                rx.text(
                    ProductsState.product_count.to_string() + " productos",
                    size="1",
                    color=theme.DIM,
                ),
                spacing="2",
                align="center",
                width="100%",
                padding="7px 9px",
                border_radius="8px",
                cursor="pointer",
                on_mouse_down=rx.noop().prevent_default,
                on_click=ProductsState.open_manager,
                _hover={"background": theme.alpha(theme.ACCENT, 0.10)},
                border_top=f"1px solid {theme.BORDER}",
            ),
            spacing="2",
            width="100%",
        ),
        width="300px",
        #El «+» de al lado abre el catálogo con la ficha en blanco: es la vía
        #rápida para meter un producto con todos sus datos
        on_add=ProductsState.open_manager,
        add_title="Añadir un producto nuevo al catálogo",
    )


# ---------------------------------------------------------------------------
# Gestor del catálogo
# ---------------------------------------------------------------------------
def _meta_chip(text, color: str, icon: str = "") -> rx.Component:
    """Dato secundario del producto, en su propia etiqueta.

    Antes iban todos seguidos separados por puntos y se pegaban al nombre. Como
    etiquetas sueltas se distinguen de un vistazo y saltan de línea solas.
    """
    return rx.hstack(
        *([rx.icon(icon, size=10, color=color, flex_shrink="0")] if icon else []),
        rx.text(
            text,
            size="1",
            color=color,
            white_space="nowrap",
            overflow="hidden",
            text_overflow="ellipsis",
        ),
        spacing="1",
        align="center",
        padding="1px 7px",
        border_radius="999px",
        background=theme.alpha(theme.TEXT, 0.04),
        border=f"1px solid {theme.BORDER}",
        max_width="160px",
        flex_shrink="0",
    )


def _catalog_row(product) -> rx.Component:
    """Ficha de un producto del catálogo.

    El nombre va **solo, en su propia línea y a todo el ancho**: es lo que se
    busca con la vista. Lo demás (unidad, sección, súper, básico, nota) baja a
    una segunda línea de etiquetas que se reparten y saltan de línea.
    """
    return rx.hstack(
        rx.center(
            rx.icon(product.cat_icon, size=15, color=product.cat_color),
            min_width="30px", width="30px", height="30px",
            border_radius="8px",
            background=product.cat_color + "22",
            border="1px solid " + product.cat_color + "55",
            flex_shrink="0",
            title=product.cat_label,
        ),
        rx.vstack(
            #Línea 1: solo el nombre, con todo el ancho disponible
            rx.text(
                product.name,
                size="2",
                color=theme.TEXT,
                weight="medium",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                width="100%",
            ),
            #Línea 2: el resto de datos, cada uno en su etiqueta
            rx.hstack(
                _meta_chip(product.qty.to_string() + " " + product.unit, theme.MUTED, "scale"),
                _meta_chip(product.cat_label, product.cat_color),
                rx.cond(product.shop != "", _meta_chip(product.shop, theme.WARNING, "store")),
                rx.cond(product.staple, _meta_chip("Básico", theme.PURPLE, "package")),
                rx.cond(product.note != "", _meta_chip(product.note, theme.ACCENT, "sticky-note")),
                spacing="1",
                align="center",
                wrap="wrap",
                width="100%",
            ),
            spacing="1",
            align="start",
            flex="1 1 0",
            min_width="0",
            width="100%",
            overflow="hidden",
        ),
        #Sin `rx.spacer()`: se llevaba la mitad del hueco libre, que es
        #justo el que le hace falta al nombre
        rx.icon(
            "pencil",
            size=15,
            color=theme.MUTED,
            cursor="pointer",
            on_click=ProductsState.edit(product.id),
            _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
            flex_shrink="0",
            title="Editar todos los datos de este producto",
        ),
        rx.icon(
            "trash-2",
            size=15,
            color=theme.MUTED,
            cursor="pointer",
            on_click=ProductsState.remove(product.id),
            _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
            flex_shrink="0",
        ),
        width="100%",
        align="center",
        spacing="3",
        padding="10px 12px",
        min_height="62px",
        #ESTE es el que faltaba: la lista es un flex en columna con altura
        #limitada, y por defecto sus hijos se ENCOGEN para caber. Por eso las
        #fichas salían aplastadas y el nombre cortado por la mitad.
        flex_shrink="0",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(
            ProductsState.editing_id == product.id,
            theme.alpha(theme.ACCENT, 0.10),
            theme.BG_SUNKEN,
        ),
        border=rx.cond(
            ProductsState.editing_id == product.id,
            f"1px solid {theme.alpha(theme.ACCENT, 0.45)}",
            f"1px solid {theme.BORDER}",
        ),
        overflow="hidden",
    )


def products_manager_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("carrot", theme.MEAL, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Catálogo de productos", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Los ingredientes salen de aquí, con sus valores por defecto",
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(
                        "x",
                        size=18,
                        color=theme.MUTED,
                        cursor="pointer",
                        on_click=ProductsState.close_manager,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Alta / edición
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            rx.cond(ProductsState.is_editing, "pencil", "plus"),
                            size=13,
                            color=rx.cond(ProductsState.is_editing, theme.ACCENT, theme.MEAL),
                        ),
                        field_label(
                            rx.cond(ProductsState.is_editing, "EDITANDO PRODUCTO", "NUEVO PRODUCTO")
                        ),
                        rx.spacer(),
                        rx.cond(
                            ProductsState.is_editing,
                            rx.text(
                                "Cancelar edición",
                                size="1",
                                color=theme.MUTED,
                                cursor="pointer",
                                on_click=ProductsState.cancel_edit,
                                _hover={"color": theme.DANGER, "text_decoration": "underline"},
                            ),
                        ),
                        width="100%",
                        align="center",
                        spacing="2",
                    ),
                    rx.input(
                        placeholder="Nombre del producto (ej. Pechuga de pollo)",
                        value=ProductsState.form_name,
                        on_change=ProductsState.set_form_name,
                        size="2",
                        width="100%",
                        max_length=40,
                        #Al darle al lápiz de un producto de abajo, el foco sube
                        #aquí: si no, la ficha se rellenaba fuera de la vista y
                        #parecía que el lápiz no hacía nada
                        id="producto-nombre",
                    ),
                    rx.flex(
                        field(
                            "CANTIDAD DE RECETA",
                            rx.input(
                                value=ProductsState.form_qty,
                                on_change=ProductsState.set_form_qty,
                                type="number",
                                size="2",
                                width="100%",
                            ),
                            "100px",
                            grow=False,
                        ),
                        field(
                            "UNIDAD DE RECETA",
                            units_select(ProductsState.form_unit, ProductsState.set_form_unit),
                            "140px",
                        ),
                        field(
                            "SECCIÓN DEL SÚPER",
                            section_select(ProductsState.form_cat, ProductsState.set_form_cat),
                            "160px",
                        ),
                        field(
                            "SUPERMERCADO",
                            shop_select(ProductsState.form_shop, ProductsState.set_form_shop),
                            "170px",
                        ),
                        wrap="wrap",
                        gap="12px",
                        width="100%",
                        align="start",
                    ),
                    #La medida con la que se compra en el súper. Es lo que se
                    #propone al guardar algo en la despensa, y lo que permite
                    #restar "300 ml" de una despensa que cuenta briks.
                    rx.flex(
                        field(
                            "MEDIDA DE COMPRA",
                            rx.input(
                                value=ProductsState.form_pack_qty,
                                on_change=ProductsState.set_form_pack_qty,
                                type="number",
                                size="2",
                                width="100%",
                                placeholder="0",
                            ),
                            "100px",
                            grow=False,
                        ),
                        field(
                            "UNIDAD DEL ENVASE",
                            units_select(
                                ProductsState.form_pack_unit, ProductsState.set_form_pack_unit
                            ),
                            "140px",
                        ),
                        rx.box(
                            rx.text(
                                "Lo que trae un envase del súper: un brik de leche, 1 l; un "
                                "paquete de arroz, 1 kg. En 0 si no aplica.",
                                size="1",
                                color=theme.DIM,
                                line_height="1.4",
                            ),
                            flex="1 1 200px",
                            min_width="180px",
                            padding_top="16px",
                        ),
                        wrap="wrap",
                        gap="12px",
                        width="100%",
                        align="start",
                    ),
                    note_input(ProductsState.form_note, ProductsState.set_form_note),
                    rx.flex(
                        field(
                            "BÁSICO DE DESPENSA",
                            staple_switch(ProductsState.form_staple, ProductsState.set_form_staple),
                            "200px",
                        ),
                        rx.hstack(
                            rx.button(
                                rx.icon(rx.cond(ProductsState.is_editing, "check", "plus"), size=15),
                                rx.text(
                                    rx.cond(ProductsState.is_editing, "Guardar cambios", "Añadir al catálogo"),
                                    size="2",
                                ),
                                on_click=ProductsState.save,
                                color_scheme=rx.cond(ProductsState.is_editing, "blue", "green"),
                                size="2",
                                type="button",
                                cursor="pointer",
                                loading=ProductsState.saving,
                            ),
                            justify="end",
                            align="center",
                            flex="1 1 auto",
                        ),
                        wrap="wrap",
                        gap="12px",
                        width="100%",
                        align="end",
                    ),
                    spacing="2",
                    width="100%",
                    align="start",
                    padding="12px",
                    border_radius=theme.RADIUS_SM,
                    background=rx.cond(
                        ProductsState.is_editing,
                        theme.alpha(theme.ACCENT, 0.07),
                        theme.BG_SUNKEN,
                    ),
                    border=rx.cond(
                        ProductsState.is_editing,
                        f"1px solid {theme.alpha(theme.ACCENT, 0.35)}",
                        f"1px solid {theme.BORDER}",
                    ),
                ),

                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Listado
                rx.input(
                    rx.input.slot(rx.icon("search", size=15)),
                    placeholder="Buscar en el catálogo...",
                    value=ProductsState.manager_search,
                    on_change=ProductsState.set_manager_search,
                    size="2",
                    width="100%",
                ),
                rx.cond(
                    ProductsState.is_empty,
                    info_banner(
                        "El catálogo está vacío. Si acabas de instalar la novedad, aplica "
                        "013_products.sql en Supabase: rellena el catálogo con los ingredientes "
                        "que ya usaban tus recetas.",
                        icon="triangle-alert",
                        color=theme.WARNING,
                    ),
                    rx.vstack(
                        rx.foreach(ProductsState.filtered, _catalog_row),
                        spacing="2",
                        width="100%",
                        max_height="260px",
                        overflow_y="auto",
                        overflow_x="hidden",
                    ),
                ),

                info_banner(
                    "Cambiar el nombre de un producto lo cambia también en las recetas y en la "
                    "lista de la compra. Borrarlo solo lo quita del desplegable.",
                    icon="info",
                    color=theme.ACCENT,
                ),

                rx.hstack(
                    rx.button(
                        "Listo",
                        on_click=ProductsState.close_manager,
                        variant="soft",
                        color_scheme="gray",
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
                "max_width": "560px",
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
        open=ProductsState.show_manager,
    )
