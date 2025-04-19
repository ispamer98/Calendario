
import reflex as rx
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment
from Calendario.state.calendar_state import CalendarState
from Calendario.database.database import SupabaseAPI
from Calendario.state.user_state import UserState


class DayState(rx.State):
    current_day: Optional[Day] = None
    show_editor: bool = False
    loading: bool = False
    current_meal: str = ""  # Nueva variable para controlar el valor del select
    current_dinner: str = "" # Nueva variable para controlar el valor del select
    current_comments: List[Comment] = []
    last_loaded_day_id: int = None
    show_comment_input: bool = False
    new_comment_text: str = ""
    @rx.event
    async def load_day_comments(self, day_id: int):

        self.last_loaded_day_id = day_id
        db = SupabaseAPI()
        self.current_comments = db.get_comments_for_day(day_id)

    @rx.var
    def reversed_comments(self) -> list[Comment]:
        """Devuelve los comentarios en orden inverso"""
        return list(reversed(self.current_comments))
    @rx.event
    def clear_current_coments(self):
        self.current_comments = []

    @rx.event
    def close_comment_input(self):
        self.show_comment_input = False

    @rx.event
    def set_new_comment_text(self, value: str):
        self.new_comment_text = value
        print(self.new_comment_text," new_coment_text\n", value,"value")

    @rx.event
    def toggle_comment_input(self):
        self.show_comment_input = not self.show_comment_input
        if not self.show_comment_input:
            self.new_comment_text = ""
    @rx.event
    async def add_comment(self, day: Day):
        if self.new_comment_text.strip():
            try:
                user_state = await self.get_state(UserState)
                db = SupabaseAPI()
                
                # Insertar comentario
                new_comment = db.add_comment(
                    day_id=day.id,
                    owner_id=user_state.current_user.id,
                    content=self.new_comment_text.strip()
                )
                
                if new_comment:
                    # Actualizar flag en la base de datos
                    db.update_day_comments_flag(day.id)
                    
                    # Obtener el día actualizado
                    updated_day = db.get_day(day.id)
                    
                    # Actualizar estado del calendario
                    calendar_state = await self.get_state(CalendarState)
                    calendar_state.update_day_in_state(updated_day)
                    
                    # Actualizar estado local
                    await self.load_day_comments(day.id)
                    self.toggle_comment_input()
                    
                    return rx.toast.success("Comentario añadido")
                
            except Exception as e:
                return rx.toast.error(f"Error: {str(e)}")
        
        self.new_comment_text = ""
        return rx.toast.error("El comentario no puede estar vacío")

    @rx.event
    async def delete_comment(self, comment_id: int , day:Day):
        try:
            db = SupabaseAPI()
            # Eliminar el comentario usando la función de la base de datos
            success = db.delete_comment(comment_id)
            
            if success:
                # Recargar comentarios del día actual
                await self.load_day_comments(day.id)
                
                # Actualizar estado del calendario
                updated_day = db.get_day(day.id)
                calendar_state = await self.get_state(CalendarState)
                calendar_state.update_day_in_state(updated_day)
                
                return rx.toast.success("Comentario eliminado correctamente")
            return rx.toast.error("Error al eliminar el comentario")
            
        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
    @rx.var
    def formatted_date(self) -> str:
        return str(rx.moment(
            date=self.current_day.date,
            format="dddd, D [de] MMMM [del] YYYY",
            locale="es"
        ))
    @rx.event
    async def set_current_day(self, day: Day):
        self.current_day = day
        self.current_meal = day.meal if day.meal is not None else ""
        self.current_dinner = day.dinner if day.dinner is not None else ""
        self.show_editor = True


        print("set current day",self.current_day)


    @rx.event
    def set_meal(self, value: str):
        """Manejador para cambios en el select de comidas."""
        self.current_meal = value

    @rx.event
    def set_dinner(self, value: str):
        """Manejador para cambios en el select de cenas."""
        self.current_dinner = value
    @rx.event
    def clear_current_day(self):
        self.current_day = None
        self.show_editor = False

    @rx.event
    def clear_meal(self):
        """Limpia los valores de comida y cena."""
        self.current_meal = ""

    @rx.event
    def clear_dinner(self):
        """Limpia los valores de comida y cena."""
        self.current_dinner = ""
    @rx.event
    async def update_day(self, form_data: dict):
        self.loading = True
        try:
            if self.current_day:
                # Usar los valores del estado en lugar de form_data
                meal = self.current_meal if self.current_meal != "" else None
                dinner = self.current_dinner if self.current_dinner != "" else None
                
                # Actualizar solo si hay cambios
                updated = False
                db = SupabaseAPI()

                if meal != self.current_day.meal:
                    updated_day = await db.update_day_meal(
                        day_id=self.current_day.id,
                        meal=meal,
                    )
                    updated = True

                if dinner != self.current_day.dinner:
                    updated_day = await db.update_day_dinner(
                        day_id=self.current_day.id,
                        dinner=dinner,
                    )
                    updated = True

                if updated:
                    calendar_state = await self.get_state(CalendarState)
                    calendar_state.update_day_in_state(updated_day)
                    toast_message = f"Dia actualizado correctamente"
                else:
                    toast_message = "No se detectaron cambios"

                self.clear_current_day()
                self.clear_meal()
                self.clear_dinner()
                return rx.toast.success(toast_message,position="top-center")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            self.loading = False
