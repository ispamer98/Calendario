
from turtle import position
import reflex as rx
from typing import Optional, List
from Calendario.database.database import SupabaseAPI
from Calendario.model.model import Day, Meal, Comment
from Calendario.state.calendar_state import CalendarState
from Calendario.database.database import SupabaseAPI


class DayState(rx.State):
    current_day: Optional[Day] = None
    show_editor: bool = False
    loading: bool = False
    current_meal: str = ""  # Nueva variable para controlar el valor del select
    current_dinner: str = "" # Nueva variable para controlar el valor del select


    @rx.var
    def formatted_date(self) -> str:
        return str(rx.moment(
            date=self.current_day.date,
            format="dddd, D [de] MMMM [del] YYYY",
            locale="es"
        ))
    @rx.event
    def set_current_day(self, day: Day):
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
