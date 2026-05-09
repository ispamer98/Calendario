import reflex as rx
from Calendario.model.model import Meal
from Calendario.state.calendar_state import CalendarState
from Calendario.state.meal_card_state import MealCardState

# =========================
# DIÁLOGO CONFIRMAR BORRADO
# =========================
def delete_confirm_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Confirmar eliminación"),
            rx.dialog.description(
                rx.cond(
                    MealCardState.meal_to_delete != "",
                    f"¿Estás seguro de que quieres eliminar '{MealCardState.meal_to_delete}'? Esta acción no se puede deshacer.",
                    "¿Estás seguro de que quieres eliminar esta comida?"
                )
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=MealCardState.close_delete_confirm
                    )
                ),
                rx.dialog.close(
                    rx.button(
                        "Eliminar",
                        color_scheme="red",
                        on_click=MealCardState.delete_meal
                    )
                ),
                spacing="3",
                margin_top="2em",
                justify="end",
            ),
            style={"max_width": "400px"}
        ),
        open=MealCardState.show_delete_confirm,
    )


# =========================
# TARJETA MOBILE (MEJORADA)
# =========================

def meal_card_mobile(meal: rx.Var[Meal]) -> rx.Component:
    selected = MealCardState.selected_meal_id == meal.id
    
    return rx.box(
        rx.card(
            rx.hstack(
                # Icono
                rx.icon(
                    "utensils",
                    size=16,
                    color=rx.cond(selected, "var(--green-9)", "var(--blue-9)"),
                ),
                
                # Contenido principal
                rx.vstack(
                    # Nombre de la comida
                    rx.text(
                        meal.name,
                        size="2",
                        weight="bold",
                        color="var(--slate-12)",
                        width="100%",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    
                    # Descripción (se expande cuando está seleccionada)
                    rx.text(
                        rx.cond(meal.description != "", meal.description, "Sin descripción"),
                        size="1",
                        color="var(--slate-11)",
                        width="100%",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space=rx.cond(selected, "normal", "nowrap"),
                        display=rx.cond(selected, "-webkit-box", "block"),
                        webkit_line_clamp=rx.cond(selected, None, "1"),
                        webkit_box_orient="vertical",
                    ),
                    
                    align="start",
                    spacing="1",
                    width="100%",
                ),
                
                # Espaciador
                rx.spacer(),
                
                # Botón eliminar (solo visible cuando está seleccionada)
                rx.cond(
                    selected,
                    rx.button(
                        rx.icon("trash-2", size=12),
                        variant="soft",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: MealCardState.open_delete_confirm(meal.id, meal.name),
                        padding="0.25em",
                    ),
                    rx.box(width="40px"),  # Espacio reservado para mantener alineación
                ),
                
                align="center",
                spacing="2",
                width="100%",
            ),
            height=rx.cond(selected, "auto", "60px"),
            padding="0.75em",
            border_radius="lg",
            background=rx.cond(selected, "var(--green-2)", "var(--slate-2)"),
            border=rx.cond(
                selected,
                "2px solid var(--green-7)",
                "1px solid var(--slate-6)",
            ),
            transform=rx.cond(selected, "scale(1.02)", "scale(1)"),
            box_shadow=rx.cond(
                selected,
                "0 4px 12px rgba(0, 0, 0, 0.1)",
                "0 1px 3px rgba(0, 0, 0, 0.05)",
            ),
            on_click=lambda: MealCardState.select_meal(meal.id),
            style={"cursor": "pointer"},
        ),
        margin="2px 0",
        filter=rx.cond(
            (MealCardState.selected_meal_id != None) & 
            (MealCardState.selected_meal_id != meal.id),
            "blur(0.5px) opacity(0.7)",
            "none",
        ),
        transition="all 200ms ease",
    )


# =========================
# TARJETA DESKTOP (MEJORADA CON CENTRADO)
# =========================
def meal_card_desktop(meal: rx.Var[Meal]) -> rx.Component:
    hovered = MealCardState.hovered_meal_id == meal.id
    someone_hovered = MealCardState.hovered_meal_id != None
    
    return rx.box(
        rx.card(
            rx.vstack(
                # Icono
                rx.icon(
                    "utensils",
                    size=24,
                    color=rx.cond(hovered, "var(--green-9)", "var(--blue-9)"),

                ),
                
                # Nombre de la comida
                rx.heading(
                    meal.name,
                    size=rx.cond(hovered, "5", "4"),
                    text_align="center",
                    width="100%",
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                
                # Descripción (truncada, se expande en hover)
                rx.box(
                    rx.text(
                        rx.cond(meal.description != "", meal.description, "Sin descripción"),
                        size="2",
                        color="var(--slate-11)",
                        text_align="center",
                        width="100%",
                        overflow="hidden",
                        text_overflow="ellipsis",
                        display="-webkit-box",
                        webkit_line_clamp=rx.cond(hovered, "3", "2"),
                        webkit_box_orient="vertical",
                        line_height="1.4",
                    ),
                    width="100%",
                    min_height=rx.cond(hovered, "60px", "40px"),
                ),
                
                # Botón eliminar (solo visible en hover)
                rx.cond(
                    hovered,
                    rx.button(
                        rx.hstack(
                            rx.icon("trash-2", size=14),
                            rx.text("Eliminar", size="1"),
                            spacing="1",
                        ),
                        variant="soft",
                        size="1",
                        color_scheme="red",
                        on_click=lambda: MealCardState.open_delete_confirm(meal.id, meal.name),
                        position="absolute",
                        top="12px",
                        right="12px",
                        opacity=0.9,
                        _hover={"opacity": 1},
                    ),
                ),
                
                spacing="3",
                align="center",
                width="100%",
                position="relative",
            ),
            height=rx.cond(hovered, "200px", "160px"),
            width=rx.cond(hovered, "320px", "280px"),
            padding=rx.cond(hovered, "1.5em", "1em"),
            border_radius="xl",
            background="var(--color-panel)",
            border=rx.cond(
                hovered,
                "2px solid var(--green-7)",
                "1px solid var(--slate-6)",
            ),
            transform=rx.cond(
                hovered, 
                "scale(1.1) translateY(-10px)", 
                "scale(1)"
            ),
            box_shadow=rx.cond(
                hovered,
                "0 20px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px var(--green-3)",
                "0 4px 12px rgba(0, 0, 0, 0.08)",
            ),
            filter=rx.cond(
                someone_hovered & ~hovered,
                "blur(1px) opacity(0.6)",
                "none",
            ),
            transition="all 300ms cubic-bezier(0.4, 0, 0.2, 1)",
            z_index=rx.cond(hovered, "50", "10"),
            on_mouse_enter=lambda: MealCardState.set_hovered_meal(meal.id),
            on_mouse_leave=MealCardState.clear_hovered_meal,
            style={
                "cursor": "pointer",
                "transform_origin": "center",
                "margin": rx.cond(hovered, "0 auto", "0"),
            },
        ),
        display="flex",
        justify_content="center",
        align_items="center",
    )


# =========================
# WRAPPER RESPONSIVE
# =========================
def meal_card(meal: rx.Var[Meal]) -> rx.Component:
    return rx.box(
        rx.mobile_only(
            meal_card_mobile(meal)
        ),
        rx.tablet_and_desktop(
            meal_card_desktop(meal)
        ),
        width="100%",
    )


# =========================
# GRID DE COMIDAS (MEJORADO CON OVERLAY PARA CLICKS)
# =========================
def meal_list_grid() -> rx.Component:
    return rx.box(
        delete_confirm_dialog(),
        rx.box(
            rx.cond(
                CalendarState.meals.length() > 0,
                # Contenedor principal (sin overlay)
                rx.box(
                    # Contenido para móvil
                    rx.mobile_only(
                        rx.vstack(
                            rx.foreach(CalendarState.meals, meal_card),
                            spacing="2",
                            width="100%",
                            padding="1em",
                            align_items="center",
                        )
                    ),
                    # Contenido para tablet/desktop
                    rx.tablet_and_desktop(
                        rx.flex(
                            rx.foreach(CalendarState.meals, meal_card),
                            wrap="wrap",
                            justify="center",
                            align="center",
                            gap="2em",
                            width="100%",
                            padding="3em",
                        )
                    ),
                    width="100%",
                ),
                # Estado vacío (sin cambios)
                rx.vstack(
                    rx.icon("utensils", size=48, color="var(--slate-8)"),
                    rx.heading("No hay comidas aún", size="5", weight="medium"),
                    rx.text("Añade tu primera comida para comenzar", color="var(--slate-10)", size="3"),
                    spacing="3",
                    align="center",
                    padding_y="6em",
                    width="100%",
                )
            ),
        ),
        width="100%",
    )