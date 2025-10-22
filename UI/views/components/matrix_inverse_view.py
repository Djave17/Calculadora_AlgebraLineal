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
        self._last_result: Optional[MatrixInverseResultVM] = None
        self._last_det_steps: List[StepVM] = []
        self._last_determinant_value: Fraction = Fraction(0)
        self._verification_container: ft.Container = ft.Container(visible=False)
        self._determinant_container: ft.Container = ft.Container(visible=False)
        self._main_content: ft.Column = ft.Column(spacing=16, expand=True, visible=True)
        self._active_section: str = "main"

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
        self._last_result = None
        self._last_det_steps = []
        self._last_determinant_value = Fraction(0)
        self._verification_container.visible = False
        self._verification_container.content = None
        self._determinant_container.visible = False
        self._determinant_container.content = None
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
        self._display_section("main")

    def verify_inverse(self) -> None:
        if self._last_result is None:
            self._show_error("Primero calcula la inversa antes de verificar A * A^-1 = I.")
            return
        verification = self._last_result.verification
        if not verification.can_verify:
            self._show_inline_verification_message(verification.message, success=False)
            return
        self._show_inline_verification(self._last_result)

    def show_determinant_steps(self) -> None:
        self._show_determinant_steps()

    def clear_fields(self) -> None:
        for row in self._cells:
            for cell in row:
                cell.value = "0"
                self._safe_update(cell)
        self._last_result = None
        self._last_det_steps = []
        self._verification_container.visible = False
        self._verification_container.content = None
        self._determinant_container.visible = False
        self._determinant_container.content = None
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
        self._last_result = None
        self._last_det_steps = []
        self._last_determinant_value = Fraction(0)
        self._main_content.visible = False
        self._main_content.controls.clear()
        self._verification_container.visible = False
        self._verification_container.content = None
        self._determinant_container.visible = False
        self._determinant_container.content = None
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
        self._last_result = result
        self._last_steps = result.steps
        self._last_pivots = result.pivot_columns
        self._last_det_steps = result.determinant_steps
        self._last_determinant_value = result.determinant
        self._steps_button.visible = bool(result.steps)
        self._safe_update(self._steps_button)

        message_color = PRIMARY_COLOR if result.is_invertible else "#c62828"
        message = ft.Text(result.message, color=message_color, weight=ft.FontWeight.BOLD)

        classification = "Invertible / no singular" if result.is_invertible else "No invertible / singular"
        classification_text = ft.Text(f"Clasificacion: {classification}", color=message_color)

        main_controls: List[ft.Control] = [
            message,
            classification_text,
            ft.Text("Construccion de la matriz aumentada [A | I]:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_matrix_card(result.initial_augmented),
            ft.Text("Transformacion paso a paso:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_steps_section(result.steps),
            ft.Text("Resultado final de Gauss-Jordan:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_matrix_card(result.final_augmented),
        ]

        if result.is_invertible and result.inverse_matrix is not None:
            main_controls.extend([
                ft.Text("Matriz inversa A^-1:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
                self._build_matrix_card(result.inverse_matrix, emphasize=True),
            ])

        main_controls.extend([
            ft.Text("Verificacion teorica (teorema de la matriz invertible):", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
            self._build_properties_section(result.properties),
        ])

        self._last_determinant_value = result.determinant
        determinant_value = self._format_fraction(result.determinant)
        det_summary = ft.Column(
            spacing=6,
            controls=[
                ft.Text("Determinante de A:", size=13, color=TEXT_DARK, weight=ft.FontWeight.W_600),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(f"det(A) = {determinant_value}", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                        ft.FilledButton(
                            "Ver pasos determinante",
                            icon=icons.FUNCTIONS,
                            on_click=self._show_determinant_steps,
                            style=ft.ButtonStyle(
                                bgcolor={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                            ),
                        ),
                    ],
                ),
            ],
        )
        main_controls.append(det_summary)

        self._main_content.controls = main_controls
        self._main_content.visible = True

        self._verification_container.visible = False
        self._verification_container.content = None
        self._verification_container.bgcolor = "#fff2ec"
        self._verification_container.border = ft.border.all(1, color=BORDER_COLOR)
        self._verification_container.border_radius = 16
        self._verification_container.padding = ft.Padding(16, 16, 16, 16)

        self._determinant_container.visible = False
        self._determinant_container.content = None
        self._determinant_container.bgcolor = "#f5f7ff"
        self._determinant_container.border = ft.border.all(1, color=BORDER_COLOR)
        self._determinant_container.border_radius = 16
        self._determinant_container.padding = ft.Padding(16, 16, 16, 16)

        self._result_container.controls = [
            self._main_content,
            self._verification_container,
            self._determinant_container,
        ]
        self._safe_update(self._result_container)
        self._display_section("main")

    def _show_inline_verification(self, result: MatrixInverseResultVM) -> None:
        verification = result.verification
        message_color = PRIMARY_COLOR if verification.holds else "#c62828"
        matrix_sections: List[ft.Control] = [
            self._build_labeled_matrix_card("Matriz A", result.original_matrix),
        ]
        if result.inverse_matrix:
            matrix_sections.append(
                self._build_labeled_matrix_card("Matriz inversa A^-1", result.inverse_matrix, emphasize=True)
            )
        if verification.product:
            matrix_sections.append(
                self._build_labeled_matrix_card(
                    "Producto A * A^-1",
                    verification.product,
                    emphasize=verification.holds,
                )
            )
        if verification.identity:
            matrix_sections.append(self._build_labeled_matrix_card("Matriz identidad I", verification.identity))

        matrices_column: Optional[ft.Control] = None
        if matrix_sections:
            matrices_column = ft.Container(
                height=260,
                content=ft.Column(
                    spacing=12,
                    controls=matrix_sections,
                    scroll=ft.ScrollMode.AUTO,
                ),
            )

        controls: List[ft.Control] = [
            ft.Text("Verificacion de la propiedad A * A^-1 = I", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ft.Text(verification.message, color=message_color, weight=ft.FontWeight.W_600, size=12),
        ]
        rows_a = len(result.original_matrix)
        cols_a = len(result.original_matrix[0]) if result.original_matrix else 0
        summary_text = ft.Text(
            f"Producto matricial A * A^-1: A es {rows_a}x{cols_a}.",
            size=12,
            color=TEXT_MUTED,
        )
        controls.append(summary_text)
        if verification.steps:
            controls.append(self._build_multiplication_text_summary(verification.steps))
        if matrices_column is not None:
            controls.append(matrices_column)

        self._verification_container.content = ft.Column(spacing=12, controls=controls)
        self._display_section("verification")

    def _show_inline_verification_message(self, message: str, success: bool) -> None:
        color = PRIMARY_COLOR if success else "#c62828"
        self._verification_container.content = ft.Column(
            spacing=8,
            controls=[
                ft.Text("Verificacion de la propiedad A * A^-1 = I", weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(message, color=color, weight=ft.FontWeight.W_600, size=12),
            ],
        )
        self._display_section("verification")

    def _show_determinant_steps(self, _event=None) -> None:
        if not self._last_result:
            self._show_error("Calcula la inversa antes de mostrar los pasos del determinante.")
            return
        if not self._last_det_steps:
            self._show_error("No hay pasos registrados para el determinante.")
            return
        steps_view = self._build_steps_section(self._last_det_steps)
        self._determinant_container.content = ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Cálculo de det(A) mediante eliminación Gauss-Jordan:",
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_DARK,
                ),
                ft.Text(
                    f"det(A) = {self._format_fraction(self._last_determinant_value)}",
                    weight=ft.FontWeight.W_600,
                    color=PRIMARY_COLOR if self._last_determinant_value != 0 else "#c62828",
                ),
                ft.Text("Registro de operaciones elementales:", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                self._build_step_text_log(self._last_det_steps),
                ft.Text("Matrices intermedias:", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                ft.Text(
                    "Se muestra cada matriz luego de aplicar la operación indicada.",
                    size=12,
                    color=TEXT_MUTED,
                ),
                steps_view,
            ],
        )
        self._display_section("determinant")

    def _display_section(self, section: str) -> None:
        self._active_section = section
        main_visible = section == "main"
        verification_visible = section == "verification" and self._verification_container.content is not None
        det_visible = section == "determinant" and self._determinant_container.content is not None

        self._main_content.visible = main_visible
        self._verification_container.visible = verification_visible
        self._determinant_container.visible = det_visible

        self._safe_update(self._main_content)
        self._safe_update(self._verification_container)
        self._safe_update(self._determinant_container)

    def _build_multiplication_text_summary(self, steps: Sequence) -> ft.Control:
        if not steps:
            return ft.Text("No hay detalles de multiplicación disponibles.", color=TEXT_MUTED, size=12)
        lines: List[ft.Control] = [
            ft.Text("Detalle de cada entrada C(i, j):", weight=ft.FontWeight.W_600, color=TEXT_DARK)
        ]
        for cell in steps:
            terms_expr = " + ".join(
                f"{self._format_fraction(term.left)}*{self._format_fraction(term.right)}"
                for term in cell.terms
            ) or "0"
            result_line = (
                f"C({cell.row + 1}, {cell.col + 1}) = {terms_expr} = {self._format_fraction(cell.result)}"
            )
            lines.append(ft.Text(result_line, size=12, color=TEXT_DARK))
            identity_color = PRIMARY_COLOR if cell.result == cell.expected else "#c62828"
            lines.append(
                ft.Text(
                    f"I({cell.row + 1}, {cell.col + 1}) = {self._format_fraction(cell.expected)}",
                    size=12,
                    color=identity_color,
                )
            )
        return ft.Column(spacing=4, controls=lines)

    def _build_step_text_log(self, steps: Sequence[StepVM]) -> ft.Control:
        if not steps:
            return ft.Text("No se registraron operaciones.", color=TEXT_MUTED, size=12)
        entries: List[ft.Control] = []
        for step in steps:
            label = "Paso inicial" if step.number == 0 else f"Paso {step.number}"
            description = step.description or step.operation
            if step.pivot_row is not None and step.pivot_col is not None:
                description += f" (pivote en fila {step.pivot_row + 1}, columna {step.pivot_col + 1})"
            entries.append(ft.Text(f"{label}: {description}", size=12, color=TEXT_DARK))
        return ft.Column(spacing=4, controls=entries)

    def _format_fraction(self, value: Fraction) -> str:
        if isinstance(value, Fraction):
            if value.denominator == 1:
                return f"{value.numerator}"
            return f"{value.numerator}/{value.denominator}"
        return str(value)

    def _build_labeled_matrix_card(
        self,
        title: str,
        matrix: Sequence[Sequence[Fraction]],
        emphasize: bool = False,
    ) -> ft.Control:
        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(title, weight=ft.FontWeight.W_600, color=TEXT_DARK, size=12),
                self._build_matrix_card(matrix, emphasize=emphasize),
            ],
        )

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
