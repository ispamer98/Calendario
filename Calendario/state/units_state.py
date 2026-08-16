# Calendario/state/units_state.py
"""
Unidades de medida configurables.

Antes eran una lista fija en el código con cosas como "pizca" o "manojo". Ahora
salen de la tabla `units` y se gestionan desde la app: añadir las tuyas, quitar
las que no uses. Son comunes a toda la app, igual que el recetario.

**La unidad se guarda como texto**, no como referencia a la tabla: cada
ingrediente, cada producto del catálogo y cada línea de la compra llevan escrito
"g", "ml"... Eso tiene una consecuencia que costó un disgusto: borrar una unidad
no rompe nada, pero deja **huérfano** todo lo que la usaba — se sigue viendo,
y ya no se puede volver a elegir en ningún desplegable.

Por eso aquí ya no se borra a ciegas:

- antes de borrar se cuenta el uso y, si la unidad está escrita en algún sitio,
  se pregunta: convertir a otra o borrar dejándola huérfana;
- las huérfanas que ya existan se listan aparte, con dos salidas: recuperarlas
  (volver a meterlas en la tabla) o convertirlas a una que sí exista.

Si la migración 006 no está aplicada, se usa la lista de reserva de
`SupabaseAPI.DEFAULT_UNITS` y todo sigue funcionando (solo que no se pueden
guardar cambios).
"""

import logging
import re
from typing import Dict, List

import reflex as rx

from Calendario.model.model import UnitUsage
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    add_unit,
    convert_unit,
    delete_unit,
    get_unit_usage,
    get_units,
    update_unit,
)

logger = logging.getLogger(__name__)

#Lo que se muestra hasta que llega la lista real de la base de datos
FALLBACK_UNITS = ["ud", "g", "kg", "ml", "l"]


