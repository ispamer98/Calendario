# Calendario/components/user_navbar.py

import reflex as rx
import os
from dotenv import load_dotenv
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.meal_editor import new_meal_input
from Calendario.state.day_state import DayState
from Calendario.state.user_state import UserState
from Calendario.state.calendar_state import CalendarState
from Calendario.state.notification_state import NotificationState

load_dotenv()
VAPID_PUBLIC = os.getenv("VAPID_PUBLIC_KEY", "")

class DrawerState(rx.State):
    is_open: bool = False
    show_profile_submenu: bool = False
    show_calendar_submenu: bool = False
    show_meal_submenu : bool = False
    show_list_submenu : bool = False   # NUEVO

    @rx.event
    def open_drawer(self):
        self.is_open = True

    @rx.event
    def close_drawer(self):
        self.is_open = False
        self.show_profile_submenu = False
        self.show_calendar_submenu = False
        self.show_meal_submenu = False
        self.show_list_submenu = False   # NUEVO

    @rx.event
    def toggle_profile_submenu(self):
        self.show_profile_submenu = not self.show_profile_submenu

    @rx.event
    def toggle_calendar_submenu(self):
        self.show_calendar_submenu = not self.show_calendar_submenu

    @rx.event
    def toggle_meal_submenu(self):
        self.show_meal_submenu = not self.show_meal_submenu

    @rx.event
    def toggle_list_submenu(self):       # NUEVO
        self.show_list_submenu = not self.show_list_submenu

def drawer_menu():
    NAVBAR_HEIGHT = "68px"

    return rx.drawer.root(
        rx.drawer.trigger(),
        rx.drawer.overlay(
            background="rgba(0, 0, 0, 0.6)",
            style={"top": NAVBAR_HEIGHT},
            on_click=DrawerState.close_drawer,
        ),
        rx.drawer.portal(
            rx.drawer.content(
                rx.flex(
                    rx.drawer.close(
                        rx.button(
                            "×",
                            on_click=DrawerState.close_drawer,
                            variant="ghost",
                            font_size="2.5em",
                            font_weight="bold",
                            color="white",
                            position="absolute",
                            top="20px",
                            right="20px",
                            padding="0",
                            width="auto",
                            height="auto",
                            min_width="auto",
                            background="transparent",
                            _hover={
                                "color": "#F54444",
                                "transform": "scale(1.5)",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                            },
                            _focus={"boxShadow": "none"},
                        ),
                    ),
                    # Submenu de calendario
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("calendar"),
                                rx.text("Calendario"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            margin_top="4em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            on_click=DrawerState.toggle_calendar_submenu,
                        ),
                        rx.cond(
                            DrawerState.show_calendar_submenu,
                            rx.vstack(
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Visualizar calendario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, UserState.go_calendar_page],
                                ),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Crear Calendario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, CalendarState.open_calendar_creator],
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),
                    # Submenu de perfil
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("settings"),
                                rx.text("Perfil"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            on_click=DrawerState.toggle_profile_submenu,
                        ),
                        rx.cond(
                            DrawerState.show_profile_submenu,
                            rx.vstack(
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Datos de usuario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, UserState.go_profile_page],
                                ),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Seguridad",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, UserState.go_security_page],
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),
                    # Submenu de comidas
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("utensils"),
                                rx.text("Comidas"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            on_click=DrawerState.toggle_meal_submenu,
                        ),
                        rx.cond(
                            DrawerState.show_meal_submenu,
                            rx.vstack(
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Añadir comida",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, DayState.open_new_meal_input ],
                                ),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Lista de comidas",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, UserState.go_meal_list],
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),
                    # ========== NUEVO SUBMENÚ: LISTA DE COMPRA ==========
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("shopping-cart"),   # icono de carrito
                                rx.text("Lista de compra"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            on_click=DrawerState.toggle_list_submenu,
                        ),
                        rx.cond(
                            DrawerState.show_list_submenu,
                            rx.vstack(
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button(
                                    rx.icon("arrow-big-right"),
                                    "Ver mi lista",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    on_click=[DrawerState.close_drawer, UserState.go_shopping_list],
                                ),
                                # Si quieres añadir más opciones como "Compartir lista" o "Historial", puedes agregarlas aquí
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),
                    direction="column",
                    align_items="start",
                    gap="1.5em",
                    height="100%",
                    padding_x="2em",
                ),
                height=f"calc(100vh - {NAVBAR_HEIGHT})",
                width="18em",
                background_color="#1e1e1e",
                box_shadow="rgba(0, 0, 0, 0.8) 0px 4px 20px",
                border_radius="0 20px 20px 0",
                position="fixed",
                top=NAVBAR_HEIGHT,
                left="0",
                z_index="1200",
            )
        ),
        open=DrawerState.is_open,
        placement="left",
        modal=True,
    )

