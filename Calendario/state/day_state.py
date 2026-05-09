from Calendario.state.notification_state import NotificationState
import reflex as rx
import re
from typing import Optional, List

from sqlalchemy import Boolean
from Calendario.utils.api import (
    get_day_comments,
    add_comment_to_day,
    delete_comment as api_delete_comment,
    get_shared_users,
    update_day_meal,
    update_day_dinner,
    get_day_details,
    get_all_meals,
    add_new_meal
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
    new_meal: str = ""
    new_meal_description : str = ""
    show_new_meal_input : bool 

    @rx.event
    def open_new_meal_input(self):
        self.show_new_meal_input = True

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

    @rx.event
    def clear_current_comments(self):
        self.current_comments = []

    @rx.event
    def close_new_meal_input(self):
        self.show_new_meal_input = False
        self.new_meal = ""
        self.new_meal_description = ""

    # Setters
    @rx.event
    def set_new_meal(self, value: str):
        self.new_meal = value

    @rx.event
    def set_new_meal_description(self, value: str):
        self.new_meal_description = value

        # Añadir nueva comida

    @rx.event
    async def add_new_meal(self):
        meal = self.new_meal.strip()
        description = self.new_meal_description.strip()

        if not meal or not description:
            return rx.toast.error("Debes rellenar todos los campos")

        # 1️⃣ Máximo 20 caracteres
        if len(meal) > 20:
            return rx.toast.error("El nombre no puede tener más de 20 caracteres")

        # 2️⃣ Solo letras, números y espacios
        if not re.match(r'^[A-Za-z0-9 ]+$', meal):
            return rx.toast.error("El nombre no puede contener caracteres especiales")

        try:
            result = await add_new_meal(meal=meal, description=description)

            if result is None:
                return rx.toast.error("Ya existe una comida con ese nombre")

            calendar_state = await self.get_state(CalendarState)
            await calendar_state.load_meals()
            self.close_new_meal_input()

            return [
                rx.toast.success("Comida añadida"),
                await calendar_state.refresh_page()
            ]

        except Exception:
            return rx.toast.error("Error al añadir la comida")



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
        # 1. Capturamos el texto REAL inmediatamente en una variable local
        texto_comentario = self.new_comment_text.strip()

        if not texto_comentario:
            return rx.toast.error("El comentario no puede estar vacío")

        try:
            user_state = await self.get_state(UserState)
            
            # 2. Guardamos en la base de datos
            new_comment = await add_comment_to_day(
                day_id=day.id,
                user_id=user_state.current_user.id,
                content=texto_comentario
            )

            if new_comment:
                # 3. Actualizamos el estado de la interfaz
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                await calendar_state.update_day_in_state(updated_day)
                await self.load_day_comments(day.id)
                self.toggle_comment_input()

                # --- NOTIFICACIONES ---
                calendar = calendar_state.current_calendar
                if calendar:
                    shared_users = await get_shared_users(calendar.id)
                    author = user_state.current_user.username

                    # Formatear la fecha
                    meses_es = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]
                    fecha_formateada = f"{day.date.day} de {meses_es[day.date.month - 1]}"

                    # Preparar resumen del texto real para el mensaje
                    resumen = (texto_comentario[:47] + "...") if len(texto_comentario) > 50 else texto_comentario

                    for user in shared_users:
                        if user.username != author:
                            NotificationState.enviar_notificacion(
                                titulo="💬 Nuevo comentario",
                                mensaje=f"{author} en '{calendar.name}' ({fecha_formateada}): \"{resumen}\"",
                                destino=user.username
                            )

                return [
                    rx.toast.success("Comentario añadido"),
                    await calendar_state.refresh_page()
                ]
            else:
                return rx.toast.error("No se pudo guardar el comentario.")

        except Exception as e:
            return rx.toast.error(f"Error: {str(e)}")
        finally:
            # Limpiamos el input al final
            self.new_comment_text = ""
        #Función para borrar el comentario
    @rx.event
    async def delete_comment(self, comment_id: int, day: Day):
        try:
            # Eliminamos el comentario desde base de datos
            success = await api_delete_comment(comment_id)
            
            if success:
                # Cargamos de nuevo los comentarios
                await self.load_day_comments(day.id)
                # Cargamos los detalles del día
                updated_day = await get_day_details(day.id)
                calendar_state = await self.get_state(CalendarState)
                # Actualizamos el día
                await calendar_state.update_day_in_state(updated_day)

                # --- NOTIFICACIONES ---
                calendar = calendar_state.current_calendar
                if calendar:
                    shared_users = await get_shared_users(calendar.id)
                    author = (await self.get_state(UserState)).current_user.username

                    # Formatear la fecha del día
                    meses_es = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]
                    dia = day.date.day
                    mes = meses_es[day.date.month - 1]
                    fecha_formateada = f"{dia} de {mes}"

                    for user in shared_users:
                        if user.username != author:
                            NotificationState.enviar_notificacion(
                                titulo="🗑️ Comentario eliminado",
                                mensaje=f"{author} ha eliminado un comentario en '{calendar.name}' del {fecha_formateada}",
                                destino=user.username
                            )
                # ----------------------

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
                updated_day = await get_day_details(self.current_day.id)
                calendar_state = await self.get_state(CalendarState)
                await calendar_state.update_day_in_state(updated_day)

                # --- NOTIFICACIONES ACTUALIZADAS ---
                calendar = calendar_state.current_calendar
                if calendar:
                    shared_users = await get_shared_users(calendar.id)
                    author = (await self.get_state(UserState)).current_user.username

                    # 1. Determinar qué cambió para el mensaje principal
                    cambio_comida = meal != self.current_day.meal
                    cambio_cena = dinner != self.current_day.dinner

                    if cambio_comida and cambio_cena:
                        detalle_cambio = "el menú completo"
                    elif cambio_comida:
                        detalle_cambio = f"la comida ({meal})" # Aquí incluimos el plato
                    elif cambio_cena:
                        detalle_cambio = f"la cena ({dinner})" # Aquí incluimos el plato
                    else:
                        detalle_cambio = "el día"

                    # 2. Formatear la fecha
                    meses_es = [
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                    ]
                    dia = self.current_day.date.day
                    mes = meses_es[self.current_day.date.month - 1]
                    fecha_formateada = f"{dia} de {mes}"

                    # 3. Construir el mensaje con el salto de línea y la flecha
                    # \n es el salto de línea para que el autor aparezca debajo
                    mensaje_notif = (
                        f"Se ha modificado {detalle_cambio} en '{calendar.name}' "
                        f"para el día {fecha_formateada}\n"
                        f"↳ {author}"
                    )

                    for user in shared_users:
                        if user.username != author:
                            NotificationState.enviar_notificacion(
                                titulo="🍽️ Menú actualizado",
                                mensaje=mensaje_notif,
                                destino=user.username
                            )
                # ----------------------

                toast_message = "Día actualizado correctamente"
                self.show_editor = False
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