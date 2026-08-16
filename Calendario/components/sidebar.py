# Calendario/components/sidebar.py

import reflex as rx

from Calendario import theme
from Calendario.state.chat_state import ChatState
from Calendario.state.nav_state import NavState
from Calendario.state.user_state import UserState

# (ruta, icono, etiqueta)
NAV_ITEMS = [
    ("/calendar", "calendar-days", "Calendario"),
    ("/menu_semanal", "clipboard-list", "Menú semanal"),
    ("/meal_list", "utensils", "Comidas"),
    ("/shopping_list", "shopping-cart", "Lista de compra"),
    #La despensa va justo detrás de la compra: son las dos caras de lo mismo,
    #lo que falta y lo que hay
    ("/despensa", "warehouse", "Despensa"),
    ("/amigos", "users", "Amigos"),
    ("/profile", "user", "Perfil"),
    ("/security", "shield", "Seguridad"),
]

#La barra inferior del móvil, con etiquetas cortas: las secciones del día a día
#caben si no se escribe "Lista de compra" entera. Perfil y seguridad siguen en
#el menú de usuario de la barra superior.
MOBILE_NAV_ITEMS = [
    ("/calendar", "calendar-days", "Calendario"),
    ("/menu_semanal", "clipboard-list", "Menú"),
    ("/meal_list", "utensils", "Comidas"),
    ("/shopping_list", "shopping-cart", "Compra"),
    ("/despensa", "warehouse", "Despensa"),
    ("/amigos", "users", "Amigos"),
]


def _unread_dot(top: str = "-4px", right: str = "-6px") -> rx.Component:
    """Chincheta de mensajes sin leer sobre el icono de Amigos.

    Va en la navegación, no solo dentro de la pestaña: enterarse de que alguien
    te ha escrito no puede depender de que se te ocurra entrar a mirar.
    """
    return rx.cond(
        ChatState.has_unread,
        rx.center(
            rx.text(ChatState.unread_label, size="1", weight="bold", color="#04120a",
                    line_height="1", font_size="10px"),
            position="absolute",
            top=top,
            right=right,
            min_width="17px",
            height="17px",
            padding_x="4px",
            border_radius="999px",
            background=theme.SUCCESS,
            border=f"2px solid {theme.BG_SIDEBAR}",
            box_shadow="0 0 0 1px rgba(0, 0, 0, 0.35)",
        ),
    )


def _nav_icon(icon: str, route: str, color) -> rx.Component:
    """Icono de navegación; el de amigos lleva encima los mensajes sin leer."""
    return rx.box(
        rx.icon(icon, size=18, color=color),
        *([_unread_dot()] if route == "/amigos" else []),
        position="relative",
        display="flex",
        flex_shrink="0",
    )


