import asyncio
import reflex as rx
from typing import Dict, List, Optional
from Calendario.utils.api import (
    get_user_shopping_lists,
    add_item_to_shopping_list,
    merge_and_share_shopping_list,
    toggle_shopping_item_status,
    remove_item_from_shopping_list,
    get_shopping_list_users,
    add_user_to_list,
    remove_user_from_list,
    get_user_by_username,
)
from Calendario.state.user_state import UserState
from Calendario.model.model import User

class ShoppingListState(rx.State):
    # Datos de la lista
    items: Dict[str, Dict] = {}
    current_list_id: Optional[int] = None
    current_user_id: int = -1

    # Formulario de añadir producto
    new_item_name: str = ""
    new_item_qty: str = "1"
    new_item_shop: str = ""
    show_add_form: bool = False
    errors: Dict[str, str] = {"name": "", "quantity": "", "supermarket": ""}

    # Gestión de usuarios
    show_users_panel: bool = False
    shared_users: List[User] = []
    new_user_input: str = ""
    add_user_error: str = ""

    # Control del polling (solo un flag, NO se guarda la tarea)
    _polling_active: bool = False

    # ------------------------------------------------------------
    # Normalización de datos
    # ------------------------------------------------------------
    def _normalize_items(self, raw_items: dict) -> dict:
        normalized = {}
        for name, details in raw_items.items():
            normalized[name] = {
                "quantity": details.get("quantity", 1),
                "supermarket": details.get("supermarket", ""),
                "bought": details.get("bought", False)
            }
        return normalized

    @rx.var
    def is_empty(self) -> bool:
        return len(self.items) == 0

    # ------------------------------------------------------------
    # Carga inicial y polling
    # ------------------------------------------------------------
    async def load_shopping_list(self):
        """Carga la lista del usuario actual desde la base de datos."""
        user_state = await self.get_state(UserState)
        if not user_state.current_user:
            return rx.redirect("/")
        self.current_user_id = user_state.current_user.id
        user_id = self.current_user_id
        lists = await get_user_shopping_lists(user_id)
        if lists:
            self.current_list_id = lists[0]["id"]
            raw_items = lists[0]["items"]
            self.items = self._normalize_items(raw_items)
        else:
            from Calendario.utils.api import SUPABASE_API
            new_list = SUPABASE_API.create_shopping_list([user_id])
            if new_list:
                self.current_list_id = new_list["id"]
                self.items = {}



    async def refresh_page(self):
        """Recarga manualmente los datos de la lista de la compra."""
        print("🔄 Recargando lista de la compra...")
        await self.load_shopping_list()
        # Si el panel de usuarios está abierto, también lo recargamos
        if self.show_users_panel:
            await self.load_shared_users()
        # Devuelve un toast informativo (opcional, como en el calendario no hay)
        # rx.toast.info("Lista actualizada", position="top-center", duration=1500)
    # ------------------------------------------------------------
    # Métodos para productos (añadir, tachar, eliminar)
    # ------------------------------------------------------------
    def validate_item(self) -> bool:
        self.errors = {"name": "", "quantity": "", "supermarket": ""}
        has_error = False
        if not self.new_item_name.strip():
            self.errors["name"] = "El nombre es obligatorio"
            has_error = True
        elif len(self.new_item_name) > 40:
            self.errors["name"] = "Máximo 40 caracteres"
            has_error = True

        if not self.new_item_qty.strip():
            self.errors["quantity"] = "Cantidad obligatoria"
            has_error = True
        else:
            try:
                qty = int(self.new_item_qty)
                if qty <= 0:
                    self.errors["quantity"] = "Debe ser >0"
                    has_error = True
                elif qty > 999:
                    self.errors["quantity"] = "Máximo 999"
                    has_error = True
                elif len(self.new_item_qty) > 3:
                    self.errors["quantity"] = "Máx 3 dígitos"
                    has_error = True
            except ValueError:
                self.errors["quantity"] = "Número entero"
                has_error = True

        if len(self.new_item_shop) > 20:
            self.errors["supermarket"] = "Máximo 20 caracteres"
            has_error = True
        return has_error

    @rx.event
    def change_qty(self, val: str):
        self.new_item_qty = val

    @rx.event
    def toggle_add_form(self):
        self.show_add_form = not self.show_add_form

    @rx.event
    def close_add_form(self):
        self.show_add_form = False
        self.errors = {"name": "", "quantity": "", "supermarket": ""}

    async def add_item(self):
        if self.validate_item():
            return
        if not self.current_list_id:
            return rx.toast.error("Lista no identificada")
        qty_int = int(self.new_item_qty) if self.new_item_qty else 1
        success = await add_item_to_shopping_list(
            self.current_list_id,
            self.new_item_name.strip(),
            qty_int,
            self.new_item_shop.strip()
        )
        if success:
            self.new_item_name = ""
            self.new_item_qty = "1"
            self.new_item_shop = ""
            self.show_add_form = False
            await self.load_shopping_list()
            rx.toast.success("Producto añadido", position="top-center")
        else:
            rx.toast.error("Error al añadir", position="top-center")

    async def toggle_bought(self, item_name: str):
        if await toggle_shopping_item_status(self.current_list_id, item_name):
            await self.load_shopping_list()
        else:
            rx.toast.error("Error al actualizar", position="top-center")

    async def delete_item(self, item_name: str):
        if await remove_item_from_shopping_list(self.current_list_id, item_name):
            await self.load_shopping_list()
        else:
            rx.toast.error("Error al eliminar", position="top-center")

    # ------------------------------------------------------------
    # Métodos para usuarios (compartir, añadir, eliminar)
    # ------------------------------------------------------------
    async def load_shared_users(self):
        if not self.current_list_id:
            return
        users = await get_shopping_list_users(self.current_list_id)
        self.shared_users = users

    @rx.event
    async def toggle_users_panel(self):
        self.show_users_panel = not self.show_users_panel
        if self.show_users_panel:
            await self.load_shared_users()
        else:
            self.shared_users = []
            self.new_user_input = ""
            self.add_user_error = ""

    @rx.event
    def set_new_user_input(self, val: str):
        self.new_user_input = val

    async def add_user_to_list(self):
        self.add_user_error = ""
        username = self.new_user_input.strip().lower()
        if not username:
            self.add_user_error = "Nombre de usuario requerido"
            return

        user_state = await self.get_state(UserState)
        current_user_id = user_state.current_user.id
        success, msg = await merge_and_share_shopping_list(current_user_id, username)

        if success:
            self.new_user_input = ""
            await self.load_shared_users()
            await self.load_shopping_list()
            rx.toast.success(msg, position="top-center")
            self.show_users_panel = False
        else:
            self.add_user_error = msg
            rx.toast.error(msg, position="top-center")

    async def remove_user_from_list(self, user_id: int, username: str):
        if user_id == self.current_user_id:
            rx.toast.error("No puedes eliminarte a ti mismo", position="top-center")
            return
        success = await remove_user_from_list(self.current_list_id, user_id)
        if success:
            await self.load_shared_users()
            rx.toast.success(
                f"Usuario {username} eliminado. Se le ha creado su propia lista.",
                position="top-center"
            )
        else:
            rx.toast.error("Error al eliminar usuario", position="top-center")