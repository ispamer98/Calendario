# Calendario/components/user_navbar.py

import reflex as rx
from Calendario.components.calendar_creator import calendar_creator
from Calendario.state.user_state import UserState
from Calendario.state.calendar_state import CalendarState


class DrawerState(rx.State):
    is_open: bool = False #Variable que controla la apertura del drawer
    show_profile_submenu: bool = False #Variable que controla la apertura del submenu de perfil
    show_calendar_submenu: bool = False #Variable que controla la apertura del submenu de calendario

    @rx.event
    def open_drawer(self):
        self.is_open = True #Si se ejecuta, abre el drawer

    @rx.event
    def close_drawer(self): 
        self.is_open = False #Si se ejecuta, cierra el drawer
        self.show_profile_submenu = False #Cierra el submenu de perfil
        self.show_calendar_submenu = False #Cierra el submenu de calendario

    @rx.event
    def toggle_profile_submenu(self):
        self.show_profile_submenu = not self.show_profile_submenu #Alterna la apertura del submenu de perfil

    @rx.event
    def toggle_calendar_submenu(self):
        self.show_calendar_submenu = not self.show_calendar_submenu #Alterna la apertura del submenu de calendario

def drawer_menu():
    NAVBAR_HEIGHT = "68px" #Alto de la navbar

    return rx.drawer.root( #Drawer vertical para los submenus
        rx.drawer.trigger(),
        rx.drawer.overlay(
            #Fondo fuera del drawer, al hacer click fuera, lo cierra
            background="rgba(0, 0, 0, 0.6)",
            style={"top": NAVBAR_HEIGHT},
            on_click=DrawerState.close_drawer, 
        ),
        rx.drawer.portal(
            rx.drawer.content(
                rx.flex(
                    rx.drawer.close(
                        rx.button( #Boton de cerrar "X"
                            "×",
                            on_click=DrawerState.close_drawer,
                            variant="ghost",
                            font_size="2.5em",
                            font_weight="bold",
                            color="white",
                            position="absolute",
                            top="20px",
                            right="20px",
                            padding="0",
                            width="auto",
                            height="auto",
                            min_width="auto",
                            background="transparent",
                            _hover={
                                "color": "#F54444",
                                "transform": "scale(1.5)",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                            },
                            _focus={"boxShadow": "none"},
                        ),
                    ),

                    # Submenu de calendario
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("calendar"),
                                rx.text("Calendario"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            margin_top="4em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            on_click=DrawerState.toggle_calendar_submenu, #Al hacer click, abre el submenu
                            
                        ),
                        rx.cond( #Si el submenú está en estado abierto
                            DrawerState.show_calendar_submenu,
                            rx.vstack( #Muestra su contenido
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button( #Botón que redirige a la pagina de calendario
                                    rx.icon("arrow-big-right"),
                                    "Visualizar calendario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    #Cierra el drawer y muestra el calendario
                                    on_click=[DrawerState.close_drawer, UserState.go_calendar_page],
                                ),
                                rx.button( #Boton que abre el creador de calendario
                                    rx.icon("arrow-big-right"),
                                    "Crear Calendario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    #Cierra el drawer y muestra el creador de calendario
                                    on_click=[DrawerState.close_drawer, CalendarState.open_calendar_creator],
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),

                    #Submenu de perfil
                    rx.box(
                        rx.button(
                            rx.hstack(
                                rx.icon("settings"),
                                rx.text("Perfil"),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                width="100%",
                            ),
                            variant="ghost",
                            width="100%",
                            justify_content="flex-start",
                            font_size="lg",
                            font_weight="600",
                            background="transparent",
                            padding_y="0.5em",
                            _hover={
                                "background": "#23282b",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease-in-out",
                                "display": "block",
                                "width": "200%",
                                "max_width" : "200px",
                                "padding_left": "0.5em",
                            },
                            #Al hacer click, abre el submenu
                            on_click=DrawerState.toggle_profile_submenu,
                        ),
                        rx.cond( #Si el submenu está en estado abierto
                            DrawerState.show_profile_submenu,
                            rx.vstack( #Muestra su contenido
                                rx.separator(margin_top="1em",margin_bottom="1em"),
                                rx.button( #Boton que muestra la información del usuario
                                    rx.icon("arrow-big-right"),
                                    "Datos de usuario",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    #Cierra el drawer y redirige a la pagina de información de usuario
                                    on_click=[DrawerState.close_drawer, UserState.go_profile_page],
                                ),
                                rx.button( #Botón que redirige al cambio de contraseña
                                    rx.icon("arrow-big-right"),
                                    "Seguridad",
                                    variant="ghost",
                                    justify_content="flex-start",
                                    width="100%",
                                    font_size="md",
                                    color="white",
                                    padding_left="1.5em",
                                    _hover={
                                        "background": "#23282b",
                                        "color": "#309DCF",
                                    },
                                    #Cierra el drawer y redirige a la pagina de seguridad 
                                    on_click=[DrawerState.close_drawer, UserState.go_security_page],
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%"
                            )
                        )
                    ),

                    direction="column",
                    align_items="start",
                    gap="1.5em",
                    height="100%",
                    padding_x="2em",
                ),
                height=f"calc(100vh - {NAVBAR_HEIGHT})",
                width="18em",
                background_color="#1e1e1e",
                box_shadow="rgba(0, 0, 0, 0.8) 0px 4px 20px",
                border_radius="0 20px 20px 0",
                position="fixed",
                top=NAVBAR_HEIGHT,
                left="0",
                z_index="1200",
            )
        ),
        open=DrawerState.is_open, #Al abrir, actualzia el estado
        placement="left",
        modal=True,
    )

#Componente de navbar ( barra superior de navegación )
def user_navbar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack( #Incluimos el drawer de lo submenus
                drawer_menu(),
                
                #Logo de la aplicación + Nombre de la misma
                rx.heading(
                    rx.hstack(
                        rx.image(
                            src="/favicon.ico",
                            width="43px",
                            height="33px"),
                        rx.text("CalendPy",
                                font_family="Sarina,cursive",
                                font_size="1.5em",),
                        
                    ),
                    background_image="linear-gradient(45deg, #4F46E5, #EC4899)",
                    background_clip="text",
                    font_weight="800",
                    font_size="1em",
                    user_select="none",
                    on_click=DrawerState.open_drawer, #Al hacer click en la cabecera, se abre el drawer
                    _hover={"transform": "scale(1.05)",
                            "cursor": "pointer"},
                ),
                
                rx.spacer(),
                calendar_creator(), #Incluimos el creador de calendario, para poder lanzarlo desde el submenu
                # Menú de usuario
                rx.menu.root( #Creamos un "menu", boton visual con el nombre de usuario
                    rx.menu.trigger(
                        rx.button(
                            rx.hstack(
                                rx.spacer(" "),
                                rx.icon("user"),
                                rx.cond( #Si el usuario está loggeado 
                                    UserState.current_user,
                                    rx.text(UserState.current_user.username), #Muestra su nombre
                                    rx.text("Usuario") #Hasta que carga la info, muestra un usuario generico
                                ),
                                rx.icon("chevron-down"),
                                spacing="2",
                                align="center",
                                color="white",
                                
                            ),
                            variant="ghost",
                            radius="full",
                            background="#23282b",
                            style={
                                "background": "transparent",
                                "color": "white",
                                "border": "1px solid rgba(255, 255, 255, 0.3)",
                                "_hover": {
                                    "background": "rgba(0, 0, 0, 0.2)",
                                    "cursor": "pointer",
                                    "transform": "scale(1.05)"
                                }
                            }
                        )
                    ),
                    rx.menu.content( #Opciones del menú
                        rx.menu.item("Perfil", #Redirige a la información de usuario
                                     rx.icon("settings"),
                                     style={"_hover" : { "background " : "#23282b"}},
                                     on_click=rx.redirect("/profile")
                                     ),
                        rx.menu.separator(), #Separador visual
                        rx.menu.item( #Botón de cerrar sesión en rojo
                            "Cerrar sesión",
                            rx.icon("log-out"), 
                            on_click=UserState.logout, #Función que cierra sesión
                            color="#EF4444",
                            style={"_hover" : { "background " : "#23282b"}}
                        ),
                        width="200px",
                    ),
                    modal=False
                ),
                justify="between",
                align="center", 
                width="100%",
                padding_y="1em",
                padding_x="2em",
                style={"box-sizing": "border-box"}
            ),
            width="100%",
            max_width="100vw",
            style={"overflow-x": "hidden"}
        ),
        position="fixed",
        top="0",
        width="100%",
        z_index="1000",
        border_bottom="1.5px solid #eee",
        border_radius="0 0 20px 20px",
        background="#1e1e1e"
    )
