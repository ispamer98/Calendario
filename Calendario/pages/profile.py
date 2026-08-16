# Calendario/pages/profile.py

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.topbar import subscribe_device_button
from Calendario.components.ui import (
    icon_badge,
    info_banner,
    page_header,
    panel,
    pill,
    stat_card,
    stats_grid,
)
from Calendario.state.calendar_state import CalendarState
from Calendario.state.notification_state import NotificationState
from Calendario.state.user_state import UserState


#Controlador de rotación del icono
class IconState(rx.State):
    rotating: bool = False

    @rx.event
    def start_rotate(self):
        self.rotating = True


def _info_row(icon: str, label: str, value) -> rx.Component:
    return rx.hstack(
        icon_badge(icon, theme.MUTED, size=15, box="34px"),
        rx.vstack(
            rx.text(label, size="1", color=theme.DIM, letter_spacing="0.04em"),
            rx.text(value, size="2", color=theme.TEXT, weight="medium"),
            spacing="0",
            align="start",
            min_width="0",
        ),
        spacing="3",
        align="center",
        width="100%",
        padding="10px 12px",
        border_radius=theme.RADIUS_SM,
        background=theme.BG_SUNKEN,
        border=f"1px solid {theme.BORDER}",
    )


def _account_card() -> rx.Component:
    return panel(
        rx.vstack(
            rx.hstack(
                rx.center(
                    rx.icon(
                        "circle-user",
                        size=34,
                        color=theme.ACCENT,
                        style={
                            "transition": "transform 2s cubic-bezier(0.4, 0.2, 0.2, 1)",
                            "transform": rx.cond(IconState.rotating, "rotateY(360deg)", "none"),
                        },
                    ),
                    min_width="64px",
                    height="64px",
                    border_radius="50%",
                    background=theme.alpha(theme.ACCENT, 0.12),
                    border=f"1px solid {theme.alpha(theme.ACCENT, 0.28)}",
                    on_mount=IconState.start_rotate,
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.text(
                        UserState.current_user.username,
                        size="5",
                        weight="bold",
                        color=theme.TEXT,
                        style={"textTransform": "capitalize"},
                    ),
                    pill("Cuenta activa", theme.SUCCESS, "circle-check"),
                    spacing="2",
                    align="start",
                    min_width="0",
                ),
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            _info_row("user", "NOMBRE DE USUARIO", UserState.current_user.username),
            _info_row("mail", "CORREO ELECTRÓNICO", UserState.masked_email),
            _info_row(
                "calendar",
                "REGISTRADO DESDE",
                rx.moment(
                    UserState.current_user.created_at,
                    format="MMMM [de] YYYY",
                    locale="es",
                    style={"textTransform": "capitalize"},
                ),
            ),
            spacing="3",
            width="100%",
            align="start",
        ),
    )


#Ajustes de los avisos de despensa: si se quieren y a qué hora
def meal_stock_card() -> rx.Component:
    """Cuándo avisar de que toca descontar lo cocinado.

    Las horas son de cada uno: en esta casa se come a las tres y se cena a las
    once, pero eso no es una ley universal.
    """
    return panel(
        rx.vstack(
            rx.hstack(
                icon_badge("warehouse", theme.PANTRY, size=17, box="38px"),
                rx.vstack(
                    rx.text("Avisos de despensa", size="3", weight="bold", color=theme.TEXT),
                    rx.text(
                        "Te recordamos descontar lo que cocinas",
                        size="1",
                        color=theme.MUTED,
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.switch(
                    checked=NotificationState.meal_stock_enabled,
                    on_change=NotificationState.toggle_meal_stock,
                    color_scheme="amber",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            rx.cond(
                NotificationState.meal_stock_enabled,
                rx.vstack(
                    rx.flex(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("sun", size=13, color=theme.MEAL),
                                rx.text("COMIDA", size="1", color=theme.MUTED, weight="medium"),
                                spacing="2",
                                align="center",
                            ),
                            rx.input(
                                value=NotificationState.meal_time,
                                on_change=NotificationState.set_meal_time,
                                type="time",
                                size="2",
                                width="100%",
                            ),
                            spacing="1",
                            align="start",
                            flex="1 1 140px",
                            min_width="140px",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("moon", size=13, color=theme.DINNER),
                                rx.text("CENA", size="1", color=theme.MUTED, weight="medium"),
                                spacing="2",
                                align="center",
                            ),
                            rx.input(
                                value=NotificationState.dinner_time,
                                on_change=NotificationState.set_dinner_time,
                                type="time",
                                size="2",
                                width="100%",
                            ),
                            spacing="1",
                            align="start",
                            flex="1 1 140px",
                            min_width="140px",
                        ),
                        width="100%",
                        gap="12px",
                        wrap="wrap",
                    ),
                    info_banner(
                        "A esa hora, si el día tiene comida puesta y no se ha descontado ya, "
                        "llega un aviso que abre directamente la ventana para restar los "
                        "ingredientes de la despensa.",
                        icon="info",
                        color=theme.PANTRY,
                    ),
                    spacing="3",
                    width="100%",
                ),
                info_banner(
                    "No recibirás avisos para descontar lo que cocinas. Puedes restarlo cuando "
                    "quieras desde el calendario o desde la despensa.",
                    icon="bell-off",
                    color=theme.MUTED,
                ),
            ),
            spacing="3",
            width="100%",
            align="start",
        ),
    )


#Tarjeta de gestión de dispositivos suscritos a notificaciones push
def devices_card() -> rx.Component:
    return panel(
        rx.vstack(
            rx.hstack(
                icon_badge("bell", theme.COMMENT, size=17, box="38px"),
                rx.vstack(
                    rx.text("Notificaciones", size="3", weight="bold", color=theme.TEXT),
                    rx.text(
                        "Dispositivos que reciben avisos de esta cuenta",
                        size="1",
                        color=theme.MUTED,
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.icon(
                    "refresh-ccw",
                    size=15,
                    color=theme.MUTED,
                    cursor="pointer",
                    on_click=NotificationState.load_my_devices,
                    _hover={"color": theme.ACCENT},
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            #Antes esto estaba en una campana perdida en la barra superior
            subscribe_device_button(),
            rx.cond(
                NotificationState.my_devices.length() > 0,
                rx.vstack(
                    rx.foreach(
                        NotificationState.my_devices,
                        lambda device: rx.hstack(
                            rx.icon("smartphone", size=15, color=theme.ACCENT, flex_shrink="0"),
                            rx.text(device["alias"], size="2", color=theme.TEXT),
                            rx.spacer(),
                            rx.icon_button(
                                rx.icon("trash-2", size=14),
                                size="1",
                                variant="soft",
                                color_scheme="red",
                                on_click=NotificationState.delete_device(device["id"]),
                            ),
                            width="100%",
                            align="center",
                            spacing="3",
                            padding="9px 12px",
                            border_radius=theme.RADIUS_SM,
                            background=theme.BG_SUNKEN,
                            border=f"1px solid {theme.BORDER}",
                        ),
                    ),
                    width="100%",
                    spacing="2",
                ),
                rx.vstack(
                    rx.center(
                        rx.icon("bell-off", size=20, color=theme.DIM),
                        width="46px",
                        height="46px",
                        border_radius="50%",
                        background=theme.BG_SUNKEN,
                        border=f"1px solid {theme.BORDER}",
                    ),
                    rx.text("Ningún dispositivo suscrito", size="2", color=theme.MUTED),
                    rx.text(
                        "Pulsa «Activar en este dispositivo» en cada móvil u ordenador "
                        "y dale un nombre para reconocerlo aquí.",
                        size="1",
                        color=theme.DIM,
                        text_align="center",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    padding_y="1.5em",
                ),
            ),
            spacing="3",
            width="100%",
            align="start",
        ),
    )


def _shortcuts_card() -> rx.Component:
    """Accesos rápidos: antes esta columna quedaba en blanco."""
    links = [
        ("/calendar", "calendar-days", "Calendario", "Tu mes de un vistazo", theme.ACCENT),
        ("/menu_semanal", "clipboard-list", "Menú semanal", "Planifica y genera la compra", theme.PURPLE),
        ("/meal_list", "chef-hat", "Recetario", "Tus platos e ingredientes", theme.MEAL),
        ("/security", "shield", "Seguridad", "Cambiar la contraseña", theme.WARNING),
    ]
    return panel(
        rx.vstack(
            rx.text("ACCESOS RÁPIDOS", size="1", color=theme.DIM, weight="bold", letter_spacing="0.12em"),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            *[
                rx.link(
                    rx.hstack(
                        icon_badge(icon, color, size=15, box="34px"),
                        rx.vstack(
                            rx.text(title, size="2", weight="medium", color=theme.TEXT),
                            rx.text(subtitle, size="1", color=theme.MUTED),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.icon("chevron-right", size=15, color=theme.DIM),
                        width="100%",
                        align="center",
                        spacing="3",
                        padding="9px 10px",
                        border_radius=theme.RADIUS_SM,
                        _hover={"background": theme.BG_CARD_HOVER},
                        transition="background 0.15s ease",
                    ),
                    href=href,
                    underline="none",
                    width="100%",
                )
                for href, icon, title, subtitle, color in links
            ],
            spacing="2",
            width="100%",
            align="start",
        ),
    )


#Página de información del usuario
@rx.page(  #Decorador indicando complemento de página
    route="/profile",
    title="Perfil | CalendPy",
    on_load=[  #Funciones al cargar la página
        UserState.on_load,
        UserState.check_autenticated,
        IconState.start_rotate,
        NotificationState.load_my_devices,
        NotificationState.load_meal_settings,
        CalendarState.load_calendars,
        CalendarState.load_meals,
    ],
)
def profile() -> rx.Component:
    return app_shell(
        rx.vstack(
            page_header(
                icon="circle-user",
                title="Tu perfil",
                subtitle="Datos de la cuenta, dispositivos y accesos rápidos",
                accent=theme.ACCENT,
            ),
            stats_grid(
                stat_card(
                    icon="calendar-days",
                    label="Calendarios",
                    value=CalendarState.calendars.length(),
                    hint="Propios y compartidos",
                    color=theme.ACCENT,
                ),
                stat_card(
                    icon="chef-hat",
                    label="Platos disponibles",
                    value=CalendarState.meals.length(),
                    color=theme.MEAL,
                ),
                stat_card(
                    icon="bell",
                    label="Dispositivos",
                    value=NotificationState.my_devices.length(),
                    hint="Con notificaciones",
                    color=theme.COMMENT,
                ),
                stat_card(
                    icon="list-checks",
                    label="Tareas de hoy",
                    value=UserState.today_pending_tasks,
                    hint="Pendientes",
                    color=theme.AGENDA,
                ),
            ),
            rx.flex(
                rx.box(
                    rx.vstack(
                        _account_card(), devices_card(), meal_stock_card(),
                        spacing="4", width="100%",
                    ),
                    flex="1 1 420px",
                    min_width="0",
                ),
                rx.box(_shortcuts_card(), flex="0 1 320px", min_width="270px"),
                width="100%",
                gap="18px",
                wrap="wrap",
                align="start",
            ),
            spacing="5",
            width="100%",
            max_width="1100px",
            margin="0 auto",
            align="center",
        ),
    )
