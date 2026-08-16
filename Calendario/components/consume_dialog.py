# Calendario/components/consume_dialog.py
"""
La ventana de "restar de la despensa" una comida.

Vive en el shell (como el resto de diálogos globales) porque se abre desde tres
sitios: el aviso del móvil a la hora de comer, el editor del día en el
calendario y la propia despensa.

Lo que se ve en cada línea es lo justo para decidir sin pensar: qué pide la
receta, qué hay en casa, qué se va a restar y cómo queda. Lo que no está en la
despensa sale primero y en otro color — ahí no hay nada que restar, hay algo que
guardar o que comprar.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import empty_state, icon_badge, info_banner
from Calendario.model.model import ConsumeRow
from Calendario.state.consume_state import ConsumeState


def _quantity_block(label: str, value, color: str) -> rx.Component:
    """Un dato de la fila (pide / tienes / restas), etiquetado y en monoespaciada."""
    return rx.vstack(
        rx.text(label, size="1", color=theme.DIM, white_space="nowrap", font_size="10px"),
        rx.text(
            value,
            size="1",
            weight="bold",
            color=color,
            font_family=theme.FONT_MONO,
            white_space="nowrap",
        ),
        spacing="0",
        align="start",
        min_width="0",
    )


def _status_pill(item: rx.Var[ConsumeRow]) -> rx.Component:
    """Chip del estado del ingrediente.

    No usa `ui.pill` porque su color llega como Var (lo decide el estado de cada
    fila) y allí el fondo se calcula en Python. Aquí se hace con el mismo truco
    que la lista de la compra: el color en hexadecimal, con la opacidad pegada
    al final.
    """
    return rx.hstack(
        rx.text(
            item.status_label,
            size="1",
            color=item.status_color,
            weight="medium",
            white_space="nowrap",
        ),
        spacing="1",
        align="center",
        padding="3px 9px",
        border_radius="999px",
        background=item.status_color + "1f",   # ~12% de opacidad
        border="1px solid " + item.status_color + "40",
        flex_shrink="0",
    )


def _row(item: rx.Var[ConsumeRow]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            #Marcar/desmarcar: solo tiene sentido en lo que sí está en casa
            rx.cond(
                item.in_pantry,
                rx.checkbox(
                    checked=item.selected,
                    on_change=ConsumeState.toggle_row(item.key),
                    color_scheme="amber",
                    size="1",
                ),
                rx.icon("circle-alert", size=15, color=theme.PANTRY, flex_shrink="0"),
            ),
            rx.box(
                rx.text(
                    item.name,
                    size="2",
                    weight="medium",
                    color=rx.cond(item.selected | ~item.in_pantry, theme.TEXT, theme.DIM),
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                flex="1 1 0",
                min_width="0",
                overflow="hidden",
            ),
            rx.cond(
                item.staple,
                rx.icon("package", size=11, color=theme.PURPLE, flex_shrink="0", title="Básico de despensa"),
            ),
            _status_pill(item),
            width="100%",
            align="center",
            spacing="2",
            min_width="0",
        ),

        rx.flex(
            _quantity_block("PIDE LA RECETA", item.need_label, theme.TEXT),
            rx.cond(
                item.in_pantry,
                _quantity_block("TIENES EN CASA", item.have_label, theme.PANTRY),
            ),
            rx.cond(
                item.in_pantry,
                _quantity_block("SE QUEDA EN", item.after_label, theme.MUTED),
            ),
            rx.spacer(),
            #Cuánto se resta, afinable a mano: la receta es una guía
            rx.cond(
                item.in_pantry,
                rx.hstack(
                    rx.icon(
                        "minus", size=13, color=theme.MUTED, cursor="pointer",
                        on_click=ConsumeState.adjust_take(item.key, -1),
                        _hover={"color": theme.DANGER},
                    ),
                    rx.text(
                        item.take_label,
                        size="1",
                        weight="bold",
                        color=rx.cond(item.selected, theme.WARNING, theme.DIM),
                        font_family=theme.FONT_MONO,
                        white_space="nowrap",
                        min_width="58px",
                        text_align="center",
                    ),
                    rx.icon(
                        "plus", size=13, color=theme.MUTED, cursor="pointer",
                        on_click=ConsumeState.adjust_take(item.key, 1),
                        _hover={"color": theme.SUCCESS},
                    ),
                    spacing="1",
                    align="center",
                    flex_shrink="0",
                    padding="3px 6px",
                    border_radius="999px",
                    background=theme.BG_SUNKEN,
                    border=f"1px solid {theme.BORDER}",
                ),
                #No está en casa: se guarda o se compra, no se resta
                rx.hstack(
                    rx.button(
                        rx.icon("warehouse", size=13),
                        rx.text("Guardar", size="1"),
                        on_click=ConsumeState.stock_missing(item.key),
                        color_scheme="amber",
                        variant="soft",
                        size="1",
                        radius="full",
                        cursor="pointer",
                        title="Guardarlo en la despensa con esta cantidad",
                    ),
                    rx.button(
                        rx.icon("shopping-cart", size=13),
                        rx.text("A la compra", size="1"),
                        on_click=ConsumeState.buy_missing(item.key),
                        color_scheme="green",
                        variant="soft",
                        size="1",
                        radius="full",
                        cursor="pointer",
                    ),
                    spacing="2",
                    align="center",
                    flex_shrink="0",
                ),
            ),
            width="100%",
            align="center",
            gap="12px",
            wrap="wrap",
        ),

        width="100%",
        spacing="2",
        align="start",
        padding="10px",
        border_radius=theme.RADIUS_SM,
        background=rx.cond(item.in_pantry, theme.BG_SUNKEN, theme.alpha(theme.PANTRY, 0.07)),
        border=rx.cond(
            item.in_pantry,
            f"1px solid {theme.BORDER}",
            f"1px solid {theme.alpha(theme.PANTRY, 0.3)}",
        ),
    )


def _already_block() -> rx.Component:
    """Lo que ya se descontó: quién, cuándo y **qué exactamente**."""
    return rx.vstack(
        rx.hstack(
            rx.icon("circle-check-big", size=16, color=theme.SUCCESS, flex_shrink="0"),
            rx.text("Ya descontado", size="2", weight="bold", color=theme.SUCCESS),
            rx.text(ConsumeState.already_label, size="1", color=theme.MUTED),
            rx.spacer(),
            rx.button(
                rx.icon("undo-2", size=14),
                rx.text("Deshacer", size="1"),
                on_click=ConsumeState.undo,
                variant="soft",
                color_scheme="gray",
                size="1",
                radius="full",
                cursor="pointer",
                title="Devuelve a la despensa exactamente lo que se restó",
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.cond(
            ConsumeState.already_items.length() > 0,
            rx.vstack(
                rx.foreach(
                    ConsumeState.already_items,
                    lambda linea: rx.hstack(
                        rx.icon("minus", size=11, color=theme.DIM, flex_shrink="0"),
                        rx.text(linea, size="1", color=theme.MUTED),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                ),
                spacing="1",
                width="100%",
                max_height="140px",
                overflow_y="auto",
            ),
        ),
        width="100%",
        spacing="2",
        padding="12px 14px",
        border_radius=theme.RADIUS_SM,
        background=theme.alpha(theme.SUCCESS, 0.07),
        border=f"1px solid {theme.alpha(theme.SUCCESS, 0.22)}",
    )


def consume_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    icon_badge(ConsumeState.slot_icon, theme.PANTRY, size=19, box="42px"),
                    rx.vstack(
                        rx.dialog.title(
                            "Descontar de la despensa", margin="0", size="4", weight="bold"
                        ),
                        rx.text(
                            ConsumeState.slot_label + ": " + ConsumeState.meal_name
                            + "  ·  " + ConsumeState.date_label,
                            size="1",
                            color=theme.MUTED,
                        ),
                        spacing="0",
                        align="start",
                        min_width="0",
                    ),
                    rx.spacer(),
                    rx.icon("x", size=18, color=theme.MUTED, cursor="pointer", on_click=ConsumeState.close),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=theme.BORDER),

                rx.cond(
                    ConsumeState.unavailable,
                    info_banner(
                        "La despensa no está disponible: falta aplicar la migración 018_pantry.sql.",
                        icon="triangle-alert",
                        color=theme.WARNING,
                    ),
                ),
                rx.cond(ConsumeState.already, _already_block()),

                #Ajustes del cálculo
                rx.flex(
                    rx.hstack(
                        rx.text("COMENSALES", size="1", color=theme.MUTED, weight="medium"),
                        rx.icon(
                            "minus", size=14, color=theme.MUTED, cursor="pointer",
                            on_click=ConsumeState.bump_people(-1), _hover={"color": theme.TEXT},
                        ),
                        rx.text(
                            ConsumeState.people,
                            size="2",
                            weight="bold",
                            color=theme.TEXT,
                            font_family=theme.FONT_MONO,
                            min_width="24px",
                            text_align="center",
                        ),
                        rx.icon(
                            "plus", size=14, color=theme.MUTED, cursor="pointer",
                            on_click=ConsumeState.bump_people(1), _hover={"color": theme.TEXT},
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text("BÁSICOS", size="1", color=theme.MUTED, weight="medium"),
                        rx.switch(
                            checked=ConsumeState.include_staples,
                            on_change=ConsumeState.toggle_staples,
                            color_scheme="purple",
                        ),
                        rx.text("Sal, aceite...", size="1", color=theme.DIM),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.cond(
                        ConsumeState.missing_count > 0,
                        rx.button(
                            rx.icon("shopping-cart", size=14),
                            rx.text("Comprar lo que falta", size="1"),
                            on_click=ConsumeState.buy_all_missing,
                            variant="soft",
                            color_scheme="green",
                            size="1",
                            radius="full",
                            cursor="pointer",
                        ),
                    ),
                    width="100%",
                    align="center",
                    gap="14px",
                    wrap="wrap",
                ),

                rx.cond(
                    ConsumeState.loading,
                    rx.center(rx.spinner(size="3", color=theme.PANTRY), width="100%", padding_y="2em"),
                    rx.cond(
                        ConsumeState.has_rows,
                        rx.vstack(
                            rx.foreach(ConsumeState.rows, _row),
                            spacing="2",
                            width="100%",
                            max_height="46vh",
                            overflow_y="auto",
                            overflow_x="hidden",
                        ),
                        empty_state(
                            icon="chef-hat",
                            title="Sin ingredientes que restar",
                            description=(
                                "Esa comida no tiene ingredientes guardados en el recetario. "
                                "Edítala y añádeselos para poder descontarla de la despensa."
                            ),
                            color=theme.MUTED,
                        ),
                    ),
                ),

                rx.cond(
                    ConsumeState.missing_count > 0,
                    info_banner(
                        "Lo marcado en ámbar no está en la despensa: o se te olvidó guardarlo al "
                        "comprarlo, o hay que comprarlo. No se resta nada de eso.",
                        icon="circle-alert",
                        color=theme.PANTRY,
                    ),
                ),
                rx.cond(
                    ConsumeState.short_count > 0,
                    info_banner(
                        "De algunos ingredientes hay menos de lo que pide la receta: se restará "
                        "lo que quede y la despensa se pondrá a cero.",
                        icon="triangle-alert",
                        color=theme.DANGER,
                    ),
                ),

                rx.hstack(
                    rx.text(
                        ConsumeState.to_take_count.to_string() + " ingredientes marcados",
                        size="1",
                        color=theme.DIM,
                    ),
                    rx.spacer(),
                    rx.button(
                        "Cancelar",
                        on_click=ConsumeState.close,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        type="button",
                        cursor="pointer",
                    ),
                    rx.button(
                        rx.icon("circle-minus", size=15),
                        rx.text("Restar de la despensa", size="2"),
                        on_click=ConsumeState.apply,
                        color_scheme="amber",
                        size="2",
                        type="button",
                        cursor="pointer",
                        loading=ConsumeState.applying,
                        disabled=~ConsumeState.can_apply,
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    padding_top="2",
                    wrap="wrap",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "max_width": "620px",
                "max_height": "92vh",
                "overflow_y": "auto",
                "overflow_x": "hidden",
                "background": theme.BG_WINDOW,
                "border": f"1px solid {theme.BORDER_STRONG}",
                "border_radius": theme.RADIUS_LG,
                "padding": "22px",
                "box_shadow": theme.SHADOW_LG,
            },
        ),
        open=ConsumeState.show,
    )


def consumed_badge(
    consumed, label, items, slot_label: str = "Comida", size: int = 12
) -> rx.Component:
    """El tick de "ya descontado", con la "i" que cuenta quién y qué.

    Va donde se ve el día (la cuadrícula del calendario y el editor): un tick
    solo dice que pasó algo; la "i" dice quién lo hizo, cuándo y con qué
    cantidades exactas, que es lo que se pregunta de verdad en una casa
    compartida.
    """
    return rx.cond(
        consumed,
        rx.hstack(
            rx.icon("circle-check-big", size=size, color=theme.SUCCESS, flex_shrink="0"),
            rx.popover.root(
                rx.popover.trigger(
                    rx.icon(
                        "info",
                        size=size - 1,
                        color=theme.MUTED,
                        cursor="pointer",
                        flex_shrink="0",
                        _hover={"color": theme.ACCENT},
                    )
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("warehouse", size=13, color=theme.PANTRY, flex_shrink="0"),
                            rx.text(
                                slot_label + " descontada de la despensa",
                                size="1",
                                weight="bold",
                                color=theme.TEXT,
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.text(label, size="1", color=theme.MUTED),
                        rx.cond(
                            items.length() > 0,
                            rx.vstack(
                                rx.text(
                                    "SE RESTÓ",
                                    size="1",
                                    color=theme.DIM,
                                    weight="bold",
                                    letter_spacing="0.1em",
                                    font_size="10px",
                                ),
                                rx.foreach(
                                    items,
                                    lambda linea: rx.text(linea, size="1", color=theme.TEXT),
                                ),
                                spacing="1",
                                align="start",
                                width="100%",
                                max_height="180px",
                                overflow_y="auto",
                            ),
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    side="top",
                    style={
                        "background": theme.BG_WINDOW,
                        "border": f"1px solid {theme.BORDER_STRONG}",
                        "border_radius": theme.RADIUS,
                        "padding": "12px",
                        "max_width": "260px",
                        "width": "auto",
                        "box_shadow": theme.SHADOW_LG,
                    },
                ),
            ),
            spacing="1",
            align="center",
            flex_shrink="0",
        ),
    )
