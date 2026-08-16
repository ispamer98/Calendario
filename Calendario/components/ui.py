"""
Kit de interfaz de CalendPy.

Piezas visuales que se repiten en todas las páginas (cabeceras, tarjetas de
estadística, paneles de cristal, estados vacíos, chips...). Antes cada página
se inventaba su propia cabecera y su propio `rx.box` con borde y blur; aquí
están una sola vez, así que cambiar el look de la app es cambiar este archivo.

Todos los helpers aceptan tanto valores de Python como Vars de Reflex, para
poder usarlos dentro de `rx.foreach` y `rx.cond`.
"""

import reflex as rx

from Calendario import theme


# ---------------------------------------------------------------------------
# Superficies
# ---------------------------------------------------------------------------
def panel(*children: rx.Component, **props) -> rx.Component:
    """Tarjeta de cristal estándar: fondo translúcido, borde tenue y blur."""
    props.setdefault("background", theme.BG_CARD)
    props.setdefault("border", f"1px solid {theme.BORDER}")
    props.setdefault("border_radius", theme.RADIUS)
    props.setdefault("backdrop_filter", "blur(12px)")
    props.setdefault("padding", "18px")
    props.setdefault("width", "100%")
    props.setdefault("box_shadow", theme.SHADOW_SM)
    return rx.box(*children, **props)


def hover_panel(*children: rx.Component, **props) -> rx.Component:
    """Como `panel`, pero reacciona al ratón (para elementos pulsables)."""
    props.setdefault(
        "_hover",
        {
            "background": theme.BG_CARD_HOVER,
            "border_color": theme.BORDER_STRONG,
            "transform": "translateY(-2px)",
            "box_shadow": theme.SHADOW,
        },
    )
    props.setdefault("transition", "all 0.18s cubic-bezier(0.4, 0, 0.2, 1)")
    return panel(*children, **props)


def icon_badge(icon: str, color: str = theme.ACCENT, size: int = 18, box: str = "40px") -> rx.Component:
    """Icono dentro de un cuadrado de color translúcido (avatar de sección)."""
    return rx.center(
        rx.icon(icon, size=size, color=color),
        min_width=box,
        width=box,
        height=box,
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(color, 0.14),
        border=f"1px solid {theme.alpha(color, 0.28)}",
        flex_shrink="0",
    )


# ---------------------------------------------------------------------------
# Cabeceras
# ---------------------------------------------------------------------------
def page_header(
    *,
    icon: str,
    title,
    subtitle,
    accent: str = theme.ACCENT,
    actions: list[rx.Component] | None = None,
    extra: rx.Component | None = None,
) -> rx.Component:
    """Cabecera de página: icono + título + subtítulo, con acciones a la derecha.

    En móvil las acciones bajan a una segunda línea en vez de comprimir el
    título hasta hacerlo ilegible.
    """
    return panel(
        rx.vstack(
            #En móvil las acciones bajan a su propia fila a lo ancho: metidas
            #al lado del título se solapaban con el subtítulo y partían el
            #título en tres líneas.
            rx.flex(
                rx.hstack(
                    icon_badge(icon, accent, size=20, box="44px"),
                    rx.vstack(
                        rx.heading(
                            title,
                            size=rx.breakpoints(initial="4", md="6"),
                            color=theme.TEXT,
                            weight="bold",
                            line_height="1.2",
                        ),
                        rx.text(subtitle, size=rx.breakpoints(initial="1", md="2"), color=theme.MUTED),
                        spacing="1",
                        align="start",
                        min_width="0",
                        width="100%",
                    ),
                    spacing="3",
                    align="center",
                    min_width="0",
                    width="100%",
                    flex=rx.breakpoints(initial="1 1 100%", md="1"),
                ),
                rx.flex(
                    *(actions or []),
                    spacing="2",
                    align="center",
                    wrap="wrap",
                    gap="8px",
                    justify=rx.breakpoints(initial="start", md="end"),
                    width=rx.breakpoints(initial="100%", md="auto"),
                    flex_shrink="0",
                ) if actions else rx.fragment(),
                width="100%",
                direction=rx.breakpoints(initial="column", md="row"),
                align=rx.breakpoints(initial="start", md="center"),
                justify="between",
                gap="14px",
            ),
            *([extra] if extra is not None else []),
            spacing="4",
            width="100%",
        ),
        padding=["16px", "16px", "22px"],
        background=f"linear-gradient(135deg, {theme.alpha(accent, 0.10)} 0%, {theme.BG_CARD} 60%)",
        border=f"1px solid {theme.alpha(accent, 0.18)}",
        border_radius=theme.RADIUS_LG,
    )


