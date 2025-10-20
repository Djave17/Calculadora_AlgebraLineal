from __future__ import annotations

import asyncio
import threading
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import flet as ft


@dataclass
class RouteTarget:
    view: Optional[ft.Control]
    config_view: Optional[ft.Control] = None
    config_visible: bool = False


@dataclass
class _RegisteredRoute:
    factory: Callable[[], RouteTarget]
    view_id: str


class MethodRouter:
    """Sincroniza el menú lateral con el contenedor central.

    Mantiene una lista de fábricas perezosas (lazy) que construyen las vistas
    únicamente cuando se navega hacia ellas. Cada navegación asegura que los
    contenedores se actualicen y que el `page.update()` se invoque una sola vez.
    Además permite esperar de forma asíncrona a que la vista nueva confirme que
    se montó mediante un evento `view_ready`.
    """

    def __init__(
        self,
        page: ft.Page,
        outlet: ft.Container,
        menu: Optional["LeftMethodsMenu"] = None,
        config_outlet: Optional[ft.Container] = None,
        on_navigate: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.page = page
        self.outlet = outlet
        self.menu = menu
        self.config_outlet = config_outlet
        self.on_navigate = on_navigate
        self._routes: Dict[str, _RegisteredRoute] = {}
        self.current_method_id: Optional[str] = None
        self._ready_event: Optional[asyncio.Event] = None
        self._ready_id: Optional[str] = None

        if self.page:
            self.page.pubsub.subscribe(self._on_pubsub)

    def register(self, method_id: str, factory: Callable[[], RouteTarget], *, view_id: Optional[str] = None) -> None:
        """Registra una fábrica para un método."""
        self._routes[method_id] = _RegisteredRoute(factory=factory, view_id=view_id or method_id)

    def clear(self) -> None:
        self._routes.clear()

    def navigate(self, method_id: str) -> Optional[RouteTarget]:
        """Construye la vista destino y sincroniza el menú/outlet."""
        registered = self._routes.get(method_id)
        if registered is None:
            return None
        try:
            target = registered.factory()
        except Exception:
            # Si la fábrica falla, reinicia el estado de espera para no dejar
            # un evento bloqueado.
            self._ready_event = None
            self._ready_id = None
            raise

        self.current_method_id = method_id

        if self.menu:
            self.menu.set_active_method(method_id)

        if self.outlet:
            self.outlet.content = target.view

        if self.config_outlet:
            self.config_outlet.content = target.config_view
            self.config_outlet.visible = bool(target.config_view) and target.config_visible

        self._schedule_ready_signal(registered.view_id)

        if self.on_navigate:
            self.on_navigate(method_id)

        self._update_page()
        return target

    async def navigate_and_wait(self, method_id: str, timeout: float = 2.0) -> bool:
        """Navega y espera a que la vista confirme su montaje mediante PubSub."""
        registered = self._routes.get(method_id)
        if registered is None:
            return False
        self._ready_event = asyncio.Event()
        self._ready_id = registered.view_id
        self.navigate(method_id)
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
        finally:
            self._ready_event = None
            self._ready_id = None

    def _update_page(self) -> None:
        try:
            if self.page:
                self.page.update()
        except AssertionError:
            pass

    def _schedule_ready_signal(self, view_id: str) -> None:
        if not self.page:
            return

        def emit() -> None:
            if not self.page:
                return
            self.page.pubsub.send_all({"type": "view_ready", "id": view_id})

        try:
            call_later = getattr(self.page, "call_later", None)
            if callable(call_later):
                call_later(emit)
                return
        except AttributeError:
            pass

        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(emit)
            return
        except RuntimeError:
            pass

        threading.Timer(0, emit).start()

    def _on_pubsub(self, message) -> None:
        if not isinstance(message, dict):
            return
        if message.get("type") != "view_ready":
            return
        if self._ready_event and self._ready_id == message.get("id"):
            self._ready_event.set()
