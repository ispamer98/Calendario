import logging
import reflex as rx
from typing import Optional

from Calendario.utils.api import delete_meal_by_id
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

logger = logging.getLogger(__name__)


class MealCardState(rx.State):
    """Estado de las tarjetas del recetario.

    Antes llevaba también el "seleccionada"/"en hover" para simular acciones
    táctiles: con la cuadrícula nueva los botones de editar y borrar están
    siempre visibles, así que aquí solo queda la confirmación de borrado.
    """

    # Estado para confirmar eliminación
    show_delete_confirm: bool = False
    meal_to_delete: str = ""
    meal_id_to_delete: Optional[int] = None

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
        #Borrar una comida la quita también de los días que la tuvieran puesta,
        #así que exigimos sesión iniciada (cualquier cliente puede invocar un
        #manejador de estado, venga o no de un botón de la interfaz)
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        if not self.meal_id_to_delete:
            self.close_delete_confirm()
            return rx.toast.error("No se pudo identificar la comida a eliminar")

        try:
            #El id de usuario va a la consulta: la base de datos comprueba que
            #esa comida es de un recetario suyo antes de borrar nada
            success = await delete_meal_by_id(self.meal_id_to_delete, user_state.current_user.id)

            if success:
                calendar_state = await self.get_state(CalendarState)
                await calendar_state.load_meals()

                name = self.meal_to_delete
                self.close_delete_confirm()

                return rx.toast.success(f"Comida '{name}' eliminada correctamente")

            self.close_delete_confirm()
            return rx.toast.error("No se pudo eliminar la comida")

        except Exception as e:
            logger.error(f"Error eliminando comida: {e}")
            self.close_delete_confirm()
            return rx.toast.error(f"Error al eliminar: {str(e)}")
