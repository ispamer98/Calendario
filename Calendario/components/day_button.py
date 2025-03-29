import reflex as rx
from Calendario.model.model import Day, Meal
from datetime import datetime
from Calendario.state.calendar_state import CalendarState

def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.vstack(
                        rx.mobile_only(
                            rx.text(
                                rx.moment(day.date, format="D"),
                                size="4",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.tablet_and_desktop(
                            rx.text(
                                rx.moment(day.date, format="DD"),
                                size="3",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.vstack(
                            rx.hstack(
                                # Icono de comida (verde)
                                rx.cond(
                                    day.meal_id != None,
                                    rx.icon("utensils-crossed", size=16, color="var(--green-9)"),  # Verde
                                    rx.box()
                                ),
                                # Icono de cena (azul)
                                rx.cond(
                                    day.dinner_id != None,
                                    rx.icon("utensils-crossed", size=16, color="var(--blue-9)"),  # Azul
                                    rx.box()
                                ),
                                # Icono de comentarios (naranja)
                                rx.cond(
                                    day.comments.length() > 0,
                                    rx.icon("message-square-more", size=16, color="var(--orange-9)"),  # Naranja
                                    rx.box()
                                ),
                                spacing="2",
                                justify="center"
                            ),
                            spacing="2",
                            align="center",
                            width="100%"
                        ),
                        spacing="2",
                        align="center",
                        width="100%"
                    ),
                    width=["80px", "100px", "120px"],
                    height=["80px", "100px", "120px"],
                    padding="2",
                    border_radius="lg",
                    background=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "linear-gradient(45deg, #4F46E5, #3B82F6)",
                        "rgba(255, 255, 255, 0.05)"
                    ),
                    border=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "none",
                        "1px solid rgba(255, 255, 255, 0.1)"
                    ),
                    box_shadow=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "lg",
                        "sm"
                    ),
                    _hover={
                        "transform": "scale(1.05)",
                        "box_shadow": "xl"
                    },
                    transition="all 0.2s"
                )
            ),
            rx.popover.content(
                rx.vstack(
                    rx.text(rx.moment(
                        day.date,
                        format="dddd, [de] D MMMM [del] YYYY", locale="es"),
                        size="2",
                        style={"text-transform": "capitalize"}),
                    rx.divider(),
                    rx.cond(
                        day.meal_id != None,
                        rx.vstack(
                            rx.text("Comida:", size="2", color="var(--green-9)", weight="bold"),
                            rx.text(day.meal_id, size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        day.dinner_id != None,
                        rx.vstack(
                            rx.text("Cena:", size="2", color="var(--blue-9)", weight="bold"),
                            rx.text(day.dinner_id, size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        day.comments.length() > 0,
                        rx.vstack(
                            rx.text("Comentarios:", size="2", color="var(--orange-9)", weight="bold"),
                            rx.foreach(
                                day.comments,
                                lambda comment: rx.text(comment, size="1")
                            ),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    spacing="3",
                    padding="2",
                    width=["200px", "240px", "280px"]
                ),
                side="right",
                align="center",
                side_offset=5
            )
        ),
        position="relative",
        margin=["2px", "4px", "6px"]
    )