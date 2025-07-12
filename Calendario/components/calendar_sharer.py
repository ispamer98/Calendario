# Calendario/components/calendar_sharer.py

import reflex as rx
from Calendario.state.calendar_state import CalendarState

def user_badge(username: str, is_owner: bool = False) -> rx.Component: #Definimos los parametros que vamos a necesitar para identificar el usuario y si es el dueño del calendario
    return rx.hstack(
        rx.cond( #Si es el dueño, se mostrará con un icono diferente
            is_owner,
            rx.icon("crown", size=16, color="var(--gold-9)"),
            rx.icon("user", size=16, color="var(--slate-11)")
        ),
        rx.text(
            username, #Estilos diferentes para dueño y usuarios
            color=rx.cond(is_owner, "var(--gold-11)", "var(--slate-12)"), #Colores del texto
            size="2", 
            weight="medium" 
        ),
        padding_y="1",
        padding_x="2", 
        border_radius="md", 
        background=rx.cond(is_owner, "var(--gold-3)", "var(--slate-3)"), #Se mostrará el fondo de un color diferente si es el dueño
        spacing="2",
        width="100%"
    )

def calendar_sharer() -> rx.Component: #Definimos el componente
    return rx.dialog.root( 
        rx.dialog.trigger( #El disparador será un boton.
            rx.button(
                "Compartir calendario", 
                variant="soft", 
                size="3", 
                _hover={"transform": "scale(1.05)"}, 
                on_click=CalendarState.load_shared_users #Cargará los usuarios asociados al calendario
                
            )
        ),
        rx.dialog.content( #Contenido del dialogo.
            rx.vstack(
                rx.heading("Compartir calendario", size="5"),
                rx.divider(margin_y="2"),
                rx.vstack(
                    rx.text("Accesos actuales:", size="2", color="var(--slate-11)"), 
                    #Creamos un componente para el dueño, y uno más por cada usuario compartido
                    user_badge(CalendarState.owner_username, is_owner=True), 
                    rx.foreach( 
                        CalendarState.shared_users,
                        lambda user: user_badge(user.username)
                    ),
                    spacing="2", 
                    width="100%", #
                    max_height="200px", 
                    overflow_y="auto", #Habilitamos scroll vertical en auto
                    padding_right="2" 
                ),
                rx.vstack( #Iniciamos el componente para compartir el calendario
                    rx.text("Agregar usuario:", size="2", color="var(--slate-11)"), 
                    rx.input( #Input para agregar un nombre de usuario
                        placeholder="Nombre de usuario", 
                        value=CalendarState.username_to_share, 
                        on_change=CalendarState.set_username_to_share, 
                        autofocus=True, 
                        variant="surface" 
                    ),
                    spacing="2", 
                    width="100%" 
                ), 
                rx.hstack( 
                    rx.dialog.close( 
                        rx.button( #Botón que cerrará el dialogo
                            "Cancelar", 
                            variant="soft", 
                            color_scheme="gray", 
                            _hover={"bg": "var(--slate-4)"} 
                        )
                    ),
                    rx.button( #Agregamos el boton para compartir
                        "Compartir", 
                        color_scheme="blue", 
                        variant="solid",
                        on_click=CalendarState.share_calendar, #Lanza la función que añade un usuario al calendario
                        _hover={"transform": "scale(1.05)"} 
                    ),
                    spacing="3", 
                    justify="end", 
                    width="100%" 
                ),
                rx.cond( #Si existe algún error, lo mostraremos
                    CalendarState.error_message, 
                    rx.text(
                        CalendarState.error_message, 
                        color="var(--red-11)",  
                        size="1", 
                        weight="medium"
                    )
                ),
                spacing="4",
                width="100%" 
            ),
            style={"max_width": "400px"}, 
            background="var(--slate-2)", 
            border="1px solid var(--slate-6)", 
            box_shadow="xl"
        ),
        
        open=CalendarState.show_calendar_sharer, #Si cambia el estado del componente y lo muestra
        on_open_change=lambda opened: ( #Alternamos el estado del componente
            rx.cond(
    opened,
    CalendarState.open_calendar_sharer(), #Si el estado es abierto, muestra el componente 
    CalendarState.close_calendar_sharer() #Si el estado es cerrado, no muestra el componente
)
    ))