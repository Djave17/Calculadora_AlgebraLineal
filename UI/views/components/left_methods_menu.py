from __future__ import annotations

from typing import Callable, Optional

import flet as ft
from flet import Colors as colors, Icons as icons

from ...methods import MethodCategory, MethodInfo
from ...styles import (
    BORDER_COLOR,
    LEFT_MENU_WIDTH,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SURFACE_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)


class LeftMethodsMenu:
    def __init__(
        self,
        categories: tuple[MethodCategory, ...],
        active_method_id: str,
        on_method_selected: Callable[[str], None],
    ) -> None:
        self._categories = categories
        self._active_method_id = active_method_id
        self._on_method_selected = on_method_selected
        self._items: list[MethodButton] = []
        self._container = self._build()

    def set_active_method(self, method_id: str) -> None:
        self._active_method_id = method_id
        for item in self._items:
            item.set_active(item.method.id == method_id)
        if self._container:
            self._container.update()

    def _build(self) -> ft.Control:
        content = ft.Column(
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        brand = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=48,
                    height=48,
                    border_radius=14,
                    bgcolor="#fff0ef",
                    content=ft.Image(
                        src="matrix-logo.png",
                        width=48,
                        height=48,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                ),
                ft.Column(
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            "MATRIX CALC",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_DARK,
                        ),
                        ft.Text(
                            "Desktop Linear Algebra Toolkit",
                            size=11,
                            color=TEXT_MUTED,
                        ),
                    ],
                ),
            ],
        )

        header = ft.Column(
            spacing=4,
            controls=[
                ft.Text(
                    "Métodos",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                ),
                ft.Text(
                    "Selecciona un método para comenzar",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )
        content.controls.extend([brand, header])

        self._items.clear()
        for category in self._categories:
            methods = list(category.methods)
            if not methods:
                continue
            content.controls.append(
                ft.Text(
                    category.label.upper(),
                    size=11,
                    color=TEXT_MUTED,
                    weight=ft.FontWeight.W_600,
                )
            )
            for method in methods:
                button = MethodButton(
                    method=method,
                    is_active=method.id == self._active_method_id,
                    on_click=self._on_method_selected,
                )
                self._items.append(button)
                content.controls.append(button.view)

        container = ft.Container(
            width=LEFT_MENU_WIDTH,
            bgcolor=SURFACE_COLOR,
            border=ft.border.only(right=ft.border.BorderSide(width=1, color=BORDER_COLOR)),
            padding=ft.Padding(24, 24, 24, 24),
            content=content,
        )
        return container

    @property
    def view(self) -> ft.Control:
        return self._container


class MethodButton:
    def __init__(
        self,
        method: MethodInfo,
        is_active: bool,
        on_click: Callable[[str], None],
    ) -> None:
        self.method = method
        self._is_active = is_active
        self._on_click = on_click
        self._icon_control: Optional[ft.Icon] = None
        self._label_control: Optional[ft.Text] = None
        self._container: Optional[ft.Container] = None
        self._control = self._build()

    def _build(self) -> ft.Control:
        icon = ft.Icon(
            name=getattr(icons, self.method.icon, icons.CHECK),
            color=colors.WHITE if self._is_active else PRIMARY_COLOR,
            size=20,
        )
        label = ft.Text(
            self.method.label,
            color=colors.WHITE if self._is_active else TEXT_DARK,
            size=13,
            weight=ft.FontWeight.BOLD if self._is_active else ft.FontWeight.W_500,
        )
        description = None
        if not self.method.available:
            description = ft.Text(
                "Próximamente",
                size=11,
                color=TEXT_MUTED,
            )
        row = ft.Row(
            controls=[
                icon,
                ft.Column([
                    label,
                    description or ft.Container(height=0),
                ], spacing=2),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        )

        container = ft.Container(
            padding=ft.Padding(16, 14, 16, 14),
            border_radius=14,
            bgcolor=PRIMARY_COLOR if self._is_active and self.method.available else None,
            ink=self.method.available,
            on_click=self._handle_click if self.method.available else None,
            content=row,
            border=ft.border.all(1, color=PRIMARY_COLOR if self.method.available else BORDER_COLOR),
        )

        if not self.method.available:
            icon.color = TEXT_MUTED
            label.color = TEXT_MUTED
            label.weight = ft.FontWeight.W_500

        self._icon_control = icon
        self._label_control = label
        self._container = container
        return container

    def set_active(self, active: bool) -> None:
        if not self.method.available:
            active = False
        self._is_active = active
        if self._icon_control and self._label_control and self._container:
            self._icon_control.color = (
                colors.WHITE if active and self.method.available else (PRIMARY_COLOR if self.method.available else TEXT_MUTED)
            )
            self._label_control.color = (
                colors.WHITE if active and self.method.available else (TEXT_DARK if self.method.available else TEXT_MUTED)
            )
            self._label_control.weight = ft.FontWeight.BOLD if active and self.method.available else ft.FontWeight.W_500
            self._container.bgcolor = PRIMARY_COLOR if active and self.method.available else None
            self._container.border = ft.border.all(1, color=PRIMARY_COLOR if self.method.available else BORDER_COLOR)
            self._container.update()

    def _handle_click(self, _event) -> None:
        if not self.method.available:
            return
        if self._on_click:
            self._on_click(self.method.id)

    @property
    def view(self) -> ft.Control:
        return self._control
