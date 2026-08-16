# Calendario/components/calendar_sharer.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario import theme
from Calendario.components.dialog_kit import field, styled_input

def _role_chip(member) -> rx.Component:
    color = rx.cond(
        member.is_owner, theme.OWNER,
        rx.cond(member.is_admin, theme.ACCENT, theme.MUTED),
    )
    return rx.hstack(
        rx.icon(
            rx.cond(member.is_owner, "crown", rx.cond(member.is_admin, "shield", "user")),
            size=11, color=color,
        ),
        rx.text(member.role_label, size="1", color=color, weight="medium", white_space="nowrap"),
        spacing="1", align="center", padding="2px 8px", border_radius="999px",
        background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}", flex_shrink="0",
    )


def _member_row(member) -> rx.Component:
    """Fila de una persona con acceso, con sus acciones según quién eres tú."""
    return rx.hstack(
        rx.box(
            rx.text(
                member.username, size="2", weight="medium", color=theme.TEXT,
                overflow="hidden", text_overflow="ellipsis", white_space="nowrap",
            ),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.cond(member.is_me, rx.text("tú", size="1", color=theme.DIM, flex_shrink="0")),
        _role_chip(member),
        #Ascender o degradar: solo el propietario, y nunca a sí mismo
        rx.cond(
            CalendarState.is_owner & ~member.is_owner,
            rx.hstack(
                rx.cond(
                    member.is_admin,
                    rx.icon(
                        "shield-off", size=14, color=theme.MUTED, cursor="pointer",
                        on_click=CalendarState.change_role(member.user_id, "member"),
                        _hover={"color": theme.WARNING, "transform": "scale(1.2)"},
                        title="Quitar administrador",
                    ),
                    rx.icon(
                        "shield-plus", size=14, color=theme.MUTED, cursor="pointer",
                        on_click=CalendarState.change_role(member.user_id, "admin"),
                        _hover={"color": theme.ACCENT, "transform": "scale(1.2)"},
                        title="Hacer administrador",
                    ),
                ),
                rx.icon(
                    "user-minus", size=14, color=theme.MUTED, cursor="pointer",
                    on_click=CalendarState.kick_member(member.user_id, member.username),
                    _hover={"color": theme.DANGER, "transform": "scale(1.2)"},
                    title="Quitar acceso",
                ),
                spacing="2", align="center", flex_shrink="0",
            ),
        ),
        width="100%", max_width="100%", align="center", spacing="2",
        padding="8px 10px", border_radius=theme.RADIUS_SM,
        background=rx.cond(member.is_owner, theme.alpha(theme.OWNER, 0.08), theme.BG_SUNKEN),
        border=rx.cond(
            member.is_owner,
            f"1px solid {theme.alpha(theme.OWNER, 0.25)}",
            f"1px solid {theme.BORDER}",
        ),
        overflow="hidden",
    )


def calendar_sharer() -> rx.Component: #Definimos el componente
    return rx.dialog.root(
        rx.dialog.trigger( #El disparador será un boton.
            rx.button(
                rx.icon("share-2", size=15),
                rx.text("Compartir", size="2"),
                variant="soft",
                color_scheme="blue",
                size="2",
                radius="full",
                cursor="pointer",
                on_click=CalendarState.load_shared_users #Cargará los usuarios asociados al calendario
            )
        ),
        rx.dialog.content( #Contenido del dialogo.
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon("share-2", size=20, color=theme.ACCENT),
                        padding="12px",
                        border_radius="14px",
                        background=theme.alpha(theme.ACCENT, 0.14),
                        border=f"1px solid {theme.alpha(theme.ACCENT, 0.3)}",
                    ),
                    rx.dialog.title("Compartir calendario", margin="0", size="4", weight="bold"),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                rx.divider(border_color=theme.BORDER),
                rx.vstack(
                    rx.text("QUIÉN TIENE ACCESO", size="1", color=theme.DIM,
                            weight="bold", letter_spacing="0.1em"),
                    rx.foreach(CalendarState.members, _member_row),
                    rx.cond(
                        CalendarState.is_owner,
                        rx.text(
                            "El propietario elimina el mes y nombra administradores. "
                            "Un administrador puede compartir y quitar accesos.",
                            size="1", color=theme.DIM, line_height="1.5",
                        ),
                    ),
                    spacing="2",
                    width="100%",
                    max_height="230px",
                    overflow_y="auto",
                    overflow_x="hidden",
                    align="start",
                ),
                field(
                    "Agregar usuario:",
                    styled_input(
                        placeholder="Nombre de usuario",
                        value=CalendarState.username_to_share,
                        on_change=CalendarState.set_username_to_share,
                        autofocus=True,
                    ),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button( #Botón que cerrará el dialogo
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                        )
                    ),
                    rx.button( #Agregamos el boton para compartir
                        "Compartir",
                        color_scheme="blue",
                        variant="solid",
                        on_click=CalendarState.share_calendar, #Lanza la función que añade un usuario al calendario
                        _hover={"transform": "scale(1.05)"}
                    ),
                    spacing="3",
                    justify="end",
                    width="100%"
                ),
                rx.cond( #Si existe algún error, lo mostraremos
                    CalendarState.error_message,
                    rx.text(
                        CalendarState.error_message,
                        color=theme.DANGER,
                        size="1",
                        weight="medium"
                    )
                ),
                spacing="4",
                width="100%"
            ),
            style={
                "max_width": "400px",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": "18px",
                "padding": "24px",
                "box_shadow": "0 24px 70px -12px rgba(0, 0, 0, 0.65)",
                "backdrop_filter": "blur(16px)",
            },
        ),

        open=CalendarState.show_calendar_sharer, #Si cambia el estado del componente y lo muestra
        on_open_change=lambda opened: ( #Alternamos el estado del componente
            rx.cond(
    opened,
    CalendarState.open_calendar_sharer(), #Si el estado es abierto, muestra el componente
    CalendarState.close_calendar_sharer() #Si el estado es cerrado, no muestra el componente
)
    ))
