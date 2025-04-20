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
                                    day.comments == True,
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
                    transition="all 0.2s",
                    
                    
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
                            "utensils-crossed",
                            color="grey",  # Color razonable para un botón de edición
                            size=18,
                            
                            style={
                                "cursor": "pointer",    # Cambia el cursor al pasar sobre el icono
                            },
                            _hover={
                                "transform": "scale(1.3)",  # Aumenta de tamaño en hover
                                "transition": "transform 0.2s"  # Transición suave
                            },
                            on_click=DayState.set_current_day(day)  # Al hacer clic, se abre meal_editor(day)
                        ),
                        rx.icon(
                            "message-square-more",
                            color="grey",
                            size=18,
                            style={
                                "cursor": "pointer",    # Cambia el cursor al pasar sobre el icono
                            },
                            _hover={
                                
                                "transform": "scale(1.3)",  # Aumenta de tamaño en hover
                                "transition": "transform 0.2s"  # Transición suave
                            },
                            on_click=DayState.toggle_comment_input
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
                        DayState.current_comments.length() > 0,
                        rx.vstack(
                            rx.text(
                                "Comentarios:", 
                                size="2", 
                                color="var(--orange-9)", 
                                weight="bold",
                                width="100%"
                            ),
                            rx.box(
                                rx.foreach(
                                    DayState.reversed_comments,
                                    lambda comment: rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.box(
                                                    rx.text(
                                                        comment.user.username,
                                                        weight="bold",
                                                        color="var(--accent-9)",
                                                        size="2",
                                                        padding_x="0.5em",
                                                    ),
                                                    background="rgba(255, 255, 255, 0.1)",
                                                    border_radius="4px",
                                                    margin_right="1em"
                                                ),
                                                rx.box(
                                                    rx.moment(
                                                        comment.created_at, 
                                                        format="DD/MM HH:mm",
                                                        color="gray.500",
                                                        size="1"
                                                    ),
                                                    margin_left="auto"
                                                ),
                                                rx.icon(
                                                    "trash",
                                                    color="var(--red-9)",
                                                    size=16,
                                                    style={"cursor" : "pointer"},
                                                    _hover={
                                                        "transform" : "scale(1.3)",
                                                        "transition" : "transform 0.2s"
                                                    },
                                                    on_click= lambda: DayState.delete_comment(comment.id,day),
                                                    margin_right="1em"

                                                ),
                                                width="100%",
                                                align_items="center"
                                            ),
                                            rx.hstack(
                                                rx.text("·", color="var(--jade-9)", size="2"),
                                                rx.scroll_area(
                                                    rx.text(
                                                        comment.content,
                                                        color="var(--jade-11)",
                                                        size="2",
                                                        weight="light",
                                                        style={
                                                            "display": "block",
                                                            "overflow": "auto",
                                                            "text_overflow": "ellipsis",
                                                            "max_height": "2.8em",  # Aproximadamente 2 líneas (ajusta según tu fuente/size)
                                                            "line_height": "1.4em", # Asegura el cálculo de altura de línea
                                                        },
                                                        white_space="normal",  # Permite saltos de línea
                                                    ),
                                                    style={
                                                        "max_height": "2.8em",  # Igual que el texto para dos líneas
                                                        "overflow_y": "auto",   # Scroll si hay más de dos líneas
                                                        "width": "100%",
                                                    },
                                                ),
                                                spacing="2",
                                                padding_left="0.5em",
                                                width="100%"
                                            ),
                                            spacing="1",
                                            padding_y="0.5em",
                                            width="100%"
                                        ),
                                        border_bottom="1px solid rgba(255, 255, 255, 0.05)",
                                        padding_bottom="2px",
                                        margin_bottom="2px",
                                        width="100%",
                                        min_height="40px",
                                    )
                                ),
                                max_height="180px",  # Ajusta según tu diseño
                                overflow_y="auto",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%"
                        ),
                        rx.box()
                    ),
                    rx.cond(
                        DayState.show_comment_input,
                        rx.hstack(
                            rx.input(
                                placeholder="Escribe tu comentario...",
                                value=DayState.new_comment_text,
                                on_change=lambda value: DayState.set_new_comment_text(value),
                                size="1",
                                width="100%",
                            ),
                            rx.button(
                                rx.icon("check"),
                                on_click=DayState.add_comment(day),
                                size="1",
                                variant="soft",
                                color_scheme="green",
                                disabled=DayState.new_comment_text.strip() == ""
                            ),
                            spacing="2",
                            width="100%"
                        )
                    ),
                    spacing="2",
                    padding="2",
                    width="260px",
                    min_width="200px"
                ),

                style={
                    "max-width": "100vw"
                },
                align="start", 
                collision_padding=20,  # Añade padding para evitar colisiones
                avoid_collisions=True,  # Intenta evitar colisiones con otros elementos
                sticky="partial",  # Mantiene el popover visible mientras sea posible
            ),
            on_open_change=DayState.close_comment_input
            
        ),
        position="relative",
        margin="2px",
        flex_shrink="0",
        on_focus=lambda: [DayState.load_day_comments(day.id),],
        
    )