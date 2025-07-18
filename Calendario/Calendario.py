"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from Calendario.pages.index import index
from Calendario.pages.login import login
from Calendario.pages.register import register
from Calendario.pages.calendar import calendar
from Calendario.pages.forgot_pasword import forgot_password
from Calendario.pages.reset_pasword import reset_password
from Calendario.pages.profile import profile
from Calendario.pages.security import security
import reflex as rx



app = rx.App( #Creamos la app de reflex
        
        #Marcamos el tema de la aplicación
        theme=rx.theme(
        appearance="dark", 
        has_background=False, #Desactiva el fondo por defecto
        radius="large",
        accent_color="blue",
        height="100vh",
        stylesheets=[ #Hoja de estilos para las fuentes de texto
        "https://fonts.googleapis.com/css2?family=Sarina&display=swap",
        ],
        ),
        #Componentes dentro del "head" html
        head_components=[rx.el.link(rel="manifest", href="/manifest.json")],
        style={ #Estilos globales, en este caso, una animación CSS
            "@keyframes spin": {
                "0%": {"transform": "rotate(0deg)"},
                "100%": {"transform": "rotate(360deg)"}
                }
        }
        
)
