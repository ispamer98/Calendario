# File: Calendario/pages/calendar.py

import reflex as rx
from Calendario.components.footer import footer
from Calendario.components.meal_editor import meal_editor
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.user_calendar import user_calendar
from Calendario.state.calendar_state import CalendarState
from Calendario.components.user_navbar import user_navbar
from Calendario.state.user_state import UserState
from Calendario.components.today_box import today_box


@rx.page(
    route="/calendar",
    title="Calendario | CalendPy",
    on_load=[
        CalendarState.reset_calendars,
        CalendarState.clean,
        UserState.on_load,
        CalendarState.load_meals,
        UserState.check_autenticated,
        CalendarState.update_current_date,
        UserState.today_info  # Nueva línea para cargar datos iniciales
    ],
)
def calendar() -> rx.Component:
    return rx.vstack(
        # ─── Navbar superior y editor de comidas ───
        user_navbar(),
        meal_editor(),

        # ─── Contenedor principal ───
        rx.container(
            rx.cond(
                # 1) Usuario autenticado
                UserState.current_user,

                # 2) Tienes calendarios creados
                rx.cond(
                    CalendarState.calendars.length() > 0,

                    # 3) Hay un calendario seleccionado
                    rx.cond(
                        CalendarState.current_calendar,

                        # ── Layout cuando hay calendario seleccionado ──
                        rx.fragment(
                            # 🖥️ Desktop: calendario + today_box a la derecha
                            rx.tablet_and_desktop(
                                rx.hstack(
                                    user_calendar(),
                                    rx.cond(
                                        UserState.today_data.length() > 0,
                                        rx.box(
                                            today_box(),
                                            margin_left="5em",   # Ajusta para separar más a la derecha
                                            margin_top="2em",    # Ajusta para más espacio arriba
                                        )
                                    ),
                                    spacing="4",
                                    align_items="flex-start",
                                )
                            ),
                            # 📱 Móvil: calendario  + botones (ya dentro de user_calendar) y luego today_box debajo
                            rx.mobile_only(
                                rx.vstack(
                                    rx.box(
                                        user_calendar(),
                                        margin_left="-1em",  # O ajusta el valor según lo que necesites
                                        margin_rigth="1em"
                                    ),
                                    rx.box(
                                        rx.divider(),
                                        width="100%",  # asegura que ocupe todo el ancho
                                        margin_bottom="1em"
                                    ),
                                    rx.cond(
                                        UserState.today_data.length() > 0,
                                        today_box()
                                    ),
                                    align_items="flex-start",
                                    spacing="2",
                                )
                            ),
                        ),

                        # ── Ningún calendario aún seleccionado ──
                        rx.vstack(
                            user_calendar(),
                            rx.cond(
                                UserState.today_data.length() > 0,
                                today_box()
                            ),
                            spacing="1",
                            align="center"
                        ),
                    ),

                    # ❌ No tienes calendarios
                    rx.vstack(
                        rx.text("No tienes ningún calendario", color="gray.600"),
                        rx.button(
                            "Crear Calendario",
                            on_click=CalendarState.open_calendar_creator
                        ),
                        align_items="center",
                        spacing="1"
                    ),
                ),

                # 🔄 Cargando usuario o datos
                rx.vstack(
                    rx.box(
                        style={
                            "border": "8px solid #f3f3f3",
                            "borderTop": "8px solid #3182ce",
                            "borderRadius": "50%",
                            "width": "60px",
                            "height": "60px",
                        },
                    ),
                    rx.text("Cargando...", margin_top="1em"),
                    align_items="center",
                    spacing="1"
                ),
            ),
            width="100%",
            max_width="1200px",
            padding_top="6em",
            align="center",
        ),
        width="100%",
        spacing="0",
        align_items="center",
        style={"overflow-x": "hidden"},
        height="100vh",
    )
