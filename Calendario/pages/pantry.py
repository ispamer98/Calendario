# pantry.py
"""
Despensa: lo que hay en casa.

La otra mitad de la lista de la compra. La lista dice lo que falta; esto dice lo
que hay, agrupado por dónde está guardado (nevera, congelador, despensa) para
que se lea igual que se abre un armario.

Se llena sola: lo que marcas como comprado en la lista entra aquí. Y cierra el
círculo por el otro lado — lo que se está acabando vuelve a la compra de un
toque.

Es una lista independiente: se comparte con quien tú digas, igual que la de la
compra y sin ir atada a ella.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.ui import (
    empty_state,
    icon_badge,
    info_banner,
    page_header,
    pill,
    stat_card,
    stats_grid,
)
from Calendario.components.item_fields import (
    expiry_input,
    field,
    field_label,
    min_qty_input,
    note_input,
    place_select,
    qty_input,
    section_select,
    shop_select,
    units_select,
)
from Calendario.components.products_manager import product_picker
from Calendario.model.model import PantryGroup, PantryRow
from Calendario.state.consume_state import ConsumeState
from Calendario.state.pantry_state import PantryState
from Calendario.state.products_state import ProductsState
from Calendario.state.shopping_list_state import ShoppingListState
from Calendario.state.units_state import UnitsState
from Calendario.state.user_state import UserState


# ---------------------------------------------------------------------------
# Fila de producto
# ---------------------------------------------------------------------------
def item_row(item: rx.Var[PantryRow]) -> rx.Component:
    return rx.hstack(
        #Sitio donde se guarda: el mismo icono que encabeza su grupo, para
        #reconocerlo también cuando la lista está filtrada o buscando
        rx.center(
            rx.icon(
                rx.match(
                    item.place,
                    *[(key, style["icon"]) for key, style in theme.PANTRY_PLACE_STYLE.items()],
                    "boxes",
                ),
                size=15,
                color=rx.match(
                    item.place,
                    *[(key, style["color"]) for key, style in theme.PANTRY_PLACE_STYLE.items()],
                    theme.MUTED,
                ),
            ),
            min_width="30px",
            width="30px",
            height="30px",
            border_radius="9px",
            background=theme.BG_SUNKEN,
            border=f"1px solid {theme.BORDER}",
            flex_shrink="0",
        ),

        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.text(
                        item.name,
                        size="2",
                        weight="medium",
                        color=rx.cond(item.empty, theme.DIM, theme.TEXT),
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    flex="1 1 0",
                    min_width="0",
                    overflow="hidden",
                ),
                #Se está acabando: es lo único que hay que mirar de un vistazo
                rx.cond(
                    item.low,
                    rx.icon(
                        rx.cond(item.empty, "circle-alert", "trending-down"),
                        size=13,
                        color=rx.cond(item.empty, theme.DANGER, theme.WARNING),
                        flex_shrink="0",
                        title=rx.cond(item.empty, "Se ha acabado", "Por debajo del mínimo"),
                    ),
                ),
                rx.cond(
                    item.expiry_label != "",
                    rx.hstack(
                        rx.icon(
                            rx.cond(item.expired, "calendar-x", "calendar-clock"),
                            size=11,
                            color=item.expiry_color,
                            flex_shrink="0",
                        ),
                        rx.text(
                            item.expiry_label,
                            size="1",
                            color=item.expiry_color,
                            white_space="nowrap",
                        ),
                        spacing="1",
                        align="center",
                        flex_shrink="0",
                    ),
                ),
                spacing="2",
                align="center",
                width="100%",
                max_width="100%",
                min_width="0",
                overflow="hidden",
            ),
            #La nota y el mínimo, si los hay
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
            rx.hstack(
                rx.cond(
                    item.min_label != "",
                    rx.text(item.min_label, size="1", color=theme.DIM, white_space="nowrap"),
                ),
                rx.cond(
                    item.updated_label != "",
                    rx.text(
                        "Actualizado " + item.updated_label,
                        size="1",
                        color=theme.DIM,
                        white_space="nowrap",
                        overflow="hidden",
                        text_overflow="ellipsis",
                    ),
                ),
                spacing="2",
                align="center",
                width="100%",
                max_width="100%",
                overflow="hidden",
            ),
            spacing="0",
            align="start",
            min_width="0",
            max_width="100%",
            overflow="hidden",
            flex="1 1 0",
        ),

        #Cuánto queda, con ajuste rápido: es lo que más se toca (gastar y reponer)
        rx.hstack(
            rx.icon(
                "minus",
                size=13,
                color=theme.MUTED,
                cursor="pointer",
                on_click=PantryState.adjust_qty(item.name, -1),
                _hover={"color": theme.DANGER},
            ),
            rx.text(
                item.qty_label,
                size="1",
                weight="bold",
                color=rx.cond(
                    item.empty,
                    theme.DANGER,
                    rx.cond(item.low, theme.WARNING, theme.TEXT),
                ),
                font_family=theme.FONT_MONO,
                white_space="nowrap",
                min_width="52px",
                text_align="center",
            ),
            rx.icon(
                "plus",
                size=13,
                color=theme.MUTED,
                cursor="pointer",
                on_click=PantryState.adjust_qty(item.name, 1),
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

        #A la compra: el camino de vuelta cuando algo se acaba
        rx.icon(
            "shopping-cart",
            size=14,
            color=rx.cond(item.low, theme.MEAL, theme.MUTED),
            cursor="pointer",
            on_click=PantryState.to_shopping_list(item.name),
            _hover={"color": theme.MEAL, "transform": "scale(1.2)"},
            flex_shrink="0",
            title="Añadir a la lista de la compra",
        ),
        rx.icon(
            "pencil",
            size=14,
            color=theme.MUTED,
            cursor="pointer",
            on_click=PantryState.open_editor(item.name),
            _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
            flex_shrink="0",
        ),
        rx.icon(
            "trash-2",
            size=14,
            color=theme.MUTED,
            cursor="pointer",
            on_click=PantryState.remove_item(item.name),
            _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
            flex_shrink="0",
        ),

        width="100%",
        align="center",
        spacing="2",
        padding="10px 10px",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(item.empty, "transparent", theme.BG_CARD),
        border=rx.cond(
            item.low,
            f"1px solid {theme.alpha(theme.WARNING, 0.35)}",
            f"1px solid {theme.BORDER}",
        ),
        opacity=rx.cond(item.empty, "0.7", "1"),
        transition="all 0.15s ease",
        _hover={"background": theme.BG_CARD_HOVER, "border_color": theme.BORDER_STRONG},
    )


def group_block(group: rx.Var[PantryGroup]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(group.icon, size=15, color=group.color),
            rx.text(group.label, size="2", weight="bold", color=theme.TEXT),
            rx.text(
                group.total.to_string() + " productos",
                size="1",
                color=theme.DIM,
                font_family=theme.FONT_MONO,
            ),
            rx.cond(
                group.low > 0,
                pill(group.low.to_string() + " por reponer", theme.WARNING, "trending-down"),
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
def _dialog_style(max_width: str = "480px") -> dict:
    return {
        "max_width": max_width,
        "max_height": "88vh",
        "overflow_y": "auto",
        "overflow_x": "hidden",
        "background": theme.BG_WINDOW,
        "border": f"1px solid {theme.BORDER_STRONG}",
        "border_radius": theme.RADIUS_LG,
        "padding": "22px",
        "box_shadow": theme.SHADOW_LG,
    }


def add_item_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("package-plus", theme.PANTRY, size=19, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Guardar en la despensa", margin="0", size="4", weight="bold"),
                        rx.text("Lo que ya tienes en casa", size="1", color=theme.MUTED),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(
                        "x", size=18, color=theme.MUTED, cursor="pointer",
                        on_click=PantryState.close_add_form,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    field_label("PRODUCTO"),
                    product_picker(
                        PantryState.new_name,
                        PantryState.pick_new_product,
                        placeholder="Elegir producto del catálogo...",
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "CANTIDAD",
                        qty_input(PantryState.new_qty, PantryState.set_new_qty),
                        "88px",
                        grow=False,
                    ),
                    field(
                        "UNIDAD",
                        units_select(PantryState.new_unit, PantryState.set_new_unit),
                        "140px",
                    ),
                    field(
                        "DÓNDE SE GUARDA",
                        place_select(PantryState.new_place, PantryState.set_new_place),
                        "160px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "AVISAR POR DEBAJO DE",
                        min_qty_input(PantryState.new_min, PantryState.set_new_min),
                        "150px",
                    ),
                    field(
                        "CADUCA EL (OPCIONAL)",
                        expiry_input(PantryState.new_expires, PantryState.set_new_expires),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "SECCIÓN DEL SÚPER",
                        section_select(PantryState.new_cat, PantryState.set_new_cat),
                        "160px",
                    ),
                    field(
                        "SUPERMERCADO",
                        shop_select(PantryState.new_shop, PantryState.set_new_shop),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    field_label("NOTA (OPCIONAL)"),
                    note_input(PantryState.new_note, PantryState.set_new_note),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    PantryState.new_already_home != "",
                    info_banner(
                        "Ya tienes " + PantryState.new_already_home + " en casa: lo que guardes "
                        "ahora se suma a eso.",
                        icon="plus",
                        color=theme.PANTRY,
                    ),
                    info_banner(
                        "Si ya tenías ese producto en casa, la cantidad se suma a la que había.",
                        icon="info",
                        color=theme.ACCENT,
                    ),
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=PantryState.close_add_form,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("plus", size=15),
                        rx.text("Guardar", size="2"),
                        on_click=PantryState.add_item,
                        color_scheme="amber",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style=_dialog_style(),
        ),
        open=PantryState.show_add_form,
    )


def edit_item_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("pencil", theme.ACCENT, size=18, box="42px"),
                    rx.dialog.title("Editar producto", margin="0", size="4", weight="bold"),
                    rx.spacer(),
                    rx.icon(
                        "x", size=18, color=theme.MUTED, cursor="pointer",
                        on_click=PantryState.close_editor,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    field_label("PRODUCTO"),
                    product_picker(
                        PantryState.edit_name,
                        PantryState.pick_edit_product,
                        placeholder="Elegir producto del catálogo...",
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "CANTIDAD",
                        qty_input(PantryState.edit_qty, PantryState.set_edit_qty),
                        "88px",
                        grow=False,
                    ),
                    field(
                        "UNIDAD",
                        units_select(PantryState.edit_unit, PantryState.set_edit_unit),
                        "140px",
                    ),
                    field(
                        "DÓNDE SE GUARDA",
                        place_select(PantryState.edit_place, PantryState.set_edit_place),
                        "160px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "AVISAR POR DEBAJO DE",
                        min_qty_input(PantryState.edit_min, PantryState.set_edit_min),
                        "150px",
                    ),
                    field(
                        "CADUCA EL",
                        expiry_input(PantryState.edit_expires, PantryState.set_edit_expires),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.flex(
                    field(
                        "SECCIÓN DEL SÚPER",
                        section_select(PantryState.edit_cat, PantryState.set_edit_cat),
                        "160px",
                    ),
                    field(
                        "SUPERMERCADO",
                        shop_select(PantryState.edit_shop, PantryState.set_edit_shop),
                        "170px",
                    ),
                    wrap="wrap",
                    gap="12px",
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    field_label("NOTA"),
                    note_input(PantryState.edit_note, PantryState.set_edit_note),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        on_click=PantryState.close_editor,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("check", size=15),
                        rx.text("Guardar", size="2"),
                        on_click=PantryState.save_edit,
                        color_scheme="green",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                    padding_top="2",
                ),
                spacing="3",
                width="100%",
            ),
            style=_dialog_style(),
        ),
        open=PantryState.show_edit_form,
    )


def users_dialog() -> rx.Component:
    """Con quién se comparte la despensa.

    Es una lista **independiente** de la de la compra: tiene su propia gente y
    se comparte igual que aquella (por nombre de usuario, fusionando stocks).
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("users", theme.PURPLE, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Despensa compartida", margin="0", size="4", weight="bold"),
                        rx.text("Todos veis y editáis el mismo stock", size="1", color=theme.MUTED),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon(
                        "x", size=18, color=theme.MUTED, cursor="pointer",
                        on_click=PantryState.toggle_users_panel,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    rx.foreach(
                        PantryState.shared_users,
                        lambda user: rx.hstack(
                            rx.icon("circle-user", size=16, color=theme.PANTRY),
                            rx.text(user.username, size="2", weight="medium", color=theme.TEXT),
                            rx.spacer(),
                            rx.cond(
                                user.id != UserState.current_user.id,
                                rx.icon_button(
                                    rx.icon("user-minus", size=14),
                                    on_click=PantryState.remove_user(user.id, user.username),
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
                    field_label("AÑADIR POR NOMBRE DE USUARIO"),
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=PantryState.new_user_input,
                        on_change=PantryState.set_new_user_input,
                        size="2",
                        width="100%",
                    ),
                    rx.cond(
                        PantryState.add_user_error != "",
                        rx.text(PantryState.add_user_error, color=theme.DANGER, size="1"),
                    ),
                    rx.text(
                        "Al añadir a alguien, su despensa actual se fusiona con la tuya. "
                        "Es aparte de la lista de la compra: compartir una no comparte la otra.",
                        size="1",
                        color=theme.DIM,
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),
                rx.hstack(
                    rx.button(
                        "Cerrar",
                        on_click=PantryState.toggle_users_panel,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("user-plus", size=15),
                        rx.text("Añadir", size="2"),
                        on_click=PantryState.add_user_to_pantry,
                        color_scheme="green",
                        size="2",
                        cursor="pointer",
                    ),
                    spacing="2",
                    justify="end",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            style=_dialog_style("440px"),
        ),
        open=PantryState.show_users_panel,
    )


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
def _auto_stock_strip() -> rx.Component:
    """El automático, en la propia cabecera: es la idea entera de la pantalla."""
    return rx.hstack(
        rx.icon(
            rx.cond(PantryState.auto_stock, "zap", "zap-off"),
            size=15,
            color=rx.cond(PantryState.auto_stock, theme.PANTRY, theme.MUTED),
            flex_shrink="0",
        ),
        rx.text(
            rx.cond(
                PantryState.auto_stock,
                "Lo que marcas como comprado entra solo en la despensa",
                "El automático está apagado: la despensa la llevas a mano",
            ),
            size="1",
            color=theme.MUTED,
        ),
        rx.spacer(),
        rx.switch(
            checked=PantryState.auto_stock,
            on_change=PantryState.toggle_auto_stock,
            color_scheme="amber",
        ),
        width="100%",
        align="center",
        spacing="2",
        padding="10px 12px",
        border_radius=theme.RADIUS_SM,
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
    )


def _place_filters() -> rx.Component:
    """Atajos por sitio: enseñar solo la nevera es lo que se hace al cocinar."""
    return rx.flex(
        *[
            rx.hstack(
                rx.icon(style["icon"], size=13, color=style["color"], flex_shrink="0"),
                rx.text(style["label"], size="1", color=theme.TEXT, white_space="nowrap"),
                spacing="2",
                align="center",
                padding="5px 11px",
                border_radius="999px",
                cursor="pointer",
                background=rx.cond(
                    PantryState.place_filter == key,
                    theme.alpha(style["color"], 0.18),
                    theme.BG_CARD,
                ),
                border=rx.cond(
                    PantryState.place_filter == key,
                    f"1px solid {theme.alpha(style['color'], 0.5)}",
                    f"1px solid {theme.BORDER}",
                ),
                on_click=PantryState.filter_place(key),
                _hover={"background": theme.BG_CARD_HOVER},
                transition="all 0.15s ease",
            )
            for key, style in theme.PANTRY_PLACE_STYLE.items()
        ],
        wrap="wrap",
        gap="8px",
        width="100%",
    )


def _toolbar() -> rx.Component:
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon("search", size=15)),
            placeholder="Buscar en la despensa...",
            value=PantryState.search,
            on_change=PantryState.set_search,
            size="2",
            width="100%",
            max_width="280px",
            variant="surface",
            radius="full",
        ),
        rx.button(
            rx.icon("trending-down", size=15),
            rx.text(rx.cond(PantryState.only_low, "Ver todo", "Solo lo que falta"), size="2"),
            on_click=PantryState.toggle_only_low,
            variant="soft",
            color_scheme=rx.cond(PantryState.only_low, "orange", "gray"),
            size="2",
            radius="full",
            cursor="pointer",
        ),
        rx.button(
            rx.icon("calendar-clock", size=15),
            rx.text(rx.cond(PantryState.only_expiring, "Ver todo", "Caduca pronto"), size="2"),
            on_click=PantryState.toggle_only_expiring,
            variant="soft",
            color_scheme=rx.cond(PantryState.only_expiring, "red", "gray"),
            size="2",
            radius="full",
            cursor="pointer",
        ),
        rx.cond(
            PantryState.has_low,
            rx.button(
                rx.icon("shopping-cart", size=15),
                rx.text("Reponer lo que falta", size="2"),
                on_click=PantryState.restock_all,
                variant="soft",
                color_scheme="green",
                size="2",
                radius="full",
                cursor="pointer",
                title="Añade a la lista de la compra todo lo que está por debajo del mínimo",
            ),
        ),
        #Vaciar del todo: borra trabajo, así que pide confirmación
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.icon("trash-2", size=15),
                    rx.text("Vaciar", size="2"),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    radius="full",
                    cursor="pointer",
                )
            ),
            rx.dialog.content(
                rx.dialog.title("Vaciar la despensa"),
                rx.dialog.description(
                    "Se borrará todo el stock. La despensa es compartida: desaparecerá también "
                    "para el resto de la casa.",
                    size="2",
                    color=theme.MUTED,
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                    rx.dialog.close(
                        rx.button("Quitar solo lo agotado", variant="soft", color_scheme="orange",
                                  on_click=PantryState.clear_empty)
                    ),
                    rx.dialog.close(
                        rx.button("Vaciar todo", color_scheme="red", on_click=PantryState.clear_all)
                    ),
                    spacing="3",
                    margin_top="1.5em",
                    justify="end",
                    wrap="wrap",
                ),
                style={
                    "max_width": "460px",
                    "background": theme.BG_WINDOW,
                    "border": f"1px solid {theme.BORDER_STRONG}",
                    "border_radius": theme.RADIUS_LG,
                    "padding": "22px",
                },
            ),
        ),
        rx.spacer(),
        #Sin botón de refrescar: el stock se sincroniza solo cada pocos segundos
        rx.hstack(
            rx.box(
                width="7px", height="7px", border_radius="50%",
                background=theme.SUCCESS,
                box_shadow=f"0 0 8px {theme.SUCCESS}",
            ),
            rx.text("En vivo", size="1", color=theme.DIM),
            spacing="2", align="center", flex_shrink="0",
            title="Los cambios de cualquiera de la casa aparecen solos",
        ),
        width="100%",
        align="center",
        spacing="2",
        wrap="wrap",
    )


