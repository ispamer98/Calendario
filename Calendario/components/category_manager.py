# Calendario/components/category_manager.py
"""
Gestor de categorías de plato.

Mismo patrón que el de unidades: se abre con el engranaje que hay junto al
desplegable de categoría. Permite crear, editar (nombre, color e icono) y
borrar. Al borrar, sus platos pasan a "Otros" en vez de quedarse huérfanos.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, info_banner
from Calendario.state.calendar_state import CalendarState


def manage_categories_button() -> rx.Component:
    return rx.icon(
        "settings-2",
        size=15,
        color=theme.MUTED,
        cursor="pointer",
        on_click=CalendarState.open_category_manager,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease",
        flex_shrink="0",
        title="Gestionar categorías",
    )


def _row(cat) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon(cat.icon, size=14, color=cat.color),
            min_width="28px", width="28px", height="28px",
            border_radius="8px",
            background=cat.color + "26",
            border="1px solid " + cat.color + "66",
            flex_shrink="0",
        ),
        rx.box(
            rx.text(
                cat.label, size="2", color=theme.TEXT, weight="medium",
                overflow="hidden", text_overflow="ellipsis", white_space="nowrap",
            ),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.icon(
            "pencil", size=14, color=theme.MUTED, cursor="pointer", flex_shrink="0",
            on_click=CalendarState.edit_category(cat.key),
            _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
        ),
        rx.icon(
            "trash-2", size=14, color=theme.MUTED, cursor="pointer", flex_shrink="0",
            on_click=CalendarState.remove_category(cat.key),
            _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
        ),
        width="100%", max_width="100%", align="center", spacing="2",
        padding="8px 10px", border_radius=theme.RADIUS_SM,
        background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}",
        overflow="hidden",
    )


def category_manager_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("layers", theme.MEAL, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Categorías de plato", margin="0", size="4", weight="bold"),
                        rx.text("Nombre, color e icono", size="1", color=theme.MUTED),
                        spacing="0", align="start",
                    ),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer",
                            on_click=CalendarState.close_category_manager),
                    width="100%", align="center", spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                rx.hstack(
                    rx.input(
                        placeholder=rx.cond(
                            CalendarState.cat_key != "", "Editando categoría...", "Nueva categoría",
                        ),
                        value=CalendarState.cat_label,
                        on_change=CalendarState.set_cat_label,
                        size="2", max_length=24, flex="1 1 0", min_width="0",
                    ),
                    rx.icon_button(
                        rx.icon("check", size=16),
                        on_click=CalendarState.save_category,
                        color_scheme="green", size="2", type="button", flex_shrink="0",
                    ),
                    width="100%", spacing="2", align="center",
                ),
                rx.flex(
                    rx.foreach(
                        CalendarState.palette,
                        lambda color: rx.box(
                            width="24px", height="24px", border_radius="50%",
                            background=color, cursor="pointer", flex_shrink="0",
                            border=rx.cond(
                                CalendarState.cat_color == color,
                                "3px solid white", "3px solid transparent",
                            ),
                            on_click=CalendarState.set_cat_color(color),
                            _hover={"transform": "scale(1.12)"},
                        ),
                    ),
                    wrap="wrap", gap="7px", width="100%",
                ),
                rx.flex(
                    rx.foreach(
                        CalendarState.icon_choices,
                        lambda ic: rx.center(
                            rx.icon(ic, size=15, color=rx.cond(
                                CalendarState.cat_icon == ic, theme.TEXT, theme.MUTED)),
                            width="32px", height="32px", border_radius="8px",
                            cursor="pointer", flex_shrink="0",
                            background=rx.cond(
                                CalendarState.cat_icon == ic, theme.BG_CARD_HOVER, theme.BG_SUNKEN),
                            border=rx.cond(
                                CalendarState.cat_icon == ic,
                                f"1px solid {theme.BORDER_STRONG}", f"1px solid {theme.BORDER}"),
                            on_click=CalendarState.set_cat_icon(ic),
                        ),
                    ),
                    wrap="wrap", gap="7px", width="100%",
                ),

                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(
                    rx.foreach(CalendarState.categories, _row),
                    spacing="2", width="100%", max_height="220px", overflow_y="auto",
                ),
                info_banner(
                    "Al borrar una categoría, sus platos pasan a «Otros». La categoría «Otros» no se puede borrar.",
                    icon="info", color=theme.ACCENT,
                ),
                rx.hstack(
                    rx.button("Listo", on_click=CalendarState.close_category_manager,
                              variant="soft", color_scheme="gray", size="2"),
                    spacing="2", justify="end", width="100%",
                ),
                spacing="3", width="100%",
            ),
            style={
                "max_width": "460px", "max_height": "88vh",
                "overflow_y": "auto", "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG, "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=CalendarState.show_category_manager,
    )
