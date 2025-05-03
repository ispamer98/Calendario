# Calendario/components/today_box.py
import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def today_box() -> rx.Component:
    return rx.cond(
        UserState.today_data.length() > 0,
        rx.vstack(
            rx.heading(
                rx.fragment(
                    "📅 Hoy ",
                    rx.moment(CalendarState.current_date_str,
                              format="dddd D [de] MMMM [de] YYYY",
                              locale="es",
                              style={"textTransform": "capitalize"}),
                    
                ),
                size="5",
                padding_bottom="1em"
            ),
            rx.foreach(
                UserState.today_data,
                lambda cal: rx.cond(
                    cal["meal"] | cal["dinner"] | cal["comments"],
                    rx.box(
                        rx.vstack(
                            rx.heading(cal["calendar_name"], size="4"),
                            rx.cond(
                                cal["meal"],
                                rx.text(f"🍽️ Comida: {cal['meal']}"),
                            ),
                            rx.cond(
                                cal["dinner"],
                                rx.text(f"🌙 Cena: {cal['dinner']}"),
                            ),
                            rx.cond(
                                cal["comments"],
                                rx.vstack(
                                    rx.text("💬 Comentarios:", weight="bold"),
                                    rx.foreach(
                                        cal["comments"],
                                        lambda comment: rx.text(
                                            f"{comment['username']}: {comment['content']}"
                                        )
                                    ),
                                    spacing="1",
                                ),
                            ),
                            spacing="2",
                        ),
                        bg="rgba(255, 255, 255, 0.05)",
                        border="1px solid rgba(255, 255, 255, 0.1)",
                        border_radius="lg",
                        padding="1.5em",
                        width="100%",
                        max_width=["400%", "800px"],
                        box_shadow="md",
                    ),
                    rx.fragment()
                )
            ),
            spacing="3",
            width="100%",
            align_items="center",
        ),
        rx.fragment(),
    )