@rx.page(
    route="/despensa",
    title="Despensa | CalendPy",
    on_load=[
        UserState.on_load,
        UserState.check_autenticated,
        PantryState.load_pantry,
        PantryState.sync_loop,
        UnitsState.load_units,
        ProductsState.load_products,
        #Los supermercados los pide el desplegable de súper de los diálogos
        ShoppingListState.load_supermarkets,
        #Si se llega desde el aviso de "toca comer", se abre directamente la
        #ventana de restar los ingredientes de esa comida
        ConsumeState.open_from_url,
    ],
)
def pantry() -> rx.Component:
    return app_shell(
        add_item_dialog(),
        edit_item_dialog(),
        users_dialog(),
        rx.vstack(
            page_header(
                icon="warehouse",
                title="Despensa",
                subtitle="Lo que hay en casa, sin abrir la nevera",
                accent=theme.PANTRY,
                actions=[
                    rx.button(
                        rx.icon("users", size=16),
                        rx.text("Compartir", size="2"),
                        on_click=PantryState.toggle_users_panel,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        radius="full",
                        cursor="pointer",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("shopping-cart", size=16),
                            rx.text("Lista de la compra", size="2"),
                            variant="soft",
                            color_scheme="green",
                            size="2",
                            radius="full",
                            cursor="pointer",
                        ),
                        href="/shopping_list",
                        underline="none",
                    ),
                    rx.button(
                        rx.icon("plus", size=16),
                        rx.text("Guardar producto", size="2"),
                        on_click=PantryState.open_add_form,
                        color_scheme="amber",
                        size="2",
                        radius="full",
                        cursor="pointer",
                    ),
                ],
                extra=_auto_stock_strip(),
            ),

            #Sin la migración 018 no hay dónde guardar el stock: se dice cuál es
            #y qué se pierde mientras tanto, igual que hace el resto de la app
            rx.cond(
                PantryState.unavailable,
                info_banner(
                    "La despensa necesita la migración 018_pantry.sql. Ejecútala en el SQL Editor "
                    "de Supabase y esta pantalla empezará a llenarse sola con lo que compres.",
                    icon="triangle-alert",
                    color=theme.WARNING,
                ),
            ),

            stats_grid(
                stat_card(
                    icon="boxes",
                    label="En casa",
                    value=PantryState.total_items,
                    color=theme.PANTRY,
                ),
                stat_card(
                    icon="trending-down",
                    label="Por reponer",
                    value=PantryState.low_count,
                    color=theme.WARNING,
                ),
                stat_card(
                    icon="calendar-clock",
                    label="Caduca pronto",
                    value=PantryState.expiring_count,
                    color=theme.ACCENT,
                ),
                stat_card(
                    icon="calendar-x",
                    label="Caducados",
                    value=PantryState.expired_count,
                    color=theme.DANGER,
                ),
            ),

            rx.cond(~PantryState.is_empty, _place_filters()),
            rx.cond(~PantryState.is_empty, _toolbar()),

            rx.cond(
                PantryState.is_empty,
                empty_state(
                    icon="warehouse",
                    title="La despensa está vacía",
                    description=(
                        "No hace falta llenarla a mano: marca la compra en la lista y lo que "
                        "compres irá entrando aquí solo. Si quieres empezar con lo que ya tienes "
                        "en casa, guárdalo tú mismo."
                    ),
                    action=rx.hstack(
                        rx.button(
                            rx.icon("plus", size=15),
                            rx.text("Guardar lo que tengo", size="2"),
                            on_click=PantryState.open_add_form,
                            color_scheme="amber",
                            size="3",
                            radius="full",
                            cursor="pointer",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("shopping-cart", size=15),
                                rx.text("Ir a la compra", size="2"),
                                variant="soft",
                                color_scheme="green",
                                size="3",
                                radius="full",
                                cursor="pointer",
                            ),
                            href="/shopping_list",
                            underline="none",
                        ),
                        spacing="2",
                        wrap="wrap",
                        justify="center",
                    ),
                    color=theme.PANTRY,
                ),
                rx.cond(
                    PantryState.has_visible_items,
                    rx.vstack(
                        rx.foreach(PantryState.groups, group_block),
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
                            on_click=PantryState.clear_filters,
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
                PantryState.low_count > 0,
                info_banner(
                    "Lo marcado como «por reponer» está por debajo del mínimo que le pusiste. "
                    "Con «Reponer lo que falta» va entero a la lista de la compra, pidiendo solo "
                    "lo que falta para llegar al mínimo.",
                    icon="trending-down",
                    color=theme.WARNING,
                ),
            ),

            spacing="5",
            width="100%",
            max_width="1000px",
            margin="0 auto",
            align="center",
        ),
    )
