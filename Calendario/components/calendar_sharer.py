import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

def user_badge(username: str, is_owner: bool = False) -> rx.Component:
    return rx.hstack(
        rx.cond(
            is_owner,
            rx.icon("crown", size=16, color="var(--gold-9)"),
            rx.icon("user", size=16, color="var(--slate-11)")
        ),
        rx.text(
            username,
            color=rx.cond(is_owner, "var(--gold-11)", "var(--slate-12)"),
            size="2",
            weight="medium"
        ),
        padding_y="1",
        padding_x="2",
        border_radius="md",
        background=rx.cond(is_owner, "var(--gold-3)", "var(--slate-3)"),
        spacing="2",
        width="100%"
    )

def calendar_sharer() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Compartir calendario", 
                variant="soft", 
                size="3",
                _hover={"transform": "scale(1.05)"},
                
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.heading("Compartir calendario", size="5"),
                rx.divider(margin_y="2"),
                
                # Sección de usuarios con acceso
                rx.vstack(
                    rx.text("Accesos actuales:", size="2", color="var(--slate-11)"),
                    user_badge(CalendarState.owner_username, is_owner=True),
                    rx.foreach(
                        CalendarState.shared_users,
                        lambda user: user_badge(user.username)
                    ),
                    spacing="2",
                    width="100%",
                    max_height="200px",
                    overflow_y="auto",
                    padding_right="2"
                ),
                
                # Input para compartir
                rx.vstack(
                    rx.text("Agregar usuario:", size="2", color="var(--slate-11)"),
                    rx.input(
                        placeholder="Nombre de usuario",
                        value=CalendarState.username_to_share,
                        on_change=CalendarState.set_username_to_share,
                        autofocus=True,
                        variant="surface"
                    ),
                    spacing="2",
                    width="100%"
                ),
                
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            _hover={"bg": "var(--slate-4)"}
                        )
                    ),
                    rx.button(
                        "Compartir", 
                        color_scheme="blue",
                        variant="solid",
                        on_click=CalendarState.share_calendar,
                        _hover={"transform": "scale(1.05)"}
                    ),
                    spacing="3",
                    justify="end",
                    width="100%"
                ),
                rx.cond(
                    CalendarState.error_message,
                    rx.text(
                        CalendarState.error_message, 
                        color="var(--red-11)", 
                        size="1",
                        weight="medium"
                    )
                ),
                spacing="4",
                width="100%"
            ),
            style={"max_width": "400px"},
            background="var(--slate-2)",
            border="1px solid var(--slate-6)",
            box_shadow="xl"
        ),
        on_mount=CalendarState.load_shared_users,
        open=CalendarState.show_calendar_sharer,
        on_open_change=lambda opened: (
            rx.cond(
    opened,
    CalendarState.open_calendar_sharer(),
    CalendarState.close_calendar_sharer()
)
    ))