def user_navbar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                drawer_menu(),
                # Logo
                rx.heading(
                    rx.hstack(
                        rx.image(src="/favicon.ico", width="43px", height="33px"),
                        rx.text("CalendPy", font_family="Sarina,cursive", font_size="1.5em"),
                    ),
                    background_image="linear-gradient(45deg, #4F46E5, #EC4899)",
                    background_clip="text",
                    font_weight="800",
                    font_size="1em",
                    user_select="none",
                    on_click=DrawerState.open_drawer,
                    _hover={"transform": "scale(1.05)", "cursor": "pointer"},
                ),
                rx.spacer(),
                calendar_creator(),
                new_meal_input(),
                # 🔔 Botón campana
                rx.button(
                    rx.icon("bell", size=20),
                    on_click=rx.call_script(
                        f"""
                        (async function() {{
                            try {{
                                let alias = window.prompt("Nombre para este dispositivo (ej: Mi iPhone, PC Casa):", "");
                                if (alias === null) return "USER_CANCEL";
                                alias = alias.trim();
                                if (alias === "") {{ alert("El alias no puede estar vacío."); return "USER_CANCEL"; }}
                                let reg;
                                for (let i = 0; i < 3; i++) {{
                                    try {{
                                        reg = await navigator.serviceWorker.register('/service-worker.js');
                                        await navigator.serviceWorker.ready;
                                        break;
                                    }} catch (e) {{ await new Promise(r => setTimeout(r, 500)); }}
                                }}
                                if (!reg) throw new Error("No se pudo registrar SW");
                                const perm = await Notification.requestPermission();
                                if (perm !== 'granted') return "PERMISO_DENEGADO";
                                const publicKey = '{VAPID_PUBLIC}';
                                const toUint8 = (b) => {{
                                    const pad = '='.repeat((4 - b.length % 4) % 4);
                                    const b64 = (b + pad).replace(/-/g, '+').replace(/_/g, '/');
                                    const raw = window.atob(b64);
                                    const out = new Uint8Array(raw.length);
                                    for (let i = 0; i < raw.length; ++i) out[i] = raw.charCodeAt(i);
                                    return out;
                                }};
                                const sub = await reg.pushManager.subscribe({{
                                    userVisibleOnly: true,
                                    applicationServerKey: toUint8(publicKey)
                                }});
                                return JSON.stringify({{ subscription: sub, alias: alias }});
                            }} catch (err) {{
                                if (err.name === "NotAllowedError") return "PERMISO_BLOQUEADO";
                                return "ERROR_" + err.message;
                            }}
                        }})();
                        """,
                        callback=NotificationState.guardar_subscripcion
                    ),
                    variant="ghost",
                    size="3",
                    _hover={"transform": "scale(1.1)", "cursor": "pointer"},
                ),
                # Menú de usuario (desplegable)
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.hstack(
                                rx.spacer(" "),
                                rx.icon("user"),
                                rx.cond(
                                    UserState.current_user,
                                    rx.text(UserState.current_user.username),
                                    rx.text("Usuario")
                                ),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                            ),
                            variant="ghost",
                            radius="full",
                            background="#23282b",
                            style={
                                "background": "transparent",
                                "color": "white",
                                "border": "1px solid rgba(255, 255, 255, 0.3)",
                                "_hover": {
                                    "background": "rgba(0, 0, 0, 0.2)",
                                    "cursor": "pointer",
                                    "transform": "scale(1.05)"
                                }
                            }
                        )
                    ),
                    rx.menu.content(
                        rx.menu.item("Perfil", rx.icon("settings"),
                                     on_click=rx.redirect("/profile")),
                        rx.menu.separator(),
                        rx.menu.item("Cerrar sesión", rx.icon("log-out"),
                                     on_click=UserState.logout,
                                     color="#EF4444"),
                        width="200px",
                    ),
                    modal=False
                ),
                justify="between",
                align="center",
                width="100%",
                padding_y="1em",
                padding_x="2em",
                style={"box-sizing": "border-box"}
            ),
            width="100%",
            max_width="100vw",
            style={"overflow-x": "hidden"}
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="1000",
        border_bottom="1.5px solid #eee",
        border_radius="0 0 20px 20px",
        background="#1e1e1e"
    )