def section_title(icon: str, title, color: str = theme.ACCENT, hint=None, action: rx.Component | None = None) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=16, color=color, flex_shrink="0"),
        rx.text(title, size="2", weight="bold", color=theme.TEXT, white_space="nowrap"),
        *([rx.text(hint, size="1", color=theme.DIM)] if hint is not None else []),
        rx.spacer(),
        *([action] if action is not None else []),
        width="100%",
        align="center",
        spacing="2",
    )


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def stat_card(*, icon: str, label, value, hint=None, color: str = theme.ACCENT) -> rx.Component:
    """Tarjeta de métrica: número grande, etiqueta y una pista opcional."""
    return panel(
        rx.hstack(
            icon_badge(icon, color),
            rx.vstack(
                rx.text(value, size="6", weight="bold", color=theme.TEXT, line_height="1.1"),
                rx.text(label, size="1", color=theme.MUTED, white_space="nowrap"),
                *([rx.text(hint, size="1", color=theme.DIM)] if hint is not None else []),
                spacing="0",
                align="start",
                min_width="0",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="14px",
        min_width="0",
    )


def stats_grid(*cards: rx.Component, columns: str = "4") -> rx.Component:
    return rx.grid(
        *cards,
        columns=rx.breakpoints(initial="2", md=columns),
        spacing="3",
        width="100%",
    )


def progress_bar(percent, color: str = theme.ACCENT, height: str = "8px") -> rx.Component:
    """Barra de progreso.

    `percent` puede ser un número o una Var **ya acotada a 0-100** (los estados
    la calculan con `min(100, ...)`, así no hace falta un `rx.cond` aquí).
    """
    width = percent.to_string() + "%" if isinstance(percent, rx.Var) else f"{percent}%"
    #El color puede venir de un rx.cond (Var): en ese caso no se puede calcular
    #el degradado en Python, así que se pinta plano
    fill = color if isinstance(color, rx.Var) else f"linear-gradient(90deg, {theme.alpha(color, 0.7)}, {color})"
    return rx.box(
        rx.box(
            width=width,
            height="100%",
            border_radius="999px",
            background=fill,
            transition="width 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
        ),
        width="100%",
        height=height,
        border_radius="999px",
        background=theme.BG_SUNKEN,
        overflow="hidden",
    )


def pill(text, color: str = theme.MUTED, icon: str | None = None, size: str = "1") -> rx.Component:
    """Chip pequeño de metadato (categoría, unidad, tiempo...)."""
    return rx.hstack(
        *([rx.icon(icon, size=12, color=color)] if icon else []),
        rx.text(text, size=size, color=color, weight="medium", white_space="nowrap"),
        spacing="1",
        align="center",
        padding="3px 9px",
        border_radius="999px",
        background=theme.alpha(color, 0.12),
        border=f"1px solid {theme.alpha(color, 0.25)}",
        flex_shrink="0",
    )


# ---------------------------------------------------------------------------
# Estados y avisos
# ---------------------------------------------------------------------------
def empty_state(
    *,
    icon: str,
    title,
    description,
    action: rx.Component | None = None,
    color: str = theme.ACCENT,
) -> rx.Component:
    """Pantalla vacía con personalidad: icono grande, explicación y una salida."""
    return rx.center(
        rx.vstack(
            rx.center(
                rx.icon(icon, size=34, color=color),
                width="82px",
                height="82px",
                border_radius="50%",
                background=theme.alpha(color, 0.10),
                border=f"1px solid {theme.alpha(color, 0.22)}",
            ),
            rx.heading(title, size="5", color=theme.TEXT, text_align="center"),
            rx.text(description, size="2", color=theme.MUTED, text_align="center", max_width="420px"),
            *([action] if action is not None else []),
            spacing="3",
            align="center",
        ),
        width="100%",
        padding_y="3.5em",
    )


def info_banner(text, icon: str = "info", color: str = theme.ACCENT) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=16, color=color, flex_shrink="0"),
        rx.text(text, size="2", color=theme.MUTED),
        spacing="3",
        align="center",
        width="100%",
        padding="12px 14px",
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(color, 0.07),
        border=f"1px solid {theme.alpha(color, 0.18)}",
    )


