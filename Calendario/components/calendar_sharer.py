import reflex as rx
from Calendario.state.calendar_state import CalendarState



# Calendario/components/calendar_sharer.py
def calendar_sharer() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Compartir calendario", variant="soft", size="3")
        ),
        rx.dialog.content(
            rx.vstack(
                rx.heading("Compartir calendario", size="5"),
                rx.input(
                    placeholder="Nombre de usuario",
                    value=CalendarState.username_to_share,
                    on_change=CalendarState.set_username_to_share,
                    autofocus=True
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray")
                    ),
                    rx.button(
                        "Compartir", 
                        color_scheme="blue",
                        on_click=CalendarState.share_calendar
                    )
                ),
                rx.cond(
                    CalendarState.error_message,
                    rx.text(CalendarState.error_message, color="red", size="2")
                )
            ),
            title="Compartir calendario",
            size="3"
        ),
        open=CalendarState.show_calendar_sharer,
        on_open_change=lambda opened: (
            rx.cond(
    opened,
    CalendarState.open_calendar_sharer(),
    CalendarState.close_calendar_sharer()
)
        )
    )