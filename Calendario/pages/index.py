# Calendario/pages/index.py

import reflex as rx

from Calendario import theme
from Calendario.components.footer import footer
from Calendario.components.ui import icon_badge, panel
from Calendario.state.user_state import UserState


#Función que redirije a la página de calendario
def redirect_to_calendar():
    return rx.vstack(rx.script("window.location.href = '/calendar'"))


def _feature(icon: str, color: str, title: str, description: str) -> rx.Component:
    return panel(
        rx.vstack(
            icon_badge(icon, color, size=19, box="44px"),
            rx.text(title, size="3", weight="bold", color=theme.TEXT),
            rx.text(description, size="2", color=theme.MUTED, line_height="1.6"),
            spacing="3",
            align="start",
            height="100%",
        ),
        padding="20px",
        height="100%",
    )


def _step(number: str, title: str, description: str, color: str) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.text(number, size="3", weight="bold", color=color),
            min_width="38px",
            height="38px",
            border_radius="50%",
            background=theme.alpha(color, 0.14),
            border=f"1px solid {theme.alpha(color, 0.3)}",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, size="2", weight="bold", color=theme.TEXT),
            rx.text(description, size="2", color=theme.MUTED, line_height="1.55"),
            spacing="1",
            align="start",
            min_width="0",
        ),
        spacing="3",
        align="start",
        width="100%",
    )


def _cta_buttons() -> rx.Component:
    return rx.flex(
        rx.link(
            rx.button(
                rx.icon("user-check", size=18),
                rx.text("Iniciar sesión", size="3", weight="medium"),
                size="4",
                color_scheme="blue",
                radius="full",
                cursor="pointer",
                _hover={"transform": "translateY(-2px)"},
                transition="all 0.18s ease",
                padding_x="2em",
            ),
            href="/login",
            underline="none",
        ),
        rx.link(
            rx.button(
                rx.icon("user-plus", size=18),
                rx.text("Crear cuenta", size="3", weight="medium"),
                size="4",
                variant="surface",
                color_scheme="gray",
                radius="full",
                cursor="pointer",
                _hover={"transform": "translateY(-2px)"},
                transition="all 0.18s ease",
                padding_x="2em",
            ),
            href="/register",
            underline="none",
        ),
        spacing="3",
        wrap="wrap",
        justify="center",
        width="100%",
    )


