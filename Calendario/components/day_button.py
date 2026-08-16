# Calendario/components/day_button.py
"""
Celda de un día en la rejilla del mes.

La celda se adapta al ancho de la columna (`aspect-ratio: 1`) en vez de usar
medidas en `vw` como antes, que descuadraban la rejilla al cambiar de tamaño
la ventana o al abrir/cerrar la barra lateral. Al pulsarla se abre un popover
con el resumen del día y los accesos a comidas, comentarios y agenda.
"""

import reflex as rx

from Calendario import theme
from Calendario.model.model import Day
from Calendario.components.consume_dialog import consumed_badge
from Calendario.state.calendar_state import CalendarState
from Calendario.state.consume_state import ConsumeState
from Calendario.state.day_state import DayState


def _marker(color: str) -> rx.Component:
    """Puntito de color bajo el número del día."""
    return rx.box(
        width="5px",
        height="5px",
        border_radius="50%",
        background=color,
        flex_shrink="0",
    )


def _day_cell(day: rx.Var[Day]) -> rx.Component:
    is_today = day.date == CalendarState.current_date_str
    return rx.box(
        rx.vstack(
            rx.text(
                rx.moment(day.date, format="D"),
                size="2",
                weight="bold",
                color=rx.cond(is_today, "white", theme.TEXT),
                line_height="1",
            ),
            #Marcadores de lo que tiene el día
            rx.hstack(
                rx.cond(day.meal != None, _marker(rx.cond(is_today, "white", theme.MEAL))),
                rx.cond(day.dinner != None, _marker(rx.cond(is_today, "rgba(255,255,255,0.75)", theme.DINNER))),
                rx.cond(day.comments == True, _marker(rx.cond(is_today, "rgba(255,255,255,0.55)", theme.COMMENT))),
                #Tareas pendientes: en amarillo, que salta a la vista
                rx.cond(
                    day.pending_tasks > 0,
                    _marker(rx.cond(is_today, "rgba(255,255,255,0.85)", theme.OWNER)),
                ),
                #Resto de la agenda (eventos, notas, tareas ya hechas)
                rx.cond(
                    (day.agenda_total > 0) & (day.pending_tasks == 0),
                    _marker(rx.cond(is_today, "rgba(255,255,255,0.4)", theme.AGENDA)),
                ),
                #Ya descontado de la despensa: se ve sin abrir el día
                rx.cond(
                    day.meal_consumed | day.dinner_consumed,
                    _marker(rx.cond(is_today, "rgba(255,255,255,0.9)", theme.PANTRY)),
                ),
                spacing="1",
                justify="center",
                height="6px",
                align="center",
            ),
            spacing="1",
            align="center",
            justify="center",
            height="100%",
            width="100%",
        ),
        width="100%",
        aspect_ratio="1 / 1",
        min_height="38px",
        display="flex",
        align_items="center",
        justify_content="center",
        border_radius=theme.RADIUS_SM,
        cursor="pointer",
        background=rx.cond(
            is_today,
            f"linear-gradient(135deg, {theme.ACCENT}, #4F46E5)",
            theme.BG_CARD,
        ),
        border=rx.cond(is_today, "none", f"1px solid {theme.BORDER}"),
        box_shadow=rx.cond(is_today, f"0 6px 18px -6px {theme.alpha(theme.ACCENT, 0.7)}", "none"),
        backdrop_filter="blur(10px)",
        _hover={
            "transform": "translateY(-2px)",
            "border_color": theme.BORDER_STRONG,
            "background": rx.cond(
                is_today,
                f"linear-gradient(135deg, {theme.ACCENT}, #4F46E5)",
                theme.BG_CARD_HOVER,
            ),
        },
        transition="all 0.16s ease",
    )


def _comment_row(comment, day: rx.Var[Day]) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(comment.user.username, weight="bold", color=theme.COMMENT, size="1"),
            rx.spacer(),
            rx.moment(comment.created_at, format="DD/MM HH:mm", size="1", color=theme.DIM),
            rx.icon(
                "trash",
                color=theme.DANGER,
                size=13,
                style={"cursor": "pointer"},
                _hover={"transform": "scale(1.25)"},
                on_click=lambda: DayState.delete_comment(comment.id, day),
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        rx.text(comment.content, color=theme.MUTED, size="1", line_height="1.4"),
        spacing="1",
        width="100%",
        padding="7px 9px",
        border_radius="9px",
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
        align="start",
    )


