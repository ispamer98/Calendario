import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.password_reset_state import PasswordResetState

@rx.page(route="/forgot_password", title="Recuperar contraseña | CalendPy")
@footer

def forgot_password() -> rx.Component:
    # Botón de volver al login en móvil y desktop
    back_button = rx.box(
        rx.mobile_only(
            rx.button(
                rx.icon("arrow-left", size=18),
                on_click=rx.redirect("/login"),
                variant="soft",
                color_scheme="blue",
                size="2",
                radius="full",
                _hover={"transform": "scale(1.05)"},
                style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
            )
        ),
        rx.tablet_and_desktop(
            rx.button(
                rx.icon("arrow-left", size=18),
                "Login",
                on_click=rx.redirect("/login"),
                variant="soft",
                color_scheme="blue",
                size="2",
                radius="full",
                _hover={"transform": "scale(1.05)"},
                style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
            )
        ),
        z_index="1000"
    )

    # Formulario de restablecimiento
    form = rx.vstack(
        rx.heading(
            "Restablecer contraseña",
            size="6",
            text_align="center",
            margin_top=["2em", "10em"],
        ),
        rx.input(
            rx.input.slot(rx.icon("mail")),
            placeholder="Correo electrónico",
            type="email",
            size="3",
            width=[ "100%","50%",],
            value=PasswordResetState.email,
            on_change=PasswordResetState.set_email,
        ),
        rx.button(
            rx.icon("send", size=18),
            "Enviar enlace",
            size="3",
            variant="surface",
            color_scheme="blue",
            radius="full",
            width=["90%", "50%"],
            is_loading=PasswordResetState.loading,
            on_click=PasswordResetState.send_reset_link,
            _hover={"transform": "scale(1.05)"},
        ),
        rx.hstack(
            rx.text("¿Recuerdas tu contraseña?", size="3"),
            rx.link(
                "Inicia sesión",
                on_click=rx.redirect("/login"),
                size="3",
            ),
            justify="center",
            opacity="0.8",
        ),
        spacing="6",
        width="100%",
        align="center",
        min_height="85vh",
        position="relative",
    )

    return rx.container(
        back_button,
        form,
        padding="2em",
        height="100%",
        class_name="forgot-password-container",
    )
