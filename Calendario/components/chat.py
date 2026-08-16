# Calendario/components/chat.py
"""
El chat de la pestaña de amigos.

Una sola conversación se pinta en dos sitios, según el ancho de pantalla:

- **Escritorio**: panel partido, lista de chats a la izquierda y conversación a
  la derecha, como cualquier mensajería.
- **Móvil**: la lista ocupa la página y, al tocar un amigo, la conversación se
  abre **a pantalla completa** por encima de todo (incluida la barra de
  navegación flotante), con su botón de volver. Meterla en la página dejaba el
  campo de escribir debajo de la barra inferior, que es justo donde estorba.

Las dos copias comparten el mismo estado, así que da igual por dónde escribas.
"""

import reflex as rx

from Calendario import theme
from Calendario.components.ui import empty_state, panel
from Calendario.state.chat_state import ChatState

#Alto del panel de escritorio: ni tan bajo que se vean tres mensajes ni tan
#alto que haya que hacer scroll de página para llegar al campo de escribir
DESK_HEIGHT = "min(64vh, 620px)"


def avatar(initial, size: str = "38px", color: str = theme.PURPLE) -> rx.Component:
    return rx.center(
        rx.text(initial, size="2", weight="bold", color=color),
        min_width=size, width=size, height=size,
        border_radius="50%",
        background=theme.alpha(color, 0.14),
        border=f"1px solid {theme.alpha(color, 0.32)}",
        flex_shrink="0",
    )


def unread_pill(count) -> rx.Component:
    """Chincheta verde con el número de mensajes sin leer."""
    return rx.center(
        rx.text(count, size="1", weight="bold", color="#04120a"),
        min_width="20px", height="20px", padding_x="6px",
        border_radius="999px", background=theme.SUCCESS, flex_shrink="0",
    )


