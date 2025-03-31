import reflex as rx
from Calendario.components import meal_editor
from Calendario.model.model import Day, Meal
from datetime import datetime
from Calendario.state.calendar_state import CalendarState
from Calendario.components.meal_editor import meal_editor
from Calendario.state.day_state import DayState

def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.vstack(
                        rx.mobile_only(
                            rx.text(
                                rx.moment(day.date, format="D"),
                                size="3",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.tablet_and_desktop(
                            rx.text(
                                rx.moment(day.date, format="DD"),
                                size="2",
                                weight="bold",
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str,
                                    "white",
                                    "gray.600"
                                )
                            )
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.cond(
                                    day.meal != None,
                                    rx.icon("utensils-crossed", 
                                            size=12,  # Tamaño fijo pequeño
                                            color="var(--green-9)"),
                                    
                                ),
                                rx.cond(
                                    day.dinner != None,
                                    rx.icon("utensils-crossed",
                                            size=12,
                                            color="var(--blue-9)"),
                                    
                                ),
                                rx.cond(
                                    day.comments.length() > 0,
                                    rx.icon("message-square-more",
                                            size=12,
                                            color="var(--orange-9)"),
                                    
                                ),
                                spacing="1",
                                justify="center",
                                padding_x="1",
                                position="relative"  # Añadido para mejor control
                            ),
                            spacing="1",
                            align="center",
                            width="100%",
                            height="20px"
                        ),
                        spacing="1",
                        align="center",
                        width="100%"
                    ),
                    style={
                        # Estilos base (móvil primero)
                        "width": "12vw",
                        "height": "12vw",
                        "min_width": "40px",
                        "min_height": "40px",
                        "max_width": "70px",
                        "max_height": "70px",
                        
                        # Media queries usando reflex
                        "@media (min-width: 768px)": {
                            "width": "10vw",
                            "height": "10vw",
                            "max_width": "60px",
                            "max_height": "60px"
                        },
                        "@media (min-width: 1024px)": {
                            "width": "8vw",
                            "height": "8vw",
                            "max_width": "70px",
                            "max_height": "70px"
                        }
                    },
                    padding="1",
                    border_radius="md",
                    background=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "linear-gradient(45deg, #4F46E5, #3B82F6)",
                        "rgba(255, 255, 255, 0.05)"
                    ),
                    border=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "none",
                        "1px solid rgba(255, 255, 255, 0.1)"
                    ),
                    box_shadow=rx.cond(
                        day.date == CalendarState.current_date_str,
                        "lg",
                        "sm"
                    ),
                    _hover={
                        "transform": "scale(1.05)",
                        "box_shadow": "xl"
                    },
                    transition="all 0.2s"
                )
            ),
            rx.popover.content(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                        rx.moment(
                            day.date,
                            format="dddd, D [de] MMMM [del] YYYY", 
                            locale="es"
                        ),
                        size="2",
                        style={"text-transform": "capitalize"}
                        ),
                        
                        rx.icon(
                            "pencil",
                            color="grey",  # Color razonable para un botón de edición
                            size=18,
                            
                            style={
                                "cursor": "pointer",    # Cambia el cursor al pasar sobre el icono
                            },
                            _hover={
                                "transform": "scale(1.3)",  # Aumenta de tamaño en hover
                                "transition": "transform 0.2s"  # Transición suave
                            },
                            on_click=DayState.set_current_day(day)  # Al hacer clic derecho, se abre meal_editor(day)
                        ),
                        width="100%",
                        justify="between",
                    ),
                    
                    
                    rx.divider(),
                    rx.cond(
                        day.meal != None,
                        rx.vstack(
                            rx.text("Comida:", 
                                    size="2", 
                                    color="var(--green-9)", 
                                    weight="bold"),
                            rx.text(day.meal, 
                                    size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        day.dinner != None,
                        rx.vstack(
                            rx.text("Cena:", 
                                    size="2", 
                                    color="var(--blue-9)", 
                                    weight="bold"),
                            rx.text(day.dinner, 
                                    size="2"),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        day.comments.length() > 0,
                        rx.vstack(
                            rx.text("Comentarios:", 
                                    size="2", 
                                    color="var(--orange-9)", 
                                    weight="bold"),
                            rx.foreach(
                                day.comments,
                                lambda comment: rx.text(comment, 
                                                        size="1")
                            ),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    spacing="2",
                    padding="2",
                    width="260px",
                    min_width="200px"
                ),

                style={
                    "max-width": "95vw"
                },
                align="start",  # Puedes usar "start", "center", o "end"
                collision_padding=20,  # Añade padding para evitar colisiones
                avoid_collisions=True,  # Intenta evitar colisiones con otros elementos
                sticky="partial",  # Mantiene el popover visible mientras sea posible
            )
        ),
        position="relative",
        margin="2px",
        flex_shrink="0"
    )