import reflex as rx
from Calendario.state.calendar_state import CalendarState



def calendar_sharer() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Compartir calendario", variant="soft", size="3")
        ),
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading("Compartir calendario", size="5"),
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=CalendarState.username_to_share,
                        on_change=CalendarState.set_username_to_share,
                    ),
                    rx.cond(
                        CalendarState.error_message_share,
                        rx.text(CalendarState.error_message_share, color="red")
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancelar", variant="soft", color_scheme="gray")
                        ),
                        rx.dialog.close(  # <<-- CIERRA EL DIÁLOGO AL SUBMIT
                            rx.button("Compartir", type="submit", color_scheme="blue")
                        ),
                        spacing="3"
                    ),
                    spacing="4"
                ),
                on_submit=CalendarState.share_calendar,
                reset_on_submit=True  # <<-- LIMPIA EL INPUT DESPUÉS DE SUBMIT
            )
        )
    )