# Calendario/components/user_calendar.py

import reflex as rx
from Calendario.components.day_button import day_button
from Calendario.components.calendar_sharer import calendar_sharer
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

#Función que devuelve los calendarios del usuario registrado
async def calendars() -> rx.Component:
    calendar_state = await CalendarState.get_state(CalendarState)
    return calendar_state.calendars

#Componente que contiene los días del mes
def calendar_grid() -> rx.Component:
    return rx.vstack(
        # Encabezados de días de la semana
        rx.grid(
            rx.foreach( #Iteramos sobre una lista con los dias de la semana
                ["L", "M", "X", "J", "V", "S", "D"],
                lambda day: rx.center(
                    rx.text(
                        day,
                        size="2",
                        weight="bold",
                        color="gray.500",
                        text_transform="uppercase",
                    ),
                    width="100%",
                    padding="2px",
                ),
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding_x="1em",
        ),
        #Grid con los botones de días según el mes
        rx.grid(
            rx.foreach( #Iteramos sobre los dias del calendario
                CalendarState.display_days,
                lambda day: rx.cond(
                    day, #Si existe registro de dia, lo crea
                    day_button(day),
                    rx.box( #Si no existe, crea un hueco vacio
                        style={
                            "width": "12vw",
                            "height": "12vw",
                            "min_width": "40px",
                            "min_height": "40px",
                            "max_width": "70px",
                            "max_height": "70px",
                            "visibility": "hidden",
                        }
                    ),
                ),
            ),
            grid_template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
            padding="1em",
        ),
        spacing="3",
        width="100%",
        align_items="center",
    )

#Componente principal, calendario del usuario
def user_calendar() -> rx.Component:
    return rx.vstack(
        # ─── 2) Resto de la UI ───
        rx.container(
            rx.vstack(
                rx.cond( #Se muestra si existe calendario
                    CalendarState.calendars.length() > 0,
                    rx.vstack(
                        rx.hstack(
                            #Si no existen calendarios, genera un botón que activa el creador
                                rx.button( 
                                    rx.icon("calendar-plus"),
                                    rx.text("Añadir calendario", margin_left="0.5em"),
                                    color_scheme="green",
                                    on_click=CalendarState.open_calendar_creator, #Disparador del creador
                                    align_items="center",
                                ),
                            
                            justify_content="center",
                            width="100%",
                            padding_bottom="1em",
                        ),
                        rx.hstack( #Selector de calendarios existentes
                            rx.select.root(
                                rx.select.trigger(
                                    placeholder="Selecciona un calendario",
                                    width="300px",
                                    min_width="300px",
                                    justify_content="center",
                                ),
                                rx.select.content( #Contenido del selector
                                    rx.select.group( #Grupo de items
                                        rx.foreach( #Iteramos sobre los calendarios guardados en estado
                                            CalendarState.calendars,
                                            lambda cal: rx.select.item(  
                                                f"{cal.name} ", #Mostramos cada nombre
                                                value=cal.id.to(str), #El valor de la selección es su id
                                                justify_content="center",
                                            ),
                                        )
                                    ),
                                    position="popper",
                                    side="bottom",
                                    align="start",
                                ),
                                value=rx.cond( #Si se ha seleccionado calendario, se guarda en el estado
                                    CalendarState.current_calendar,
                                    CalendarState.current_calendar.id.to(str), #Se muestra su nombre
                                    "", #Si no hay calendario seleccionado, se muestra el selector vacio
                                ),
                                on_change=CalendarState.set_current_calendar, #Al seleccionar, pasamos el calendario al estado
                                width="100%",
                                variant="surface",
                                radius="full",
                            ),
                            rx.icon( #Icono para refrescar la información del calendario
                                tag="refresh-ccw",
                                color="cyan",
                                size=28,
                                on_click=CalendarState.refresh_page, #Funcion de refresco de info
                                style={"cursor": "pointer"},
                            ),
                        ),
                        rx.cond( #Si existe calendario seleccionado
                            CalendarState.current_calendar,
                            rx.hstack(
                                rx.vstack(
                                    rx.heading( #Mostramos el nombre en la cabecera
                                        CalendarState.calendar_title,
                                        size="6",
                                        padding_bottom="1em",
                                        padding_top="2em",
                                    ),
                                    calendar_grid(), #Componente que aloja los días del calendario
                                    rx.hstack(
                                        calendar_sharer(), #Debajo de los dias, el boton para compartir
                                        rx.dialog.root( #Creamos un boton que eliminará el calendario seleccionado
                                            rx.dialog.trigger(
                                                rx.hstack( 
                                                    rx.text("Eliminar"),
                                                    rx.icon(
                                                        "calendar-off",
                                                        color_scheme="red",
                                                        variant="ghost",
                                                    ),
                                                    style={
                                                        "_hover": {
                                                            "color": "red",
                                                            "transform": "scale(1.12)",
                                                            "cursor": "pointer",
                                                        }
                                                    },
                                                    margin_top="0.5em",
                                                ),
                                            ), 
                                            #Al hacer click en el boton, se abre el dialogo avisando de la eliminación
                                            rx.dialog.content(
                                                rx.dialog.title("Confirmar eliminación"),
                                                rx.dialog.description(
                                                    "¿Estás seguro de querer eliminar este calendario y todos sus datos?"
                                                ),
                                                rx.flex(
                                                    rx.dialog.close(
                                                        rx.button( #Boton de cancelar, cierra el dialogo
                                                            "Cancelar",
                                                            variant="soft",
                                                            color_scheme="gray",
                                                        )
                                                    ),
                                                    rx.dialog.close(
                                                        rx.button( #Boton de eliminar, tambien cierra el dialogo
                                                            "Eliminar",
                                                            color_scheme="red", 
                                                            #Al hacer click, actua la función que borrará el calendario con sus datos
                                                            on_click=CalendarState.delete_calendar(
                                                                CalendarState.current_calendar.id #Pasamos la id para poder ubicarlo
                                                            ),
                                                        )
                                                    ),
                                                    spacing="3",
                                                    margin_top="2em",
                                                    justify="end",
                                                ),
                                            ),
                                        ),
                                        spacing="7",
                                    ),
                                    
                                    spacing="4",
                                    align_items="center",
                                ),
                            ),
                        ),
                        align_items="center",
                        width="100%",
                    ),
                )
            ),
            align_items="center",
            justify_content="center",
            width="100%",
            padding="2em",
        ),

        on_mount=UserState.today_info, #Al cargar el calendario, recuperamos la info del dia en curso
        align_items="center",
        justify_content="center",
        width="100vw",
        
    )
