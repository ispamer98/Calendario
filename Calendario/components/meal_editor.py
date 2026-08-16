# Calendario/components/meal_editor.py
"""
Editor de un día del calendario: comida, cena y agenda (tareas/eventos/notas).

El alta de comidas ya no vive aquí — la lleva `meal_form.py`, que además
permite editar ingredientes. Desde este diálogo se abre con el botón de
"Nueva comida".
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge
from Calendario.model.model import DayItem
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.components.meal_picker import meal_picker
from Calendario.components.picker import manage_option, option, picker
from Calendario.components.consume_dialog import consumed_badge
from Calendario.state.consume_state import ConsumeState
from Calendario.state.meal_form_state import MealFormState


#Icono/control de cada elemento de agenda (checkbox si es tarea, icono informativo si no)
def agenda_item_icon(item: rx.Var[DayItem]) -> rx.Component:
    """Icono del tipo. Si el tipo se puede marcar, además hace de casilla."""
    return rx.cond(
        item.completable,
        rx.icon(
            rx.cond(item.completed, "square-check", item.type_icon),
            size=15,
            color=rx.cond(item.completed, theme.AGENDA, item.type_color),
            style={"cursor": "pointer"},
            on_click=DayState.toggle_day_item(item.id),
            flex_shrink="0",
        ),
        rx.icon(item.type_icon, size=15, color=item.type_color, flex_shrink="0"),
    )


#Fila para un elemento de agenda (tarea/evento/nota) dentro del editor del día
def agenda_item_row(item: rx.Var[DayItem]) -> rx.Component:
    return rx.hstack(
        agenda_item_icon(item),
        rx.cond(
            item.time_label != "",
            rx.text(
                item.time_label,
                size="1",
                color=theme.AGENDA,
                font_family=theme.FONT_MONO,
                white_space="nowrap",
                flex_shrink="0",
            ),
        ),
        rx.text(
            item.title,
            size="2",
            text_decoration=rx.cond(item.completed, "line-through", "none"),
            color=rx.cond(item.completed, theme.MUTED, theme.TEXT),
            overflow="hidden",
            text_overflow="ellipsis",
            white_space="nowrap",
        ),
        rx.spacer(),
        rx.icon(
            "x",
            size=14,
            color=theme.DANGER,
            style={"cursor": "pointer"},
            _hover={"transform": "scale(1.3)", "transition": "transform 0.2s"},
            on_click=DayState.delete_day_item(item.id),
        ),
        width="100%",
        align="center",
        spacing="2",
        padding="6px 9px",
        border_radius="9px",
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
    )


#Sección de agenda diaria (tareas/eventos/notas) dentro del editor del día
def agenda_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("list-checks", size=14, color=theme.AGENDA),
            rx.text("Agenda del día", color=theme.AGENDA, size="1", weight="bold", letter_spacing="0.04em"),
            rx.spacer(),
            rx.icon(
                rx.cond(DayState.show_agenda_input, "minus", "plus"),
                size=16,
                color=theme.AGENDA,
                style={"cursor": "pointer"},
                _hover={"transform": "scale(1.3)", "transition": "transform 0.2s"},
                on_click=DayState.toggle_agenda_input,
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.cond(
            DayState.show_agenda_input,
            rx.vstack(
                #Tipo + resumen de la franja elegida
                rx.hstack(
                    rx.box(
                        picker(
                            display=DayState.new_item_type_label,
                            options=[
                                rx.foreach(
                                    DayState.task_types,
                                    lambda t: option(
                                        t.label, t.key, DayState.set_new_item_type,
                                        color=t.color, icon=t.icon,
                                        selected=t.key == DayState.new_item_type,
                                    ),
                                )
                            ],
                            placeholder="Tipo",
                            search_placeholder="Buscar tipo...",
                            footer=manage_option(DayState.open_type_manager, "Gestionar tipos"),
                            width="230px",
                            on_add=DayState.open_type_manager,
                            add_title="Añadir un tipo nuevo",
                        ),
                        flex="1 1 0",
                        min_width="0",
                    ),
                    #El gestor de tipos se abre desde el propio desplegable
                    rx.hstack(
                        rx.icon("clock", size=12, color=theme.AGENDA),
                        rx.text(
                            DayState.slot_preview,
                            size="1",
                            color=theme.TEXT,
                            font_family=theme.FONT_MONO,
                            white_space="nowrap",
                        ),
                        spacing="2",
                        align="center",
                        padding="5px 10px",
                        border_radius="999px",
                        background=theme.alpha(theme.AGENDA, 0.12),
                        border=f"1px solid {theme.alpha(theme.AGENDA, 0.28)}",
                        flex_shrink="0",
                    ),
                    width="100%",
                    spacing="2",
                    align="center",
                ),
                #Franja horaria: inicio en tramos de 15 min + duración
                rx.hstack(
                    rx.box(
                        #96 tramos de 15 minutos: aquí el buscador no es un lujo,
                        #se escribe "19" y salen las cuatro horas de las siete
                        picker(
                            display=DayState.new_item_time,
                            options=[
                                rx.foreach(
                                    DayState.time_slots,
                                    lambda slot: option(
                                        slot, slot, DayState.set_new_item_time,
                                        selected=slot == DayState.new_item_time,
                                    ),
                                )
                            ],
                            placeholder="Hora",
                            search_placeholder="Buscar hora (ej. 19)...",
                            width="190px",
                        ),
                        flex="1 1 0",
                        min_width="0",
                    ),
                    rx.box(
                        picker(
                            display=DayState.new_item_duration_label,
                            options=[
                                rx.foreach(
                                    DayState.durations,
                                    lambda d: option(
                                        d["label"], d["value"], DayState.set_new_item_duration,
                                        selected=d["value"] == DayState.new_item_duration,
                                    ),
                                )
                            ],
                            placeholder="Duración",
                            search_placeholder="Buscar duración...",
                            width="190px",
                        ),
                        flex="1 1 0",
                        min_width="0",
                    ),
                    #Quitar la hora y dejarlo como algo "sin franja"
                    rx.cond(
                        DayState.new_item_time != "",
                        rx.icon(
                            "eraser",
                            size=15,
                            color=theme.MUTED,
                            style={"cursor": "pointer"},
                            _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
                            on_click=DayState.clear_new_item_time,
                            flex_shrink="0",
                            title="Sin hora",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.input(
                        placeholder="¿Qué hay que hacer?",
                        value=DayState.new_item_title,
                        on_change=DayState.set_new_item_title,
                        #Enter añade la tarea (ya no envía el formulario del día)
                        on_key_down=DayState.agenda_key_down,
                        size="2",
                        flex="1 1 0",
                        min_width="0",
                    ),
                    rx.icon_button(
                        rx.icon("check", size=15),
                        on_click=DayState.add_day_item,
                        color_scheme="jade",
                        size="2",
                        type="button",
                        flex_shrink="0",
                    ),
                    width="100%",
                    spacing="2",
                    align="center",
                ),
                width="100%",
                spacing="2",
                margin_top="0.4em",
            ),
        ),
        rx.cond(
            DayState.current_day_items.length() > 0,
            rx.vstack(
                rx.foreach(DayState.current_day_items, agenda_item_row),
                width="100%",
                spacing="1",
                max_height="170px",
                overflow_y="auto",
                margin_top="0.4em",
            ),
            rx.text(
                "Sin tareas, eventos ni notas para este día.",
                size="1",
                color=theme.DIM,
                margin_top="0.4em",
            ),
        ),
        width="100%",
        spacing="1",
    )


def _meal_options() -> rx.Component:
    """Platos agrupados por categoría: con 100+ comidas la lista plana no vale."""
    return rx.select.content(
        rx.foreach(
            CalendarState.meal_groups,
            lambda group: rx.select.group(
                rx.select.label(group.label),
                rx.foreach(group.meals, lambda meal: rx.select.item(meal.name, value=meal.name)),
            ),
        ),
        position="popper",
        style={"max_height": "280px"},
    )


def _slot(label: str, icon: str, color: str, name: str, value, on_change, on_clear) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=13, color=color),
            rx.text(label, color=color, size="1", weight="bold", letter_spacing="0.04em"),
            rx.spacer(),
            rx.cond(
                value != "",
                rx.icon(
                    "rotate-ccw",
                    color=theme.MUTED,
                    size=14,
                    style={"cursor": "pointer"},
                    _hover={"color": theme.DANGER, "transform": "scale(1.25)"},
                    on_click=on_clear,
                ),
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        meal_picker(value, on_change, on_add=MealFormState.open_new),
        spacing="1",
        width="100%",
        align="start",
    )


def _stock_row(slot: str, label: str, value, consumed, consumed_label, consumed_items) -> rx.Component:
    """La fila de despensa de un plato: si ya se restó, quién, y el botón de restar.

    Solo aparece cuando hay plato asignado: sin comida no hay nada que descontar.
    """
    return rx.cond(
        value != "",
        rx.hstack(
            rx.icon("warehouse", size=13, color=theme.PANTRY, flex_shrink="0"),
            rx.cond(
                consumed,
                rx.hstack(
                    rx.text("Ya descontado de la despensa", size="1", color=theme.SUCCESS),
                    consumed_badge(consumed, consumed_label, consumed_items, label),
                    spacing="2",
                    align="center",
                ),
                rx.text("Sin descontar de la despensa", size="1", color=theme.MUTED),
            ),
            rx.spacer(),
            rx.button(
                rx.icon(rx.cond(consumed, "rotate-ccw", "circle-minus"), size=13),
                rx.text(rx.cond(consumed, "Revisar", "Restar"), size="1"),
                on_click=ConsumeState.open_for(DayState.current_day.id, slot),
                variant="soft",
                color_scheme="amber",
                size="1",
                radius="full",
                type="button",
                cursor="pointer",
            ),
            width="100%",
            align="center",
            spacing="2",
            padding="6px 10px",
            border_radius="8px",
            background=theme.BG_SUNKEN,
            border=f"1px solid {theme.BORDER}",
        ),
    )


def meal_editor() -> rx.Component:
    #Componente que editará las comidas para el dia seleccionado
    return rx.dialog.root(
        rx.dialog.content(
            rx.form.root(
                rx.vstack(
                    rx.hstack(
                        icon_badge("calendar-days", theme.ACCENT, size=18, box="42px"),
                        rx.vstack(
                            rx.text(
                                rx.moment(
                                    DayState.current_day.date,
                                    format="dddd, D [de] MMMM",
                                    locale="es",
                                ),
                                style={"text-transform": "capitalize"},
                                size="3",
                                weight="bold",
                                color=theme.TEXT,
                            ),
                            rx.text(
                                rx.moment(DayState.current_day.date, format="YYYY", locale="es"),
                                size="1",
                                color=theme.MUTED,
                            ),
                            spacing="0",
                            align="start",
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.box(height="1px", width="100%", background=theme.BORDER),

                    _slot(
                        "COMIDA", "sun", theme.MEAL, "meal",
                        DayState.current_meal, DayState.set_meal, DayState.clear_meal,
                    ),
                    _stock_row(
                        "meal", "Comida", DayState.current_meal,
                        DayState.current_day.meal_consumed,
                        DayState.current_day.meal_consumed_label,
                        DayState.current_day.meal_consumed_items,
                    ),
                    _slot(
                        "CENA", "moon", theme.DINNER, "dinner",
                        DayState.current_dinner, DayState.set_dinner, DayState.clear_dinner,
                    ),
                    _stock_row(
                        "dinner", "Cena", DayState.current_dinner,
                        DayState.current_day.dinner_consumed,
                        DayState.current_day.dinner_consumed_label,
                        DayState.current_day.dinner_consumed_items,
                    ),

                    rx.button(
                        rx.icon("plus", size=14),
                        rx.text("Nueva comida al recetario", size="1"),
                        color_scheme="green",
                        variant="soft",
                        size="1",
                        type="button",
                        on_click=MealFormState.open_new,
                        cursor="pointer",
                        radius="full",
                    ),

                    rx.box(height="1px", width="100%", background=theme.BORDER),

                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                type="button",
                                on_click=DayState.clear_current_day,
                                color_scheme="gray",
                                variant="soft",
                                size="2",
                            )
                        ),
                        rx.dialog.close(
                            rx.button("Guardar", type="submit", color_scheme="green", size="2")
                        ),
                        spacing="2",
                        justify="end",
                        width="100%",
                    ),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                on_submit=DayState.update_day,
                width="100%",
            ),
            #Fuera del formulario a propósito: dentro, pulsar Enter al escribir
            #una tarea enviaba el día entero y salía "no se detectaron cambios"
            rx.vstack(
                rx.box(height="1px", width="100%", background=theme.BORDER),
                agenda_section(),
                width="100%",
                spacing="3",
                margin_top="0.8em",
            ),
            style={
                "max_width": "420px",
                "max_height": "88vh",
                "overflow_y": "auto",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=DayState.show_editor,
    )
