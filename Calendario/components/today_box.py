# Calendario/components/today_box.py
import reflex as rx
from Calendario.state.user_state import UserState

def today_box() -> rx.Component:
    return rx.cond(
        UserState.today_data.length() > 0,
        rx.vstack(
            rx.heading("📅 Hoy", size="5", padding_bottom="1em"),
            rx.foreach(
                UserState.today_data,
                lambda cal: rx.box(
                    rx.vstack(
                        rx.heading(cal["calendar_name"], size="4"),
                        rx.text(f"🍽️ Comida: {cal['meal'] | '–'}"),
                        rx.text(f"🌙 Cena: {cal['dinner'] | '–'}"),
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
                    max_width=["100%", "400px"],
                    box_shadow="md",
                )
            ),
            spacing="3",
            width="100%",
            align_items="center",
        ),
        rx.fragment(),
    )