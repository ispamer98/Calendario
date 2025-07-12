# Calendario/components/day_button.py


import reflex as rx
from Calendario.model.model import Day
from Calendario.state.calendar_state import CalendarState
from Calendario.state.day_state import DayState

def day_button(day: rx.Var[Day]) -> rx.Component:
    return rx.box(
        rx.popover.root( #Iniciamos el popver
            rx.popover.trigger(
                rx.button( #Botón disparador
                    rx.vstack(
                        #Estilos diferentes para el día actual y el resto de dias
                        rx.mobile_only( #Formato para movil
                            rx.text(
                                rx.moment(day.date, format="D"), #Muestra el dia con un solo digito siempre que sea posible
                                size="3", 
                                weight="bold", 
                                color=rx.cond(
                                    day.date == CalendarState.current_date_str, 
                                    "black", 
                                    "gray.600" 
                                )
                            )
                        ),
                        rx.tablet_and_desktop( #Formato para tablet y escritorio
                            rx.text(
                                rx.moment(day.date, format="DD"), #Muestra el día con dos dígitos 
                                size="2", 
                                weight="bold", 
                                color=rx.cond( 
                                    day.date == CalendarState.current_date_str,
                                    "black",
                                    "gray.600" 
                                )
                            )
                        ),
                        rx.vstack( #Alojamos iconos de comida/cena/comentarios
                            rx.hstack(
                                rx.cond( #Comprobamos si existe comida asociada para el día
                                    day.meal != None, 
                                    rx.icon("utensils-crossed", 
                                            size=12, 
                                            color="var(--green-9)"),
                                    
                                ),
                                rx.cond( #Comprobamos si existe cena asociada para el día
                                    day.dinner != None, 
                                    rx.icon("utensils-crossed",
                                            size=12, 
                                            color="var(--blue-9)"), 
                                    
                                ),
                                rx.cond( #Comprobamos si existen comentarios asociados para el día
                                    day.comments == True,
                                    rx.icon("message-square-more", 
                                            size=12, 
                                            color="var(--orange-9)"), 
                                    
                                ),
                                spacing="1", 
                                justify="center",
                                padding_x="1",
                                position="relative" 
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
                    style={ #Estilos según el tamaño de pantalla
                        
                        #Estilos para el movil
                        "width": "12vw", 
                        "height": "12vw", 
                        "min_width": "40px", 
                        "min_height": "40px", 
                        "max_width": "70px", 
                        "max_height": "70px", 
                        
                        #Estilos para tablet (pantallas ≥ 768 px)
                        "@media (min-width: 768px)": {
                            "width": "10vw",
                            "height": "10vw", 
                            "max_width": "60px", 
                            "max_height": "60px" 
                        },
                        #Estilos para escritorio (pantallas ≥ 1024 px)
                        "@media (min-width: 1024px)": {
                            "width": "8vw", 
                            "height": "8vw", 
                            "max_width": "70px", 
                            "max_height": "70px" 
                        }
                    },
                    padding="1", 
                    border_radius="md",
                    background=rx.cond( #Estilos distintos para el día actual y el resto de días
                        day.date == CalendarState.current_date_str, 
                        "linear-gradient(45deg, #4F46E5, #3B82F6)", 
                        "rgba(255, 255, 255, 0.05)" 
                    ),
                    border=rx.cond( 
                        day.date == CalendarState.current_date_str,
                        "none", 
                        "1px solid rgba(255, 255, 255, 0.1)" 
                    ),
                    _hover={ 
                        "transform": "scale(1.05)", 
                    },
                    transition="all 0.2s"
                    
                    
                )
            ),
            rx.popover.content( #Contenido del popover, al hacer click en el día
                rx.vstack(
                    rx.hstack( #Encabezado ( fecha más botones de acción )
                        rx.text(
                        rx.moment(
                            day.date, #Fecha del día
                            format="dddd, D [de] MMMM [del] YYYY", 
                            locale="es"
                        ),
                        size="2",
                        style={"text-transform": "capitalize"} 
                        ),
                        
                        rx.icon( #Icono de edición de comida/cena
                            "utensils-crossed",
                            color="grey", 
                            size=18, 
                            
                            style={
                                "cursor": "pointer",
                            },
                            _hover={
                                "transform": "scale(1.3)", 
                                "transition": "transform 0.2s" 
                            },
                            on_click=DayState.set_current_day(day)  #Apertura del editor de comida/cena para el día seleccionado
                        ),
                        rx.icon( #Icono de edición para los comentarios
                            "message-square-more",
                            color="grey",
                            size=18, 
                            style={
                                "cursor": "pointer", 
                            },
                            _hover={
                                "transform": "scale(1.3)", 
                                "transition": "transform 0.2s" 
                            },
                            on_click=DayState.toggle_comment_input #Dispara el input para escribir comentario
                        ),
                        width="100%",
                        justify="between",
                    ),
                    
                    
                    rx.divider(), #Línea divisoria
                    rx.cond( #Info de la comida, si existe, muestra el registro
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
                        rx.box() #Si no existe comida, crea un espacio sin información
                    ),
                    rx.cond( #Info de la cena, si existe, muestra el registro
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
                        rx.box() #Si no existe cena, crea un espacio sin información
                    ),
                    rx.cond( #Info de los comentarios, si existen, muestra el registro
                        DayState.current_comments.length() > 0,
                        rx.vstack(
                            rx.text(
                                "Comentarios:",
                                size="2",
                                color="var(--orange-9)",
                                weight="bold",
                                width="100%" 
                            ),
                            rx.box( #Contenedor para los comentarios
                                rx.foreach( 
                                    DayState.reversed_comments, #Formatea el orden de los comentarios
                                    lambda comment: rx.box(
                                        rx.vstack( #Contenedor vertical para comentarios
                                            rx.hstack( #Contenedor horizontal para usuario y fecha
                                                rx.box( #Caja para el usuario
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
                                                rx.box( #Caja para la fecha del comentario
                                                    rx.moment(
                                                        comment.created_at, 
                                                        format="DD/MM HH:mm", 
                                                        color="gray.500", 
                                                        size="1" 
                                                    ),
                                                    margin_left="auto" 
                                                ),
                                                rx.icon( #Icono para eliminar el comentario
                                                    "trash", 
                                                    color="var(--red-9)",
                                                    size=16, 
                                                    style={"cursor" : "pointer"},
                                                    _hover={ 
                                                        "transform" : "scale(1.3)",
                                                        "transition" : "transform 0.2s" 
                                                    },
                                                    on_click= lambda: DayState.delete_comment(comment.id,day), #Función que borra el comentario
                                                    margin_right="1em"

                                                ),
                                                width="100%",
                                                align_items="center" 
                                            ),
                                            rx.hstack( #Nuevo contenedor horizontal para el contenido del comentario
                                                rx.text("·", color="var(--jade-9)", size="2"),
                                                rx.scroll_area(
                                                    rx.text( #Zona de texto para el contenido del comentario
                                                        comment.content,
                                                        color="var(--jade-11)",
                                                        size="2",
                                                        weight="light",
                                                        style={
                                                            "display": "block", #Visualización en una linea si es posible
                                                            "overflow": "auto", #Scroll si es necesario, para no ocupar más de lo permitido por comentario
                                                            "text_overflow": "ellipsis", #Añade puntos suspensivos si fuese necesario
                                                            "max_height": "2.8em",  
                                                            "line_height": "1.4em", 
                                                        },
                                                        white_space="normal",  #Permite saltos de línea
                                                    ),
                                                    style={
                                                        "max_height": "2.8em",  #Contenedor con máximo dos lineas
                                                        "overflow_y": "auto",   #Scroll si hay más de dos líneas
                                                        "width": "100%", 
                                                    },
                                                ),
                                                spacing="2", #Espacio entre punto y comentario
                                                padding_left="0.5em",
                                                width="100%" 
                                            ),
                                            spacing="1", #Separación entre comentarios
                                            padding_y="0.5em", 
                                            width="100%" 
                                        ),
                                        border_bottom="1px solid rgba(255, 255, 255, 0.05)", # línea divisoria inferior
                                        padding_bottom="2px",
                                        margin_bottom="2px", 
                                        width="100%", 
                                        min_height="40px", 
                                    )
                                ),
                                max_height="180px",  #Altura máxima del contenedor de comentarios
                                overflow_y="auto", #Activa el scroll vertical sobre los comentarios 
                                width="100%",
                            ),
                            spacing="1",
                            width="100%" 
                        ),
                        rx.box() #Caja vacía para ocupar el espacio del input
                    ),
                    rx.cond( #Condición para ver el input de comentario
                        DayState.show_comment_input,
                        rx.hstack( #Contenedor para el input de comentario
                            rx.input( 
                                placeholder="Escribe tu comentario...",
                                value=DayState.new_comment_text, #Lee el contenido alojado en el estado
                                on_change=lambda value: DayState.set_new_comment_text(value), #Al cambiar, manda el valor al estado
                                size="1", 
                                width="100%", 
                            ),
                            rx.button( #Botón de añadir comentario
                                rx.icon("check"),
                                on_click=DayState.add_comment(day), #Activa la función que añade el comentario
                                size="1", 
                                variant="soft", 
                                color_scheme="green",
                                disabled=DayState.new_comment_text.strip() == "" #Cuando se cierra, resetea el input en el estado
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
                collision_padding=20,  #Separación con el borde de la pantalla
                avoid_collisions=True,  #Evitamos que se solapen los items
                sticky="partial",  #Mantiene el contenido visible
            ),
            on_open_change=DayState.close_comment_input #Cerramos el input
            
        ),
        position="relative",
        margin="2px",
        flex_shrink="0", #Impide que se encoja
        on_click=lambda: [DayState.load_day_comments(day.id),], #Carga de comentarios asociados
        
    )