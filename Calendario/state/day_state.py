from Calendario.state.notification_state import NotificationState
import reflex as rx
from typing import Dict, Optional, List

from Calendario.utils.api import (
    get_day_comments,
    get_today_info,
    get_task_types,
    add_task_type,
    update_task_type,
    delete_task_type,
    add_comment_to_day,
    delete_comment as api_delete_comment,
    get_shared_users,
    update_day_meal,
    update_day_dinner,
    get_day_details,
    get_day_items,
    add_day_item as api_add_day_item,
    toggle_day_item_completed,
    delete_day_item as api_delete_day_item,
)
from Calendario.model.model import Day, Comment, DayItem, CatalogEntry
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState

#Etiquetas legibles para cada tipo de elemento de agenda
AGENDA_TYPE_LABELS = {"task": "tarea", "event": "evento", "note": "nota"}


def _end_time(start: Optional[str], duration_minutes: str) -> Optional[str]:
    """Hora de fin a partir del inicio y la duración, en tramos de 15 minutos.

    Si se pasa de medianoche se corta en 23:59: una tarea de un día no debería
    invadir el siguiente sin decirlo.
    """
    if not start:
        return None
    try:
        minutes = int(duration_minutes)
    except (ValueError, TypeError):
        return None
    if minutes <= 0:
        return None
    try:
        hh, mm = start.split(":")
        total = int(hh) * 60 + int(mm) + minutes
    except (ValueError, AttributeError):
        return None
    if total >= 24 * 60:
        return "23:59"
    return f"{total // 60:02d}:{total % 60:02d}"


