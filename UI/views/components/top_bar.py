from __future__ import annotations

import flet as ft
from flet import Colors, Icons

from ...styles import BACKGROUND_COLOR, PRIMARY_COLOR, TOP_BAR_HEIGHT


class TopBar:
    """Simple wrapper que expone la barra superior como un control reutilizable."""

    def __init__(self, on_toggle_settings) -> None:
        self._on_toggle_settings = on_toggle_settings
        self._control = self._build()

    def _build(self) -> ft.Control:
        settings_button = ft.IconButton(
            icon=Icons.SETTINGS_OUTLINED,
            icon_color=PRIMARY_COLOR,
            on_click=self._handle_toggle,
            tooltip="Configuración",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(12, 12, 12, 12),
                bgcolor={ft.ControlState.HOVERED: "#ffe3e3"},
            ),
        )

        return ft.Container(
            height=TOP_BAR_HEIGHT,
            bgcolor=BACKGROUND_COLOR,
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                controls=[
                    ft.Container(expand=True),
                    settings_button,
                ],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    @property
    def view(self) -> ft.Control:
        return self._control

    def _handle_toggle(self, _event) -> None:
        if self._on_toggle_settings:
            self._on_toggle_settings()
