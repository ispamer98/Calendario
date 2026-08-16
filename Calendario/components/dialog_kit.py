# Calendario/components/dialog_kit.py
"""
Look común para los diálogos de la app: cabecera con icono en avatar de
color + título, cuerpo con separación generosa entre campos, pie con
acciones. Evita repetir el mismo `rx.dialog.content` con estilos distintos
en cada formulario (crear calendario, compartir, comidas, usuarios...).
"""
import reflex as rx

from Calendario import theme


def form_dialog_content(
    *,
    icon: str,
    title: str,
    form: rx.Component,
    accent: str = theme.ACCENT,
    max_width: str = "420px",
) -> rx.Component:
    return rx.dialog.content(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=20, color=accent),
                    padding="12px",
                    border_radius="14px",
                    background=theme.alpha(accent, 0.14),
                    border=f"1px solid {theme.alpha(accent, 0.3)}",
                ),
                rx.dialog.title(title, margin="0", size="4", weight="bold"),
                spacing="3",
                align="center",
                width="100%",
            ),
            rx.divider(border_color=theme.BORDER),
            form,
            spacing="4",
            width="100%",
        ),
        style={
            "max_width": max_width,
            "background": theme.BG_WINDOW,
            "border": f"1px solid {theme.BORDER_STRONG}",
            "border_radius": "18px",
            "padding": "24px",
            "box_shadow": "0 24px 70px -12px rgba(0, 0, 0, 0.65)",
            "backdrop_filter": "blur(16px)",
        },
    )


def field(label: str, *children: rx.Component, hint: str = "") -> rx.Component:
    """Fila "etiqueta + input(s)" — mismo espaciado/tipografía en todos los formularios."""
    return rx.vstack(
        rx.text(label, size="1", color=theme.MUTED, weight="medium", letter_spacing="0.02em"),
        *children,
        *([rx.text(hint, size="1", color=theme.MUTED, opacity="0.7")] if hint else []),
        spacing="1",
        width="100%",
        align="start",
    )


def dialog_footer(
    *, confirm_label: str, color_scheme: str = "blue", cancel_label: str = "Cancelar",
    on_cancel=None,
) -> rx.Component:
    """Pie de formulario. `on_cancel` es obligatorio cuando el diálogo controla
    su apertura con `open=...`: ahí `rx.dialog.close` no basta, porque el estado
    sigue diciendo que está abierto y se vuelve a abrir solo."""
    cancel = rx.button(
        cancel_label, variant="soft", color_scheme="gray", type="button", size="2",
        **({"on_click": on_cancel} if on_cancel is not None else {}),
    )
    return rx.hstack(
        rx.dialog.close(cancel),
        rx.dialog.close(rx.button(confirm_label, type="submit", color_scheme=color_scheme, size="2")),
        spacing="2",
        justify="end",
        width="100%",
        padding_top="2",
    )


def styled_input(**props) -> rx.Component:
    props.setdefault("size", "3")
    props.setdefault("width", "100%")
    return rx.input(**props)


#El antiguo `styled_select` (un `rx.select` de Radix, sin buscador) se ha
#quitado: todos los desplegables de la app usan ya `components/picker.py`, que
#deja escribir para filtrar. No quedaba nadie usándolo.


def glass_card(*children: rx.Component, **props) -> rx.Component:
    """Tarjeta translúcida estándar (fondo + borde + blur) usada en toda la app."""
    props.setdefault("background", theme.BG_CARD)
    props.setdefault("border", f"1px solid {theme.BORDER}")
    props.setdefault("border_radius", "12px")
    props.setdefault("backdrop_filter", "blur(10px)")
    props.setdefault("transition", "background 0.15s ease, border-color 0.15s ease")
    return rx.vstack(*children, **props)
