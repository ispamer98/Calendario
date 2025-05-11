import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def today_box() -> rx.Component:
    return rx.cond(
        UserState.today_data.length() > 0,
        rx.vstack(
            rx.heading(
                rx.fragment(
                    "📅📍 Hoy ",
                    rx.moment(
                        CalendarState.current_date_str,
                        format="dddd D [de] MMMM [de] YYYY",
                        locale="es",
                        style={"textTransform": "capitalize"},
                        on_mount=CalendarState.update_current_date
                    ),
                ),
                size="5",
                padding_bottom="1em",
                align="center",  # Centra el texto de la cabecera
            ),
            rx.foreach(
                UserState.today_data,
                lambda cal: rx.cond(
                    cal["meal"] | cal["dinner"] | cal["comments"],
                    rx.box(
                        rx.vstack(
                            rx.heading(cal["calendar_name"], size="4", align="center"),
                            rx.cond(
                                cal["meal"],
                                rx.box(
                                rx.text(f" Comida 🍽️ :",align="center",weight="bold",color="var(--green-9)"),
                                rx.text(f"· {cal['meal']}", align="center")
                                )
                            ),
                            rx.cond(
                                cal["dinner"],
                                rx.box(
                                    rx.text(f" Cena 🌙 :", align="center",weight="bold",color="var(--blue-9)"),
                                    rx.text(f"· {cal["dinner"]}",align="center"))
                            ),
                            rx.cond(
                                cal["comments"],
                                rx.vstack(
                                    rx.text(" Comentarios 💬 :", weight="bold", align="center",color="var(--orange-9)"),
                                    rx.foreach(
                                        cal["comments"],
                                        lambda comment: rx.hstack(
                                            rx.text(
                                                f"· {comment['username']} : ",
                                                align="center",color="var(--accent-9)"
                                            ),
                                            rx.text(
                                                f"{comment['content']}",
                                                align="center"
                                            )
                                        )
                                    ),
                                    spacing="1",
                                    align_items="center",
                                ),
                            ),
                            spacing="2",
                            align_items="center",  # Centrado vertical y horizontal del contenido
                        ),
                        bg="rgba(255, 255, 255, 0.05)",
                        border="1px solid rgba(255, 255, 255, 0.1)",
                        border_radius="lg",
                        padding="1.5em",
                        width="100%",
                        box_shadow="md",
                        align_items="center",
                        justify_content="center",
                        display="flex",
                        flex_direction="column",
                    ),
                    rx.fragment(),
                ),
            ),
            spacing="3",
            width=["100%", "300px"],
            min_width="250px",
            align_items="center",
            justify="center",
        ),
        rx.fragment(),
    )