import reflex as rx
from typing import Optional, List
from Calendario.utils.api import (
    get_day_comments,
    add_comment_to_day,
    delete_comment as api_delete_comment,
    update_day_meal,
    update_day_dinner,
    get_day_details
)
from Calendario.model.model import Day, Comment
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState


class DayState(rx.State):
    current_day: Optional[Day] = None #Dia en curso
    show_editor: bool = False #Manejador para mostrar el editor del día
    loading: bool = False #Manejador de carga
    current_meal: str = "" #Comida para el día seleccionado
    current_dinner: str = ""   #Cena para el día seleccionado
    current_comments: List[Comment] = [] #Comentarios del día seleccionado
    last_loaded_day_id: int = None #Último día cargado
    show_comment_input: bool = False #Manejador para el input de nuevo comentario
    new_comment_text: str = "" #Texto de nuevo comentario

    #Cargamos los comentarios para el día elegido
    @rx.event
    async def load_day_comments(self, day_id: int):
        self.last_loaded_day_id = day_id
        comments = await get_day_comments(day_id)
        self.current_comments = comments

    #Mostramos los comentarios en orden cronológico
    @rx.var
    def reversed_comments(self) -> list[Comment]:
        return list(reversed(self.current_comments))

    #Limpiamos el registro de comentarios para el día
    @rx.event
    def clear_current_comments(self):
        self.current_comments = []

    #Cerramos el input de comentarios
    @rx.event
    def close_comment_input(self):
        self.show_comment_input = False
        self.new_comment_text=""
        
    #Asigna texto del input a nuevo comentario
    @rx.event
    def set_new_comment_text(self, value: str):
        self.new_comment_text = value

    #Alterna entre mostrar y ocultar el input de comentarios
    @rx.event
    def toggle_comment_input(self):
        self.show_comment_input = not self.show_comment_input
        if not self.show_comment_input:
            self.new_comment_text = ""

    #Función que añade comentario al día seleccionado
    @rx.event
    async def add_comment(self, day: Day):
        #Verificamos que el input de comentario no esté vacío
        if not self.new_comment_text.strip():
            return rx.toast.error("El comentario no puede estar vacío")

        try:
            #Recuperamos el estado del usuario
            user_state = await self.get_state(UserState)
            #Añadimos el comentario al día
            new_comment = await add_comment_to_day(
                day_id=day.id,
                user_id=user_state.current_user.id,
                content=self.new_comment_text.strip()
            )
            #Si el nuevo comentario se añade en el día
            if new_comment:
                #Recuperamos los detalles del día
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                #Actualizamos el día
                await calendar_state.update_day_in_state(updated_day)
                #Cargamos los comentarios
                await self.load_day_comments(day.id)
                #Alternamos para cerrar el input de comentarios
                self.toggle_comment_input()
                #Retornamos mensaje de éxito y recargamos la página
                return [rx.toast.success("Comentario añadido"),
                        await calendar_state.refresh_page()]

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            #Limpiamos el campo de comentario
            self.new_comment_text = ""

    #Función para borrar el comentario
    @rx.event
    async def delete_comment(self, comment_id: int, day: Day):
        try:
            #Eliminamos el comentario desde base de datos
            success = await api_delete_comment(comment_id)
            
            if success:
                #Si tenemos éxito, cargamos de nuevo los comentarios
                await self.load_day_comments(day.id)
                #Cargamos los detalles del día
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                #Actualizamos el día
                await calendar_state.update_day_in_state(updated_day)
                #Retornamos mensaje de éxito y refrescamos la página
                return [rx.toast.success("Comentario eliminado correctamente"),
                        await calendar_state.refresh_page()]
            return rx.toast.error("Error al eliminar el comentario")
            
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")

    #Función para cargar el día seleccionado con sus detalles
    @rx.event
    async def set_current_day(self, day: Day):
        self.current_day = day 
        self.current_meal = day.meal or ""
        self.current_dinner = day.dinner or ""
        self.show_editor = True #Abrimos el editor al seleccionar el día

    @rx.event
    def set_meal(self, value: str):
        self.current_meal = value

    @rx.event
    def set_dinner(self, value: str):
        self.current_dinner = value

    #Al cerrar el día, limpiamos registros
    @rx.event
    def clear_current_day(self):
        self.current_day = None
        self.show_editor = False

    @rx.event
    def clear_meal(self):
        self.current_meal = ""

    @rx.event
    def clear_dinner(self):
        self.current_dinner = ""

    #Función que actualiza el día
    @rx.event
    async def update_day(self, form_data: dict):
        self.loading = True
        try:
            #Si no existe día seleccionado, para la función
            if not self.current_day:
                return
            meal = self.current_meal or None
            dinner = self.current_dinner or None
            updated = False
            #Actualizamos la comida si existen diferencias
            if meal != self.current_day.meal:
                await update_day_meal(self.current_day.id, meal)
                updated = True
            #Actualizamos la cena si existen diferencias
            if dinner != self.current_day.dinner:
                await update_day_dinner(self.current_day.id, dinner)
                updated = True
            #Si encontramos diferencias
            if updated:
                #Guardamos los detalles del día
                updated_day = await get_day_details(self.current_day.id)
                calendar_state = await self.get_state(CalendarState)
                #Actualizamos el día
                await calendar_state.update_day_in_state(updated_day)
                toast_message = "Día actualizado correctamente"
                self.show_editor = False
                #Refrescamos la página
                return await calendar_state.refresh_page()
            else:
                toast_message = "No se detectaron cambios"
            
            #Después de todo, limpiamos el día seleccionado
            self.clear_current_day()
            #Y retornamos el mensaje
            return rx.toast.success(toast_message, position="top-center")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.loading = False