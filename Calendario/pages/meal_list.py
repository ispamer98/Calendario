# Calendario/pages/meal_list.py

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.meal_card import meal_list_grid
from Calendario.components.ui import (
    collapsible,
    page_header,
    stat_card,
    stats_grid,
    tip,
)
from Calendario.components.recipe_book_sharer import (
    recipe_book_sharer_dialog,
    share_recipe_book_button,
)
from Calendario.state.calendar_state import CalendarState
from Calendario.state.meal_form_state import MealFormState
from Calendario.state.products_state import ProductsState
from Calendario.state.recipe_book_state import RecipeBookState
from Calendario.state.units_state import UnitsState


def _category_chip(chip) -> rx.Component:
    """Chip de filtro por categoría, con su recuento. Los datos vienen del
    catálogo configurable, no de una tabla fija en el código."""
    is_active = CalendarState.meal_category == chip.cat_key
    return rx.hstack(
        rx.icon(chip.cat_icon, size=13, color=chip.cat_color),
        rx.text(chip.cat_label, size="1", weight="medium", color=rx.cond(is_active, theme.TEXT, theme.MUTED)),
        rx.text(chip.ingredient_count.to_string(), size="1", color=theme.DIM),
        spacing="2",
        align="center",
        cursor="pointer",
        padding="6px 12px",
        border_radius="999px",
        background=rx.cond(is_active, theme.BG_CARD_HOVER, theme.BG_CARD),
        border=rx.cond(is_active, f"1px solid {theme.BORDER_STRONG}", f"1px solid {theme.BORDER}"),
        on_click=CalendarState.set_meal_category(chip.cat_key),
        transition="all 0.15s ease",
        flex_shrink="0",
    )


def _filters() -> rx.Component:
    all_active = CalendarState.meal_category == "todas"
    return rx.vstack(
        rx.hstack(
            rx.input(
                rx.input.slot(rx.icon("search", size=15)),
                placeholder="Buscar por plato o ingrediente...",
                value=CalendarState.meal_search,
                on_change=CalendarState.set_meal_search,
                size="2",
                width="100%",
                max_width="340px",
                variant="surface",
                radius="full",
            ),
            rx.text(CalendarState.meal_count_label, size="1", color=theme.DIM, white_space="nowrap"),
            rx.spacer(),
            width="100%",
            align="center",
            spacing="3",
            wrap="wrap",
        ),
        collapsible(
            rx.hstack(
            rx.hstack(
                rx.icon("layout-grid", size=13, color=rx.cond(all_active, theme.TEXT, theme.MUTED)),
                rx.text("Todas", size="1", weight="medium", color=rx.cond(all_active, theme.TEXT, theme.MUTED)),
                spacing="2",
                align="center",
                cursor="pointer",
                padding="6px 12px",
                border_radius="999px",
                background=rx.cond(all_active, theme.alpha(theme.ACCENT, 0.18), theme.BG_CARD),
                border=rx.cond(
                    all_active,
                    f"1px solid {theme.alpha(theme.ACCENT, 0.5)}",
                    f"1px solid {theme.BORDER}",
                ),
                on_click=CalendarState.set_meal_category("todas"),
                transition="all 0.15s ease",
                flex_shrink="0",
            ),
            rx.foreach(CalendarState.category_chips, _category_chip),
            spacing="2",
            width="100%",
            wrap="wrap",
            ),
            title="FILTRAR POR CATEGORÍA",
            icon="filter",
            color=theme.MEAL,
        ),
        spacing="3",
        width="100%",
    )


# Página de listado de comidas
@rx.page(
    route="/meal_list",
    title="Comidas | CalendPy",
    on_load=[
        CalendarState.load_meals,
        CalendarState.clear_meal_filters,
        CalendarState.load_categories,
        UnitsState.load_units,
        ProductsState.load_products,
        RecipeBookState.load_book,
    ],
)
def meal_list() -> rx.Component:
    return app_shell(
        recipe_book_sharer_dialog(),
        rx.vstack(
            page_header(
                icon="chef-hat",
                title="Recetario",
                subtitle="Tus platos y sus ingredientes: la materia prima del menú semanal",
                accent=theme.MEAL,
                actions=[
                    share_recipe_book_button(),
                    rx.button(
                        rx.icon("plus", size=16),
                        rx.text("Nueva comida", size="2"),
                        on_click=MealFormState.open_new,
                        color_scheme="green",
                        size="2",
                        cursor="pointer",
                        radius="full",
                    ),
                ],
                extra=_filters(),
            ),

            stats_grid(
                stat_card(
                    icon="utensils",
                    label="Platos en total",
                    value=CalendarState.meals.length(),
                    color=theme.MEAL,
                ),
                stat_card(
                    icon="carrot",
                    label="Con ingredientes",
                    value=CalendarState.meals_with_ingredients,
                    hint="Listos para la compra",
                    color=theme.ACCENT,
                ),
                stat_card(
                    icon="layers",
                    label="Categorías",
                    value=CalendarState.category_count,
                    color=theme.PURPLE,
                ),
                stat_card(
                    icon="filter",
                    label="Mostrando",
                    value=CalendarState.filtered_meals.length(),
                    color=theme.OWNER,
                ),
            ),

            meal_list_grid(),

            #Zona que antes quedaba vacía: ahora explica cómo encaja todo
            rx.cond(
                CalendarState.meals.length() > 0,
                collapsible(
                    rx.grid(
                        tip(
                            "clipboard-list",
                            "Planifica la semana",
                            "Sentaos el sábado, rellenad comida y cena de lunes a domingo y dejad que la compra se calcule sola.",
                            theme.ACCENT,
                        ),
                        tip(
                            "carrot",
                            "Ingredientes = compra",
                            "Un plato sin ingredientes se puede planificar, pero no aporta nada a la lista. Edítalo y añádeselos.",
                            theme.MEAL,
                        ),
                        tip(
                            "dices",
                            "Sin ideas",
                            "En el menú semanal, 'Sorpréndeme' rellena los huecos vacíos con platos al azar sin repetir.",
                            theme.PURPLE,
                        ),
                        columns=rx.breakpoints(initial="1", md="3"),
                        spacing="3",
                        width="100%",
                    ),
                    title="CÓMO FUNCIONA EL RECETARIO",
                    icon="circle-help",
                    color=theme.ACCENT,
                ),
            ),

            spacing="5",
            width="100%",
            max_width="1400px",
            margin="0 auto",
            align="center",
        ),
    )
