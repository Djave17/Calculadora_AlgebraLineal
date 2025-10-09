from __future__ import annotations

from fractions import Fraction
from typing import List, Optional

import flet as ft
from flet import Colors as colors

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel, MatrixEquationResultVM, ResultVM

from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class MatrixEquationView:
    """Editor para resolver AX = B columna por columna."""

    MIN_ROWS = 2
    MAX_ROWS = 8
    MIN_COLS = 2
    MAX_COLS = 12
    MIN_RHS = 1
    MAX_RHS = 6

    def __init__(
        self,
        page: ft.Page,
        view_model: MatrixCalculatorViewModel,
        on_show_steps,
    ) -> None:
        self._page = page
        self._vm = view_model
        self._on_show_steps = on_show_steps

        self._rows = max(self.MIN_ROWS, min(self.MAX_ROWS, view_model.rows))
        self._cols = max(self.MIN_COLS, min(self.MAX_COLS, view_model.cols))
        self._rhs_cols = 1

        self._a_cells: List[List[ft.TextField]] = []
        self._b_cells: List[List[ft.TextField]] = []
        self._latest_results: Optional[MatrixEquationResultVM] = None

        self._rows_field = ft.TextField(
            label="Filas",
            value=str(self._rows),
            width=90,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=lambda e: self._handle_dimension_change(),
            on_submit=lambda e: self._handle_dimension_change(),
        )
        self._cols_field = ft.TextField(
            label="Columnas de A",
            value=str(self._cols),
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=lambda e: self._handle_dimension_change(),
            on_submit=lambda e: self._handle_dimension_change(),
        )
        self._rhs_field = ft.TextField(
            label="Columnas de B",
            value=str(self._rhs_cols),
            width=140,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=lambda e: self._handle_dimension_change(),
            on_submit=lambda e: self._handle_dimension_change(),
        )

        self._matrix_a_container = ft.Column(spacing=6, expand=True)
        self._matrix_b_container = ft.Column(spacing=6, expand=True)
        self._results_container = ft.Column(spacing=10, expand=True)

        self._root = self._build()
        self._rebuild_tables()
        self._render_placeholder_results()

    @property
    def view(self) -> ft.Control:
        return self._root

    # ------------------------------ Construcción ------------------------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Ecuación matricial AX = B", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Especifica A y B para resolver cada columna de B como un sistema independiente.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        dims = ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[self._rows_field, self._cols_field, self._rhs_field],
        )

        matrices_row = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16,
            controls=[
                ft.Container(
                    col={"xs": 12, "md": 6},
                    bgcolor=SURFACE_COLOR,
                    border_radius=16,
                    padding=ft.Padding(20, 20, 20, 20),
                    border=ft.border.all(1, color=PRIMARY_COLOR),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text("Matriz A", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            self._matrix_a_container,
                        ],
                    ),
                ),
                ft.Container(
                    col={"xs": 12, "md": 6},
                    bgcolor=SURFACE_COLOR,
                    border_radius=16,
                    padding=ft.Padding(20, 20, 20, 20),
                    border=ft.border.all(1, color=BORDER_COLOR),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text("Matriz B", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            self._matrix_b_container,
                        ],
                    ),
                ),
            ],
        )

        actions = ft.Row(
            spacing=12,
            controls=[
                ft.FilledButton("Resolver", icon=ft.icons.PLAY_ARROW, on_click=self._handle_resolve),
                ft.OutlinedButton("Limpiar", icon=ft.icons.CLEAR, on_click=self._handle_clear),
            ],
        )

        results_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=20,
            border=ft.border.all(1, color=BORDER_COLOR),
            padding=ft.Padding(20, 20, 20, 20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Diagnóstico global", size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    self._results_container,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(24, 16, 24, 24),
            content=ft.Column(
                expand=True,
                spacing=18,
                controls=[header, dims, matrices_row, actions, results_card],
            ),
        )

    # ------------------------------ Tablas ------------------------------
    def _rebuild_tables(self) -> None:
        self._a_cells = []
        self._matrix_a_container.controls.clear()
        for r in range(self._rows):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for c in range(self._cols):
                field = ft.TextField(
                    value="0",
                    width=70,
                    height=44,
                    text_align=ft.TextAlign.CENTER,
                    bgcolor="#fff5f4",
                    border_color=PRIMARY_COLOR,
                    focused_border_color=SECONDARY_COLOR,
                    content_padding=ft.Padding(0, 6, 0, 6),
                    cursor_color=PRIMARY_COLOR,
                )
                row_fields.append(field)
                row_controls.append(field)
            self._a_cells.append(row_fields)
            self._matrix_a_container.controls.append(ft.Row(row_controls, spacing=8))

        self._b_cells = []
        self._matrix_b_container.controls.clear()
        for r in range(self._rows):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for c in range(self._rhs_cols):
                field = ft.TextField(
                    value="0",
                    width=70,
                    height=44,
                    text_align=ft.TextAlign.CENTER,
                    bgcolor="#fff7f5",
                    border_color=BORDER_COLOR,
                    focused_border_color=PRIMARY_COLOR,
                    content_padding=ft.Padding(0, 6, 0, 6),
                    cursor_color=PRIMARY_COLOR,
                )
                row_fields.append(field)
                row_controls.append(field)
            self._b_cells.append(row_fields)
            self._matrix_b_container.controls.append(ft.Row(row_controls, spacing=8))

        self._matrix_a_container.update()
        self._matrix_b_container.update()

    # ------------------------------ Eventos ------------------------------
    def _handle_dimension_change(self) -> None:
        try:
            rows = int(self._rows_field.value or self._rows)
            cols = int(self._cols_field.value or self._cols)
            rhs = int(self._rhs_field.value or self._rhs_cols)
        except ValueError:
            self._show_error("Dimensiones inválidas; usa números enteros.")
            return

        rows = max(self.MIN_ROWS, min(self.MAX_ROWS, rows))
        cols = max(self.MIN_COLS, min(self.MAX_COLS, cols))
        rhs = max(self.MIN_RHS, min(self.MAX_RHS, rhs))

        self._rows = rows
        self._cols = cols
        self._rhs_cols = rhs

        self._rows_field.value = str(rows)
        self._cols_field.value = str(cols)
        self._rhs_field.value = str(rhs)

        self._rows_field.update()
        self._cols_field.update()
        self._rhs_field.update()

        self._rebuild_tables()
        self._render_placeholder_results()

    def _handle_resolve(self, _event) -> None:
        try:
            a_rows = self._collect_matrix(self._a_cells)
            b_rows = self._collect_matrix(self._b_cells)
        except ValueError as exc:  # pragma: no cover - validación de entrada
            self._show_error(str(exc))
            return

        self._vm.rows = self._rows
        self._vm.cols = self._cols

        try:
            result = self._vm.solve_matrix_equation(a_rows, b_rows)
        except Exception as exc:  # pragma: no cover - propagación lógica
            self._show_error(str(exc))
            return

        self._latest_results = result
        self._render_results(result)

    def _handle_clear(self, _event) -> None:
        for fields in (self._a_cells, self._b_cells):
            for row in fields:
                for field in row:
                    field.value = "0"
                    field.update()
        self._latest_results = None
        self._render_placeholder_results()

    # ------------------------------ Resultados ------------------------------
    def _render_placeholder_results(self) -> None:
        self._results_container.controls.clear()
        self._results_container.controls.append(
            ft.Text("Introduce matrices A y B para analizar la ecuación.", color=TEXT_MUTED)
        )
        self._results_container.update()

    def _render_results(self, data: MatrixEquationResultVM) -> None:
        from ...helpers import format_result_lines

        self._results_container.controls.clear()

        self._results_container.controls.append(
            ft.Text(f"Diagnóstico global: {data.status}", weight=ft.FontWeight.BOLD)
        )

        for column_vm in data.columns:
            result = column_vm.result
            header = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Columna {column_vm.label}", weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        "Ver pasos",
                        icon=ft.icons.NAVIGATE_NEXT,
                        on_click=lambda e, res=result, lbl=column_vm.label: self._show_steps(res, lbl),
                        disabled=not result.steps,
                    ),
                ],
            )
            self._results_container.controls.append(header)
            for line in format_result_lines(result, [f"x{idx}" for idx in range(1, self._cols + 1)]):
                self._results_container.controls.append(ft.Text(line, size=12))
            self._results_container.controls.append(ft.Divider(color=BORDER_COLOR))

        self._results_container.update()

    def _show_steps(self, result: ResultVM, label: str) -> None:
        if not result.steps:
            self._show_error("No hay pasos registrados para esta columna.")
            return
        self._on_show_steps(result.steps, result.pivot_cols or [])

    # ------------------------------ Utilidades ------------------------------
    def _collect_matrix(self, cells: List[List[ft.TextField]]) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in cells]
        return parse_matrix(raw)

    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(bgcolor=colors.ERROR, content=ft.Text(message))
        self._page.snack_bar.open = True
        self._page.update()
