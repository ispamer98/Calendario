# Calendario/pages/menu_semanal.py
"""
Planificador del menú semanal.

La pantalla pensada para el ritual del sábado: rellenar la semana entre dos y
sacar la lista de la compra de golpe.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.calendar_sharer import calendar_sharer
from Calendario.components.calendar_switcher import calendar_switcher
from Calendario.components.ui import (
    collapsible,
    empty_state,
    info_banner,
    page_header,
    pill,
    progress_bar,
    stat_card,
    stats_grid,
    tip,
)
from Calendario.components.week_planner import generator_dialog, week_grid
from Calendario.state.calendar_state import CalendarState
from Calendario.state.menu_state import MenuState
from Calendario.state.units_state import UnitsState
from Calendario.state.user_state import UserState


def _week_nav() -> rx.Component:
    """Flechas de semana + botón para volver a la semana en curso."""
    return rx.hstack(
        rx.icon_button(
            rx.icon("chevron-left", size=16),
            on_click=MenuState.previous_week,
            variant="soft",
            color_scheme="gray",
            size="2",
            cursor="pointer",
        ),
        rx.vstack(
            rx.text(MenuState.week_label, size="2", weight="bold", color=theme.TEXT, white_space="nowrap"),
            rx.text(
                MenuState.week_subtitle + " · " + MenuState.week_year,
                size="1",
                color=theme.MUTED,
                white_space="nowrap",
            ),
            spacing="0",
            align="center",
            min_width="150px",
        ),
        rx.icon_button(
            rx.icon("chevron-right", size=16),
            on_click=MenuState.next_week,
            variant="soft",
            color_scheme="gray",
            size="2",
            cursor="pointer",
        ),
        rx.cond(
            ~MenuState.is_current_week,
            rx.button(
                rx.icon("undo-2", size=14),
                rx.text("Hoy", size="1"),
                on_click=MenuState.this_week,
                variant="soft",
                color_scheme="blue",
                size="1",
                cursor="pointer",
                radius="full",
            ),
        ),
        spacing="2",
        align="center",
        #En móvil ocupa su propia fila completa, con las flechas a los extremos
        width=rx.breakpoints(initial="100%", md="auto"),
        justify=rx.breakpoints(initial="between", md="start"),
        padding=rx.breakpoints(initial="8px 10px", md="0"),
        border_radius=theme.RADIUS_SM,
        background=rx.breakpoints(initial=theme.BG_SUNKEN, md="transparent"),
        border=rx.breakpoints(initial=f"1px solid {theme.BORDER}", md="1px solid transparent"),
    )


def _progress_strip() -> rx.Component:
    return rx.vstack(
        #El menú vive dentro del calendario del mes: dejarlo claro evita la duda
        #de "¿esto lo ve mi chica o no?"
        rx.hstack(
            rx.icon("calendar-days", size=13, color=theme.DIM),
            rx.text("Se guarda en", size="1", color=theme.DIM),
            rx.text(CalendarState.current_calendar_name, size="1", color=theme.TEXT, weight="medium"),
            rx.cond(
                CalendarState.current_is_shared,
                #Bocadillo con el calendario y quién tiene acceso
                rx.popover.root(
                    rx.popover.trigger(
                        rx.box(
                            pill(
                                "Compartido con "
                                + (CalendarState.current_shared_count - 1).to_string()
                                + " más",
                                theme.PURPLE,
                                "users",
                            ),
                            cursor="pointer",
                            on_click=CalendarState.load_shared_users,
                        )
                    ),
                    rx.popover.content(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("calendar-days", size=13, color=theme.ACCENT),
                                rx.text(
                                    CalendarState.current_calendar_name,
                                    size="2",
                                    weight="bold",
                                    color=theme.TEXT,
                                ),
                                spacing="2",
                                align="center",
                            ),
                            rx.text(
                                CalendarState.calendar_title,
                                size="1",
                                color=theme.DIM,
                            ),
                            rx.box(height="1px", width="100%", background=theme.BORDER),
                            rx.text(
                                "CON ACCESO",
                                size="1",
                                color=theme.DIM,
                                weight="bold",
                                letter_spacing="0.1em",
                            ),
                            rx.hstack(
                                rx.icon("crown", size=13, color=theme.OWNER),
                                rx.text(
                                    CalendarState.owner_username,
                                    size="2",
                                    color=theme.TEXT,
                                    weight="medium",
                                ),
                                rx.text("propietario", size="1", color=theme.DIM),
                                spacing="2",
                                align="center",
                            ),
                            rx.foreach(
                                CalendarState.shared_users,
                                lambda u: rx.hstack(
                                    rx.icon("user", size=13, color=theme.PURPLE),
                                    rx.text(u.username, size="2", color=theme.TEXT),
                                    spacing="2",
                                    align="center",
                                ),
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        side="bottom",
                        style={
                            "background": theme.BG_WINDOW,
                            "border": f"1px solid {theme.BORDER_STRONG}",
                            "border_radius": theme.RADIUS,
                            "padding": "14px",
                            "width": "250px",
                            "box_shadow": theme.SHADOW_LG,
                        },
                    ),
                ),
                pill("Solo tú", theme.MUTED, "lock"),
            ),
            width="100%",
            align="center",
            spacing="2",
            wrap="wrap",
        ),
        rx.hstack(
            rx.text("Semana planificada", size="1", color=theme.MUTED),
            rx.spacer(),
            rx.text(
                MenuState.filled_slots.to_string() + " / " + MenuState.total_slots.to_string() + " platos",
                size="1",
                color=theme.TEXT,
                weight="bold",
                font_family=theme.FONT_MONO,
            ),
            width="100%",
            align="center",
        ),
        progress_bar(MenuState.week_percent, theme.MEAL),
        spacing="2",
        width="100%",
    )


def _toolbar() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("dices", size=15),
            rx.text("Sorpréndeme", size="2"),
            on_click=MenuState.surprise_me,
            variant="soft",
            color_scheme="purple",
            size="2",
            cursor="pointer",
            radius="full",
        ),
        rx.button(
            rx.icon("copy", size=15),
            rx.text("Copiar semana anterior", size="2"),
            on_click=MenuState.copy_previous_week,
            variant="soft",
            color_scheme="gray",
            size="2",
            cursor="pointer",
            radius="full",
        ),
        #Vaciar la semana borra trabajo hecho: pide confirmación
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.icon("eraser", size=15),
                    rx.text("Vaciar", size="2"),
                    variant="soft",
                    color_scheme="red",
                    size="2",
                    cursor="pointer",
                    radius="full",
                )
            ),
            rx.dialog.content(
                rx.dialog.title("Vaciar la semana"),
                rx.dialog.description(
                    "Se quitarán todas las comidas y cenas de los siete días. Los platos del recetario no se tocan.",
                    size="2",
                    color=theme.MUTED,
                ),
                rx.flex(
                    rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                    rx.dialog.close(
                        rx.button("Vaciar semana", color_scheme="red", on_click=MenuState.clear_week)
                    ),
                    spacing="3",
                    margin_top="1.5em",
                    justify="end",
                ),
                style={
                    "max_width": "420px",
                    "background": theme.BG_WINDOW,
                    "border": f"1px solid {theme.BORDER_STRONG}",
                    "border_radius": theme.RADIUS_LG,
                    "padding": "22px",
                },
            ),
        ),
        #Compartir el menú = compartir el calendario, y eso solo el dueño
        rx.cond(CalendarState.can_share, calendar_sharer()),
        rx.spacer(),
        rx.button(
            rx.icon("shopping-cart", size=16),
            rx.text("Generar lista de la compra", size="2", weight="medium"),
            on_click=MenuState.open_generator,
            color_scheme="green",
            size="3",
            cursor="pointer",
            radius="full",
            disabled=MenuState.is_week_empty,
        ),
        width="100%",
        align="center",
        spacing="2",
        wrap="wrap",
    )


@rx.page(
    route="/menu_semanal",
    title="Menú semanal | CalendPy",
    on_load=[
        UserState.on_load,
        UserState.check_autenticated,
        CalendarState.load_meals,
        CalendarState.load_calendars,
        CalendarState.auto_select_calendar,
        CalendarState.load_shared_users,
        MenuState.load_week,
        UnitsState.load_units,
        CalendarState.load_categories,
    ],
)
def menu_semanal() -> rx.Component:
    return app_shell(
        generator_dialog(),
        rx.vstack(
            page_header(
                icon="clipboard-list",
                title="Menú semanal",
                subtitle="Rellena la semana y saca la compra de una sentada",
                accent=theme.ACCENT,
                actions=[_week_nav()],
                extra=_progress_strip(),
            ),

            #El selector de calendario también aquí, para móviles donde la
            #barra superior no lo muestra
            rx.box(
                calendar_switcher(compact=False),
                display=["flex !important", "none !important", "none !important"],
                width="100%",
            ),

            stats_grid(
                stat_card(
                    icon="utensils-crossed",
                    label="Platos planificados",
                    value=MenuState.filled_slots,
                    color=theme.MEAL,
                ),
                stat_card(
                    icon="circle-dashed",
                    label="Huecos por llenar",
                    value=MenuState.empty_slots,
                    color=theme.WARNING,
                ),
                stat_card(
                    icon="percent",
                    label="Completada",
                    value=MenuState.week_percent.to_string() + "%",
                    color=theme.ACCENT,
                ),
                stat_card(
                    icon="book-open",
                    label="Platos disponibles",
                    value=CalendarState.meals.length(),
                    hint="En tu recetario",
                    color=theme.PURPLE,
                ),
            ),

            _toolbar(),

            #Aviso si la semana pisa un mes sin calendario creado
            rx.cond(
                MenuState.has_missing_days,
                info_banner(
                    "No hay calendario para estos días: " + MenuState.missing_label
                    + ". Crea el calendario de ese mes para poder planificarlos.",
                    icon="triangle-alert",
                    color=theme.WARNING,
                ),
            ),

            rx.cond(
                MenuState.loading,
                rx.center(rx.spinner(size="3", color=theme.ACCENT), width="100%", padding_y="4em"),
                rx.cond(
                    MenuState.week_days.length() > 0,
                    week_grid(),
                    empty_state(
                        icon="calendar-x",
                        title="Esta semana no tiene calendario",
                        description="El menú semanal se apoya en los días del calendario del mes. Crea el calendario del mes correspondiente y vuelve aquí.",
                        action=rx.button(
                            rx.icon("calendar-plus", size=15),
                            "Crear calendario",
                            on_click=CalendarState.open_calendar_creator,
                            color_scheme="blue",
                            size="3",
                            cursor="pointer",
                        ),
                        color=theme.WARNING,
                    ),
                ),
            ),

            #Explicación del flujo, plegada para no ocupar media pantalla
            collapsible(
                rx.grid(
                tip(
                    "calendar-check",
                    "1 · Rellena la semana",
                    "Elige comida y cena de cada día. Se guarda solo, y aparece igual en el calendario del mes.",
                    theme.ACCENT,
                ),
                tip(
                    "carrot",
                    "2 · Se suman los ingredientes",
                    "Cada plato aporta los suyos y se agrupan por producto: 200 g de arroz aquí y 160 allí son 360 g.",
                    theme.MEAL,
                ),
                tip(
                    "shopping-cart",
                    "3 · A la lista de la compra",
                    "Ordenada por secciones del súper, con cantidades. Allí puedes editar, tachar y borrar lo que quieras.",
                    theme.PURPLE,
                ),
                    columns=rx.breakpoints(initial="1", md="3"),
                    spacing="3",
                    width="100%",
                ),
                title="CÓMO FUNCIONA EL MENÚ SEMANAL",
                icon="circle-help",
                color=theme.ACCENT,
            ),

            spacing="5",
            width="100%",
            max_width="1400px",
            margin="0 auto",
            align="center",
        ),
    )
