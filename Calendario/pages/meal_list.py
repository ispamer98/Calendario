import reflex as rx
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState
from Calendario.state.meal_card_state import MealCardState
from Calendario.components.user_navbar import user_navbar
from Calendario.components.meal_editor import new_meal_input
from Calendario.components.meal_card import meal_list_grid

# Página de listado de comidas
@rx.page(
    route="/meal_list",
    title="Comidas | CalendPy",
    on_load=[
        CalendarState.reset_calendars,
        CalendarState.clean,
        CalendarState.load_meals,
        MealCardState.deselect_meal,
        MealCardState.clear_hovered_meal,
    ],
)
def meal_list() -> rx.Component:
    return rx.vstack(
        user_navbar(),
        new_meal_input(),
        
        # Contenido principal de la página
        rx.container(
            rx.vstack(
                # Cabecera de la página
                rx.hstack(
                    rx.vstack(
                        rx.heading(
                            "Lista de Comidas",
                            size="7",
                            weight="bold",
                            color="var(--slate-12)",
                        ),
                        rx.text(
                            "Gestiona todas las comidas disponibles para tu calendario",
                            size="3",
                            color="var(--slate-11)",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    # Botón para añadir nueva comida
                    rx.button(
                        rx.hstack(
                            rx.icon("plus", size=18),
                            rx.text("Añadir"),
                            spacing="2",
                        ),
                        color_scheme="green",
                        variant="solid",
                        size="3",
                        on_click=DayState.open_new_meal_input,
                        _hover={
                            "transform": "translateY(-2px)",
                            "box_shadow": "0 8px 25px rgba(72, 187, 120, 0.3)"
                        },
                        transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    ),
                    width="100%",
                    align="center",
                    padding_top="2em",
                    padding_bottom="1em",
                ),
                
                # Grid de comidas
                rx.box(
                    meal_list_grid(),
                    width="100%",
                    min_height="60vh",
                ),
                
                # Información y guías
                rx.vstack(
                    # Información sobre uso
                    rx.box(
                        rx.hstack(
                            rx.icon("info", size=18, color="var(--blue-9)"),
                            rx.text(
                                "Estas comidas estarán disponibles para seleccionar tanto en 'Comida' como en 'Cena' en tu calendario.",
                                size="2",
                                color="var(--slate-11)",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        background="var(--blue-2)",
                        padding="1em",
                        border_radius="lg",
                        border="1px solid var(--blue-5)",
                        width="100%",
                    ),
                    
                    # Guías de uso
                    rx.hstack(
                        # Instrucciones para móvil
                        rx.mobile_only(
                            rx.box(
                                rx.hstack(
                                    rx.icon("smartphone", size=16, color="var(--green-9)"),
                                    rx.vstack(
                                        rx.text(
                                            "Toca una comida para seleccionarla",
                                            size="2",
                                            weight="medium",
                                        ),
                                        rx.text(
                                            "Toca fuera de la tarjeta para cancelar la selección",
                                            size="1",
                                            color="var(--slate-10)",
                                        ),
                                        spacing="0",
                                    ),
                                    spacing="2",
                                ),
                                background="var(--green-2)",
                                padding="1em",
                                border_radius="lg",
                                border="1px solid var(--green-5)",
                                width="100%",
                            )
                        ),
                        
                        # Instrucciones para desktop
                        rx.tablet_and_desktop(
                            rx.box(
                                rx.hstack(
                                    rx.icon("mouse-pointer", size=16, color="var(--blue-9)"),
                                    rx.vstack(
                                        rx.text(
                                            "Pasa el cursor sobre una comida para destacarla",
                                            size="2",
                                            weight="medium",
                                        ),
                                        rx.text(
                                            "Se expandirá y el resto se difuminará",
                                            size="1",
                                            color="var(--slate-10)",
                                        ),
                                        spacing="0",
                                    ),
                                    spacing="2",
                                ),
                                background="var(--blue-2)",
                                padding="1em",
                                border_radius="lg",
                                border="1px solid var(--blue-5)",
                                width="100%",
                            )
                        ),
                        
                        spacing="2",
                        width="100%",
                    ),
                    
                    spacing="3",
                    width="100%",
                    margin_top="2em",
                ),
                
                spacing="4",
                width="100%",
                max_width="1400px",
                align="start",
            ),
            padding_top="6em",
            padding_x="1em",
            width="100%",
        ),
        
        width="100%",
        spacing="0",
        min_height="100vh",
        background="linear-gradient(180deg, var(--slate-1) 0%, var(--slate-2) 100%)",
    )