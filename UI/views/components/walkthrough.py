from __future__ import annotations

from typing import Callable

import flet as ft
from flet import Colors as colors, Icons as icons

from ...styles import (
    BACKGROUND_COLOR,
    CARD_RADIUS,
    PRIMARY_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)


class WalkthroughView:
    def __init__(self, on_start: Callable[[], None]) -> None:
        self._on_start = on_start
        self._control = self._build()

    def _build(self) -> ft.Control:
        cards = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=16,
            spacing=16,
            controls=[
                self._build_card("Método de Gauss", icons.WAVES),
                self._build_card("Operaciones", icons.GRID_VIEW),
                self._build_card("Calculadora", icons.CALCULATE_OUTLINED),
            ],
        )

        logo = ft.Container(
            width=80,
            height=80,
            border_radius=24,
            bgcolor="#fff0ef",
            alignment=ft.alignment.center,
            content=ft.Image(
                src="matrix-logo.png",
                width=64,
                height=64,
                fit=ft.ImageFit.CONTAIN,
            ),
        )

        hero = ft.Row(
            spacing=16,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[logo, ft.Text("MATRIX CALC", size=40, weight=ft.FontWeight.BOLD, color=TEXT_DARK)],
        )

        description = ft.Text(
            "Bienvenido a MatrixCalc, tu herramienta definitiva para el cálculo de matrices. "
            "Explora nuestros métodos y aprende operaciones matemáticas con matrices.",
            size=16,
            color=TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
            width=680,
        )

        start_button = ft.ElevatedButton(
            "Comenzar",
            on_click=lambda e: self._on_start() if self._on_start else None,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                color={ft.ControlState.DEFAULT: colors.WHITE},
                padding=ft.Padding(28, 16, 28, 16),
                shape=ft.RoundedRectangleBorder(radius=18),
            ),
        )

        column = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=28,
            controls=[
                hero,
                description,
                cards,
                start_button,
            ],
        )

        return ft.Container(
            expand=True,
            bgcolor=BACKGROUND_COLOR,
            padding=ft.Padding(32, 48, 32, 48),
            content=column,
        )

    @property
    def view(self) -> ft.Control:
        return self._control

    def _build_card(self, title: str, icon: str) -> ft.Control:
        return ft.Container(
            col={"xs": 12, "md": 4, "lg": 3},
            width=220,
            padding=ft.Padding(20, 24, 20, 24),
            bgcolor=PRIMARY_COLOR,
            border_radius=CARD_RADIUS,
            shadow=ft.BoxShadow(
                blur_radius=12,
                color="rgba(166, 8, 15, 0.12)",
                spread_radius=1,
            ),
            content=ft.Column(
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, color=colors.WHITE, size=36),
                    ft.Text(title, color=colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(
                        "Accede rápidamente a herramientas clave para el estudio de álgebra lineal.",
                        color=colors.WHITE,
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