def _agenda_row(item) -> rx.Component:
    """Una entrada de la agenda dentro del resumen del día."""
    return rx.hstack(
        rx.cond(
            item.completable,
            rx.icon(
                rx.cond(item.completed, "square-check", item.type_icon),
                size=13,
                color=rx.cond(item.completed, theme.AGENDA, item.type_color),
                style={"cursor": "pointer"},
                on_click=DayState.toggle_day_item(item.id),
                flex_shrink="0",
            ),
            rx.icon(item.type_icon, size=13, color=item.type_color, flex_shrink="0"),
        ),
        rx.cond(
            item.time_label != "",
            rx.text(
                item.time_label,
                size="1",
                color=theme.AGENDA,
                font_family=theme.FONT_MONO,
                white_space="nowrap",
                flex_shrink="0",
            ),
        ),
        rx.box(
            rx.text(
                item.title,
                size="1",
                color=rx.cond(item.completed, theme.DIM, theme.TEXT),
                text_decoration=rx.cond(item.completed, "line-through", "none"),
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
            ),
            flex="1 1 0",
            min_width="0",
        ),
        width="100%",
        align="center",
        spacing="2",
        padding="5px 8px",
        border_radius="8px",
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
    )


def _summary_line(
    label: str, color: str, value, day: rx.Var[Day], slot: str,
    consumed, consumed_label, consumed_items,
) -> rx.Component:
    """Comida o cena del día, con lo de la despensa a la vista.

    Aquí es donde se cierra el círculo desde el calendario: el tick dice si esos
    ingredientes ya se restaron (y la "i", quién y qué exactamente), y el botón
    permite restarlos en cualquier momento, sin esperar al aviso de la hora de
    comer. Comida y cena van por separado a propósito: se cocinan por separado.
    """
    return rx.hstack(
        rx.box(width="3px", height="26px", border_radius="2px", background=color, flex_shrink="0"),
        rx.vstack(
            rx.hstack(
                rx.text(label, size="1", color=color, weight="bold", letter_spacing="0.04em"),
                consumed_badge(consumed, consumed_label, consumed_items, label.capitalize()),
                spacing="2",
                align="center",
            ),
            rx.text(value, size="2", color=theme.TEXT, line_height="1.2"),
            spacing="0",
            align="start",
            min_width="0",
        ),
        rx.spacer(),
        rx.icon(
            rx.cond(consumed, "rotate-ccw", "circle-minus"),
            size=15,
            color=rx.cond(consumed, theme.MUTED, theme.PANTRY),
            cursor="pointer",
            flex_shrink="0",
            on_click=ConsumeState.open_for(day.id, slot),
            _hover={"color": theme.PANTRY, "transform": "scale(1.2)"},
            title="Restar de la despensa los ingredientes de este plato",
        ),
        spacing="2",
        align="center",
        width="100%",
    )


