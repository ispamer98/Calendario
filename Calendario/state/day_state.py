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
    current_day: Optional[Day] = None
    show_editor: bool = False
    loading: bool = False
    current_meal: str = ""
    current_dinner: str = ""
    current_comments: List[Comment] = []
    last_loaded_day_id: int = None
    show_comment_input: bool = False
    new_comment_text: str = ""


    @rx.event
    async def load_day_comments(self, day_id: int):
        self.last_loaded_day_id = day_id
        comments = await get_day_comments(day_id)
        self.current_comments = comments

    @rx.var
    def reversed_comments(self) -> list[Comment]:
        return list(reversed(self.current_comments))

    @rx.event
    def clear_current_comments(self):
        self.current_comments = []

    @rx.event
    def close_comment_input(self):
        self.show_comment_input = False
        self.new_comment_text=""
        

    @rx.event
    def set_new_comment_text(self, value: str):
        self.new_comment_text = value

    @rx.event
    def toggle_comment_input(self):
        self.show_comment_input = not self.show_comment_input
        if not self.show_comment_input:
            self.new_comment_text = ""

    @rx.event
    async def add_comment(self, day: Day):
        if not self.new_comment_text.strip():
            return rx.toast.error("El comentario no puede estar vacío")

        try:
            user_state = await self.get_state(UserState)
            new_comment = await add_comment_to_day(
                day_id=day.id,
                user_id=user_state.current_user.id,
                content=self.new_comment_text.strip()
            )

            if new_comment:
                # Actualizar estado del calendario
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                
                # Actualizar estado local
                await self.load_day_comments(day.id)
                self.toggle_comment_input()
                return rx.toast.success("Comentario añadido")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.new_comment_text = ""

    @rx.event
    async def delete_comment(self, comment_id: int, day: Day):
        try:
            success = await api_delete_comment(comment_id)
            
            if success:
                # Actualizar comentarios
                await self.load_day_comments(day.id)
                
                # Actualizar estado del día
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                
                return rx.toast.success("Comentario eliminado correctamente")
            return rx.toast.error("Error al eliminar el comentario")
            
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")

    @rx.event
    async def set_current_day(self, day: Day):
        self.current_day = day
        self.current_meal = day.meal or ""
        self.current_dinner = day.dinner or ""
        self.show_editor = True

    @rx.event
    def set_meal(self, value: str):
        self.current_meal = value

    @rx.event
    def set_dinner(self, value: str):
        self.current_dinner = value

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

    @rx.event
    async def update_day(self, form_data: dict):
        self.loading = True
        try:
            if not self.current_day:
                return

            meal = self.current_meal or None
            dinner = self.current_dinner or None
            updated = False

            if meal != self.current_day.meal:
                await update_day_meal(self.current_day.id, meal)
                updated = True

            if dinner != self.current_day.dinner:
                await update_day_dinner(self.current_day.id, dinner)
                updated = True

            if updated:
                updated_day = await get_day_details(self.current_day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                toast_message = "Día actualizado correctamente"
            else:
                toast_message = "No se detectaron cambios"

            self.clear_current_day()
            return rx.toast.success(toast_message, position="top-center")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.loading = False