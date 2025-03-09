#calendar_creator.py

from turtle import width
import reflex as rx
from Calendario.state.calendar_state import CalendarState

def calendar_creator() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Crear Nuevo Calendario",
                variant="solid",
                color_scheme="jade",
                size="3"
            )
        ),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading("Crear nuevo Calendario", size="5"),
                    rx.text("Nombre del Calendario",size="2",color="gray"),
                    rx.input(
                        placeholder="Ej: Comidas de Marzo 2025",
                        name="calendar_name",
                        required=True,
                        value=CalendarState.new_calendar_name,
                        on_change=CalendarState.set_new_calendar_name
                    ),
                    rx.text("Selecciona el mes", size="2", color="gray", margin_top="1em"),
                    rx.input(
                        type="month",
                        name="calendar_month",
                        required=True,
                        value=CalendarState.new_calendar_month,
                        on_change=CalendarState.set_new_calendar_month
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Calncelar", variant="soft")
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Crear",
                                type="submit",
                                variant="solid",
                                color_scheme="jade"
                            )
                        ),
                        spacing="3",
                        margin_top="2em",
                        justify="end"
                    ),
                    spacing="3",
                    width="100%",
                ),
                on_submit=CalendarState.create_calendar,
            ),
            style={"max_width":450},
            box_shadow="1g",
            padding="2em",
            border_radius="8px",
        ),
    )