#Página indice/principal
@rx.page(  #Decorador indicando página
    route="/",
    title="CalendPy · Planifica tus comidas y tu compra",
    on_load=[UserState.on_load],  #Comprobaciones al cargar página
)
@footer  #Insertamos el pie de página
def index() -> rx.Component:
    return rx.cond(  #Comprueba el estado de usuario, y si hay usuario, redirije directamente al calendario
        UserState.current_user,
        redirect_to_calendar(),
        rx.box(
            rx.vstack(
                # ---------------- Portada ----------------
                rx.vstack(
                    rx.image(
                        src="/favicon.ico",
                        width=["120px", "150px", "170px"],
                        height="auto",
                        margin_bottom="0.4em",
                    ),
                    rx.hstack(
                        rx.box(
                            width="6px",
                            height="6px",
                            border_radius="50%",
                            background=theme.MEAL,
                        ),
                        rx.text(
                            "PLANIFICADOR DE COMIDAS Y COMPRA",
                            size="1",
                            color=theme.MUTED,
                            weight="bold",
                            letter_spacing="0.18em",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.heading(
                        rx.text(
                            "Deja de improvisar ",
                            rx.text("la cena", as_="span", class_name="brand-gradient-text"),
                            as_="span",
                        ),
                        size=rx.breakpoints(initial="7", md="8", lg="9"),
                        text_align="center",
                        line_height="1.15",
                    ),
                    rx.text(
                        "Planifica el mes, rellena la semana entre dos y llévate la lista "
                        "de la compra hecha, con las cantidades ya sumadas.",
                        size=rx.breakpoints(initial="3", md="4"),
                        color=theme.MUTED,
                        text_align="center",
                        max_width="620px",
                        line_height="1.6",
                    ),
                    _cta_buttons(),
                    spacing="4",
                    align="center",
                    width="100%",
                    padding_y=["2.5em", "3em", "4em"],
                ),

                # ---------------- Qué hace ----------------
                rx.grid(
                    _feature(
                        "calendar-days",
                        theme.ACCENT,
                        "Un calendario por mes",
                        "Asigna comida y cena a cada día, con comentarios y agenda para tareas, eventos y notas.",
                    ),
                    _feature(
                        "clipboard-list",
                        theme.PURPLE,
                        "Menú semanal",
                        "Vista de lunes a domingo para rellenar la semana de una sentada. ¿Sin ideas? El botón «Sorpréndeme» rellena los huecos.",
                    ),
                    _feature(
                        "shopping-cart",
                        theme.MEAL,
                        "La compra, sola",
                        "Los ingredientes de los platos de la semana se suman y se ordenan por secciones del súper.",
                    ),
                    _feature(
                        "users",
                        theme.OWNER,
                        "Compartido",
                        "Invita a quien quieras a tu calendario y a tu lista: todos veis y editáis lo mismo, al momento.",
                    ),
                    _feature(
                        "chef-hat",
                        theme.WARNING,
                        "Recetario propio",
                        "Más de 100 platos fáciles listos para usar, y los tuyos con sus ingredientes y su tiempo.",
                    ),
                    _feature(
                        "bell",
                        theme.COMMENT,
                        "Avisos al móvil",
                        "Notificaciones cuando alguien cambia el menú, comenta un día o comparte un calendario contigo.",
                    ),
                    columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                    spacing="4",
                    width="100%",
                ),

                # ---------------- Cómo funciona ----------------
                panel(
                    rx.vstack(
                        rx.vstack(
                            rx.text(
                                "EL RITUAL DEL SÁBADO",
                                size="1",
                                color=theme.DIM,
                                weight="bold",
                                letter_spacing="0.14em",
                            ),
                            rx.heading("Tres pasos y la semana resuelta", size="6", color=theme.TEXT),
                            spacing="1",
                            align="start",
                        ),
                        rx.box(height="1px", width="100%", background=theme.BORDER),
                        rx.grid(
                            _step(
                                "1",
                                "Rellenad la semana",
                                "Comida y cena de lunes a domingo, eligiendo del recetario.",
                                theme.ACCENT,
                            ),
                            _step(
                                "2",
                                "Generad la compra",
                                "Se suman los ingredientes de todos los platos, ajustados a los comensales.",
                                theme.MEAL,
                            ),
                            _step(
                                "3",
                                "Al súper",
                                "Lista por secciones, con cantidades, que podéis tachar desde el móvil los dos a la vez.",
                                theme.PURPLE,
                            ),
                            columns=rx.breakpoints(initial="1", md="3"),
                            spacing="4",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    padding=["20px", "24px", "30px"],
                    border_radius=theme.RADIUS_LG,
                    background=f"linear-gradient(135deg, {theme.alpha(theme.ACCENT, 0.08)} 0%, {theme.BG_CARD} 60%)",
                ),

                # ---------------- Cierre ----------------
                rx.vstack(
                    rx.heading("¿Empezamos?", size="6", color=theme.TEXT, text_align="center"),
                    rx.text(
                        "Es gratis y son dos minutos.",
                        size="2",
                        color=theme.MUTED,
                        text_align="center",
                    ),
                    _cta_buttons(),
                    spacing="3",
                    align="center",
                    width="100%",
                    padding_y="2.5em",
                ),

                spacing="6",
                width="100%",
                max_width="1100px",
                margin="0 auto",
                padding_x=["1em", "1.5em", "2em"],
                padding_bottom="3em",
            ),
            width="100%",
            min_height="100vh",
            background=f"radial-gradient(circle at top, {theme.BG_TOPBAR} 0%, {theme.BG_APP} 55%)",
        ),
    )
