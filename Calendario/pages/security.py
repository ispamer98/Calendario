# Calendario/pages/security.py

import reflex as rx

from Calendario import theme
from Calendario.components.app_shell import app_shell
from Calendario.components.show_pasw_switch import show_pasw_switch_security
from Calendario.components.ui import icon_badge, info_banner, page_header, panel
from Calendario.state.user_state import UserState


def _field(label: str, *children: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="1", color=theme.MUTED, weight="medium", letter_spacing="0.04em"),
        *children,
        spacing="1",
        width="100%",
        align="start",
    )


def _requirement(icon: str, text: str, met) -> rx.Component:
    """Requisito de la contraseña, que se pone en verde al cumplirse."""
    return rx.hstack(
        rx.icon(
            rx.cond(met, "circle-check", "circle"),
            size=14,
            color=rx.cond(met, theme.SUCCESS, theme.DIM),
            flex_shrink="0",
        ),
        rx.text(text, size="1", color=rx.cond(met, theme.TEXT, theme.MUTED)),
        spacing="2",
        align="center",
        width="100%",
    )


def _password_card() -> rx.Component:
    return panel(
        rx.vstack(
            rx.hstack(
                icon_badge("key-round", theme.ACCENT, size=18, box="42px"),
                rx.vstack(
                    rx.text("Cambiar la contraseña", size="3", weight="bold", color=theme.TEXT),
                    rx.text("Al cambiarla se cerrará la sesión", size="1", color=theme.MUTED),
                    spacing="0",
                    align="start",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            rx.form(
                rx.vstack(
                    _field(
                        "CONTRASEÑA ACTUAL",
                        rx.input(
                            rx.input.slot(rx.icon("lock", size=15)),
                            type="password",
                            name="current_password",
                            placeholder="Tu contraseña de ahora",
                            value=UserState.current_password,
                            on_change=UserState.set_current_password,
                            size="3",
                            width="100%",
                            required=True,
                        ),
                    ),
                    _field(
                        "NUEVA CONTRASEÑA",
                        rx.input(
                            rx.input.slot(rx.icon("lock-keyhole", size=15)),
                            type=rx.cond(UserState.show_new_pasw, "text", "password"),
                            name="new_password",
                            placeholder="La nueva",
                            value=UserState.new_password,
                            on_change=UserState.set_new_password,
                            size="3",
                            width="100%",
                            required=True,
                        ),
                        show_pasw_switch_security(),  #Switch que muestra la contraseña
                    ),
                    _field(
                        "REPITE LA NUEVA",
                        rx.input(
                            rx.input.slot(rx.icon("lock-keyhole", size=15)),
                            type="password",
                            name="confirm_password",
                            placeholder="Otra vez, para confirmar",
                            value=UserState.confirm_password,
                            on_change=UserState.set_confirm_password,
                            size="3",
                            width="100%",
                            required=True,
                        ),
                    ),
                    #Botón que valida los campos y si está correcto, cambia la contraseña
                    rx.button(
                        rx.icon("key-round", size=16),
                        rx.text("Cambiar contraseña", size="2", weight="medium"),
                        on_click=UserState.change_password,
                        color_scheme="blue",
                        size="3",
                        width="100%",
                        radius="full",
                        cursor="pointer",
                        margin_top="0.5em",
                        _hover={"transform": "translateY(-1px)"},
                        transition="all 0.16s ease",
                    ),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
            align="start",
        ),
    )


def _requirements_card() -> rx.Component:
    """Comprobación en vivo de los requisitos: antes solo se avisaba al fallar."""
    return panel(
        rx.vstack(
            rx.hstack(
                icon_badge("shield-check", theme.SUCCESS, size=17, box="38px"),
                rx.vstack(
                    rx.text("Requisitos", size="3", weight="bold", color=theme.TEXT),
                    rx.text("Se marcan solos al escribir", size="1", color=theme.MUTED),
                    spacing="0",
                    align="start",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            _requirement("ruler", "Al menos 8 caracteres", UserState.pasw_has_length),
            _requirement("case-upper", "Una letra mayúscula", UserState.pasw_has_upper),
            _requirement("hash", "Un número", UserState.pasw_has_digit),
            _requirement("asterisk", "Un carácter especial (!, @, #...)", UserState.pasw_has_special),
            _requirement("copy-check", "Las dos contraseñas coinciden", UserState.pasw_matches),
            rx.box(height="1px", width="100%", background=theme.BORDER),
            info_banner(
                "Usa una contraseña que no repitas en otros sitios. Si la olvidas, puedes recuperarla "
                "desde «¿Olvidaste tu contraseña?» en la pantalla de inicio de sesión.",
                icon="lightbulb",
                color=theme.WARNING,
            ),
            spacing="2",
            width="100%",
            align="start",
        ),
    )


#Página de cambio de contraseña
@rx.page(  #Decorador que indica componente de página
    route="/security",
    title="Seguridad | CalendPy",
    on_load=[  #Funciones al cargar la página
        UserState.on_load,
        UserState.check_autenticated,
        UserState.reset_switch,
        UserState.reset_security,
    ],
)
def security() -> rx.Component:
    return app_shell(
        rx.vstack(
            page_header(
                icon="shield",
                title="Seguridad",
                subtitle="Protege tu cuenta con una contraseña que no uses en ningún otro sitio",
                accent=theme.WARNING,
            ),
            rx.flex(
                rx.box(_password_card(), flex="1 1 380px", min_width="0"),
                rx.box(_requirements_card(), flex="1 1 320px", min_width="270px"),
                width="100%",
                gap="18px",
                wrap="wrap",
                align="start",
            ),
            spacing="5",
            width="100%",
            max_width="900px",
            margin="0 auto",
            align="center",
        ),
    )
