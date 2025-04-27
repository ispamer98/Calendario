# Calendario/pages/reset_password.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.password_reset_state import PasswordResetState

@rx.page(route="/reset_password", title="Nueva contraseña | CalendPy", on_load=PasswordResetState.on_load)
@footer
def reset_password() -> rx.Component:
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

    # Formulario de nueva contraseña
    form = rx.vstack(
        rx.heading(
            "Establecer nueva contraseña",
            size="6",
            text_align="center",
            margin_top=["2em", "10em"],
        ),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Nueva contraseña",
            type="password",
            size="3",
            width="100%",
            value=PasswordResetState.new_password,
            on_change=PasswordResetState.set_new_password,
        ),
        rx.input(
            rx.input.slot(rx.icon("lock")),
            placeholder="Confirmar nueva contraseña",
            type="password",
            size="3",
            width="100%",
            value=PasswordResetState.confirm_password,
            on_change=PasswordResetState.set_confirm_password,
        ),
        rx.button(
            rx.icon("check", size=18),
            "Actualizar contraseña",
            size="3",
            variant="surface",
            color_scheme="blue",
            radius="full",
            width=["90%", "50%"],
            is_loading=PasswordResetState.loading,
            on_click=PasswordResetState.update_password,
            _hover={"transform": "scale(1.05)"},
        ),
        rx.hstack(
            rx.text("¿Ya recuerdas tu contraseña?", size="3"),
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
        class_name="reset-password-container",
    )
