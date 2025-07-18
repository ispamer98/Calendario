#login_card_state

import reflex as rx

#Estado que maneja la lógica del login
class Login_state(rx.State):
    is_open: bool = False
    show_pasw: bool = False

    #Controlamos la visibilidad de la contraseña del formulario de login
    @rx.event 
    def swith_on(self, value: bool = True):
        self.show_pasw = value

    @rx.event
    def swith_off(self, value: bool = False):
        self.show_pasw = value