def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.popover.root(  #Iniciamos el popover
            rx.popover.trigger(_day_cell(day)),
            rx.popover.content(  #Contenido del popover, al hacer click en el día
                rx.vstack(
                    rx.hstack(  #Encabezado ( fecha más botones de acción )
                        rx.text(
                            rx.moment(day.date, format="dddd, D [de] MMMM", locale="es"),
                            size="2",
                            weight="bold",
                            color=theme.TEXT,
                            style={"text-transform": "capitalize"},
                        ),
                        rx.spacer(),
                        rx.icon(  #Icono de edición de comida/cena y agenda
                            "square-pen",
                            color=theme.MUTED,
                            size=16,
                            style={"cursor": "pointer"},
                            _hover={"color": theme.ACCENT, "transform": "scale(1.25)"},
                            on_click=DayState.set_current_day(day),
                            title="Editar comida, cena y agenda",
                        ),
                        rx.icon(  #Icono de edición para los comentarios
                            "message-square-more",
                            color=theme.MUTED,
                            size=16,
                            style={"cursor": "pointer"},
                            _hover={"color": theme.COMMENT, "transform": "scale(1.25)"},
                            on_click=DayState.toggle_comment_input,
                            title="Comentar",
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.box(height="1px", width="100%", background=theme.BORDER),

                    rx.cond(  #Info de la comida, si existe, muestra el registro
                        day.meal != None,
                        _summary_line(
                            "COMIDA", theme.MEAL, day.meal, day, "meal",
                            day.meal_consumed, day.meal_consumed_label, day.meal_consumed_items,
                        ),
                    ),
                    rx.cond(  #Info de la cena, si existe, muestra el registro
                        day.dinner != None,
                        _summary_line(
                            "CENA", theme.DINNER, day.dinner, day, "dinner",
                            day.dinner_consumed, day.dinner_consumed_label, day.dinner_consumed_items,
                        ),
                    ),
                    #Si el día está completamente vacío, invitamos a rellenarlo
                    rx.cond(
                        (day.meal == None) & (day.dinner == None),
                        rx.text("Sin comida ni cena asignadas.", size="1", color=theme.DIM),
                    ),

                    #Agenda del día: tareas, eventos y notas con su franja horaria
                    rx.cond(
                        DayState.current_day_items.length() > 0,
                        rx.vstack(
                            rx.hstack(
                                rx.icon("list-checks", size=12, color=theme.AGENDA),
                                rx.text(
                                    "AGENDA",
                                    size="1",
                                    color=theme.AGENDA,
                                    weight="bold",
                                    letter_spacing="0.04em",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.foreach(DayState.current_day_items, _agenda_row),
                                    spacing="1",
                                    width="100%",
                                ),
                                max_height="150px",
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                            align="start",
                        ),
                    ),

                    rx.cond(  #Info de los comentarios, si existen, muestra el registro
                        DayState.current_comments.length() > 0,
                        rx.vstack(
                            rx.hstack(
                                rx.icon("message-square-more", size=12, color=theme.COMMENT),
                                rx.text(
                                    "COMENTARIOS",
                                    size="1",
                                    color=theme.COMMENT,
                                    weight="bold",
                                    letter_spacing="0.04em",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.box(  #Contenedor para los comentarios
                                rx.vstack(
                                    rx.foreach(
                                        DayState.reversed_comments,  #Formatea el orden de los comentarios
                                        lambda comment: _comment_row(comment, day),
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                                max_height="170px",  #Altura máxima del contenedor de comentarios
                                overflow_y="auto",  #Activa el scroll vertical sobre los comentarios
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                            align="start",
                        ),
                    ),
                    rx.cond(  #Condición para ver el input de comentario
                        DayState.show_comment_input,
                        rx.vstack(
                        rx.hstack(  #Contenedor para el input de comentario
                            rx.input(
                                placeholder="Escribe tu comentario...",
                                value=DayState.new_comment_text,  #Lee el contenido alojado en el estado
                                on_change=DayState.set_new_comment_text,
                                size="1",
                                width="100%",
                            ),
                            rx.icon_button(  #Botón de añadir comentario
                                rx.icon("check", size=14),
                                on_click=DayState.add_comment(day),  #Activa la función que añade el comentario
                                size="1",
                                variant="soft",
                                color_scheme="green",
                                disabled=(DayState.new_comment_text.strip() == "") | DayState.sending_comment,  #Evita comentarios vacíos
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.cond(
                            DayState.comment_error != "",
                            rx.text(DayState.comment_error, size="1", color=theme.DANGER),
                        ),
                        spacing="1",
                        width="100%",
                        align="start",
                        ),
                    ),
                    spacing="3",
                    padding="2px",
                    width="270px",
                    align="start",
                ),
                style={
                    "max-width": "100vw",
                    "background": theme.BG_WINDOW,
                    "border": f"1px solid {theme.BORDER_STRONG}",
                    "border_radius": theme.RADIUS,
                    "box_shadow": theme.SHADOW_LG,
                    "backdrop_filter": "blur(16px)",
                },
                align="start",
                collision_padding=16,  #Separación con el borde de la pantalla
                avoid_collisions=True,  #Evitamos que se solapen los items
                sticky="partial",  #Mantiene el contenido visible
            ),
            on_open_change=DayState.close_comment_input,  #Cerramos el input
        ),
        width="100%",
        min_width="0",
        on_click=lambda: [
            DayState.load_day_comments(day.id),
            DayState.load_day_items(day.id),
        ],  #Carga de comentarios y agenda asociados
    )
