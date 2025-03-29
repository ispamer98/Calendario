# Calendario/components/calendar_creator.py
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calendar_creator() -> rx.Component:
    # Obtener fecha actual
    today = datetime.today()
    
    # Calcular rango permitido (mes actual hasta 12 meses en el futuro)
    min_date = today.strftime("%Y-%m")
    max_date = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

    return rx.dialog.root(
        rx.dialog.trigger(
            rx.box()
        ),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading("Crear nuevo Calendario", size="5"),
                    rx.text("Nombre del Calendario", size="2", color="gray"),
                    rx.input(
                        placeholder="Ej: Comidas de Marzo 2025",
                        name="calendar_name",
                        required=True,
                        value=CalendarState.new_calendar_name,
                        on_change=CalendarState.set_new_calendar_name,
                        _hover={"border_color": "blue.400"}
                    ),
                    rx.text("Selecciona el mes", size="2", color="gray", margin_top="1em"),
                    rx.input(
                        type="month",
                        name="calendar_month",
                        required=True,
                        min=min_date,
                        max=max_date,
                        value=CalendarState.new_calendar_month,
                        on_change=CalendarState.set_new_calendar_month
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                on_click=CalendarState.close_calendar_creator
                            )
                        ),
                        rx.button(
                            "Crear",
                            type="submit",
                            variant="solid",
                            color_scheme="jade",
                            on_click=CalendarState.create_calendar
                        ),
                        spacing="3",
                        margin_top="2em",
                        justify="end"
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            style={"max_width": 450},
            box_shadow="lg",
            padding="2em",
            border_radius="8px",
        ),
        open=CalendarState.show_calendar_creator,
    )