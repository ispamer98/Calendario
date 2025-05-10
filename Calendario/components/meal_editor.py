
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.model.model import Day
from Calendario.state.user_state import UserState
from Calendario.utils.api import get_all_meals

def meal_editor() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.box()),
        rx.dialog.content(
            rx.form.root(
                rx.vstack(
                    rx.text(
                        rx.moment(DayState.current_day.date,
                                format="dddd, D [de] MMMM [del] YYYY", 
                                locale="es"
                        ),
                        style={"text-transform": "capitalize"},
                        size="5"

                    ),
                    rx.text(
                        "Comida:",
                        color="var(--green-9)",
                        font_weight="bold",
                        margin_bottom="0.2em"
                    ),
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecciona una comida"
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ),
                                    ),
                                ),
                            ),
                            name="meal",
                            value=DayState.current_meal,
                            on_change=DayState.set_meal,
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon(
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
                            on_click=DayState.clear_meal
                        ),
                    ),
                    rx.text(
                        "Cena:",
                        color="var(--blue-9)",
                        font_weight="bold",
                        margin_bottom="0.2em",
                        margin_top="0.5em"
                    ),
                    rx.hstack(
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecciona una cena"
                            ),
                            rx.select.content(
                                rx.select.group(
                                    rx.foreach(
                                        CalendarState.meals,
                                        lambda meal: rx.select.item(
                                            meal.name, 
                                            value=meal.name
                                        ),
                                    ),
                                ),
                            ),
                            name="dinner",
                            value=DayState.current_dinner,
                            on_change=DayState.set_dinner,
                            width="300px",
                            min_width="300px",
                        ),
                        rx.icon(
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
                            on_click=DayState.clear_dinner
                        ),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                type="button",
                                on_click=DayState.clear_current_day,
                                color_scheme="red",
                                variant="soft",
                                size="3",
                                _hover={
                                    "background": "var(--red-9)",
                                    "color": "white"
                                }
                            )
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Guardar",
                                type="submit",
                                disabled=DayState.loading,
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
                on_submit=DayState.update_day
            ),
            max_width="500px",
            align_items="center",
        ),
        open=DayState.show_editor
    )