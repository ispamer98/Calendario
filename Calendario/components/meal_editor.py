# Calendario/components/meal_editor.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState

def meal_editor() -> rx.Component:
    #Componente que editará las comidas para el dia seleccionado
    return rx.dialog.root(
        rx.dialog.content(
            #Contenido del dialogo, almacena un formulario para editar las comidas
            rx.form.root(
                rx.vstack(
                    rx.text( #Mostramos la fecha del día seleccionado formateada y en español
                        rx.moment(DayState.current_day.date,
                                format="dddd, D [de] MMMM [del] YYYY", 
                                locale="es"
                        ),
                        style={"text-transform": "capitalize"}, 
                        size="5"

                    ),
                    rx.text( #Campo para editar la comida
                        "Comida:",
                        color="var(--green-9)",
                        font_weight="bold",
                        margin_bottom="0.2em"
                    ),
                    rx.hstack( 
                        rx.select.root( #Creamos un selector
                            rx.select.trigger(
                                placeholder="Selecciona una comida"
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach( #El contenido será la lista de comidas alojadas en el estado
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ), #Creará un componente por comida, alojando su valor de nombre
                                    ),
                                ),
                            ),
                            name="meal",
                            value=DayState.current_meal,
                            on_change=DayState.set_meal, #Actualiza la comida 
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon( #Icono para limpiar el selector
                            "rotate-ccw",
                            color="red",
                            size=18,
                            style={
                                "cursor": "pointer",
                            },
                            _hover={
                                "transform": "scale(1.3)",
                                "transition": "transform 0.2s"
                            },
                            on_click=DayState.clear_meal #Función que limpia el contenido
                        ),
                    ),
                    rx.text( #Campo para editar la cena
                        "Cena:",
                        color="var(--blue-9)",
                        font_weight="bold",
                        margin_bottom="0.2em",
                        margin_top="0.5em"
                    ),
                    rx.hstack(
                        rx.select.root( #Creamos un selector
                            rx.select.trigger(
                                placeholder="Selecciona una cena"
                            ),
                            rx.select.content( 
                                rx.select.group(
                                    rx.foreach( #El contenido será la lista de cenas alojadas en el estado
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ), #Creará un componente por cena, alojando su valor de nombre
                                    ),
                                ),
                            ),
                            name="dinner",
                            value=DayState.current_dinner,
                            on_change=DayState.set_dinner, #Actualiza la cena
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon( #Icono para limpiar el selector
                            "rotate-ccw",
                            color="red", 
                            size=18,
                            style={
                                "cursor": "pointer",
                            },
                            _hover={
                                "transform": "scale(1.3)",
                                "transition": "transform 0.2s"
                            },
                            on_click=DayState.clear_dinner #Función que limpia el contenido
                        ),
                    ),
                    rx.hstack( 
                        rx.dialog.close( #Botón de cierre del dialogo
                            rx.button(
                                "Cancelar",
                                type="button",
                                on_click=DayState.clear_current_day, #Limpia el dia seleccionao al salir
                                color_scheme="red",
                                variant="soft",
                                size="3",
                                _hover={
                                    "background": "var(--red-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        rx.dialog.close( #Creamos otro boton de cierre
                            rx.button(
                                "Guardar",
                                type="submit", #Tipo submint para guardar la comida
                                color_scheme="green",
                                variant="soft",
                                size="3",
                                _hover={
                                    "background": "var(--green-9)",
                                    "color": "white"
                                },
                            )
                        ),
                        spacing="3",
                        margin_top="1em"
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                on_submit=DayState.update_day #Al hacer click en el boton de "submint", actualiza la info del dia
            ),
            max_width="500px",
            align_items="center",
        ),
        open=DayState.show_editor #Controlador de visionado del dialogo
    )