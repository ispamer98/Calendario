import reflex as rx
from Calendario.model.model import Day,Meal
from datetime import datetime

from Calendario.state.calendar_state import CalendarState


def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.tooltip(
            rx.button(
                rx.vstack(
                    rx.vstack(
                        rx.moment(day.date, format="DD"),
                        rx.hstack(
                            rx.cond(
                                (day.meal_id != None) | (day.dinner_id != None),
                                rx.hstack(
                                    rx.cond(
                                        day.meal_id != None,
                                        rx.text(day.meal_id),
                                        rx.text("NO TIENE MEAL ID")
                                    ),
                                    rx.cond(
                                        day.dinner_id != None,
                                        rx.text(day.dinner_id),  # Lo mismo aquí
                                        rx.text("NO TIENE DINNER ID")
                                    ),
                                    rx.icon("utensils", size=12, color="blue"),
                                )
                            ),
                            rx.cond(
                                day.comments.length() > 0,
                                rx.icon("message-square-more", size=12, color="blue")
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
                background_color=rx.cond(
                    day.date == CalendarState.current_date_str,
                    "grey",
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
        
    )

def detail_popover(day: rx.Var[Day]) -> rx.Component:
    pass