class DayState(rx.State):
    current_day: Optional[Day] = None #Dia en curso
    show_editor: bool = False #Manejador para mostrar el editor del día
    loading: bool = False #Manejador de carga
    current_meal: str = "" #Comida para el día seleccionado
    current_dinner: str = ""   #Cena para el día seleccionado
    current_comments: List[Comment] = [] #Comentarios del día seleccionado
    last_loaded_day_id: Optional[int] = None #Último día cargado
    show_comment_input: bool = False #Manejador para el input de nuevo comentario
    new_comment_text: str = "" #Texto de nuevo comentario
    sending_comment: bool = False #Evita que un doble toque envíe dos veces
    comment_error: str = "" #Aviso en línea, en vez de una notificación

    #Agenda diaria (tareas / eventos / notas) del día seleccionado
    current_day_items: List[DayItem] = []
    new_item_title: str = ""
    new_item_type: str = "task"
    new_item_time: str = ""          # hora de inicio, en tramos de 15 min
    new_item_duration: str = "30"    # duración en minutos ("0" = sin franja)
    show_agenda_input: bool = False

    #Catálogo de tipos de agenda (tabla task_types, configurable)
    task_types: List[CatalogEntry] = []
    show_type_manager: bool = False
    new_type_label: str = ""
    new_type_color: str = "#34d399"
    new_type_icon: str = "list-checks"
    new_type_completable: bool = True

    # ---------------------- Gestor de tipos de agenda ----------------------

    @rx.event
    async def load_task_types(self):
        rows = await get_task_types()
        self.task_types = [
            CatalogEntry(key=r["key"], label=r["label"], color=r["color"],
                         icon=r["icon"], completable=r["completable"])
            for r in rows
        ]

    @rx.event
    async def open_type_manager(self):
        self.show_type_manager = True
        self.new_type_label = ""
        await self.load_task_types()

    @rx.event
    def close_type_manager(self):
        self.show_type_manager = False
        self.new_type_label = ""

    @rx.event
    def set_new_type_label(self, v: str):
        self.new_type_label = v

    @rx.event
    def set_new_type_color(self, v: str):
        self.new_type_color = v

    @rx.event
    def set_new_type_icon(self, v: str):
        self.new_type_icon = v

    @rx.event
    def toggle_new_type_completable(self, v: bool):
        self.new_type_completable = v

    @rx.var
    def type_palette(self) -> List[str]:
        return ["#eab308", "#38bdf8", "#a78bfa", "#22c55e", "#f472b6", "#ef4444", "#f97316", "#34d399"]

    @rx.var
    def type_icons(self) -> List[str]:
        #Todos comprobados contra lucide: si uno no existiera, se pintaría vacío
        return [
            "list-checks", "square-check", "calendar-clock", "sticky-note",
            "bell", "alarm-clock", "flag", "star", "heart", "trophy", "target",
            "zap", "briefcase", "graduation-cap", "book-open", "wallet",
            "dumbbell", "bike", "stethoscope", "pill", "baby", "dog", "cat",
            "car", "plane", "gift", "music", "gamepad-2", "coffee", "beer",
            "shopping-bag", "shirt", "wrench", "hammer", "scissors",
            "paint-roller", "phone", "mail", "camera", "leaf", "sun", "moon",
        ]

    #Tipo en edición (su clave). Vacía = estamos dando de alta uno nuevo
    editing_type: str = ""

    @rx.var
    def is_editing_type(self) -> bool:
        return self.editing_type != ""

    @rx.event
    def edit_task_type(self, key: str):
        """Carga un tipo en el formulario para cambiarle nombre, color o icono."""
        tipo = next((t for t in self.task_types if t.key == key), None)
        if not tipo:
            return
        self.editing_type = tipo.key
        self.new_type_label = tipo.label
        self.new_type_color = tipo.color
        self.new_type_icon = tipo.icon
        self.new_type_completable = tipo.completable
        return rx.set_focus("tipo-nombre")

    @rx.event
    def cancel_type_edit(self):
        self.editing_type = ""
        self.new_type_label = ""

    @rx.event
    async def save_task_type(self):
        """Da de alta el tipo, o guarda los cambios si se está editando."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        label = self.new_type_label.strip()
        if not label:
            return rx.toast.error("Escribe el nombre del tipo", position="top-center")
        if len(label) > 24:
            return rx.toast.error("Máximo 24 caracteres", position="top-center")

        if self.editing_type:
            #La clave no se toca: es lo que guardan las tareas ya creadas
            if not await update_task_type(
                self.editing_type, label, self.new_type_color,
                self.new_type_icon, self.new_type_completable,
            ):
                return rx.toast.error("No se pudo guardar el cambio", position="top-center")
            self.editing_type = ""
            self.new_type_label = ""
            await self.load_task_types()
            return rx.toast.success(f"Tipo '{label}' actualizado", position="top-center")

        if not await add_task_type(label, self.new_type_color, self.new_type_icon, self.new_type_completable):
            return rx.toast.error(
                "No se pudo guardar. ¿Está aplicada la migración 009_task_types.sql?",
                position="top-center",
            )
        self.new_type_label = ""
        await self.load_task_types()
        return rx.toast.success(f"Tipo '{label}' añadido", position="top-center")

    @rx.event
    async def remove_task_type(self, key: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if len(self.task_types) <= 1:
            return rx.toast.error("Deja al menos un tipo", position="top-center")
        if not await delete_task_type(key):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        if self.editing_type == key:
            self.editing_type = ""
            self.new_type_label = ""
        await self.load_task_types()
        return rx.toast.success("Tipo eliminado", position="top-center")

    def _type_map(self) -> dict:
        return {t.key: t for t in self.task_types}

    #Todas las horas del día en tramos de 15 minutos ("00:00" ... "23:45")
    @rx.var
    def time_slots(self) -> List[str]:
        return [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]

    #Duraciones ofrecidas, con su etiqueta
    @rx.var
    def durations(self) -> List[Dict[str, str]]:
        return [
            {"value": "0", "label": "Sin fin"},
            {"value": "15", "label": "15 min"},
            {"value": "30", "label": "30 min"},
            {"value": "45", "label": "45 min"},
            {"value": "60", "label": "1 h"},
            {"value": "90", "label": "1 h 30"},
            {"value": "120", "label": "2 h"},
            {"value": "180", "label": "3 h"},
            {"value": "240", "label": "4 h"},
            {"value": "480", "label": "8 h"},
        ]

    #Etiquetas legibles de lo elegido, para pintarlas en los desplegables con
    #buscador (que muestran texto, no el valor interno)
    @rx.var
    def new_item_type_label(self) -> str:
        return next(
            (t.label for t in self.task_types if t.key == self.new_item_type),
            self.new_item_type,
        )

    @rx.var
    def new_item_duration_label(self) -> str:
        return next(
            (d["label"] for d in self.durations if d["value"] == self.new_item_duration),
            self.new_item_duration,
        )

    #Vista previa de la franja mientras se rellena el formulario
    @rx.var
    def slot_preview(self) -> str:
        if not self.new_item_time:
            return "Sin hora"
        end = _end_time(self.new_item_time, self.new_item_duration)
        return f"{self.new_item_time} – {end}" if end else self.new_item_time

    #Cargamos los comentarios para el día elegido
    @rx.event
    async def load_day_comments(self, day_id: int):
        self.last_loaded_day_id = day_id
        user_state = await self.get_state(UserState)
        comments = await get_day_comments(day_id, user_state.current_user.id)
        self.current_comments = comments

    #Mostramos los comentarios en orden cronológico
    @rx.var
    def reversed_comments(self) -> list[Comment]:
        return list(reversed(self.current_comments))

    @rx.event
    def clear_current_comments(self):
        self.current_comments = []

    #Cerramos el input de comentarios
    @rx.event
    def close_comment_input(self):
        self.show_comment_input = False
        self.new_comment_text=""
        self.comment_error = ""
        
    #Asigna texto del input a nuevo comentario
    @rx.event
    def set_new_comment_text(self, value: str):
        self.new_comment_text = value
        #En cuanto escribe algo, el aviso sobra
        if value.strip():
            self.comment_error = ""

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
        #Un segundo toque llegaba con el campo ya vaciado y saltaba el error
        if self.sending_comment:
            return
        texto_comentario = self.new_comment_text.strip()

        if not texto_comentario:
            #Aviso pegado al campo: una notificación para esto es exagerado
            self.comment_error = "Escribe algo antes de enviar"
            return

        self.comment_error = ""
        self.sending_comment = True

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
                updated_day = await get_day_details(day.id, user_state.current_user.id)
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
            self.sending_comment = False
        #Función para borrar el comentario
    @rx.event
    async def delete_comment(self, comment_id: int, day: Day):
        try:
            user_state = await self.get_state(UserState)
            # Eliminamos el comentario desde base de datos
            success = await api_delete_comment(comment_id, user_state.current_user.id)

            if success:
                # Cargamos de nuevo los comentarios
                await self.load_day_comments(day.id)
                # Cargamos los detalles del día
                updated_day = await get_day_details(day.id, user_state.current_user.id)
                calendar_state = await self.get_state(CalendarState)
                # Actualizamos el día
                await calendar_state.update_day_in_state(updated_day)

                # --- NOTIFICACIONES ---
                calendar = calendar_state.current_calendar
                if calendar:
                    shared_users = await get_shared_users(calendar.id)
                    author = user_state.current_user.username

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

    # ---------------------- Agenda diaria (tareas / eventos / notas) ----------------------

    @rx.event
    def set_new_item_title(self, value: str):
        self.new_item_title = value

    @rx.event
    def set_new_item_type(self, value: str):
        self.new_item_type = value

    @rx.event
    def set_new_item_time(self, value: str):
        self.new_item_time = value

    @rx.event
    def set_new_item_duration(self, value: str):
        self.new_item_duration = value

    @rx.event
    def clear_new_item_time(self):
        self.new_item_time = ""

    @rx.event
    def agenda_key_down(self, key: str):
        """Enter añade la entrada de agenda, sin tocar el formulario del día."""
        if key == "Enter":
            return DayState.add_day_item

    @rx.event
    def toggle_agenda_input(self):
        self.show_agenda_input = not self.show_agenda_input
        if not self.show_agenda_input:
            self.new_item_title = ""
            self.new_item_time = ""
            self.new_item_duration = "30"

    #Cargamos los elementos de agenda para el día indicado
    @rx.event
    async def load_day_items(self, day_id: int):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return
        #El catálogo hace falta para saber qué icono y color lleva cada tipo
        if not self.task_types:
            await self.load_task_types()
        items = await get_day_items(day_id, user_state.current_user.id)
        self.current_day_items = [self._decorate(i) for i in items]

    def _decorate(self, item: DayItem) -> DayItem:
        """Pone al elemento el icono y el color de su tipo.

        El tipo es configurable, así que no se puede resolver con un `rx.cond`
        fijo en el componente: llega ya resuelto desde aquí.
        """
        entry = self._type_map().get(item.item_type)
        if entry:
            item.type_icon = entry.icon
            item.type_color = entry.color
            item.type_label = entry.label
            item.completable = entry.completable
        else:
            #Tipo borrado del catálogo: se pinta neutro pero no se pierde
            item.type_icon = "circle-dot"
            item.type_color = "#94a3b8"
            item.type_label = item.item_type
            item.completable = item.item_type == "task"
        return item

    async def _refresh_today(self):
        """Recarga el panel de Hoy.

        `refresh_page` devuelve el evento `today_info` en vez de ejecutarlo, y
        al llamarla con await ese evento se perdía: por eso las tareas nuevas
        no aparecían en Hoy hasta recargar la página.
        """
        user_state = await self.get_state(UserState)
        if user_state.current_user:
            user_state.today_data = await get_today_info(user_state.current_user.id)

    #Añadimos un nuevo elemento (tarea/evento/nota) al día seleccionado actualmente
    @rx.event
    async def add_day_item(self):
        if not self.current_day:
            return
        day = self.current_day
        title = self.new_item_title.strip()
        if not title:
            return rx.toast.error("El título no puede estar vacío", position="top-center")
        if len(title) > 60:
            return rx.toast.error("Máximo 60 caracteres", position="top-center")

        user_state = await self.get_state(UserState)
        start = self.new_item_time.strip() or None
        new_item = await api_add_day_item(
            day.id, user_state.current_user.id, self.new_item_type, title,
            "", start, _end_time(start, self.new_item_duration),
        )
        if not new_item:
            return rx.toast.error("No se pudo añadir el elemento a la agenda", position="top-center")

        self.new_item_title = ""
        self.new_item_time = ""
        self.new_item_duration = "30"
        self.show_agenda_input = False
        await self.load_day_items(day.id)
        calendar_state = await self.get_state(CalendarState)
        await calendar_state.refresh_page()
        await self._refresh_today()

        #Notificamos a los usuarios con acceso al calendario
        calendar = calendar_state.current_calendar
        if calendar:
            shared_users = await get_shared_users(calendar.id)
            author = user_state.current_user.username
            meses_es = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            fecha_formateada = f"{day.date.day} de {meses_es[day.date.month - 1]}"
            etiqueta = AGENDA_TYPE_LABELS.get(self.new_item_type, "elemento")
            for user in shared_users:
                if user.username != author:
                    NotificationState.enviar_notificacion(
                        titulo="🗓️ Nueva entrada en la agenda",
                        mensaje=f"{author} añadió {etiqueta} \"{title}\" en '{calendar.name}' ({fecha_formateada})",
                        destino=user.username,
                    )

        return rx.toast.success("Añadido a la agenda", position="top-center")

    #Alterna el estado completado/pendiente de una tarea
    @rx.event
    async def toggle_day_item(self, item_id: int):
        user_state = await self.get_state(UserState)
        success = await toggle_day_item_completed(item_id, user_state.current_user.id)
        if success and self.current_day:
            await self.load_day_items(self.current_day.id)
            calendar_state = await self.get_state(CalendarState)
            await calendar_state.refresh_page()
            await self._refresh_today()

    #Elimina un elemento de la agenda del día seleccionado actualmente
    @rx.event
    async def delete_day_item(self, item_id: int):
        if not self.current_day:
            return
        user_state = await self.get_state(UserState)
        success = await api_delete_day_item(item_id, user_state.current_user.id)
        if success:
            await self.load_day_items(self.current_day.id)
            calendar_state = await self.get_state(CalendarState)
            await calendar_state.refresh_page()
            await self._refresh_today()
        else:
            return rx.toast.error("No se pudo eliminar el elemento", position="top-center")

    @rx.event
    async def open_today(self):
        """Abre el editor del día de hoy desde el panel de Hoy."""
        import pytz
        from datetime import datetime as _dt

        calendar_state = await self.get_state(CalendarState)
        hoy = _dt.now(pytz.timezone("Europe/Madrid")).date()
        dia = next((d for d in calendar_state.days if d.date.date() == hoy), None)
        if not dia:
            return rx.toast.info(
                "Hoy no está en el calendario seleccionado", position="top-center"
            )
        await self.load_day_comments(dia.id)
        await self.load_day_items(dia.id)
        self.current_day = dia
        self.current_meal = dia.meal or ""
        self.current_dinner = dia.dinner or ""
        self.show_editor = True

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
        self.current_day_items = []
        self.show_agenda_input = False
        self.new_item_title = ""
        self.new_item_time = ""
        self.new_item_duration = "30"

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
            user_state = await self.get_state(UserState)
            user_id = user_state.current_user.id
            meal = self.current_meal or None
            dinner = self.current_dinner or None
            updated = False
            #Actualizamos la comida si existen diferencias
            if meal != self.current_day.meal:
                result = await update_day_meal(self.current_day.id, meal, user_id)
                if result is None:
                    return rx.toast.error("No tienes permiso para modificar este día", position="top-center")
                updated = True
            #Actualizamos la cena si existen diferencias
            if dinner != self.current_day.dinner:
                result = await update_day_dinner(self.current_day.id, dinner, user_id)
                if result is None:
                    return rx.toast.error("No tienes permiso para modificar este día", position="top-center")
                updated = True
            #Si encontramos diferencias
            if updated:
                updated_day = await get_day_details(self.current_day.id, user_id)
                calendar_state = await self.get_state(CalendarState)
                await calendar_state.update_day_in_state(updated_day)

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