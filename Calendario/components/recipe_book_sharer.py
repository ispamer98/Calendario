# Calendario/components/recipe_book_sharer.py
"""
Compartir el recetario, con el mismo lenguaje que la lista de la compra.

Al añadir a alguien, su recetario y el tuyo se fusionan: a partir de ahí los dos
veis y editáis exactamente las mismas recetas. Al quitarlo, se lleva una copia
(un recetario es trabajo de meses; dejarle a cero sería destructivo).
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, info_banner
from Calendario.state.recipe_book_state import RecipeBookState
from Calendario.state.user_state import UserState


def share_recipe_book_button() -> rx.Component:
    return rx.button(
        rx.icon("users", size=16),
        rx.text("Compartir recetario", size="2"),
        on_click=RecipeBookState.toggle_panel,
        variant="soft",
        color_scheme="gray",
        size="2",
        radius="full",
        cursor="pointer",
    )


def recipe_book_sharer_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("users", theme.MEAL, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Recetario compartido", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Quien esté aquí ve y edita las mismas recetas que tú",
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
                        on_click=RecipeBookState.close_panel,
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                rx.vstack(
                    rx.foreach(
                        RecipeBookState.shared_users,
                        lambda user: rx.hstack(
                            rx.icon("circle-user", size=16, color=theme.MEAL),
                            rx.text(user.username, size="2", weight="medium", color=theme.TEXT),
                            rx.spacer(),
                            rx.cond(
                                user.id != UserState.current_user.id,
                                rx.icon_button(
                                    rx.icon("user-minus", size=14),
                                    on_click=RecipeBookState.remove_user(user.id, user.username),
                                    color_scheme="red",
                                    variant="ghost",
                                    size="1",
                                    title="Quitar del recetario compartido",
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
                    rx.text(
                        "AÑADIR POR NOMBRE DE USUARIO",
                        size="1",
                        color=theme.MUTED,
                        weight="medium",
                    ),
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=RecipeBookState.new_user_input,
                        on_change=RecipeBookState.set_new_user_input,
                        size="2",
                        width="100%",
                    ),
                    rx.cond(
                        RecipeBookState.error != "",
                        rx.text(RecipeBookState.error, color=theme.DANGER, size="1"),
                    ),
                    spacing="1",
                    width="100%",
                    align="start",
                ),

                info_banner(
                    "Al añadir a alguien, su recetario y el tuyo se fusionan en uno solo. Si los "
                    "dos tenéis un plato con el mismo nombre, se queda el tuyo.",
                    icon="info",
                    color=theme.ACCENT,
                ),

                rx.hstack(
                    rx.button(
                        "Cerrar",
                        on_click=RecipeBookState.close_panel,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.button(
                        rx.icon("user-plus", size=15),
                        rx.text("Compartir", size="2"),
                        on_click=RecipeBookState.share,
                        color_scheme="green",
                        size="2",
                        loading=RecipeBookState.sharing,
                        cursor="pointer",
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
        open=RecipeBookState.show_panel,
    )
