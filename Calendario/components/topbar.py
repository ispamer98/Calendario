# Calendario/components/topbar.py

import reflex as rx
import os
from dotenv import load_dotenv

from Calendario import theme
from Calendario.components.calendar_switcher import calendar_switcher
from Calendario.state.nav_state import NavState
from Calendario.state.user_state import UserState
from Calendario.state.notification_state import NotificationState

load_dotenv()
VAPID_PUBLIC = os.getenv("VAPID_PUBLIC_KEY", "")

VIEW_TITLES = {
    "/calendar": ("Calendario", "calendar-days"),
    "/menu_semanal": ("Menú semanal", "clipboard-list"),
    "/meal_list": ("Comidas", "utensils"),
    "/shopping_list": ("Lista de la compra", "shopping-cart"),
    "/amigos": ("Amigos", "users"),
    "/profile": ("Perfil", "user"),
    "/security": ("Seguridad", "shield"),
}

#Páginas en las que tiene sentido cambiar de calendario desde la barra superior
CALENDAR_ROUTES = ("/calendar", "/menu_semanal")


def _view_title() -> rx.Component:
    return rx.box(
        rx.match(
            NavState.active_route,
            *[
                (route, rx.hstack(
                    rx.icon(icon, size=18, color=theme.MUTED),
                    rx.text(title, size=rx.breakpoints(initial="3", md="4"), weight="bold", color=theme.TEXT, white_space="nowrap"),
                    spacing="2",
                    align="center",
                ))
                for route, (title, icon) in VIEW_TITLES.items()
            ],
            rx.text("CalendPy", size=rx.breakpoints(initial="3", md="4"), weight="bold", color=theme.TEXT),
        ),
        min_width="0",
        overflow="hidden",
        flex="1",
    )


def subscribe_device_button() -> rx.Component:
    """Suscribe ESTE dispositivo a las notificaciones push.

    Vivía como campana suelta en la barra superior; ahora está donde tiene
    sentido: junto a la lista de dispositivos, en el perfil.
    """
    return rx.box(
        rx.hstack(
            rx.icon("bell-plus", size=15, color=theme.COMMENT),
            rx.text("Activar en este dispositivo", size="2", color=theme.COMMENT, weight="medium"),
            spacing="2",
            align="center",
        ),
        on_click=rx.call_script(
            f"""
            (async function() {{
                try {{
                    let alias = window.prompt("Nombre para este dispositivo (ej: Mi iPhone, PC Casa):", "");
                    if (alias === null) return "USER_CANCEL";
                    alias = alias.trim();
                    if (alias === "") {{ alert("El alias no puede estar vacío."); return "USER_CANCEL"; }}
                    // El service worker tarda en ACTIVARSE: usando el registro que
                    // devuelve register() antes de que esté listo, pushManager falla.
                    // navigator.serviceWorker.ready espera a que esté operativo.
                    try {{ await navigator.serviceWorker.register('/service-worker.js'); }} catch (e) {{}}
                    const reg = await navigator.serviceWorker.ready;
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
                    // Si este dispositivo ya estaba suscrito, se reutiliza: volver a
                    // llamar a subscribe() con una suscripción viva lanza InvalidStateError
                    let sub = await reg.pushManager.getSubscription();
                    if (!sub) {{
                        sub = await reg.pushManager.subscribe({{
                            userVisibleOnly: true,
                            applicationServerKey: toUint8(publicKey)
                        }});
                    }}
                    return JSON.stringify({{ subscription: sub, alias: alias }});
                }} catch (err) {{
                    if (err.name === "NotAllowedError") return "PERMISO_BLOQUEADO";
                    return "ERROR_" + err.message;
                }}
            }})();
            """,
            callback=NotificationState.guardar_subscripcion
        ),
        cursor="pointer",
        padding="9px 14px",
        border_radius="999px",
        background=theme.alpha(theme.COMMENT, 0.12),
        border=f"1px solid {theme.alpha(theme.COMMENT, 0.3)}",
        _hover={"background": theme.alpha(theme.COMMENT, 0.2)},
        transition="background 0.15s ease",
        title="Suscribir este dispositivo a notificaciones",
    )


def _user_menu() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.hstack(
                rx.icon("circle-user", size=20, color=theme.ACCENT, flex_shrink="0"),
                rx.cond(
                    UserState.current_user,
                    rx.text(UserState.current_user.username, size="2", color=theme.TEXT, weight="medium", white_space="nowrap"),
                    rx.text("Usuario", size="2", color=theme.MUTED, white_space="nowrap"),
                ),
                rx.icon("chevron-down", size=14, color=theme.MUTED),
                cursor="pointer",
                align="center",
                spacing="2",
                padding="6px 12px",
                border_radius="999px",
                background=theme.BG_CARD,
                border=f"1px solid {theme.BORDER}",
                _hover={"border_color": theme.BORDER_STRONG, "background": theme.BG_CARD_HOVER},
            )
        ),
        rx.menu.content(
            rx.menu.item("Perfil", rx.icon("user", size=14), on_click=rx.redirect("/profile")),
            rx.menu.item("Seguridad", rx.icon("shield", size=14), on_click=rx.redirect("/security")),
            rx.menu.separator(),
            rx.menu.item("Cerrar sesión", rx.icon("log-out", size=14), on_click=UserState.logout, color=theme.DANGER),
            width="200px",
        ),
        modal=False,
    )


def topbar() -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(
                rx.cond(NavState.sidebar_collapsed, "menu", "menu"),
                size=20,
                color=theme.MUTED,
            ),
            on_click=NavState.toggle_sidebar,
            cursor="pointer",
            padding="8px",
            border_radius="8px",
            flex_shrink="0",
            _hover={"background": theme.alpha(theme.ACCENT, 0.10)},
            display=["none !important", "none !important", "flex !important"],
        ),
        _view_title(),
        #Selector de calendario: arriba y siempre visible en las vistas donde
        #importa qué mes estás mirando, en vez de escondido en la página
        rx.cond(
            (NavState.active_route == CALENDAR_ROUTES[0]) | (NavState.active_route == CALENDAR_ROUTES[1]),
            rx.box(
                calendar_switcher(compact=True),
                display=["none !important", "flex !important", "flex !important"],
                flex_shrink="0",
            ),
        ),
        _user_menu(),
        width="100%",
        align="center",
        spacing="3",
        padding=["10px 12px", "10px 12px", "14px 24px"],
        background=theme.BG_TOPBAR,
        border_bottom=f"1px solid {theme.BORDER}",
        backdrop_filter="blur(12px)",
        position="sticky",
        top="0",
        z_index="40",
        overflow_x="hidden",
    )
