from __future__ import annotations

import flet as ft
from flet import Colors as colors

from ...styles import PRIMARY_COLOR, SECONDARY_COLOR, TEXT_DARK, TEXT_MUTED
from .numerical_methods_closed_view import NumericalMethodsClosedView
from .numerical_methods_open_view import NumericalMethodsOpenView


class NumericalMethodsView:
    """Vista general que permite elegir métodos cerrados o abiertos."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._mode: str = "closed"
        self._closed_view = NumericalMethodsClosedView(page)
        self._open_view = NumericalMethodsOpenView(page)
        self._content_container = ft.Container(content=self._closed_view.view, expand=True)

        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        selector = ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Selecciona tipo de método", size=14, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
                    ft.Dropdown(
                        value=self._mode,
                        options=[
                        ft.dropdown.Option("closed", "Métodos cerrados"),
                        ft.dropdown.Option("open", "Métodos abiertos"),
                        ],
                        border_color=PRIMARY_COLOR,
                        focused_border_color=PRIMARY_COLOR,
                        text_style=ft.TextStyle(color=PRIMARY_COLOR, weight=ft.FontWeight.W_600),
                        label_style=ft.TextStyle(color=PRIMARY_COLOR),
                        on_change=lambda e: self._set_mode(e.control.value),
                ),
            ],
        )

        hero = ft.Column(
            spacing=4,
            controls=[
                ft.Text("Métodos numéricos", size=26, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Elige si usarás un método cerrado u abierto. Cada variante incluye gráfica, límite de iteraciones y comprobación f(raíz).",
                    size=13,
                    color=TEXT_MUTED,
                ),
            ],
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(12, 12, 12, 24),
            content=ft.Column(
                spacing=20,
                controls=[
                    hero,
                    selector,
                    self._content_container,
                ],
            ),
        )

    def _set_mode(self, mode: str) -> None:
        if not mode or mode == self._mode:
            return
        self._mode = mode
        self._content_container.content = self._closed_view.view if mode == "closed" else self._open_view.view
        self._safe_update(self._content_container)

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
