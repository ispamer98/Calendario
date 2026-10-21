# Calendario/components/week_planner.py
"""
Cuadrícula del menú semanal.

Siete tarjetas (lunes a domingo), cada una con su comida y su cena. Se elige
el plato en un desplegable agrupado por categoría y se guarda al instante: la
idea es sentarse un rato, rellenar la semana entre dos, y pulsar "generar
lista de la compra".
"""

import reflex as rx

from Calendario import theme
from Calendario.components.meal_picker import meal_picker
from Calendario.components.ui import pill, progress_bar
from Calendario.model.model import GeneratedItem, MealGroup, WeekDay
from Calendario.state.calendar_state import CalendarState
from Calendario.state.meal_form_state import MealFormState
from Calendario.state.menu_state import MenuState


def _cat_color(category) -> rx.Component:
    return rx.match(
        category,
        *[(key, style["color"]) for key, style in theme.MEAL_CATEGORY_STYLE.items()],
        theme.MUTED,
    )


def _meal_options() -> rx.Component:
    """Contenido del desplegable: platos agrupados por categoría."""
    return rx.select.content(
        rx.foreach(
            CalendarState.meal_groups,
            lambda group: rx.select.group(
                rx.select.label(group.label),
                rx.foreach(
                    group.meals,
                    lambda meal: rx.select.item(meal.name, value=meal.name),
                ),
            ),
        ),
        position="popper",
        side="bottom",
        style={"max_height": "300px"},
    )


