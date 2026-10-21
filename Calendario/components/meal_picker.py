# Calendario/components/meal_picker.py
"""
Selector de plato con buscador.

Con 125 platos una lista plana es inmanejable, así que se escribe para filtrar.
Usa el mismo desplegable que el resto de la app (`components/picker.py`), que es
el que sabe funcionar **dentro de un diálogo**: se escribe en el propio campo,
porque un buscador metido dentro de la lista nunca llega a recibir el foco
cuando hay un diálogo abierto (Radix lo atrapa).
"""

import reflex as rx

from Calendario import theme
from Calendario.components.picker import clear_option, manage_button, option, picker
from Calendario.state.calendar_state import CalendarState


def meal_picker(
    value, on_select, placeholder: str = "Elegir plato...", on_add=None, picker_id=None,
) -> rx.Component:
    """Desplegable de plato. Con `on_add`, lleva al lado el engranaje de siempre
    para dar de alta una comida nueva sin salir de aquí.

    `picker_id`: ver la nota en `picker()`. Hace falta pasarlo cuando este
    desplegable se repite dentro de un `rx.foreach` (el menú semanal), para que
    cada fila tenga el suyo y no se abran todas a la vez.
    """
    return picker(
        display=value,
        options=[
            rx.foreach(
                CalendarState.picker_results,
                lambda m: option(
                    m.name,
                    m.name,
                    on_select,
                    color=m.cat_color,
                    icon=m.cat_icon,
                    hint=m.prep_minutes.to_string() + "'",
                    selected=m.name == value,
                ),
            )
        ],
        placeholder=placeholder,
        footer=rx.cond(value != "", clear_option(on_select, "Quitar plato")),
        width="300px",
        on_add=on_add,
        add_title="Añadir una comida al recetario",
        picker_id=picker_id,
    )