def tip(icon: str, title: str, description: str, color: str = theme.ACCENT) -> rx.Component:
    """Tarjeta de consejo, para llenar de contenido útil las zonas muertas."""
    return panel(
        rx.hstack(
            icon_badge(icon, color, size=16, box="34px"),
            rx.vstack(
                rx.text(title, size="2", weight="bold", color=theme.TEXT),
                rx.text(description, size="1", color=theme.MUTED, line_height="1.5"),
                spacing="1",
                align="start",
                min_width="0",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="14px",
    )


def legend_item(color: str, label: str, icon: str | None = None) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=13, color=color) if icon else rx.box(
            width="9px", height="9px", border_radius="3px", background=color, flex_shrink="0",
        ),
        rx.text(label, size="1", color=theme.MUTED, white_space="nowrap"),
        spacing="2",
        align="center",
    )


def collapsible(
    *children: rx.Component,
    title: str,
    icon: str = "chevron-down",
    color: str = theme.ACCENT,
    hint: str = "",
    default_open: bool = False,
) -> rx.Component:
    """Sección plegable.

    Para que la información de apoyo (filtros, consejos, leyendas) no ocupe
    media pantalla: se muestra el titular y se despliega solo si te interesa.
    Usa el acordeón de Radix, así que no hace falta estado propio.
    """
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.hstack(
                rx.icon(icon, size=14, color=color, flex_shrink="0"),
                rx.text(title, size="1", weight="bold", color=theme.TEXT, letter_spacing="0.02em"),
                *([rx.text(hint, size="1", color=theme.DIM)] if hint else []),
                spacing="2",
                align="center",
                width="100%",
            ),
            content=rx.box(*children, width="100%", padding_top="10px"),
            value="panel",
        ),
        type="single",
        collapsible=True,
        default_value="panel" if default_open else None,
        width="100%",
        variant="ghost",
        style={
            "background": theme.BG_CARD,
            "border": f"1px solid {theme.BORDER}",
            "border_radius": theme.RADIUS,
            "padding": "6px 14px",
            "backdrop_filter": "blur(12px)",
            "--accordion-content-padding": "0px",
        },
    )


def divider() -> rx.Component:
    return rx.box(height="1px", width="100%", background=theme.BORDER)


def spinner_block(text: str = "Cargando...") -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=theme.ACCENT),
            rx.text(text, size="2", color=theme.MUTED),
            spacing="3",
            align="center",
        ),
        width="100%",
        padding_y="4em",
    )


def action_button(label: str, icon: str, color: str = theme.ACCENT, **props) -> rx.Component:
    """Botón principal con el degradado de marca."""
    props.setdefault("size", "2")
    return rx.button(
        rx.icon(icon, size=16),
        rx.text(label, size="2", weight="medium"),
        background=theme.alpha(color, 0.16),
        color=color,
        border=f"1px solid {theme.alpha(color, 0.32)}",
        border_radius="999px",
        cursor="pointer",
        _hover={"background": theme.alpha(color, 0.26), "transform": "translateY(-1px)"},
        transition="all 0.16s ease",
        **props,
    )
