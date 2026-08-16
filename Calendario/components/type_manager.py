# Calendario/components/type_manager.py
"""Gestor de tipos de entrada de agenda (tarea, evento, nota... y los tuyos)."""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import icon_badge, info_banner
from Calendario.state.day_state import DayState


def manage_types_button() -> rx.Component:
    return rx.icon(
        "settings-2", size=15, color=theme.MUTED, cursor="pointer",
        on_click=DayState.open_type_manager,
        _hover={"color": theme.ACCENT, "transform": "scale(1.15)"},
        transition="all 0.15s ease", flex_shrink="0",
        title="Gestionar tipos",
    )


def _row(t) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon(t.icon, size=14, color=t.color),
            min_width="28px", width="28px", height="28px", border_radius="8px",
            background=t.color + "26", border="1px solid " + t.color + "66", flex_shrink="0",
        ),
        rx.box(
            rx.text(t.label, size="2", color=theme.TEXT, weight="medium",
                    overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.cond(t.completable, rx.icon("square-check", size=13, color=theme.AGENDA, flex_shrink="0")),
        #Editar: carga el tipo arriba (nombre, color, icono y si se marca)
        rx.icon("pencil", size=14, color=theme.MUTED, cursor="pointer", flex_shrink="0",
                on_click=DayState.edit_task_type(t.key),
                title="Editar este tipo",
                _hover={"color": theme.ACCENT, "transform": "scale(1.2)"}),
        rx.icon("trash-2", size=14, color=theme.MUTED, cursor="pointer", flex_shrink="0",
                on_click=DayState.remove_task_type(t.key),
                _hover={"color": theme.DANGER, "transform": "scale(1.2)"}),
        width="100%", max_width="100%", align="center", spacing="2",
        padding="10px", min_height="46px", flex_shrink="0", border_radius=theme.RADIUS_SM,
        background=rx.cond(
            DayState.editing_type == t.key,
            theme.alpha(theme.ACCENT, 0.10),
            theme.BG_SUNKEN,
        ),
        border=rx.cond(
            DayState.editing_type == t.key,
            f"1px solid {theme.alpha(theme.ACCENT, 0.45)}",
            f"1px solid {theme.BORDER}",
        ),
        overflow="hidden",
    )


def type_manager_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge("list-checks", theme.AGENDA, size=18, box="42px"),
                    rx.vstack(
                        rx.dialog.title("Tipos de agenda", margin="0", size="4", weight="bold"),
                        rx.text("Tarea, evento, nota... y los que quieras", size="1", color=theme.MUTED),
                        spacing="0", align="start",
                    ),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer",
                            on_click=DayState.close_type_manager),
                    width="100%", align="center", spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.hstack(
                    rx.icon(
                        rx.cond(DayState.is_editing_type, "pencil", "plus"),
                        size=13,
                        color=rx.cond(DayState.is_editing_type, theme.ACCENT, theme.AGENDA),
                    ),
                    rx.text(
                        rx.cond(DayState.is_editing_type, "EDITANDO TIPO", "NUEVO TIPO"),
                        size="1", color=theme.MUTED, weight="medium",
                    ),
                    rx.spacer(),
                    rx.cond(
                        DayState.is_editing_type,
                        rx.text(
                            "Cancelar edición", size="1", color=theme.MUTED, cursor="pointer",
                            on_click=DayState.cancel_type_edit,
                            _hover={"color": theme.DANGER, "text_decoration": "underline"},
                        ),
                    ),
                    width="100%", align="center", spacing="2",
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Nuevo tipo (ej. Recordatorio)",
                        value=DayState.new_type_label,
                        on_change=DayState.set_new_type_label,
                        size="2", max_length=24, flex="1 1 0", min_width="0",
                        id="tipo-nombre",
                    ),
                    rx.button(
                        rx.icon(rx.cond(DayState.is_editing_type, "check", "plus"), size=16),
                        rx.text(rx.cond(DayState.is_editing_type, "Guardar", "Añadir"), size="2"),
                        on_click=DayState.save_task_type,
                        color_scheme=rx.cond(DayState.is_editing_type, "blue", "green"),
                        size="2", type="button", flex_shrink="0", cursor="pointer",
                    ),
                    width="100%", spacing="2", align="center",
                ),
                rx.hstack(
                    rx.switch(checked=DayState.new_type_completable,
                              on_change=DayState.toggle_new_type_completable, color_scheme="jade"),
                    rx.text("Se puede marcar como hecho", size="1", color=theme.MUTED),
                    spacing="2", align="center", width="100%",
                ),
                rx.flex(
                    rx.foreach(DayState.type_palette, lambda c: rx.box(
                        width="24px", height="24px", border_radius="50%", background=c,
                        cursor="pointer", flex_shrink="0",
                        border=rx.cond(DayState.new_type_color == c, "3px solid white", "3px solid transparent"),
                        on_click=DayState.set_new_type_color(c),
                    )),
                    wrap="wrap", gap="7px", width="100%",
                ),
                rx.flex(
                    rx.foreach(DayState.type_icons, lambda ic: rx.center(
                        rx.icon(ic, size=15, color=rx.cond(DayState.new_type_icon == ic, theme.TEXT, theme.MUTED)),
                        width="32px", height="32px", border_radius="8px", cursor="pointer", flex_shrink="0",
                        background=rx.cond(DayState.new_type_icon == ic, theme.BG_CARD_HOVER, theme.BG_SUNKEN),
                        border=f"1px solid {theme.BORDER}",
                        on_click=DayState.set_new_type_icon(ic),
                    )),
                    wrap="wrap", gap="7px", width="100%",
                    max_height="132px", overflow_y="auto",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),
                rx.vstack(rx.foreach(DayState.task_types, _row), spacing="2", width="100%",
                          max_height="200px", overflow_y="auto"),
                info_banner("Borrar un tipo no toca las entradas que ya lo usaban.",
                            icon="info", color=theme.ACCENT),
                rx.hstack(
                    rx.button("Listo", on_click=DayState.close_type_manager,
                              variant="soft", color_scheme="gray", size="2"),
                    spacing="2", justify="end", width="100%",
                ),
                spacing="3", width="100%",
            ),
            style={
                "max_width": "440px", "max_height": "88vh", "overflow_y": "auto",
                "overflow_x": "hidden", "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG, "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=DayState.show_type_manager,
    )
