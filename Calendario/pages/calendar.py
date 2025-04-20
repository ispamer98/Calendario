import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.meal_editor import meal_editor
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState

def toast(): 
    return rx.toast(title=CalendarState.toast_info, position="top-center")

@rx.page(route="/calendar",
         title="Calendario | CalendPy",
         on_load=[CalendarState.reset_calendars,
                                     CalendarState.clean,
                                     UserState.on_load,
                                     CalendarState.load_meals,
                                     UserState.check_autenticated,
                                     
                                     ])
def calendar() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        meal_editor(),
        rx.container(
            rx.vstack(
                rx.cond(
                    UserState.current_user,
                    rx.cond(
                        CalendarState.calendars,
                        user_calendar(),
                        
                        rx.vstack(
                            rx.text("No tienes ningún calendario"),
                            rx.button("Crear Calendario", on_click=CalendarState.open_calendar_creator),
                            align_items="center"  # Centrar contenido dentro del vstack
                        ),
                    ),
                    rx.vstack(
                        rx.box(
                            # Círculo de carga con animación CSS
                            style={
                                "border": "8px solid #f3f3f3",
                                "borderTop": "8px solid #3182ce",
                                "borderRadius": "50%",
                                "width": "60px",
                                "height": "60px",
                                "animation": "spin 1s linear infinite",
                                # Definición de la animación
                                "@keyframes spin": {
                                    "0%": {"transform": "rotate(0deg)"},
                                    "100%": {"transform": "rotate(360deg)"}
                                },
                            }
                        ),
                        rx.text("Cargando...", margin_top="1em"),
                        align_items="center"
                    ),
                ),
                width="100%",
                align_items="center",  # Centrar todo dentro del vstack principal
            ),
            width="100%",
            max_width="1200px",
            padding_x="2em",
            padding_top="6em",
            align="center"  # Centrar el container horizontalmente
        ),
        width="100%",
        spacing="0",
        align_items="center",  # Centrar la pila de elementos
        style={"overflow-x": "hidden"}, 
        heigth="100%"
    )
