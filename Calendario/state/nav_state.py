# Calendario/state/nav_state.py

import reflex as rx


class NavState(rx.State):
    """Estado de la navegación: colapso de la sidebar y ruta activa."""

    sidebar_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

    @rx.var
    def active_route(self) -> str:
        return self.router.url.path
