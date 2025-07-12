#Calendario/pages/calendar.py

import reflex as rx
from Calendario.components.meal_editor import meal_editor
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState
from Calendario.components.today_box import today_box

#Página de calendario
@rx.page( #Decorador indicando componente página
    route="/calendar",
    title="Calendario | CalendPy",
    on_load=[ #Acciones al cargar la página
        CalendarState.reset_calendars,
        CalendarState.clean,
        UserState.on_load,
        CalendarState.load_meals,
        UserState.check_autenticated,
        CalendarState.update_current_date,
        CalendarState.refresh_page
    ],
)
def calendar() -> rx.Component:
    # Estructura del componente global como Stack Vertical
    return rx.vstack(
        user_navbar(),  # Incluimos la navbar
        meal_editor(),  # Y el editor de comidas para que pueda lanzarse
        rx.container(  # Contenedor principal
            rx.cond(
                UserState.current_user,  # Si existe registro de usuario loggeado
                rx.cond(
                    CalendarState.calendars.length() > 0,  # Si el usuario tiene calendarios creados
                    rx.fragment(
                        rx.tablet_and_desktop(  # Creamos la vista de escritorio
                            rx.hstack(  # Stack horizontal
                                user_calendar(),  # Lanzamos el calendario
                                rx.cond(
                                    UserState.today_data.length() > 0,  # Si existen registros en el día de hoy
                                    rx.box(
                                        today_box(),  # Mostramos la box con la info de hoy
                                        margin_left="5em",
                                        margin_top="2em",
                                    )
                                ),
                                spacing="4",
                                align_items="flex-start",
                            )
                        ),
                        rx.mobile_only(  # Creamos la vista para móvil
                            rx.vstack(  # Stack vertical
                                rx.box(
                                    user_calendar(),  # Lanzamos el calendario
                                    margin_left="-1em",
                                    margin_rigth="1em"
                                ),
                                rx.box(  # Divisor
                                    rx.divider(),
                                    width="100%",
                                    margin_bottom="1em"
                                ),
                                rx.cond(
                                    UserState.today_data.length() > 0,  # Si hay registros del día de hoy
                                    today_box()  # Mostramos la info de hoy
                                ),
                                align_items="flex-start",
                                spacing="2",
                            )
                        ),
                    ),

                    #Si no existen calendarios registrados
                    rx.vstack(
                        rx.text("No tienes ningún calendario", color="gray.600"), #Texto informativo
                        rx.separator(margin_top="1em", width="250px"),
                        rx.button( #Botón que dispara el creador de calendario
                            rx.icon("calendar-plus"),
                            rx.text("Añadir calendario", margin_left="0.5em"),
                            color_scheme="green",
                            on_click=CalendarState.open_calendar_creator, #Acción que abre el creador de calendario
                            align_items="center",
                            margin_top="1em"
                        ),
                        align_items="center",
                        spacing="1"
                    ),
                ),

                #Si no se ha cargado la información del usuario loggeado todavia
                rx.vstack(
                    rx.box( #Se muestra un efecto de spinner
                        style={
                            "border": "8px solid #f3f3f3",
                            "borderTop": "8px solid #3182ce",
                            "borderRadius": "50%",
                            "width": "60px",
                            "height": "60px",
                            "animation": "spin 1s linear infinite"
                        }
                    ),
                    rx.text("Cargando...", margin_top="1em"), #Texto de la animación
                    align_items="center",
                    spacing="1"
                ),
            ),
            width="100%",
            max_width="1200px",
            padding_top="6em",
            align="center",
        ),
        width="100%",
        spacing="0",
        align_items="center",
        style={"overflow-x": "hidden"},
        height="100vh",
    )
