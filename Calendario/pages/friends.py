# Calendario/pages/friends.py
"""
Pestaña de amigos.

Antes era una libreta de contactos con un botón de "avisar": tenías la lista,
pero no podías hacer gran cosa con ella. Ahora la página **es la conversación**:
chat con cada amigo (con su aviso al móvil, su hora y su doble check) y, debajo,
el trámite de siempre — pedir amistad, aceptar, quitar y elegir si quieres que
te avisen de los cambios en lo que compartís.

Se ve igual en el móvil que en el PC: en pantalla ancha, panel partido; en el
teléfono, lista de chats y conversación a pantalla completa.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.chat import (
    avatar, chat_desktop, chat_empty, chat_mobile_list, chat_mobile_overlay,
)
from Calendario.components.dialog_kit import form_dialog_content
from Calendario.components.ui import (
    action_button, collapsible, info_banner, page_header, panel, stat_card, stats_grid, tip,
)
from Calendario.state.chat_state import ChatState
from Calendario.state.friends_state import FriendsState
from Calendario.state.user_state import UserState


# ---------------------------------------------------------------------------
# Filas de gestión
# ---------------------------------------------------------------------------
def _friend_row(f) -> rx.Component:
    return rx.hstack(
        avatar(f["initial"], size="34px"),
        rx.box(
            rx.text(f["username"], size="2", weight="medium", color=theme.TEXT,
                    overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.button(
            rx.icon("message-circle", size=14), rx.text("Escribir", size="1"),
            on_click=ChatState.open_chat(f["user_id"], f["username"]),
            variant="soft", color_scheme="blue", size="1", radius="full",
            cursor="pointer", flex_shrink="0",
        ),
        rx.icon("user-minus", size=15, color=theme.MUTED, cursor="pointer", flex_shrink="0",
                on_click=FriendsState.remove(f["id"]),
                _hover={"color": theme.DANGER, "transform": "scale(1.2)"}),
        width="100%", max_width="100%", align="center", spacing="3",
        padding="10px 12px", border_radius=theme.RADIUS_SM,
        background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}", overflow="hidden",
    )


def _incoming_row(f) -> rx.Component:
    return rx.hstack(
        avatar(f["initial"], size="34px", color=theme.MEAL),
        rx.box(
            rx.text(f["username"], size="2", weight="medium", color=theme.TEXT),
            rx.text("quiere ser tu amigo", size="1", color=theme.DIM),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.icon_button(rx.icon("check", size=15), size="1", color_scheme="green",
                       on_click=FriendsState.respond(f["id"], True, f["username"]), flex_shrink="0"),
        rx.icon_button(rx.icon("x", size=15), size="1", variant="soft", color_scheme="red",
                       on_click=FriendsState.respond(f["id"], False, f["username"]), flex_shrink="0"),
        width="100%", max_width="100%", align="center", spacing="3",
        padding="10px 12px", border_radius=theme.RADIUS_SM,
        background=theme.alpha(theme.MEAL, 0.08),
        border=f"1px solid {theme.alpha(theme.MEAL, 0.25)}", overflow="hidden",
    )


def _outgoing_row(f) -> rx.Component:
    return rx.hstack(
        avatar(f["initial"], size="34px", color=theme.MUTED),
        rx.box(
            rx.text(f["username"], size="2", color=theme.MUTED),
            rx.text("pendiente de aceptar", size="1", color=theme.DIM),
            flex="1 1 0", min_width="0", overflow="hidden",
        ),
        rx.icon("clock", size=15, color=theme.WARNING, flex_shrink="0"),
        rx.icon("x", size=15, color=theme.MUTED, cursor="pointer", flex_shrink="0",
                on_click=FriendsState.remove(f["id"]),
                _hover={"color": theme.DANGER}),
        width="100%", max_width="100%", align="center", spacing="3",
        padding="10px 12px", border_radius=theme.RADIUS_SM,
        background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}", overflow="hidden",
    )


# ---------------------------------------------------------------------------
# Añadir amigo
# ---------------------------------------------------------------------------
def add_friend_dialog() -> rx.Component:
    return rx.dialog.root(
        form_dialog_content(
            icon="user-plus",
            title="Añadir amigo",
            accent=theme.PURPLE,
            form=rx.vstack(
                rx.text(
                    "Escribe su nombre de usuario de CalendPy. Le llegará un aviso "
                    "al móvil y, cuando acepte, podréis escribiros y compartir "
                    "calendarios, recetario y lista de la compra.",
                    size="1", color=theme.MUTED, line_height="1.5",
                ),
                rx.input(
                    rx.input.slot(rx.icon("search", size=15)),
                    placeholder="Nombre de usuario",
                    value=FriendsState.new_friend,
                    on_change=FriendsState.set_new_friend,
                    size="3", width="100%", auto_complete=False,
                ),
                rx.cond(
                    FriendsState.error != "",
                    rx.hstack(
                        rx.icon("circle-alert", size=14, color=theme.DANGER),
                        rx.text(FriendsState.error, size="1", color=theme.DANGER),
                        spacing="2", align="center",
                    ),
                ),
                rx.hstack(
                    rx.button("Cancelar", on_click=FriendsState.close_add,
                              variant="soft", color_scheme="gray", size="2", type="button"),
                    rx.button(rx.icon("send", size=15), rx.text("Enviar solicitud", size="2"),
                              on_click=FriendsState.send_request, color_scheme="green", size="2",
                              loading=FriendsState.loading, cursor="pointer", type="button"),
                    spacing="2", justify="end", width="100%", padding_top="2",
                ),
                spacing="3", width="100%", align="start",
            ),
        ),
        open=FriendsState.show_add,
    )


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
@rx.page(
    route="/amigos",
    title="Amigos | CalendPy",
    on_load=[
        UserState.on_load,
        UserState.check_autenticated,
        FriendsState.load,
        ChatState.load,
        #Sondeo: es lo que hace que un mensaje aparezca solo, sin recargar
        ChatState.poll_loop,
    ],
)
def friends() -> rx.Component:
    return app_shell(
        add_friend_dialog(),
        #Conversación a pantalla completa del móvil: va fuera del flujo, encima
        #de todo (incluida la barra de navegación inferior)
        chat_mobile_overlay(),
        rx.vstack(
            page_header(
                icon="users",
                title="Amigos",
                subtitle="Habla con ellos y compartid calendarios, recetario y compra",
                accent=theme.PURPLE,
                actions=[
                    action_button("Añadir amigo", "user-plus", theme.PURPLE,
                                  on_click=FriendsState.open_add),
                ],
            ),

            stats_grid(
                stat_card(icon="users", label="Amigos", value=FriendsState.friend_count,
                          color=theme.PURPLE),
                stat_card(icon="mail", label="Sin leer", value=ChatState.unread_total,
                          hint="Mensajes", color=theme.SUCCESS),
                stat_card(icon="user-plus", label="Solicitudes", value=FriendsState.incoming_count,
                          hint="Por responder", color=theme.MEAL),
                stat_card(icon="bell", label="Avisos", value=rx.cond(FriendsState.notify_changes, "Sí", "No"),
                          hint="De cambios", color=theme.ACCENT),
            ),

            #Sin la tabla del chat se ve todo pero no se puede escribir: mejor
            #decirlo aquí que dejar que el usuario descubra el fallo al enviar
            rx.cond(
                ~ChatState.chat_ready,
                info_banner(
                    "El chat necesita la migración 016_chat.sql: ejecútala en el editor SQL "
                    "de Supabase y podréis escribiros.",
                    icon="triangle-alert", color=theme.WARNING,
                ),
            ),

            #Lo primero que hay que atender: quién está esperando respuesta
            rx.cond(
                FriendsState.incoming_count > 0,
                panel(
                    rx.vstack(
                        rx.text("SOLICITUDES RECIBIDAS", size="1", color=theme.MEAL,
                                weight="bold", letter_spacing="0.1em"),
                        rx.foreach(FriendsState.incoming, _incoming_row),
                        spacing="2", width="100%", align="start",
                    ),
                ),
            ),

            #El chat: panel partido en el PC, lista + pantalla completa en móvil
            rx.cond(
                ChatState.has_conversations,
                rx.fragment(
                    chat_desktop(),
                    chat_mobile_list(),
                ),
                rx.cond(
                    FriendsState.outgoing_count > 0,
                    info_banner(
                        "Ya has mandado tu solicitud. En cuanto la acepte podréis hablar aquí.",
                        icon="clock", color=theme.WARNING,
                    ),
                    chat_empty(),
                ),
            ),

            #Gestión: plegada, porque el día a día es hablar, no administrar
            rx.cond(
                FriendsState.has_nothing,
                rx.fragment(),
                collapsible(
                    rx.vstack(
                        rx.cond(
                            FriendsState.friend_count > 0,
                            rx.vstack(
                                rx.text("TUS AMIGOS", size="1", color=theme.DIM,
                                        weight="bold", letter_spacing="0.1em"),
                                rx.foreach(FriendsState.friends, _friend_row),
                                spacing="2", width="100%", align="start",
                            ),
                        ),
                        rx.cond(
                            FriendsState.outgoing_count > 0,
                            rx.vstack(
                                rx.text("SOLICITUDES ENVIADAS", size="1", color=theme.DIM,
                                        weight="bold", letter_spacing="0.1em"),
                                rx.foreach(FriendsState.outgoing, _outgoing_row),
                                spacing="2", width="100%", align="start",
                            ),
                        ),
                        spacing="4", width="100%", align="start", padding_bottom="10px",
                    ),
                    title="GESTIONAR AMIGOS",
                    icon="settings-2",
                    color=theme.PURPLE,
                    hint="Quitar amistades y ver solicitudes enviadas",
                ),
            ),

            panel(
                rx.hstack(
                    rx.center(
                        rx.icon("bell-ring", size=16, color=theme.ACCENT),
                        min_width="36px", width="36px", height="36px",
                        border_radius=theme.RADIUS_SM,
                        background=theme.alpha(theme.ACCENT, 0.14),
                        border=f"1px solid {theme.alpha(theme.ACCENT, 0.28)}",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text("Avisarme de los cambios", size="2", weight="bold", color=theme.TEXT),
                        rx.text("Cuando alguien modifique un calendario o una lista que compartimos",
                                size="1", color=theme.MUTED),
                        spacing="0", align="start", min_width="0",
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=FriendsState.notify_changes,
                        on_change=FriendsState.toggle_notify_changes,
                        color_scheme="green",
                    ),
                    width="100%", align="center", spacing="3",
                ),
            ),

            #Qué gana uno teniendo amigos aquí, dicho en la propia página
            rx.grid(
                tip("message-circle", "Habla sin salir de la app",
                    "Lo que le escribas le llega al móvil como notificación, aunque no tenga la app abierta.",
                    theme.PURPLE),
                tip("calendar-days", "Calendarios compartidos",
                    "Comparte un calendario y ambos veis y editáis las comidas, la agenda y los comentarios.",
                    theme.ACCENT),
                tip("shopping-cart", "Una sola lista de la compra",
                    "Si tacha un producto en el súper, se te tacha a ti: es la misma lista para los dos.",
                    theme.MEAL),
                columns=rx.breakpoints(initial="1", md="3"),
                spacing="3", width="100%",
            ),

            info_banner(
                "Los mensajes de un amigo llegan siempre al móvil; el interruptor de arriba "
                "solo silencia los avisos automáticos de calendario.",
                icon="info", color=theme.ACCENT,
            ),

            spacing="4", width="100%", align="center",
        ),
    )
