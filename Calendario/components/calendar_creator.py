# Calendario/components/calendar_creator.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from datetime import datetime

def calendar_creator() -> rx.Component:
    today = datetime.today()    # Obtenemos la fecha actual

    # Calculamos el rango permitido (mes actual hasta 12 meses en el futuro) 
    min_date = today.strftime("%Y-%m")
    max_date = datetime(today.year + 1, 12, 1).strftime("%Y-%m")

    return rx.dialog.root(
        rx.dialog.content(
            rx.form( #Creamos un formulario
                rx.vstack(
                    rx.heading("Crear nuevo Calendario", size="5"), 
                    rx.text("Nombre del Calendario", size="2", color="gray"),
                    rx.input( 
                        placeholder="Ej: Comidas de Marzo", 
                        name="calendar_name", 
                        value=CalendarState.new_calendar_name, 
                        on_change=CalendarState.set_new_calendar_name,
                        _hover={"border_color": "blue.400"}
                    ),
                    rx.text("Selecciona el mes", size="2", color="gray", margin_top="1em"),
                    rx.input(
                        type="month", #Tipo de input, para que lo maneje reflex
                        name="calendar_month",
                        min=min_date, #Valor minimo del input
                        max=max_date, #Valor máximo
                        value=CalendarState.new_calendar_month, 
                        on_change=CalendarState.set_new_calendar_month 
                    ),
                    rx.hstack( 
                        rx.dialog.close( #Configuramos el cierre del dialogo
                            rx.button( 
                                "Cancelar", 
                                type="button", 
                                color_scheme="red", 
                                size="3", 
                                variant="soft", 
                                on_click=CalendarState.close_calendar_creator, 
                                _hover={ 
                                    "background": "var(--red-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        rx.button(
                            "Crear",
                            type="submit", 
                            variant="soft", 
                            color_scheme="green", 
                            on_click=CalendarState.create_calendar, #Dispara el creador de calenadrios
                            size="3", 
                            _hover={ 
                                "background": "var(--green-9)",
                                "color": "white"
                            }
                        ),
                        spacing="3", 
                        margin_top="2em", 
                        justify="end" 
                    ),
                    spacing="3", 
                    width="100%", 
                    align_items="center", 
                ),
            ),
            style={"max_width": 450}, #Le damos un valor máximo de ancho
            padding="2em", 
            border_radius="8px", 
            
        ),
        open=CalendarState.show_calendar_creator, #Cambiamos el estado para visualizar el componente
    )