class UnitsState(rx.State):
    units: List[str] = FALLBACK_UNITS
    show_manager: bool = False
    new_unit: str = ""
    loading: bool = False
    #Unidad en edición (su nombre original). Vacía = estamos dando de alta
    editing_unit: str = ""

    #{unidad en minúsculas: veces que está escrita}. Solo se calcula al abrir
    #el gestor: recorre recetas y listas enteras y no hace falta para pintar
    #un desplegable.
    usage: Dict[str, int] = {}
    usage_loaded: bool = False

    #Borrado en dos pasos cuando la unidad está en uso
    pending_delete: str = ""
    pending_delete_count: int = 0
    #Unidad de destino del conversor (sirve para el borrado y para las huérfanas)
    convert_to: str = ""
    #Huérfana que se está convirtiendo ("" = ninguna)
    converting_orphan: str = ""

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    @rx.event
    async def load_units(self):
        self.units = await get_units()

    async def _load_usage(self):
        try:
            self.usage = await get_unit_usage()
            self.usage_loaded = True
        except Exception as e:
            logger.warning(f"No se pudo contar el uso de las unidades: {e}")
            self.usage = {}
            self.usage_loaded = False

    @rx.event
    async def open_manager(self):
        self.show_manager = True
        self._reset_form()
        await self.load_units()
        await self._load_usage()

    @rx.event
    def close_manager(self):
        self.show_manager = False
        self._reset_form()

    @rx.event
    def toggle_manager(self, opened: bool):
        """Cierra el gestor cuando Radix lo pide (Escape o clic fuera).

        `open` está controlado desde el estado: si nadie atiende esta señal,
        Radix pide cerrar y no pasa nada, y el diálogo solo se deja cerrar con
        la X o con «Listo».
        """
        if not opened:
            return UnitsState.close_manager

    def _reset_form(self):
        self.new_unit = ""
        self.editing_unit = ""
        self.pending_delete = ""
        self.pending_delete_count = 0
        self.convert_to = ""
        self.converting_orphan = ""

    @rx.event
    def set_new_unit(self, value: str):
        self.new_unit = value

    @rx.event
    def set_convert_to(self, value: str):
        self.convert_to = value

    # ------------------------------------------------------------------
    # Lecturas para la interfaz
    # ------------------------------------------------------------------
    @rx.var
    def unit_count(self) -> int:
        return len(self.units)

    @rx.var
    def is_editing(self) -> bool:
        return self.editing_unit != ""

    @rx.var
    def rows(self) -> List[UnitUsage]:
        """Las unidades del desplegable, con la cuenta de dónde se usan."""
        return [
            UnitUsage(name=u, count=self.usage.get(u.strip().lower(), 0), orphan=False)
            for u in self.units
        ]

    @rx.var
    def orphans(self) -> List[UnitUsage]:
        """Unidades escritas en los datos que ya no están en la tabla.

        Es exactamente el estropicio de borrar "g" para poner "gr": los 168
        ingredientes que decían "g" siguen diciéndolo, pero "g" ya no se puede
        elegir. Aquí salen para poder arreglarlos.
        """
        if not self.usage_loaded:
            return []
        conocidas = {u.strip().lower() for u in self.units}
        return sorted(
            (
                UnitUsage(name=nombre, count=veces, orphan=True)
                for nombre, veces in self.usage.items()
                if nombre not in conocidas
            ),
            key=lambda u: (-u.count, u.name),
        )

    @rx.var
    def has_orphans(self) -> bool:
        return len(self.orphans) > 0

    @rx.var
    def orphan_count(self) -> int:
        return len(self.orphans)

    @rx.var
    def is_confirming_delete(self) -> bool:
        return self.pending_delete != ""

    @rx.var
    def is_converting_orphan(self) -> bool:
        return self.converting_orphan != ""

    @rx.var
    def convert_targets(self) -> List[str]:
        """Unidades a las que se puede convertir: todas menos la de origen."""
        origen = (self.pending_delete or self.converting_orphan).strip().lower()
        return [u for u in self.units if u.strip().lower() != origen]

    # ------------------------------------------------------------------
    # Alta y renombrado
    # ------------------------------------------------------------------
    @rx.event
    def edit(self, name: str):
        """Carga una unidad en el campo de texto para renombrarla."""
        self.pending_delete = ""
        self.converting_orphan = ""
        self.editing_unit = name
        self.new_unit = name
        return rx.set_focus("unidad-nombre")

    @rx.event
    def cancel_edit(self):
        self.editing_unit = ""
        self.new_unit = ""

    def _validate(self, name: str) -> str:
        """Devuelve el mensaje de error, o "" si el nombre vale."""
        if not name:
            return "Escribe la unidad"
        if len(name) > 12:
            return "Máximo 12 caracteres"
        #Solo texto corto: es una etiqueta, no una frase
        if not re.match(r"^[\wÁÉÍÓÚÜÑáéíóúüñ0-9./·º ]+$", name):
            return "Esa unidad tiene caracteres raros"
        return ""

    @rx.event
    async def add(self):
        #Las unidades las ve todo el mundo: hace falta sesión iniciada
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        name = self.new_unit.strip()
        error = self._validate(name)
        if error:
            return rx.toast.error(error, position="top-center")
        #Editando: chocar consigo misma no es un duplicado
        if any(
            u.lower() == name.lower() and u.lower() != self.editing_unit.lower()
            for u in self.units
        ):
            return rx.toast.error(f"'{name}' ya está en la lista", position="top-center")

        self.loading = True
        try:
            if self.editing_unit:
                anterior = self.editing_unit
                if anterior == name:
                    self.cancel_edit()
                    return
                if not await update_unit(anterior, name):
                    return rx.toast.error("No se pudo renombrar la unidad", position="top-center")
                self.editing_unit = ""
                self.new_unit = ""
                await self.load_units()
                await self._load_usage()
                return rx.toast.success(
                    f"'{anterior}' ahora es '{name}' (cambiada también donde ya se usaba)",
                    position="top-center",
                )

            if not await add_unit(name):
                return rx.toast.error(
                    "No se pudo guardar. ¿Está aplicada la migración 006_units.sql?",
                    position="top-center",
                )
            self.new_unit = ""
            await self.load_units()
            await self._load_usage()
            return rx.toast.success(f"Unidad '{name}' añadida", position="top-center")
        finally:
            self.loading = False

    # ------------------------------------------------------------------
    # Borrado: nunca a ciegas si la unidad está escrita en algún sitio
    # ------------------------------------------------------------------
    @rx.event
    async def remove(self, name: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        if len(self.units) <= 1:
            return rx.toast.error("Deja al menos una unidad", position="top-center")

        if not self.usage_loaded:
            await self._load_usage()

        veces = self.usage.get(name.strip().lower(), 0)
        if veces > 0:
            #Aquí está el arreglo: en vez de borrarla y dejar huérfanos 168
            #ingredientes, se pregunta primero
            self.pending_delete = name
            self.pending_delete_count = veces
            self.convert_to = next(
                (u for u in self.units if u.strip().lower() != name.strip().lower()), ""
            )
            self.converting_orphan = ""
            self.editing_unit = ""
            return

        return await self._do_delete(name)

    async def _do_delete(self, name: str):
        if not await delete_unit(name):
            return rx.toast.error("No se pudo eliminar", position="top-center")
        if self.editing_unit.lower() == name.lower():
            self.cancel_edit()
        self.pending_delete = ""
        self.pending_delete_count = 0
        await self.load_units()
        await self._load_usage()
        return rx.toast.success(f"'{name}' quitada del desplegable", position="top-center")

    @rx.event
    def cancel_delete(self):
        self.pending_delete = ""
        self.pending_delete_count = 0
        self.convert_to = ""

    @rx.event
    async def confirm_delete_keeping_usages(self):
        """Borra la unidad dejando huérfano lo que la usaba (a sabiendas)."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        name = self.pending_delete
        if not name:
            return
        self.loading = True
        try:
            resultado = await self._do_delete(name)
            #Sigue apareciendo, ahora en el apartado de huérfanas, para que no
            #se olvide que hay datos apuntando a una unidad que no existe
            return resultado
        finally:
            self.loading = False

    @rx.event
    async def convert_and_delete(self):
        """Pasa todo lo que usaba la unidad a otra y luego la borra."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        origen = self.pending_delete
        destino = self.convert_to.strip()
        if not origen:
            return
        if not destino:
            return rx.toast.error("Elige a qué unidad se convierte", position="top-center")
        if destino.lower() == origen.lower():
            return rx.toast.error("Elige una unidad distinta", position="top-center")

        self.loading = True
        try:
            cambiados = await convert_unit(origen, destino)
            if cambiados < 0:
                return rx.toast.error("No se pudo convertir la unidad", position="top-center")
            if not await delete_unit(origen):
                await self.load_units()
                await self._load_usage()
                return rx.toast.warning(
                    f"Convertidos {cambiados} a '{destino}', pero '{origen}' sigue en la lista",
                    position="top-center",
                )
            self.pending_delete = ""
            self.pending_delete_count = 0
            await self.load_units()
            await self._load_usage()
            return rx.toast.success(
                f"'{origen}' borrada: {cambiados} pasaron a '{destino}'",
                position="top-center",
            )
        finally:
            self.loading = False

    # ------------------------------------------------------------------
    # Huérfanas: las que quedaron escritas sin estar en la lista
    # ------------------------------------------------------------------
    @rx.event
    def start_orphan_convert(self, name: str):
        self.converting_orphan = name
        self.pending_delete = ""
        self.pending_delete_count = 0
        self.editing_unit = ""
        self.convert_to = next(
            (u for u in self.units if u.strip().lower() != name.strip().lower()), ""
        )

    @rx.event
    def cancel_orphan_convert(self):
        self.converting_orphan = ""
        self.convert_to = ""

    @rx.event
    async def convert_orphan(self):
        """Reescribe la unidad huérfana como una de las que sí existen."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        origen = self.converting_orphan
        destino = self.convert_to.strip()
        if not origen:
            return
        if not destino:
            return rx.toast.error("Elige a qué unidad se convierte", position="top-center")

        self.loading = True
        try:
            cambiados = await convert_unit(origen, destino)
            if cambiados < 0:
                return rx.toast.error("No se pudo convertir la unidad", position="top-center")
            self.converting_orphan = ""
            self.convert_to = ""
            await self._load_usage()
            return rx.toast.success(
                f"{cambiados} pasaron de '{origen}' a '{destino}'", position="top-center"
            )
        finally:
            self.loading = False

    @rx.event
    async def restore_orphan(self, name: str):
        """Devuelve la unidad al desplegable, tal y como estaba escrita."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        error = self._validate(name.strip())
        if error:
            return rx.toast.error(
                f"No se puede recuperar '{name}': {error.lower()}", position="top-center"
            )
        if not await add_unit(name.strip()):
            return rx.toast.error("No se pudo recuperar la unidad", position="top-center")
        await self.load_units()
        await self._load_usage()
        return rx.toast.success(
            f"'{name}' vuelve a estar en el desplegable", position="top-center"
        )
