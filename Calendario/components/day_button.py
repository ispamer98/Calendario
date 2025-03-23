import reflex as rx
from Calendario.model.model import Day,Meal
from datetime import datetime

from Calendario.state.calendar_state import CalendarState


def day_button(day: rx.Var[Day]) -> rx.Component:

    
    # Comparación directa
    is_today = day.date == CalendarState.current_date_str  # Comparación directa de strings
    has_meal = (day.meal_id != None)
    has_dinner = (day.dinner_id != None)
    has_comments = (day.comments.length() > 0)  

    meal_name = CalendarState.get_meal_name(day.meal_id.to(int))
    dinner_name = CalendarState.get_meal_name(day.dinner_id.to(int))
    # Asignación de variables locales
    return rx.box(

            rx.tooltip(
                rx.button(
                    rx.vstack(
                        rx.vstack(
                            rx.moment(day.date, format="DD"),
                            rx.hstack(
                                rx.cond(
                                    has_meal | has_dinner,
                                    rx.hstack(
                                        
                                        rx.icon("utensils", size=12, color="blue"),
                                    )
                                ),
                                rx.cond(
                                    has_comments,
                                    rx.icon("message-square-more", size=12, color = "blue")
                                ),
                            ),
                            
                            spacing="1",
                            align="center"

                        ),
                        spacing="1"
                    ),
                    width="100%",
                    height="100%",
                    padding="2px",
                    # En el frontend
                    
                    background_color=rx.cond(
                        is_today, 
                        "grey",  # si es el día actual
                        "#blue-aqua"
                    ),
                    _hover={
                    "background_color": "rgba(255, 255, 255, 0.1)",
                    "transform": "scale(1.05)"
                    },
                    on_mouse_enter=CalendarState.set_hovered_day(day.id),
                    on_mouse_leave=CalendarState.clear_hovered_day,

                ),
                content=detail_popover(day),
                
                placement="right",

            ),
            min_width="60px",
            min_height="60px",
            position="relative",
            on_mount=CalendarState.load_meals
    )

def detail_popover(day: rx.Var[Day]) -> rx.Component:
    pass