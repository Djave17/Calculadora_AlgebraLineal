from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Sequence

import flet as ft
from flet import Icons as icons

from ViewModels.matrix_inverse_vm import MatrixInverseResultVM, MatrixInverseViewModel, PropertyCheckVM
from ViewModels.resolucion_matriz_vm import StepVM

from ...helpers import parse_matrix
from ...styles import (
    BORDER_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SURFACE_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)
from .steps_dialog import show_steps_dialog


class MatrixInverseView:
    MIN_ORDER = 2
    MAX_ORDER = 8

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._order = 3
        self._view_model = MatrixInverseViewModel()

        self._cells: List[List[ft.TextField]] = []
        self._matrix_container = ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._info_text = ft.Text("", size=12, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)
        self._result_container = ft.Column(spacing=16, expand=True)
        self._steps_button = ft.TextButton(
            "Ver pasos en ventana",
            icon=icons.OPEN_IN_NEW,
            visible=False,
            on_click=self._show_steps_dialog,
        )
        self._last_steps: List[StepVM] = []
        self._last_pivots: List[int] = []

        self._root = self._build()
        self._rebuild_table()
        self._update_info_label()
        self._render_placeholder()

    @property
    def view(self) -> ft.Control:
        return self._root

    def order(self) -> int:
        return self._order

    def set_order(self, order: int) -> None:
        order = max(self.MIN_ORDER, min(self.MAX_ORDER, order))
        if order == self._order:
            return
        self._order = order
        self._rebuild_table()
        self._update_info_label()
        self._render_placeholder()

    def resolve(self) -> None:
        try:
            matrix = self._collect_matrix()
        except ValueError as exc:
            self._show_error(str(exc))
            return
        try:
            result = self._view_model.compute(matrix)
        except ValueError as exc:
            self._show_error(str(exc))
            return
        self._render_result(result)

    def clear_fields(self) -> None:
        for row in self._cells:
            for cell in row:
                cell.value = "0"
                self._safe_update(cell)
        self._render_placeholder()

    # --------------------------- Construcción --------------------------- #
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=4,
            controls=[
                ft.Text("Inversa de una matriz", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Aplica Gauss-Jordan sobre [A | I] para obtener [I | A⁻¹] y comprueba propiedades de invertibilidad.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        matrix_card = ft.Container(
            expand=True,
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(24, 24, 24, 24),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("Matriz A", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                    ft.Text(
                                        "Introduce los elementos de A para armar la matriz aumentada [A | I].",
                                        size=12,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                            ft.Container(
                                bgcolor="#ffe4dd",
                                border_radius=12,
                                padding=ft.Padding(12, 6, 12, 6),
                                content=self._info_text,
                            ),
                        ],
                    ),
                    ft.Container(
                        alignment=ft.alignment.center,
                        bgcolor="#fffaf6",
                        border=ft.border.all(1, color=BORDER_COLOR),
                        border_radius=16,
                        padding=ft.Padding(12, 16, 12, 16),
                        content=self._matrix_container,
                    ),
                ],
            ),
        )

        process_card = ft.Container(
            expand=True,
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(24, 24, 24, 24),
            content=ft.Column(
                spacing=16,
                expand=True,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Proceso Gauss-Jordan", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            self._steps_button,
                        ],
                    ),
                    self._result_container,
                ],
            ),
        )

        body = ft.Column(
            expand=True,
            spacing=16,
            controls=[matrix_card, process_card],
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(16, 0, 16, 0),
            content=ft.Column(
                expand=True,
                spacing=18,
                controls=[header, body],
            ),
        )

    def _rebuild_table(self) -> None:
        self._matrix_container.controls.clear()
        self._cells.clear()
        for _ in range(self._order):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for _ in range(self._order):
                field = ft.TextField(
                    value="0",
                    width=72,
                    height=44,
                    text_align=ft.TextAlign.CENTER,
                    bgcolor="#fff4ef",
                    border_color=BORDER_COLOR,
                    focused_border_color=PRIMARY_COLOR,
                    cursor_color=PRIMARY_COLOR,
                    content_padding=ft.Padding(0, 6, 0, 6),
                    border_radius=12,
                )
                row_fields.append(field)
                row_controls.append(field)
            self._cells.append(row_fields)
            self._matrix_container.controls.append(
                ft.Row(row_controls, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )
        self._safe_update(self._matrix_container)

    def _update_info_label(self) -> None:
        self._info_text.value = f"Orden {self._order} × {self._order}"
        self._safe_update(self._info_text)

    # --------------------------- Renderizado --------------------------- #
    def _render_placeholder(self) -> None:
        self._last_steps = []
        self._last_pivots = []
        self._steps_button.visible = False
        self._safe_update(self._steps_button)
        self._result_container.controls = [
            ft.Text(
                "Ingresa una matriz cuadrada A y utiliza el panel de la derecha para ejecutar Gauss-Jordan.",
                color=TEXT_MUTED,
            )
        ]
        self._safe_update(self._result_container)

    def _render_result(self, result: MatrixInverseResultVM) -> None:
        self._last_steps = result.steps
        self._last_pivots = result.pivot_columns
        self._steps_button.visible = bool(result.steps)
        self._safe_update(self._steps_button)

        message_color = PRIMARY_COLOR if result.is_invertible else "#c62828"
        message = ft.Text(result.message, color=message_color, weight=ft.FontWeight.BOLD)

        content: List[ft.Control] = [
            message,
            ft.Text("Construcción de la matriz aumentada [A | I]:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_matrix_card(result.initial_augmented),
            ft.Text("Transformación paso a paso:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_steps_section(result.steps),
            ft.Text("Resultado final de Gauss-Jordan:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_matrix_card(result.final_augmented),
        ]

        if result.is_invertible and result.inverse_matrix is not None:
            content.extend([
                ft.Text("Matriz inversa A⁻¹:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
                self._build_matrix_card(result.inverse_matrix, emphasize=True),
            ])

        content.extend([
            ft.Text("Verificación teórica (teorema de la matriz invertible):", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_properties_section(result.properties),
        ])

        self._result_container.controls = content
        self._safe_update(self._result_container)

    def _build_matrix_card(self, matrix: Sequence[Sequence[Fraction]], emphasize: bool = False) -> ft.Control:
        grid = self._build_matrix_grid(matrix)
        return ft.Container(
            bgcolor="#fffaf6" if emphasize else "#fff7f5",
            border=ft.border.all(1, color=PRIMARY_COLOR if emphasize else BORDER_COLOR),
            border_radius=14,
            padding=ft.Padding(12, 12, 12, 12),
            content=grid,
        )

    def _build_matrix_grid(
        self,
        matrix: Sequence[Sequence[Fraction]],
        pivot: Optional[tuple[int, int]] = None,
    ) -> ft.Column:
        column = ft.Column(spacing=4)
        for i, row in enumerate(matrix):
            cells: List[ft.Control] = []
            for j, value in enumerate(row):
                is_pivot = pivot is not None and pivot == (i, j)
                cells.append(
                    ft.Container(
                        width=64,
                        height=32,
                        alignment=ft.alignment.center,
                        bgcolor=SECONDARY_COLOR if is_pivot else ft.Colors.WHITE,
                        border=ft.border.all(1, color=PRIMARY_COLOR if is_pivot else BORDER_COLOR),
                        border_radius=8,
                        content=ft.Text(str(value), color=TEXT_DARK if not is_pivot else ft.Colors.WHITE, size=12),
                    )
                )
            column.controls.append(ft.Row(cells, spacing=6))
        return column

    def _build_steps_section(self, steps: Sequence[StepVM]) -> ft.Control:
        if not steps:
            return ft.Text("No se registraron pasos.", color=TEXT_MUTED)
        cards: List[ft.Control] = []
        for step in steps:
            label = "Paso inicial" if step.number == 0 else f"Paso {step.number}"
            pivot_text = ""
            if step.pivot_row is not None and step.pivot_col is not None:
                pivot_text = f" (pivote en fila {step.pivot_row + 1}, columna {step.pivot_col + 1})"
            description = ft.Text(f"{label}: {step.description}{pivot_text}", color=TEXT_DARK, weight=ft.FontWeight.W_600)
            matrix = step.after_matrix or []
            cards.append(
                ft.Container(
                    bgcolor="#fff1f1" if step.number != 0 else "#f8f9ff",
                    border=ft.border.all(1, color=PRIMARY_COLOR if step.number != 0 else BORDER_COLOR),
                    border_radius=14,
                    padding=ft.Padding(12, 12, 12, 12),
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            description,
                            self._build_matrix_grid(matrix, pivot=(step.pivot_row, step.pivot_col) if step.pivot_row is not None and step.pivot_col is not None else None),
                        ],
                    ),
                )
            )
        return ft.Column(spacing=10, controls=cards, scroll=ft.ScrollMode.AUTO)

    def _build_properties_section(self, properties: Sequence[PropertyCheckVM]) -> ft.Control:
        items: List[ft.Control] = []
        for prop in properties:
            icon_name = icons.CHECK_CIRCLE if prop.holds else icons.ERROR_OUTLINE
            icon_color = PRIMARY_COLOR if prop.holds else "#d32f2f"
            items.append(
                ft.Container(
                    bgcolor="#f1f8f6" if prop.holds else "#fff5f5",
                    border_radius=12,
                    padding=ft.Padding(12, 12, 12, 12),
                    border=ft.border.all(1, color=PRIMARY_COLOR if prop.holds else "#f8b4b4"),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(icon_name, color=icon_color, size=20),
                                    ft.Text(f"({prop.code}) {prop.label}", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                                ],
                            ),
                            ft.Text(prop.interpretation, size=12, color=TEXT_MUTED),
                        ],
                    ),
                )
            )
        return ft.Column(spacing=10, controls=items)

    # ----------------------------- Utilidades ----------------------------- #
    def _collect_matrix(self) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in self._cells]
        matrix = parse_matrix(raw)
        if len(matrix) != len(matrix[0]):
            raise ValueError("A debe ser cuadrada (mismo número de filas y columnas).")
        return matrix

    def _show_steps_dialog(self, _event=None) -> None:
        if not self._last_steps:
            return
        show_steps_dialog(self._page, self._last_steps, self._last_pivots, title="Pasos Gauss-Jordan para A⁻¹")

    def _show_error(self, message: str) -> None:
        if not self._page:
            return
        self._page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#f48f8f")
        self._page.snack_bar.open = True
        self._page.update()

    def _safe_update(self, control: Optional[ft.Control]) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
