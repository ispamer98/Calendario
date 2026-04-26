import reflex as rx
from Calendario.utils.api import delete_meal_by_id
from Calendario.state.calendar_state import CalendarState
from typing import Optional
import time
import asyncio

class MealCardState(rx.State):
    # Controla qué tarjeta está seleccionada (para móvil)
    selected_meal_id: Optional[int] = None
    
    # Controla qué tarjeta está en hover (para desktop)
    hovered_meal_id: Optional[int] = None
    
    # Estado para confirmar eliminación
    show_delete_confirm: bool = False
    meal_to_delete: str = ""
    meal_id_to_delete: Optional[int] = None
    
    # Timestamp de última selección para evitar deselección inmediata
    last_select_time: float = 0.0
    
    # Control para saber si se está haciendo hover en desktop
    is_hovering_desktop: bool = False

    @rx.event
    def handle_click_outside(self):
        """Deselecciona tarjeta solo si se hace click fuera de todas las tarjetas"""
        # Ignorar clicks muy cercanos a la selección para evitar parpadeos
        if time.time() - (self.last_select_time or 0) < 0.1:
            return
        self.deselect_meal()

    @rx.event
    def select_meal(self, meal_id: int):
        """Selecciona una comida (para móvil)"""
        now = time.time()
        self.last_select_time = now
        
        # Siempre seleccionar la nueva tarjeta (no toggle)
        self.selected_meal_id = meal_id
    
    @rx.event
    def deselect_meal(self):
        """Deselecciona todas las tarjetas"""
        self.selected_meal_id = None
        self.is_hovering_desktop = False
    
    @rx.event
    def set_hovered_meal(self, meal_id: int):
        """Establece qué tarjeta está en hover (desktop)"""
        self.hovered_meal_id = meal_id
        self.is_hovering_desktop = True
    
    @rx.event
    def clear_hovered_meal(self):
        """Limpia el hover (desktop)"""
        self.hovered_meal_id = None
        self.is_hovering_desktop = False
    
    @rx.event
    def open_delete_confirm(self, meal_id: int, meal_name: str):
        """Abre el diálogo de confirmación de eliminación"""
        self.meal_id_to_delete = meal_id
        self.meal_to_delete = meal_name
        self.show_delete_confirm = True
    
    @rx.event
    def close_delete_confirm(self):
        """Cierra el diálogo de confirmación"""
        self.show_delete_confirm = False
        self.meal_id_to_delete = None
        self.meal_to_delete = ""
    
    @rx.event
    async def delete_meal(self):
        """Elimina la comida de la base de datos"""
        if not self.meal_id_to_delete:
            self.close_delete_confirm()
            return rx.toast.error("No se pudo identificar la comida a eliminar")
        
        try:
            success = await delete_meal_by_id(self.meal_id_to_delete)
            
            if success:
                calendar_state = await self.get_state(CalendarState)
                await calendar_state.load_meals()
                
                self.close_delete_confirm()
                self.deselect_meal()
                self.clear_hovered_meal()
                
                return rx.toast.success(f"Comida '{self.meal_to_delete}' eliminada correctamente")
            else:
                self.close_delete_confirm()
                return rx.toast.error("No se pudo eliminar la comida")
                
        except Exception as e:
            print(f"Error eliminando comida: {e}")
            self.close_delete_confirm()
            return rx.toast.error(f"Error al eliminar: {str(e)}")