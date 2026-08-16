# Calendario/components/supermarket_manager.py
"""
Gestor de supermercados (nombre + color).

Estaba dentro de `pages/shopping_list.py`, así que solo se podía abrir desde la
lista de la compra. Ahora que un ingrediente del recetario también lleva
supermercado, el diálogo vive en el shell y se abre desde cualquier sitio,
igual que el gestor de unidades.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, info_banner
from Calendario.state.shopping_list_state import ShoppingListState


def manage_shops_button(title: str = "Gestionar supermercados") -> rx.Component:
    return rx.icon(
        "settings-2",
        size=15,
        color=theme.MUTED,
        cursor="pointer",
        on_click=ShoppingListState.open_shops_panel,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease",
        flex_shrink="0",
        title=title,
    )


def supermarket_manager_dialog() -> rx.Component:
    """Gestor de supermercados: nombre + color, y borrar los que no uses."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("store", theme.WARNING, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Supermercados", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Cada uno con su color, para reconocerlos de un vistazo",
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
                        on_click=ShoppingListState.close_shops_panel,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Alta y edición: nombre + paleta de colores
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            rx.cond(ShoppingListState.is_editing_shop, "pencil", "plus"),
                            size=13,
                            color=rx.cond(ShoppingListState.is_editing_shop, theme.ACCENT, theme.MEAL),
                        ),
                        rx.text(
                            rx.cond(
                                ShoppingListState.is_editing_shop,
                                "EDITANDO SUPERMERCADO",
                                "NUEVO SUPERMERCADO",
                            ),
                            size="1",
                            color=theme.MUTED,
                            weight="medium",
                        ),
                        rx.spacer(),
                        rx.cond(
                            ShoppingListState.is_editing_shop,
                            rx.text(
                                "Cancelar edición",
                                size="1",
                                color=theme.MUTED,
                                cursor="pointer",
                                on_click=ShoppingListState.cancel_shop_edit,
                                _hover={"color": theme.DANGER, "text_decoration": "underline"},
                            ),
                        ),
                        width="100%",
                        align="center",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.input(
                            placeholder="Nombre del supermercado",
                            value=ShoppingListState.new_shop_name,
                            on_change=ShoppingListState.set_new_shop_name,
                            size="2",
                            max_length=20,
                            flex="1 1 0",
                            min_width="0",
                            id="supermercado-nombre",
                        ),
                        rx.button(
                            rx.icon(
                                rx.cond(ShoppingListState.is_editing_shop, "check", "plus"),
                                size=16,
                            ),
                            rx.text(
                                rx.cond(ShoppingListState.is_editing_shop, "Guardar", "Añadir"),
                                size="2",
                            ),
                            on_click=ShoppingListState.add_supermarket,
                            color_scheme=rx.cond(ShoppingListState.is_editing_shop, "blue", "green"),
                            size="2",
                            type="button",
                            flex_shrink="0",
                            cursor="pointer",
                        ),
                        width="100%",
                        spacing="2",
                        align="center",
                    ),
                    rx.flex(
                        rx.foreach(
                            ShoppingListState.palette,
                            lambda color: rx.box(
                                width="26px",
                                height="26px",
                                border_radius="50%",
                                background=color,
                                cursor="pointer",
                                border=rx.cond(
                                    ShoppingListState.new_shop_color == color,
                                    "3px solid white",
                                    "3px solid transparent",
                                ),
                                on_click=ShoppingListState.set_new_shop_color(color),
                                _hover={"transform": "scale(1.12)"},
                                transition="transform 0.15s ease",
                                flex_shrink="0",
                            ),
                        ),
                        wrap="wrap",
                        gap="8px",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                    align="start",
                ),

                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Listado actual
                rx.vstack(
                    rx.foreach(
                        ShoppingListState.supermarkets,
                        lambda shop: rx.hstack(
                            rx.center(
                                rx.text(shop.initial, size="1", weight="bold", color=shop.color),
                                min_width="26px", width="26px", height="26px",
                                border_radius="50%",
                                background=shop.color + "26",
                                border="1px solid " + shop.color + "66",
                                flex_shrink="0",
                            ),
                            rx.box(
                                rx.text(
                                    shop.name, size="2", color=theme.TEXT, weight="medium",
                                    overflow="hidden", text_overflow="ellipsis", white_space="nowrap",
                                ),
                                flex="1 1 0", min_width="0", overflow="hidden",
                            ),
                            #Cambiar el color sobre la marcha
                            rx.foreach(
                                ShoppingListState.palette,
                                lambda color: rx.box(
                                    width="14px", height="14px", border_radius="50%",
                                    background=color, cursor="pointer", flex_shrink="0",
                                    on_click=ShoppingListState.recolor_supermarket(shop.name, color),
                                    _hover={"transform": "scale(1.3)"},
                                    transition="transform 0.15s ease",
                                ),
                            ),
                            #Editar nombre y color en el formulario de arriba
                            rx.icon(
                                "pencil",
                                size=14,
                                color=theme.MUTED,
                                cursor="pointer",
                                on_click=ShoppingListState.edit_supermarket(shop.name),
                                _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
                                flex_shrink="0",
                                title="Cambiar el nombre o el color",
                            ),
                            rx.icon(
                                "trash-2",
                                size=14,
                                color=theme.MUTED,
                                cursor="pointer",
                                on_click=ShoppingListState.remove_supermarket(shop.name),
                                _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
                                flex_shrink="0",
                            ),
                            width="100%",
                            align="center",
                            spacing="2",
                            padding="10px",
                            min_height="46px",
                            flex_shrink="0",
                            border_radius=theme.RADIUS_SM,
                            background=rx.cond(
                                ShoppingListState.editing_shop == shop.name,
                                theme.alpha(theme.ACCENT, 0.10),
                                theme.BG_SUNKEN,
                            ),
                            border=rx.cond(
                                ShoppingListState.editing_shop == shop.name,
                                f"1px solid {theme.alpha(theme.ACCENT, 0.45)}",
                                f"1px solid {theme.BORDER}",
                            ),
                        ),
                    ),
                    spacing="2",
                    width="100%",
                    max_height="240px",
                    overflow_y="auto",
                ),

                info_banner(
                    "Cambiar el nombre de un supermercado lo cambia también en la lista de la "
                    "compra, en el catálogo y en las recetas. Borrarlo no toca los productos que "
                    "lo tuvieran: solo pierden el color.",
                    icon="info",
                    color=theme.ACCENT,
                ),
                rx.hstack(
                    rx.button(
                        "Listo",
                        on_click=ShoppingListState.close_shops_panel,
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
                "max_width": "460px",
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
        open=ShoppingListState.show_shops_panel,
    )