# ---------------------------------------------------------------------------
# Lista de conversaciones
# ---------------------------------------------------------------------------
def _conversation_row(c) -> rx.Component:
    activa = ChatState.active_id == c["user_id"]
    return rx.hstack(
        avatar(c["initial"]),
        rx.vstack(
            rx.hstack(
                rx.text(c["username"], size="2", weight="bold", color=theme.TEXT,
                        overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                rx.spacer(),
                rx.text(c["time_label"], size="1", color=theme.DIM, flex_shrink="0"),
                width="100%", align="center", spacing="2",
            ),
            rx.hstack(
                rx.text(
                    c["preview"], size="1",
                    color=rx.cond(c["unread"] > 0, theme.TEXT, theme.MUTED),
                    weight=rx.cond(c["unread"] > 0, "medium", "regular"),
                    font_style=rx.cond(c["empty"], "italic", "normal"),
                    overflow="hidden", text_overflow="ellipsis", white_space="nowrap",
                    flex="1 1 0", min_width="0",
                ),
                rx.cond(c["unread"] > 0, unread_pill(c["unread"])),
                width="100%", align="center", spacing="2",
            ),
            spacing="1", align="start", flex="1 1 0", min_width="0", width="100%",
        ),
        on_click=ChatState.open_chat(c["user_id"], c["username"]),
        cursor="pointer",
        width="100%", max_width="100%", align="center", spacing="3",
        padding="10px 12px", border_radius=theme.RADIUS_SM,
        background=rx.cond(activa, theme.alpha(theme.PURPLE, 0.12), "transparent"),
        border=rx.cond(
            activa,
            f"1px solid {theme.alpha(theme.PURPLE, 0.3)}",
            "1px solid transparent",
        ),
        _hover={"background": theme.alpha(theme.PURPLE, 0.08)},
        transition="background 0.14s ease",
        overflow="hidden",
    )


def conversation_list(**props) -> rx.Component:
    return rx.vstack(
        rx.foreach(ChatState.conversations, _conversation_row),
        spacing="1", width="100%", align="start", **props,
    )


# ---------------------------------------------------------------------------
# Conversación
# ---------------------------------------------------------------------------
def _bubble(m) -> rx.Component:
    return rx.fragment(
        #Separador de día: solo lo lleva el primer mensaje de cada jornada
        rx.cond(
            m["show_day"],
            rx.center(
                rx.text(m["day_label"], size="1", color=theme.MUTED,
                        padding="3px 10px", border_radius="999px",
                        background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}"),
                width="100%", padding_y="6px",
            ),
        ),
        rx.flex(
            rx.box(
                rx.text(
                    m["body"], size="2", color=theme.TEXT,
                    white_space="pre-wrap", word_break="break-word",
                ),
                rx.hstack(
                    rx.text(m["time_label"], size="1", color=theme.DIM),
                    #Doble check solo en lo mío: saber si lo ha leído es media
                    #gracia de mandar un mensaje en vez de un aviso suelto
                    rx.cond(
                        m["mine"],
                        rx.cond(
                            m["read"],
                            rx.icon("check-check", size=13, color=theme.ACCENT),
                            rx.icon("check", size=13, color=theme.DIM),
                        ),
                    ),
                    spacing="1", align="center", justify="end", width="100%",
                    margin_top="2px",
                ),
                max_width="82%",
                padding="8px 11px",
                background=rx.cond(m["mine"], theme.alpha(theme.ACCENT, 0.16), theme.BG_RAISED),
                border=rx.cond(
                    m["mine"],
                    f"1px solid {theme.alpha(theme.ACCENT, 0.32)}",
                    f"1px solid {theme.BORDER}",
                ),
                border_radius=rx.cond(m["mine"], "14px 14px 4px 14px", "14px 14px 14px 4px"),
                box_shadow=theme.SHADOW_SM,
            ),
            width="100%",
            justify=rx.cond(m["mine"], "end", "start"),
        ),
    )


def _quick_chips() -> rx.Component:
    """Mensajes de un toque: la evolución de los antiguos avisos rápidos."""
    return rx.hstack(
        rx.foreach(
            ChatState.quick_messages,
            lambda m: rx.box(
                rx.text(m, size="1", color=theme.TEXT, white_space="nowrap"),
                on_click=ChatState.send_quick(m),
                cursor="pointer", padding="6px 11px", border_radius="999px",
                background=theme.BG_SUNKEN, border=f"1px solid {theme.BORDER}",
                _hover={"border_color": theme.BORDER_STRONG, "background": theme.BG_CARD_HOVER},
                flex_shrink="0",
            ),
        ),
        spacing="2", width="100%",
        overflow_x="auto", padding_bottom="2px",
        #La fila de chips se desliza a un lado en móvil sin barra a la vista
        style={"scrollbar_width": "none", "&::-webkit-scrollbar": {"display": "none"}},
    )


def _composer() -> rx.Component:
    return rx.form(
        rx.hstack(
            rx.input(
                name="body",
                placeholder="Escribe un mensaje...",
                max_length=1000,
                auto_complete=False,
                size="3", flex="1 1 0", min_width="0", radius="full",
            ),
            rx.button(
                rx.icon("send", size=16),
                type="submit", size="3", radius="full", cursor="pointer",
                loading=ChatState.sending, color_scheme="blue", flex_shrink="0",
            ),
            width="100%", spacing="2", align="center",
        ),
        on_submit=ChatState.send,
        reset_on_submit=True,
        width="100%",
    )


def _messages_area(scroll_id: str) -> rx.Component:
    return rx.box(
        rx.cond(
            ChatState.empty_conversation,
            rx.center(
                rx.vstack(
                    rx.icon("message-circle-heart", size=30, color=theme.alpha(theme.PURPLE, 0.7)),
                    rx.text("Aún no os habéis dicho nada", size="2", color=theme.MUTED),
                    rx.text("Lo que escribas le llega al móvil al momento",
                            size="1", color=theme.DIM, text_align="center"),
                    spacing="2", align="center",
                ),
                width="100%", height="100%", min_height="140px",
            ),
            rx.vstack(
                rx.foreach(ChatState.messages, _bubble),
                spacing="2", width="100%", align="stretch",
            ),
        ),
        id=scroll_id,
        flex="1 1 0", min_height="0",
        width="100%", overflow_y="auto", overflow_x="hidden",
        padding="12px 14px",
    )


def _chat_header(*, mobile: bool) -> rx.Component:
    return rx.hstack(
        *(
            [rx.box(
                rx.icon("arrow-left", size=20, color=theme.TEXT),
                on_click=ChatState.close_chat,
                cursor="pointer", padding="6px", border_radius="8px", flex_shrink="0",
                _hover={"background": theme.alpha(theme.ACCENT, 0.1)},
            )] if mobile else []
        ),
        avatar(ChatState.active_initial, size="34px"),
        rx.vstack(
            rx.text(ChatState.active_name, size="2", weight="bold", color=theme.TEXT,
                    white_space="nowrap", overflow="hidden", text_overflow="ellipsis"),
            rx.text("Le llega al móvil si lo tiene vinculado", size="1", color=theme.DIM,
                    white_space="nowrap", overflow="hidden", text_overflow="ellipsis"),
            spacing="0", align="start", flex="1 1 0", min_width="0",
        ),
        *(
            [rx.icon("x", size=18, color=theme.MUTED, cursor="pointer", flex_shrink="0",
                     on_click=ChatState.close_chat)] if not mobile else []
        ),
        width="100%", align="center", spacing="3", flex_shrink="0",
        padding="10px 14px",
        border_bottom=f"1px solid {theme.BORDER}",
        background=theme.BG_SUNKEN,
    )


def _conversation_pane(*, mobile: bool) -> rx.Component:
    """Cabecera + mensajes + chips + campo de escribir."""
    return rx.vstack(
        _chat_header(mobile=mobile),
        _messages_area("chat-scroll-mob" if mobile else "chat-scroll-desk"),
        rx.vstack(
            _quick_chips(),
            _composer(),
            spacing="2", width="100%", flex_shrink="0",
            padding="10px 14px",
            border_top=f"1px solid {theme.BORDER}",
            background=theme.BG_SUNKEN,
            #En el móvil, el hueco que reserve el sistema abajo (la barra
            #gestual del iPhone se comía el botón de enviar)
            padding_bottom="calc(10px + env(safe-area-inset-bottom))" if mobile else "10px",
        ),
        spacing="0", width="100%", height="100%", align="stretch",
    )


# ---------------------------------------------------------------------------
# Montajes por plataforma
# ---------------------------------------------------------------------------
def chat_desktop() -> rx.Component:
    """Panel partido de escritorio: lista a la izquierda, conversación a la derecha."""
    return panel(
        rx.hstack(
            rx.box(
                conversation_list(padding="10px"),
                width="300px", min_width="300px", height="100%",
                overflow_y="auto",
                border_right=f"1px solid {theme.BORDER}",
                background=theme.alpha("#000000", 0.12),
            ),
            rx.box(
                rx.cond(
                    ChatState.chat_open,
                    _conversation_pane(mobile=False),
                    rx.center(
                        rx.vstack(
                            rx.icon("messages-square", size=34, color=theme.alpha(theme.PURPLE, 0.6)),
                            rx.text("Elige a quién escribir", size="3", weight="bold", color=theme.TEXT),
                            rx.text("Tus mensajes le llegan al móvil como notificación",
                                    size="1", color=theme.MUTED),
                            spacing="2", align="center",
                        ),
                        width="100%", height="100%",
                    ),
                ),
                flex="1 1 0", min_width="0", height="100%",
            ),
            width="100%", height=DESK_HEIGHT, spacing="0", align="stretch",
        ),
        padding="0", overflow="hidden",
        display=["none !important", "none !important", "block !important"],
    )


def chat_mobile_list() -> rx.Component:
    """En móvil la lista de chats ocupa la página; el chat se abre encima."""
    return panel(
        rx.vstack(
            rx.hstack(
                rx.icon("messages-square", size=16, color=theme.PURPLE),
                rx.text("CONVERSACIONES", size="1", color=theme.DIM,
                        weight="bold", letter_spacing="0.1em"),
                width="100%", align="center", spacing="2",
            ),
            conversation_list(),
            spacing="3", width="100%", align="start",
        ),
        display=["block !important", "block !important", "none !important"],
    )


def chat_mobile_overlay() -> rx.Component:
    """Conversación a pantalla completa en móvil, por encima de la barra inferior."""
    return rx.cond(
        ChatState.chat_open,
        rx.box(
            _conversation_pane(mobile=True),
            position="fixed", top="0", left="0", right="0", bottom="0",
            z_index="70",
            background=f"radial-gradient(circle at top, {theme.BG_TOPBAR} 0%, {theme.BG_APP} 55%)",
            display=["flex !important", "flex !important", "none !important"],
            flex_direction="column",
        ),
    )


def chat_empty() -> rx.Component:
    """Cuando aún no hay ningún amigo con quien hablar."""
    return empty_state(
        icon="users",
        title="Todavía no tienes amigos aquí",
        description=(
            "Busca a alguien por su nombre de usuario y mándale una solicitud. "
            "Cuando la acepte podréis escribiros, avisaros al móvil y compartir "
            "calendarios, recetario y lista de la compra."
        ),
        color=theme.PURPLE,
    )
