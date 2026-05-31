# shopping_list.py

import reflex as rx
from typing import Dict
from Calendario.state.user_state import UserState
from Calendario.state.shopping_list_state import ShoppingListState
from Calendario.components.user_navbar import user_navbar

def item_row(name: str, data: Dict) -> rx.Component:
    """Fila horizontal con botón check-check, nombre, cantidad, supermercado y eliminar."""
    return rx.hstack(
        rx.icon_button(
            rx.cond(
                data.get("bought", False),
                rx.icon("check-check", color="gray"),
                rx.icon("check-check", color="green"),
            ),
            on_click=lambda: ShoppingListState.toggle_bought(name),
            variant="ghost",
            size="3",
        ),
        rx.text(
            name,
            weight="bold",
            text_decoration=rx.cond(data.get("bought", False), "line-through", "none"),
            color=rx.cond(data.get("bought", False), "var(--slate-9)", "var(--slate-12)"),
            flex_grow="1",
        ),
        rx.badge(f"x{data.get('quantity', 1)}", variant="soft", color_scheme="blue"),
        rx.cond(
            data.get("supermarket", "") != "",
            rx.badge(data["supermarket"], variant="surface", color_scheme="orange"),
        ),
        rx.spacer(),
        rx.icon_button(
            rx.icon("trash-2"),
            on_click=lambda: ShoppingListState.delete_item(name),
            variant="ghost",
            color_scheme="red",
            size="2",
        ),
        width="100%",
        align="center",
        padding="1em",
        border_radius="lg",
        transition="all 0.2s ease",
        spacing="3",
        flex_wrap="wrap",
        _hover={
            "background": "var(--slate-3)",
            "box_shadow": "0 2px 8px rgba(0,0,0,0.05)",
            "cursor": "pointer",
        },
    )


