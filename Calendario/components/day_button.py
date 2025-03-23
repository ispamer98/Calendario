import reflex as rx
from Calendario.model.model import Day
from datetime import datetime

from Calendario.state.calendar_state import CalendarState



def day_button(day: rx.Var[Day]) -> rx.Component:

    
    # Comparación directa
    is_today = day.date == CalendarState.current_date_str  # Comparación directa de strings


    has_meal = (day.meal_id != None) | (day.dinner_id != None)  
    has_comments = (day.comments.length() > 0)  

    return rx.box(

            rx.tooltip(
                rx.button(
                    rx.vstack(
                        rx.hstack(
                            rx.moment(day.date, format="DD"),
                            rx.cond(
                                has_meal,
                                rx.icon("utensils", size=12, color="green")
                            ),
                            rx.cond(
                                has_comments,
                                rx.icon("message-square-more", size=12, color = "orange")
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
                        "transparent",  # si es el día actual
                        "#FFA500"
                    ),
                    _hover={
                    "background_color": "rgba(255, 255, 255, 0.1)",
                    "transform": "scale(1.05)"
                    },
                    on_mouse_enter=CalendarState.set_hovered_day(day.id),
                    on_mouse_leave=CalendarState.clear_hovered_day,

                ),
                content=detail_popover(day),
                open_delay=1500,
                placement="right",

            ),
            min_width="60px",
            min_height="60px",
            position="relative",
    )

def detail_popover(day: rx.Var[Day]) -> rx.Component:
    pass