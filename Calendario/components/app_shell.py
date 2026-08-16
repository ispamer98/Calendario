# Calendario/components/app_shell.py
"""
Shell común para las páginas autenticadas: sidebar + topbar + fondo con
degradado radial. Sustituye a los `rx.vstack(user_navbar(), ...)` sueltos
que había antes en cada página (calendar, meal_list, shopping_list,
profile, security) — mismo layout, un único sitio donde mantenerlo.
"""
import reflex as rx

from Calendario import theme
from Calendario.components.sidebar import sidebar, mobile_bottom_nav
from Calendario.state.chat_state import ChatState
from Calendario.state.nav_state import NavState
from Calendario.components.topbar import topbar
from Calendario.components.calendar_creator import calendar_creator
from Calendario.components.meal_form import meal_form_dialog
from Calendario.components.category_manager import category_manager_dialog
from Calendario.components.type_manager import type_manager_dialog
from Calendario.components.units_manager import units_manager_dialog
from Calendario.components.supermarket_manager import supermarket_manager_dialog
from Calendario.components.products_manager import products_manager_dialog
from Calendario.components.consume_dialog import consume_dialog


def app_shell(*content: rx.Component) -> rx.Component:
    return rx.box(
        #Arranca el sondeo de mensajes sin leer al entrar en cualquier página de
        #la app: así la chincheta de "Amigos" se entera de que te han escrito
        #estés donde estés, sin tener que añadir nada al `on_load` de cada
        #página. El propio bucle se protege de arrancar dos veces.
        rx.box(on_mount=ChatState.badge_loop, display="none"),
        calendar_creator(),
        #Gestor de unidades: se abre desde el recetario y desde la compra
        units_manager_dialog(),
        #Gestor de supermercados: ahora también hace falta en el recetario, así
        #que vive aquí y no dentro de la página de la compra
        supermarket_manager_dialog(),
        #Catálogo de productos: se abre desde cualquier desplegable de producto
        products_manager_dialog(),
        category_manager_dialog(),
        type_manager_dialog(),
        #Diálogo de alta/edición de comidas: vive en el shell para poder
        #abrirlo desde cualquier página (recetario, editor del día...)
        meal_form_dialog(),
        #Descontar de la despensa lo cocinado: se abre desde el aviso del móvil,
        #desde el editor del día y desde la propia despensa
        consume_dialog(),
        rx.hstack(
            sidebar(),
            rx.vstack(
                topbar(),
                rx.box(
                    #`max_width: 100%` + `min_width: 0`: sin esto el contenido
                    #no puede encogerse y desborda
                    rx.box(
                        *content,
                        width="100%",
                        max_width="1400px",
                        margin="0 auto",
                    ),
                    width="100%",
                    max_width="100%",
                    min_width="0",
                    overflow_x="hidden",
                    padding=["14px", "14px", "28px"],
                    #Hueco para la barra flotante del móvil (que ahora va
                    #despegada del borde), más el margen que reserve el sistema
                    padding_bottom=[
                        "calc(112px + env(safe-area-inset-bottom))",
                        "calc(112px + env(safe-area-inset-bottom))",
                        "28px",
                    ],
                    flex="1",
                ),
                #ESTE es el bug que aplastaba la barra lateral, desbordaba a la
                #derecha (la línea gris) y dejaba los widgets pegados a la
                #izquierda: un hijo de flex con `width: 100%` y el `min-width:
                #auto` por defecto exige el ancho entero MÁS la barra lateral,
                #así que el contenedor acababa siendo más ancho que la pantalla
                #y `margin: 0 auto` no podía centrar nada.
                flex="1",
                min_width="0",
                max_width="100%",
                overflow_x="clip",
                #La barra lateral está fuera del flujo (`position: fixed`), así
                #que hay que dejarle su hueco. Solo en escritorio: en móvil no
                #se muestra y la navegación va en la barra inferior.
                style={
                    "@media screen and (min-width: 48em)": {
                        "marginLeft": rx.cond(NavState.sidebar_collapsed, "68px", "232px"),
                    }
                },
                min_height="100vh",
                spacing="0",
                align="start",
            ),
            width="100%",
            max_width="100%",
            #`clip` en vez de `hidden`: recorta el desbordamiento igual, pero no
            #crea contenedor de scroll, así la barra lateral sigue pegada
            #(`position: sticky`) en páginas largas
            overflow_x="clip",
            spacing="0",
            align="stretch",
        ),
        mobile_bottom_nav(),
        min_height="100vh",
        width="100%",
        max_width="100%",
        overflow_x="clip",
        background=f"radial-gradient(circle at top, {theme.BG_TOPBAR} 0%, {theme.BG_APP} 55%)",
    )