@rx.page(
    route="/shopping_list",
    title="Lista de Compras | CalendPy",
    on_load=ShoppingListState.load_shopping_list,
)
def shopping_list() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        rx.container(
            rx.vstack(
                # ========= CABECERA =========
                rx.vstack(
                    rx.heading(
                        "Mi Cesta de la Compra",
                        size="8",
                        text_align="center",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text(
                            "¡Añade productos y comparte tu lista!",
                            color="var(--slate-11)",
                            flex_grow="1",
                        ),
                        # Botón Usuarios (el actualizador lo movemos abajo)
                        rx.button(
                            rx.hstack(
                                rx.icon("users", size=18),
                                rx.text("Usuarios"),
                                spacing="2",
                            ),
                            on_click=ShoppingListState.toggle_users_panel,
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                        ),
                        spacing="3",
                        width="100%",
                        align="center",
                    ),
                    spacing="2",
                    width="100%",
                ),

                # ========= DIÁLOGO DE USUARIOS =========
                rx.dialog.root(

                    rx.dialog.content(
                        rx.vstack(
                            rx.heading("Usuarios con acceso", size="5"),
                            rx.divider(),
                            rx.vstack(
                                rx.foreach(
                                    ShoppingListState.shared_users,
                                    lambda user: rx.hstack(
                                        rx.text(user.username, weight="bold"),
                                        rx.spacer(),
                                        rx.cond(
                                            user.id != UserState.current_user.id,
                                            rx.icon_button(
                                                rx.icon("user-minus"),
                                                on_click=lambda: ShoppingListState.remove_user_from_list(
                                                    user.id, user.username
                                                ),
                                                color_scheme="red",
                                                variant="ghost",
                                                size="2",
                                            ),
                                        ),
                                        width="100%",
                                        padding="0.5em",
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                                max_height="200px",
                                overflow_y="auto",
                            ),
                            rx.divider(),
                            rx.vstack(
                                rx.text("Añadir usuario por nombre:", size="2", weight="bold"),
                                rx.input(
                                    placeholder="Nombre de usuario",
                                    value=ShoppingListState.new_user_input,
                                    on_change=ShoppingListState.set_new_user_input,
                                ),
                                rx.cond(
                                    ShoppingListState.add_user_error != "",
                                    rx.text(
                                        ShoppingListState.add_user_error,
                                        color="red",
                                        size="1",
                                    ),
                                ),
                                rx.button(
                                    "Añadir",
                                    on_click=ShoppingListState.add_user_to_list,
                                    color_scheme="green",
                                    variant="solid",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            rx.dialog.close(
                                rx.button("Cerrar", variant="ghost", margin_top="1em"),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        max_width="400px",
                    ),
                    open=ShoppingListState.show_users_panel,
                    on_open_change=lambda opened: rx.cond(
                        opened,
                        ShoppingListState.toggle_users_panel,
                        ShoppingListState.toggle_users_panel,
                    ),
                ),

                # ========= BOTÓN AÑADIR PRODUCTO =========
                rx.button(
                    rx.hstack(
                        rx.icon("plus-circle", size=20),
                        rx.text("Añadir producto"),
                        spacing="2",
                    ),
                    on_click=ShoppingListState.toggle_add_form,
                    variant="soft",
                    color_scheme="green",
                    size="3",
                    width="100%",
                    margin_top="0.5em",  # reducido
                ),

                # ========= FORMULARIO DE AÑADIR (con iconos y botones centrados) =========
                rx.cond(
                    ShoppingListState.show_add_form,
                    rx.card(
                        rx.vstack(
                            # Campo nombre con icono
                            rx.hstack(
                                rx.icon("package", color="var(--slate-9)"),
                                rx.input(
                                    placeholder="Producto (ej. Leche, Pan...)",
                                    value=ShoppingListState.new_item_name,
                                    on_change=ShoppingListState.set_new_item_name,
                                    flex_grow="1",
                                    max_length=40,
                                    variant="soft",
                                ),
                                width="100%",
                                spacing="3",
                            ),
                            # Cantidad y supermercado en una fila
                            rx.hstack(
                                rx.hstack(
                                    rx.icon("hash", color="var(--slate-9)"),
                                    rx.input(
                                        placeholder="Cant.",
                                        type="number",
                                        value=ShoppingListState.new_item_qty,
                                        on_change=ShoppingListState.change_qty,
                                        width="100px",
                                        variant="soft",
                                    ),
                                    spacing="2",
                                    flex_grow="1",
                                ),
                                rx.hstack(
                                    rx.icon("store", color="var(--slate-9)"),
                                    rx.input(
                                        placeholder="Supermercado (opcional)",
                                        value=ShoppingListState.new_item_shop,
                                        on_change=ShoppingListState.set_new_item_shop,
                                        max_length=20,
                                        variant="soft",
                                    ),
                                    spacing="2",
                                    flex_grow="2",
                                ),
                                spacing="3",
                                width="100%",
                                flex_wrap="wrap",
                            ),
                            # Botones centrados con separación pequeña
                            rx.hstack(
                                rx.button(
                                    "Cancelar",
                                    on_click=ShoppingListState.close_add_form,
                                    variant="solid",
                                    color_scheme="red",
                                    background="var(--red-9)",
                                    _hover={"background": "var(--red-10)"},
                                ),
                                rx.button(
                                    rx.hstack(
                                        rx.icon("shopping-cart"),
                                        rx.text("Añadir"),
                                    ),
                                    on_click=ShoppingListState.add_item,
                                    color_scheme="green",
                                    variant="solid",
                                ),
                                spacing="2",
                                justify="center",
                                width="100%",
                            ),
                            # Mensajes de error
                            rx.cond(
                                ShoppingListState.errors["name"] != "",
                                rx.text(ShoppingListState.errors["name"], color="red", size="1"),
                            ),
                            rx.cond(
                                ShoppingListState.errors["quantity"] != "",
                                rx.text(ShoppingListState.errors["quantity"], color="red", size="1"),
                            ),
                            rx.cond(
                                ShoppingListState.errors["supermarket"] != "",
                                rx.text(ShoppingListState.errors["supermarket"], color="red", size="1"),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        width="100%",
                        variant="surface",
                        margin_top="0.5em",
                        border_radius="xl",
                        shadow="md",
                    ),
                ),

                # ========= BOTÓN ACTUALIZAR (justo encima del listado) =========
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon("refresh-ccw", size=18),
                            rx.text("Actualizar"),
                            spacing="2",
                        ),
                        on_click=ShoppingListState.refresh_page,
                        variant="soft",
                        color_scheme="blue",
                        size="3",
                    ),
                    width="100%",
                    justify="center",  # Centra el contenido horizontalmente
                    align="center",    # Centra el contenido verticalmente
                    margin_top="0.5em",
                    margin_bottom="0.5em",
                    # Eliminamos margin_right="150px" y rx.spacer() para que no lo desplacen
                ),

                rx.divider(size="4", margin_top="0.5em", margin_bottom="0.5em"),

                # ========= LISTADO DE PRODUCTOS =========
                rx.cond(
                    ShoppingListState.is_empty,
                    rx.center(
                        rx.vstack(
                            rx.icon("shopping-bag", size=3, color="var(--slate-9)"),
                            rx.text("No hay productos en tu lista", color="var(--slate-9)"),
                            rx.text(
                                "Añade tu primer producto usando el botón de arriba",
                                size="2",
                                color="var(--slate-10)",
                            ),
                            spacing="4",
                            align="center",
                        ),
                        width="100%",
                        padding="4em",
                    ),
                    rx.vstack(
                        rx.foreach(
                            ShoppingListState.items,
                            lambda item: item_row(item[0], item[1])
                        ),
                        spacing="2",
                        width="100%",
                    ),
                ),
                spacing="4",  # reducido de 6 a 4
                width="100%",
            ),
            max_width="900px",
            padding_top="7em",
            padding_x="1.5em",
            margin="auto",
        ),
        min_height="100vh",
        background="var(--slate-2)",
    )