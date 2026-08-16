# Calendario/components/calendar_creator.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario import theme
from Calendario.components.dialog_kit import (
    form_dialog_content, field, dialog_footer, styled_input,
)
from datetime import datetime

def calendar_creator() -> rx.Component:
    today = datetime.today()    # Obtenemos la fecha actual

    # Calculamos el rango permitido (mes actual hasta 12 meses en el futuro)
    min_date = today.strftime("%Y-%m")
    max_date = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

    return rx.dialog.root(
        form_dialog_content(
            icon="calendar-plus",
            title="Crear nuevo calendario",
            accent=theme.ACCENT,
            form=rx.form(
                rx.vstack(
                    field(
                        "Nombre del calendario",
                        styled_input(
                            placeholder="Ej: Comidas de Marzo",
                            name="calendar_name",
                            value=CalendarState.new_calendar_name,
                            on_change=CalendarState.set_new_calendar_name,
                        ),
                    ),
                    field(
                        "Selecciona el mes",
                        styled_input(
                            type="month",
                            name="calendar_month",
                            min=min_date,
                            max=max_date,
                            value=CalendarState.new_calendar_month,
                            on_change=CalendarState.set_new_calendar_month,
                        ),
                    ),
                    dialog_footer(
                        confirm_label="Crear",
                        color_scheme="blue",
                        on_cancel=CalendarState.close_calendar_creator,
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=CalendarState.create_calendar,
                width="100%",
            ),
        ),
        open=CalendarState.show_calendar_creator,
    )
