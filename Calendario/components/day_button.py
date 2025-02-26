import reflex as rx

def day_button(day: str = None) -> rx.Component:

    return rx.box(
            rx.button(
                rx.text("Día",day),
                rx.box(
                    rx.text("Línea 1", style={"margin": "0"}),
                    rx.text("Línea 2", style={"margin": "0"}),
                    class_name="extra_text",
                ),
                class_name="day_button",
            ),
            _hover="a",
            style={"display": "flex", "justifyContent": "center", "alignItems": "center"
            },
        )