def _slot(day: rx.Var[WeekDay], slot: str) -> rx.Component:
    """Una ranura (comida o cena) de un día."""
    is_meal = slot == "meal"
    value = day.meal if is_meal else day.dinner
    category = day.meal_category if is_meal else day.dinner_category
    color = theme.MEAL if is_meal else theme.DINNER
    label = "Comida" if is_meal else "Cena"
    icon = "sun" if is_meal else "moon"

    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=12, color=color),
            rx.text(label, size="1", color=color, weight="bold", letter_spacing="0.04em"),
            rx.spacer(),
            #El botón de limpiar solo aparece si hay algo que limpiar
            rx.cond(
                value != "",
                rx.icon(
                    "x",
                    size=13,
                    color=theme.MUTED,
                    cursor="pointer",
                    on_click=MenuState.clear_slot(day.day_id, slot),
                    _hover={"color": theme.DANGER, "transform": "scale(1.25)"},
                ),
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        meal_picker(
            value,
            lambda v: MenuState.set_slot(day.day_id, slot, v),
            "Elegir...",
            on_add=MealFormState.open_new,
            #`_day_card` (y por tanto `_slot`) se construye una sola vez como
            #plantilla del `rx.foreach`: sin un id que dependa del propio día,
            #los siete compartirían el mismo y se abrirían todos a la vez.
            picker_id="wk-" + slot + "-" + day.day_id.to_string(),
        ),
        #Punto de color con la categoría del plato elegido
        rx.cond(
            value != "",
            rx.hstack(
                rx.box(
                    width="6px",
                    height="6px",
                    border_radius="50%",
                    background=_cat_color(category),
                    flex_shrink="0",
                ),
                rx.text(
                    value,
                    size="1",
                    color=theme.MUTED,
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
        ),
        spacing="1",
        width="100%",
        align="start",
    )


def _day_card(day: rx.Var[WeekDay]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text(
                    day.day_name,
                    size="2",
                    weight="bold",
                    color=rx.cond(day.is_today, theme.ACCENT, theme.TEXT),
                ),
                rx.text(day.date_label, size="1", color=theme.DIM),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.cond(day.is_today, pill("HOY", theme.ACCENT, "circle-dot")),
            rx.cond(
                day.is_weekend & ~day.is_today,
                rx.icon("party-popper", size=13, color=theme.PURPLE),
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.box(height="1px", width="100%", background=theme.BORDER),
        _slot(day, "meal"),
        _slot(day, "dinner"),
        spacing="3",
        width="100%",
        align="start",
        padding="14px",
        border_radius=theme.RADIUS,
        background=rx.cond(day.is_today, theme.alpha(theme.ACCENT, 0.07), theme.BG_CARD),
        border=rx.cond(
            day.is_today,
            f"1px solid {theme.alpha(theme.ACCENT, 0.35)}",
            f"1px solid {theme.BORDER}",
        ),
        opacity=rx.cond(day.is_past, "0.72", "1"),
        backdrop_filter="blur(10px)",
        box_shadow=theme.SHADOW_SM,
        transition="all 0.18s ease",
        _hover={"border_color": theme.BORDER_STRONG},
    )


def week_grid() -> rx.Component:
    return rx.grid(
        rx.foreach(MenuState.week_days, _day_card),
        columns=rx.breakpoints(initial="1", sm="2", md="3", xl="4"),
        spacing="3",
        width="100%",
        align_items="stretch",
    )


# ---------------------------------------------------------------------------
# Diálogo de generación de la lista de la compra
# ---------------------------------------------------------------------------
def _preview_row(item: rx.Var[GeneratedItem]) -> rx.Component:
    color = rx.match(
        item.cat,
        *[(key, style["color"]) for key, style in theme.SHOP_CATEGORY_STYLE.items()],
        theme.MUTED,
    )
    return rx.hstack(
        #Marcar/desmarcar lo que va a la lista
        rx.icon(
            rx.cond(item.selected, "square-check", "square"),
            size=15,
            color=rx.cond(item.selected, theme.MEAL, theme.DIM),
            flex_shrink="0",
        ),
        rx.box(width="6px", height="6px", border_radius="50%", background=color, flex_shrink="0"),
        rx.text(
            item.name,
            size="1",
            color=rx.cond(item.selected, theme.TEXT, theme.DIM),
            text_decoration=rx.cond(item.selected, "none", "line-through"),
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        #Lo que traiga el ingrediente de la receta: dónde comprarlo y la nota
        rx.cond(
            item.shop != "",
            rx.hstack(
                rx.icon("store", size=10, color=theme.WARNING, flex_shrink="0"),
                rx.text(item.shop, size="1", color=theme.DIM, white_space="nowrap"),
                spacing="1",
                align="center",
                flex_shrink="0",
            ),
        ),
        rx.cond(
            item.note != "",
            rx.icon("sticky-note", size=10, color=theme.ACCENT, flex_shrink="0", title=item.note),
        ),
        rx.spacer(),
        rx.text(
            item.qty_label,
            size="1",
            color=rx.cond(item.selected, theme.MUTED, theme.DIM),
            font_family=theme.FONT_MONO,
            white_space="nowrap",
        ),
        on_click=MenuState.toggle_item(item.key),
        cursor="pointer",
        width="100%",
        align="center",
        spacing="2",
        padding="5px 8px",
        border_radius="8px",
        opacity=rx.cond(item.selected, "1", "0.55"),
        _hover={"background": theme.BG_RAISED},
        transition="opacity 0.15s ease",
    )


def generator_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.center(
                        rx.icon("shopping-cart", size=20, color=theme.MEAL),
                        min_width="44px",
                        height="44px",
                        border_radius=theme.RADIUS_SM,
                        background=theme.alpha(theme.MEAL, 0.14),
                        border=f"1px solid {theme.alpha(theme.MEAL, 0.3)}",
                    ),
                    rx.vstack(
                        rx.dialog.title("Generar lista de la compra", margin="0", size="4", weight="bold"),
                        rx.text(
                            "Suma los ingredientes de los "
                            + MenuState.planned_meals_count.to_string()
                            + " platos de la semana",
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer", on_click=MenuState.close_generator),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Comensales + básicos de despensa
                rx.hstack(
                    rx.vstack(
                        rx.text("COMENSALES", size="1", color=theme.MUTED, weight="medium"),
                        rx.hstack(
                            rx.icon("users", size=15, color=theme.ACCENT),
                            rx.input(
                                value=MenuState.people,
                                on_change=MenuState.set_people,
                                on_blur=MenuState.refresh_preview,
                                type="number",
                                size="2",
                                width="80px",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.text("BÁSICOS DE DESPENSA", size="1", color=theme.MUTED, weight="medium"),
                        rx.hstack(
                            rx.switch(
                                checked=MenuState.include_staples,
                                on_change=[MenuState.toggle_staples, MenuState.refresh_preview],
                                color_scheme="green",
                            ),
                            rx.text("Aceite, sal, especias...", size="1", color=theme.DIM),
                            spacing="2",
                            align="center",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    width="100%",
                    align="start",
                    spacing="3",
                    wrap="wrap",
                ),

                #Vista previa
                rx.cond(
                    MenuState.preview_count > 0,
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                MenuState.selected_count.to_string()
                                + " de "
                                + MenuState.preview_count.to_string()
                                + " productos",
                                size="1",
                                weight="bold",
                                color=theme.TEXT,
                            ),
                            rx.spacer(),
                            #Marcar/desmarcar todo de golpe
                            rx.text(
                                "Todos",
                                size="1",
                                color=theme.ACCENT,
                                cursor="pointer",
                                on_click=MenuState.select_all,
                                _hover={"text_decoration": "underline"},
                            ),
                            rx.text("·", size="1", color=theme.DIM),
                            rx.text(
                                "Ninguno",
                                size="1",
                                color=theme.ACCENT,
                                cursor="pointer",
                                on_click=MenuState.select_none,
                                _hover={"text_decoration": "underline"},
                            ),
                            width="100%",
                            align="center",
                            spacing="2",
                        ),
                        rx.text(
                            "Toca un producto para quitarlo de la compra",
                            size="1",
                            color=theme.DIM,
                        ),
                        rx.box(
                            rx.foreach(MenuState.preview_items, _preview_row),
                            width="100%",
                            max_height="230px",
                            overflow_y="auto",
                            padding="4px",
                            border_radius=theme.RADIUS_SM,
                            background=theme.BG_SUNKEN,
                            border=f"1px solid {theme.BORDER}",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(
                        rx.text(
                            "No hay ingredientes que añadir. Comprueba que los platos de la semana tengan ingredientes en el recetario.",
                            size="1",
                            color=theme.WARNING,
                        ),
                        padding="12px",
                        border_radius=theme.RADIUS_SM,
                        background=theme.alpha(theme.WARNING, 0.08),
                        border=f"1px solid {theme.alpha(theme.WARNING, 0.2)}",
                        width="100%",
                    ),
                ),

                rx.box(height="1px", width="100%", background=theme.BORDER),

                #Las dos formas de volcar en la lista
                rx.vstack(
                    rx.button(
                        rx.icon("plus", size=15),
                        rx.text("Añadir a mi lista actual", size="2"),
                        on_click=MenuState.generate("merge"),
                        color_scheme="green",
                        size="3",
                        width="100%",
                        cursor="pointer",
                        loading=MenuState.generating,
                        disabled=~MenuState.has_selection,
                    ),
                    rx.button(
                        rx.icon("refresh-ccw", size=15),
                        rx.text("Rehacer la lista de esta semana", size="2"),
                        on_click=MenuState.generate("replace"),
                        variant="soft",
                        color_scheme="blue",
                        size="3",
                        width="100%",
                        cursor="pointer",
                        loading=MenuState.generating,
                        disabled=~MenuState.has_selection,
                    ),
                    rx.text(
                        "«Añadir» deja la compra de esta semana al día sin quitarte nada. «Rehacer» además retira lo que ya no está en el menú. Puedes darle las veces que quieras: las cantidades de la semana se recalculan, no se suman. Lo que añadiste a mano nunca se toca.",
                        size="1",
                        color=theme.DIM,
                        line_height="1.5",
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "520px",
                "max_height": "88vh",
                "overflow_y": "auto",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=MenuState.show_generator,
    )