def _nav_item(route: str, icon: str, label: str) -> rx.Component:
    is_active = NavState.active_route == route
    return rx.link(
        rx.hstack(
            rx.box(
                width="3px",
                height="20px",
                border_radius="2px",
                background=rx.cond(is_active, theme.ACCENT, "transparent"),
                flex_shrink="0",
            ),
            _nav_icon(icon, route, rx.cond(is_active, theme.ACCENT, theme.MUTED)),
            rx.cond(
                ~NavState.sidebar_collapsed,
                rx.text(
                    label,
                    size="2",
                    weight=rx.cond(is_active, "bold", "medium"),
                    color=rx.cond(is_active, theme.TEXT, theme.MUTED),
                    white_space="nowrap",
                ),
            ),
            align="center",
            spacing="3",
            width="100%",
            padding_y="10px",
            padding_right="3",
            border_radius="8px",
            background=rx.cond(is_active, theme.alpha(theme.ACCENT, 0.10), "transparent"),
            _hover={"background": theme.alpha(theme.ACCENT, 0.06)},
        ),
        href=route,
        width="100%",
        title=label,
        underline="none",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/favicon.ico", width="26px", height="20px", flex_shrink="0"),
                    rx.cond(
                        ~NavState.sidebar_collapsed,
                        rx.vstack(
                            rx.text("CALENDPY", size="3", weight="bold", letter_spacing="0.12em", color=theme.TEXT),
                            rx.text("TU AGENDA Y COMIDAS", size="1", color=theme.MUTED, letter_spacing="0.06em"),
                            spacing="0",
                        ),
                    ),
                    align="center",
                    spacing="3",
                    width="100%",
                ),
                href="/calendar",
                underline="none",
                padding="18px 16px",
                width="100%",
            ),
            rx.divider(border_color=theme.BORDER),
            rx.vstack(
                *[_nav_item(r, i, l) for r, i, l in NAV_ITEMS],
                spacing="1",
                width="100%",
                padding="10px",
            ),
            rx.spacer(),
            rx.divider(border_color=theme.BORDER),
            rx.vstack(
                rx.hstack(
                    rx.icon("log-out", size=16, color=theme.DANGER, flex_shrink="0"),
                    rx.cond(
                        ~NavState.sidebar_collapsed,
                        rx.text("Cerrar sesión", size="1", color=theme.DANGER),
                    ),
                    on_click=UserState.logout,
                    cursor="pointer",
                    spacing="3",
                    align="center",
                    padding="8px",
                    width="100%",
                    border_radius="8px",
                    _hover={"background": theme.alpha(theme.DANGER, 0.08)},
                ),
                rx.hstack(
                    rx.icon(
                        rx.cond(NavState.sidebar_collapsed, "chevrons-right", "chevrons-left"),
                        size=16,
                        color=theme.MUTED,
                    ),
                    rx.cond(
                        ~NavState.sidebar_collapsed,
                        rx.text("Colapsar", size="1", color=theme.MUTED),
                    ),
                    on_click=NavState.toggle_sidebar,
                    cursor="pointer",
                    spacing="3",
                    align="center",
                    padding="8px",
                    width="100%",
                    border_radius="8px",
                    _hover={"background": theme.alpha(theme.ACCENT, 0.06)},
                ),
                spacing="1",
                width="100%",
                padding="10px",
            ),
            height="100%",
            width="100%",
            spacing="0",
        ),
        width=rx.cond(NavState.sidebar_collapsed, "68px", "232px"),
        min_width=rx.cond(NavState.sidebar_collapsed, "68px", "232px"),
        #`fixed` y no `sticky`: sticky depende de que ningún ancestro tenga
        #overflow ni transform, y aquí hay varios contenedores por encima. Con
        #`fixed` el menú se queda clavado a la ventana pase lo que pase, que es
        #justo lo que se pide: verlo entero estés donde estés de la página.
        position="fixed",
        top="0",
        left="0",
        height="100vh",
        background=theme.BG_SIDEBAR,
        border_right=f"1px solid {theme.BORDER}",
        transition="width 0.16s ease, min-width 0.16s ease",
        #`clip` y no `hidden`: hace falta recortar para la animación de colapsar,
        #pero `hidden` crea contenedor de scroll y anula el `position: sticky`
        #del menú de dentro, que es lo que hace que acompañe al desplazamiento
        overflow="clip",
        z_index="50",
        flex_shrink="0",
        # En móvil la navegación pasa a la barra inferior (mobile_bottom_nav).
        # !important: .rt-Box trae display:block incondicional en su CSS base, con más
        # prioridad de cascada que el estilo condicional que genera Emotion — sin
        # !important esta regla pierde y la sidebar se queda visible en cualquier ancho.
        display=["none !important", "none !important", "block !important"],
    )


def _mobile_nav_item(route: str, icon: str, label: str) -> rx.Component:
    is_active = NavState.active_route == route
    return rx.link(
        rx.vstack(
            _nav_icon(icon, route, rx.cond(is_active, theme.ACCENT, theme.MUTED)),
            rx.text(
                label,
                size="1",
                color=rx.cond(is_active, theme.ACCENT, theme.MUTED),
                weight=rx.cond(is_active, "bold", "medium"),
                white_space="nowrap",
                font_size="10px",
            ),
            align="center",
            justify="center",
            spacing="1",
            flex_shrink="0",
            #Con seis secciones hay que apretar más: el ancho mínimo baja a lo
            #que ocupa la etiqueta más larga en una pantalla estrecha. Si aun
            #así no caben (móviles de 320px), la barra desliza en horizontal.
            min_width="48px",
            padding_y="2",
        ),
        href=route,
        underline="none",
        flex="1 1 0",
    )


def mobile_bottom_nav() -> rx.Component:
    """Barra de navegación inferior del móvil.

    Va **flotando**, separada de los bordes: pegada abajo la comían las
    esquinas redondeadas de la pantalla y la barra gestual del sistema. El
    `env(safe-area-inset-bottom)` la sube además lo que pida el propio móvil
    (en un iPhone con notch son ~34px, en Android suele ser 0).
    """
    return rx.hstack(
        *[_mobile_nav_item(r, i, l) for r, i, l in MOBILE_NAV_ITEMS],
        align="center",
        justify="between",
        spacing="0",
        padding="8px 8px",
        background="rgba(10, 15, 22, 0.92)",
        backdrop_filter="blur(16px)",
        border=f"1px solid {theme.BORDER_STRONG}",
        border_radius="22px",
        box_shadow="0 12px 34px -8px rgba(0, 0, 0, 0.75)",
        overflow_x="auto",
        position="fixed",
        #Separada del borde inferior + lo que reserve el sistema
        bottom="calc(16px + env(safe-area-inset-bottom))",
        left="12px",
        right="12px",
        z_index="60",
        display=["flex !important", "flex !important", "none !important"],
    )
