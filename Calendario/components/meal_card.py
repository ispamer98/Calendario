# Calendario/components/meal_card.py
"""
Tarjetas del recetario.

La versión anterior tenía dos problemas: en escritorio las tarjetas se
apilaban con `flex wrap` creciendo y encogiendo al pasar el ratón (saltos de
maquetación), y en móvil eran una lista vertical de filas de 60 px. Ahora es
una **cuadrícula** de verdad, con el mismo componente en los dos tamaños y una
tarjeta que dice de un vistazo qué es el plato: categoría, tiempo e
ingredientes.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import empty_state, pill
from Calendario.model.model import MealCard
from Calendario.state.calendar_state import CalendarState
from Calendario.state.meal_card_state import MealCardState
from Calendario.state.meal_form_state import MealFormState


# =========================
# DIÁLOGO CONFIRMAR BORRADO
# =========================
def delete_confirm_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Eliminar comida"),
            rx.dialog.description(
                rx.cond(
                    MealCardState.meal_to_delete != "",
                    "Vas a eliminar '" + MealCardState.meal_to_delete
                    + "'. También desaparecerá de los días del calendario que la tuvieran asignada.",
                    "¿Seguro que quieres eliminar esta comida?",
                ),
                size="2",
                color=theme.MUTED,
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=MealCardState.close_delete_confirm,
                    )
                ),
                rx.dialog.close(
                    rx.button("Eliminar", color_scheme="red", on_click=MealCardState.delete_meal)
                ),
                spacing="3",
                margin_top="1.5em",
                justify="end",
            ),
            style={
                "max_width": "420px",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=MealCardState.show_delete_confirm,
    )


# =========================
# TARJETA
# =========================
def meal_card(meal: rx.Var[MealCard]) -> rx.Component:
    color = meal.cat_color
    return rx.box(
        rx.vstack(
            #Cabecera: icono de categoría + nombre + acciones
            rx.hstack(
                rx.center(
                    rx.icon(meal.cat_icon, size=17, color=color),
                    min_width="38px",
                    height="38px",
                    border_radius=theme.RADIUS_SM,
                    background=theme.BG_RAISED,
                    border=f"1px solid {theme.BORDER}",
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.text(
                        meal.name,
                        size="3",
                        weight="bold",
                        color=theme.TEXT,
                        line_height="1.25",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        display="-webkit-box",
                        webkit_line_clamp="2",
                        webkit_box_orient="vertical",
                    ),
                    rx.text(meal.cat_label, size="1", color=color, weight="medium"),
                    spacing="0",
                    align="start",
                    min_width="0",
                    flex="1",
                ),
                rx.hstack(
                    rx.icon(
                        "pencil",
                        size=15,
                        color=theme.MUTED,
                        cursor="pointer",
                        on_click=MealFormState.open_edit(meal.id),
                        _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
                        transition="all 0.15s ease",
                    ),
                    rx.icon(
                        "trash-2",
                        size=15,
                        color=theme.MUTED,
                        cursor="pointer",
                        on_click=MealCardState.open_delete_confirm(meal.id, meal.name),
                        _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
                        transition="all 0.15s ease",
                    ),
                    spacing="3",
                    align="center",
                    flex_shrink="0",
                ),
                width="100%",
                align="start",
                spacing="3",
            ),

            #Descripción
            rx.text(
                rx.cond(meal.description != "", meal.description, "Sin descripción todavía."),
                size="1",
                color=theme.MUTED,
                line_height="1.5",
                overflow="hidden",
                text_overflow="ellipsis",
                display="-webkit-box",
                webkit_line_clamp="2",
                webkit_box_orient="vertical",
                min_height="2.9em",
                max_height="3em",
                width="100%",
                min_width="0",
            ),

            rx.spacer(),

            #Pie: tiempo e ingredientes
            rx.hstack(
                pill(meal.prep_minutes.to_string() + " min", theme.MUTED, "clock"),
                rx.cond(
                    meal.ingredient_count > 0,
                    pill(meal.ingredient_count.to_string() + " ingr.", theme.MEAL, "carrot"),
                    pill("Sin ingredientes", theme.WARNING, "triangle-alert"),
                ),
                spacing="2",
                align="center",
                width="100%",
                wrap="wrap",
            ),
            spacing="3",
            align="start",
            height="100%",
            width="100%",
        ),
        padding="16px",
        height="100%",
        min_height="205px",
        overflow="hidden",
        border_radius=theme.RADIUS,
        background=theme.BG_CARD,
        border=f"1px solid {theme.BORDER}",
        backdrop_filter="blur(10px)",
        box_shadow=theme.SHADOW_SM,
        transition="all 0.18s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={
            "background": theme.BG_CARD_HOVER,
            "border_color": theme.BORDER_STRONG,
            "transform": "translateY(-3px)",
            "box_shadow": theme.SHADOW,
        },
    )


# =========================
# CUADRÍCULA
# =========================
def meal_list_grid() -> rx.Component:
    return rx.box(
        delete_confirm_dialog(),
        rx.cond(
            CalendarState.meals.length() > 0,
            rx.cond(
                CalendarState.filtered_meals.length() > 0,
                #1 columna en móvil, 2 en tablet, 3 en escritorio y 4 en pantallas grandes
                rx.grid(
                    rx.foreach(CalendarState.meal_cards, meal_card),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"),
                    spacing="4",
                    width="100%",
                    align_items="stretch",
                ),
                empty_state(
                    icon="search-x",
                    title="Sin resultados",
                    description="Ninguna comida coincide con los filtros activos. Prueba con otro nombre o quita el filtro de categoría.",
                    action=rx.button(
                        rx.icon("rotate-ccw", size=15),
                        "Quitar filtros",
                        on_click=CalendarState.clear_meal_filters,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        cursor="pointer",
                    ),
                    color=theme.MUTED,
                ),
            ),
            empty_state(
                icon="chef-hat",
                title="Tu recetario está vacío",
                description="Añade tus platos habituales con sus ingredientes y el menú semanal podrá construir la lista de la compra por ti.",
                action=rx.button(
                    rx.icon("plus", size=15),
                    "Añadir mi primera comida",
                    on_click=MealFormState.open_new,
                    color_scheme="green",
                    size="3",
                    cursor="pointer",
                ),
                color=theme.MEAL,
            ),
        ),
        width="100%",
    )
