# Calendario/pages/reset_password.py
import reflex as rx
from Calendario.components.footer import footer
from Calendario.state.password_reset_state import PasswordResetState

# Reset Password Page
@rx.page(route="/reset_password", title="Crear nueva contraseña | CalendPy", on_load=PasswordResetState.on_load)
@footer
def reset_password() -> rx.Component:
    return rx.center(
        rx.container(
            # Back button identical to login_form
            rx.box(
                rx.mobile_only(
                    rx.button(
                        rx.icon("arrow-left", size=18),
                        on_click=rx.redirect("/"),
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
                        "Inicio",
                        on_click=rx.redirect("/"),
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        style={"position": "fixed", "left": "1.5rem", "top": "1.5rem"},
                    )
                ),
                z_index="1000",
            ),

            rx.vstack(
                # Title section
                rx.center(
                    rx.heading(
                        "Crear nueva contraseña",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),

                # New password field
                rx.vstack(
                    rx.text(
                        "Nueva contraseña",
                        size="3",
                        weight="medium",
                        width="100%",
                        text_align="left",
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
                    spacing="2",
                    width="100%",
                ),

                # Confirm password field
                rx.vstack(
                    rx.text(
                        "Confirmar contraseña",
                        size="3",
                        weight="medium",
                        width="100%",
                        text_align="left",
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("lock")),
                        placeholder="Confirmar contraseña",
                        type="password",
                        size="3",
                        width="100%",
                        value=PasswordResetState.confirm_password,
                        on_change=PasswordResetState.set_confirm_password,
                    ),
                    spacing="2",
                    width="100%",
                ),

                # Submit button
                rx.button(
                    rx.icon("check", size=18),
                    "Cambiar contraseña",
                    size="3",
                    variant="surface",
                    color_scheme="blue",
                    radius="full",
                    _hover={"transform": "scale(1.05)"},
                    on_click=PasswordResetState.update_password,
                    is_loading=PasswordResetState.loading,
                    width="100%",
                ),

                # Link to login
                rx.center(
                    rx.vstack(
                        rx.hstack(
                            rx.text("¿Ya recuerdas tu contraseña?", size="3"),
                            rx.link(
                                "Inicia sesión",
                                on_click=rx.redirect("/login"),
                                size="3",
                            ),
                        ),
                    ),
                    opacity="0.8",
                    spacing="2",
                    width="100%",
                ),

                spacing="6",
                width="100%",
            ),

            max_width="28em",
            padding="2em",
        ),
        width="100%",
        padding_top="4em",
    )
