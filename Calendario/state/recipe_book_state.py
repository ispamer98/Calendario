# Calendario/state/recipe_book_state.py
"""
Compartir el recetario.

Mismo trato que la lista de la compra: tu recetario es tuyo hasta que lo
compartes con alguien; en ese momento los dos recetarios **se fusionan** en uno
solo y a partir de ahí ambos veis y editáis exactamente las mismas recetas.

Quien se da de alta empieza con el suyo vacío: no hereda las comidas de nadie.
"""

import logging
from typing import List, Optional

import reflex as rx

from Calendario.model.model import User
from Calendario.state.calendar_state import CalendarState
from Calendario.state.user_state import UserState
from Calendario.utils.api import (
    get_recipe_book,
    get_recipe_book_users,
    remove_user_from_recipe_book,
    share_recipe_book,
)

logger = logging.getLogger(__name__)


class RecipeBookState(rx.State):
    book_id: Optional[int] = None
    shared_users: List[User] = []

    show_panel: bool = False
    new_user_input: str = ""
    error: str = ""
    sharing: bool = False

    @rx.var
    def shared_count(self) -> int:
        return len(self.shared_users)

    @rx.var
    def is_shared(self) -> bool:
        return len(self.shared_users) > 1

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------
    @rx.event
    async def load_book(self):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            self.book_id = None
            self.shared_users = []
            return
        book = await get_recipe_book(user_state.current_user.id)
        self.book_id = book["id"] if book else None
        if self.book_id:
            self.shared_users = await get_recipe_book_users(self.book_id)

    @rx.event
    async def toggle_panel(self):
        self.show_panel = not self.show_panel
        self.error = ""
        self.new_user_input = ""
        if self.show_panel:
            await self.load_book()

    @rx.event
    def close_panel(self):
        self.show_panel = False
        self.error = ""
        self.new_user_input = ""

    @rx.event
    def set_new_user_input(self, value: str):
        self.new_user_input = value

    # ------------------------------------------------------------------
    # Compartir / dejar de compartir
    # ------------------------------------------------------------------
    @rx.event
    async def share(self):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")

        username = self.new_user_input.strip().lower()
        if not username:
            self.error = "Escribe el nombre de usuario"
            return

        self.sharing = True
        try:
            ok, msg = await share_recipe_book(user_state.current_user.id, username)
            if not ok:
                self.error = msg
                return rx.toast.error(msg, position="top-center")

            self.new_user_input = ""
            self.error = ""
            await self.load_book()
            #Las recetas del otro ya son tuyas: el recetario en pantalla cambia
            calendar_state = await self.get_state(CalendarState)
            await calendar_state.load_meals()
            return rx.toast.success(msg, position="top-center")
        finally:
            self.sharing = False

    @rx.event
    async def remove_user(self, user_id: int, username: str):
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        if not self.book_id:
            return
        if user_id == user_state.current_user.id:
            return rx.toast.error("No puedes quitarte a ti mismo", position="top-center")

        if not await remove_user_from_recipe_book(
            self.book_id, user_id, user_state.current_user.id
        ):
            return rx.toast.error("No se pudo quitar del recetario", position="top-center")

        await self.load_book()
        return rx.toast.success(
            f"{username} ya no comparte tu recetario. Se le ha dejado una copia de las recetas.",
            position="top-center",
        )
