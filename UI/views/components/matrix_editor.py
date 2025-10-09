from __future__ import annotations

from fractions import Fraction
from typing import Callable, List, Optional, Sequence, Tuple

import flet as ft
from flet import Icons as icons

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel, ResultVM, StepVM

from ...helpers import (
    format_result_lines,
    matrix_header_labels,
    parse_matrix,
)
from ...methods import MethodInfo
from ...styles import (
    ACCENT_COLOR,
    BORDER_COLOR,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SURFACE_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)

ToolbarAction = Callable[[str], None]


class MatrixEditor:
    TOOLBAR_TOKENS: Tuple[str, ...] = (
        "sin",
        "cos",
        "tan",
        "√",
        "log",
        "ln",
        "π",
        "e",
        "^",
        "/",
        "(",
        ")",
    )

    def __init__(
        self,
        page: ft.Page,
        rows: int,
        cols: int,
        method: MethodInfo,
        on_request_steps: Callable[[List[StepVM], List[int]], None],
        on_toggle_settings: Callable[[], None] | None = None,
    ) -> None:
        self._page = page
        self.rows = rows
        self.cols = cols
        self.method = method
        self._analysis_context = method.analysis_context
        self._force_homogeneous = method.force_homogeneous
        self._variable_prefix = method.variable_prefix
        self.category_label = method.category
        self._cells: List[List[ft.TextField]] = []
        self._active_cell: Optional[Tuple[int, int]] = None
        self._on_request_steps = on_request_steps
        self._on_toggle_settings = on_toggle_settings
        self._last_steps: List[StepVM] = []
        self._last_pivot_cols: List[int] = []
        self._result_section: Optional[ft.Column] = None
        self._steps_button: Optional[ft.TextButton] = None
        self._matrix_container: Optional[ft.Container] = None
        self._placeholder_container: Optional[ft.Container] = None
        self._matrix_stack: Optional[ft.Stack] = None
        self._matrix_scroll_row: Optional[ft.Row] = None
        self._method_title: Optional[ft.Text] = None
        self._method_badge: Optional[ft.Text] = None
        self._dimension_hint: Optional[ft.Text] = None
        self._toolbar_container: Optional[ft.Container] = None

        self._root = self._build()
        self._rebuild_matrix()
        self._update_method_labels()
        self._update_layout_width()
        self._apply_method_constraints()

    # ------------------------------ Construcción ------------------------------
    def _build(self) -> ft.Control:
        self._method_title = ft.Text(
            self.method.label,
            size=22,
            weight=ft.FontWeight.BOLD,
            color=TEXT_DARK,
        )
        self._method_badge = ft.Text(
            self.method.category,
            size=12,
            color=TEXT_MUTED,
        )
        title_column = ft.Column(
            spacing=2,
            controls=[self._method_title, self._method_badge],
        )

        header_controls: List[ft.Control] = [title_column]
        if self._on_toggle_settings is not None:
            header_controls.append(
                ft.IconButton(
                    icon=icons.SETTINGS_OUTLINED,
                    icon_color=PRIMARY_COLOR,
                    tooltip="Configuración",
                    on_click=lambda _: self._on_toggle_settings(),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding(10, 10, 10, 10),
                        bgcolor={ft.ControlState.HOVERED: "#ffe3e3"},
                    ),
                )
            )

        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=header_controls,
        )

        toolbar = self._build_toolbar()

        self._matrix_container = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=PRIMARY_COLOR),
            border_radius=20,
            padding=ft.Padding(20, 24, 20, 24),
            expand=True,
            visible=self.method.available,
            content=ft.Column(spacing=18, expand=True),
        )

        self._placeholder_container = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(24, 28, 24, 28),
            visible=not self.method.available,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Método en preparación",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_DARK,
                    ),
                    ft.Text(
                        "Este módulo aún no cuenta con resolución interactiva."
                        " Usa Gauss-Jordan para explorar los pasos disponibles.",
                        size=13,
                        color=TEXT_MUTED,
                        width=420,
                    ),
                ],
                spacing=10,
            ),
        )

        self._matrix_stack = ft.Stack(
            controls=[
                self._matrix_container,
                self._placeholder_container,
            ],
        )

        self._matrix_scroll_row = ft.Row(
            controls=[self._matrix_stack],
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

        self._result_section = ft.Column(
            spacing=6,
            expand=True,
            controls=[
                ft.Text(
                    "Resuelve un sistema para ver el diagnóstico.",
                    size=13,
                    color=TEXT_MUTED,
                )
            ],
        )
        self._steps_button = ft.TextButton(
            "Ver pasos Gauss–Jordan",
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                overlay_color=ACCENT_COLOR,
            ),
            visible=False,
            on_click=self._handle_steps_clicked,
        )

        results_card = ft.Container(
            expand=True,
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(20, 20, 20, 20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(
                        "Resultado",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_DARK,
                    ),
                    self._result_section,
                    self._steps_button,
                ],
            ),
        )

        matrix_wrapper = ft.Container(
            expand=True,
            content=self._matrix_scroll_row,
        )

        content_column = ft.Column(
            expand=True,
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                matrix_wrapper,
                results_card,
            ],
        )

        root_column = ft.Column(
            expand=True,
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                header,
                toolbar,
                content_column,
            ],
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(24, 16, 24, 24),
            content=root_column,
        )

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build_toolbar(self) -> ft.Control:
        buttons = []
        for token in self.TOOLBAR_TOKENS:
            buttons.append(
                ft.TextButton(
                    token,
                    style=ft.ButtonStyle(
                        color={ft.ControlState.DEFAULT: TEXT_DARK},
                        bgcolor={ft.ControlState.HOVERED: "#ffe3e3"},
                        padding=ft.Padding(10, 8, 10, 8),
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                    on_click=lambda e, t=token: self._insert_token(t),
                )
            )
        toolbar = ft.Container(
            expand=True,
            border=ft.border.all(1, color=PRIMARY_COLOR),
            border_radius=16,
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor="#fff0ef",
            content=ft.Row(
                expand=True,
                controls=buttons,
                wrap=True,
                spacing=8,
                run_spacing=8,
            ),
        )
        self._toolbar_container = toolbar
        return toolbar

    # ------------------------------ Interacción ------------------------------
    def _insert_token(self, token: str) -> None:
        if self._active_cell is None:
            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("Selecciona primero una celda."),
                bgcolor=SECONDARY_COLOR,
            )
            self._page.snack_bar.open = True
            self._page.update()
            return
        row, col = self._active_cell
        field = self._cells[row][col]
        field.value = (field.value or "") + token
        field.update()

    def _handle_focus(self, row: int, col: int) -> None:
        self._active_cell = (row, col)

    def _handle_steps_clicked(self, _event) -> None:
        if self._last_steps and self._on_request_steps:
            self._on_request_steps(self._last_steps, self._last_pivot_cols)

    # ------------------------------ API pública ------------------------------
    def set_dimensions(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self._rebuild_matrix()
        self._update_dimension_hint()
        self._update_layout_width()
        self._apply_method_constraints()
        self._safe_update(self._root)

    def update_method(self, method: MethodInfo) -> None:
        self.method = method
        self._analysis_context = method.analysis_context
        self._force_homogeneous = method.force_homogeneous
        self._variable_prefix = method.variable_prefix
        self.category_label = method.category
        self._update_method_labels()
        if self._placeholder_container:
            self._placeholder_container.visible = not method.available
        if self._matrix_container:
            self._matrix_container.visible = method.available
        if not method.available:
            self.clear_results()
        self._rebuild_matrix()
        self._update_layout_width()
        self._apply_method_constraints()
        self._safe_update(self._root)

    def update_method_category(self, category_label: str) -> None:
        self.category_label = category_label
        self._update_method_labels()
        self._safe_update(self._root)

    def get_augmented_matrix(self) -> List[List[Fraction]]:
        raw_values: List[List[str]] = []
        for row_fields in self._cells:
            raw_values.append([field.value or "0" for field in row_fields])
        matrix = parse_matrix(raw_values)
        if self._force_homogeneous:
            for row in matrix:
                if row:
                    row[-1] = Fraction(0)
        return matrix

    def clear_matrix(self) -> None:
        for row_fields in self._cells:
            for field in row_fields:
                field.value = "0"
                field.update()
        self.clear_results()
        self._apply_method_constraints()
        self._apply_method_constraints()

    def clear_results(self) -> None:
        if self._result_section:
            self._result_section.controls.clear()
            self._result_section.controls.append(
                ft.Text(
                    "Resuelve un sistema para ver el diagnóstico.",
                    size=13,
                    color=TEXT_MUTED,
                )
            )
            self._safe_update(self._result_section)
        if self._steps_button:
            self._steps_button.visible = False
            self._safe_update(self._steps_button)
        self._last_steps = []
        self._last_pivot_cols = []

    def show_result(self, result: ResultVM) -> None:
        base_lines = format_result_lines(result, self._solution_labels())
        if self._result_section:
            self._result_section.controls.clear()
            for line in base_lines:
                self._result_section.controls.append(
                    ft.Text(line, size=13, color=TEXT_DARK)
                )
            contextual_lines = self._contextual_result_lines(result)
            for line in contextual_lines:
                self._result_section.controls.append(
                    ft.Text(line, size=12, color=TEXT_MUTED)
                )
            self._safe_update(self._result_section)
        self._last_steps = result.steps or []
        self._last_pivot_cols = result.pivot_cols or []
        if self._steps_button:
            self._steps_button.visible = bool(self._last_steps)
            self._safe_update(self._steps_button)

    # ------------------------------ Utilidades internas ------------------------------
    def _rebuild_matrix(self) -> None:
        if not self._matrix_container:
            return
        container_column = self._matrix_container.content
        if isinstance(container_column, ft.Column):
            container_column.controls.clear()
            self._cells = []
            self._active_cell = None
            header_row = self._build_header_row()
            container_column.controls.append(header_row)
            for row_idx in range(self.rows):
                container_column.controls.append(self._build_matrix_row(row_idx))
            self._dimension_hint = ft.Text(
                size=12,
                color=TEXT_MUTED,
            )
            self._update_dimension_hint()
            container_column.controls.append(self._dimension_hint)
            # No llamar update() aquí; el control puede no estar montado aún.
        self.clear_results()
        self._update_layout_width()
        self._apply_method_constraints()

    def _build_header_row(self) -> ft.Control:
        labels = self._header_labels()
        cells = [
            ft.Text("#", width=32, text_align=ft.TextAlign.CENTER, color=TEXT_MUTED)
        ]
        for label in labels[:-1]:
            cells.append(
                ft.Text(
                    label,
                    width=76,
                    text_align=ft.TextAlign.CENTER,
                    color=TEXT_MUTED,
                    weight=ft.FontWeight.W_600,
                )
            )
        cells.append(
            ft.Text(
                labels[-1],
                width=76,
                text_align=ft.TextAlign.CENTER,
                color=SECONDARY_COLOR,
                weight=ft.FontWeight.W_600,
            )
        )
        return ft.Row(cells, spacing=8)

    def _build_matrix_row(self, row_idx: int) -> ft.Control:
        row_fields: List[ft.TextField] = []
        controls: List[ft.Control] = [
            ft.Container(
                width=32,
                alignment=ft.alignment.center,
                content=ft.Text(str(row_idx + 1), color=TEXT_MUTED),
            )
        ]
        for col_idx in range(self.cols + 1):
            field = ft.TextField(
                value="0",
                text_align=ft.TextAlign.CENTER,
                width=76,
                bgcolor="#fff5f4",
                border_color=PRIMARY_COLOR,
                focused_border_color=SECONDARY_COLOR,
                content_padding=ft.Padding(0, 6, 0, 6),
                height=48,
                cursor_color=PRIMARY_COLOR,
                on_focus=lambda e, r=row_idx, c=col_idx: self._handle_focus(r, c),
            )
            row_fields.append(field)
            controls.append(field)
        self._cells.append(row_fields)
        return ft.Row(controls, spacing=8)

    def _update_method_labels(self) -> None:
        if self._method_title:
            self._method_title.value = self.method.label
            self._safe_update(self._method_title)
        if self._method_badge:
            self._method_badge.value = self.category_label
            self._safe_update(self._method_badge)

    def _update_dimension_hint(self) -> None:
        if self._dimension_hint:
            hint_suffix = "(A|b)"
            if self._force_homogeneous:
                hint_suffix = "(A|0)"
            self._dimension_hint.value = f"Matriz {self.rows}×{self.cols} {hint_suffix}"
            self._safe_update(self._dimension_hint)

    def _calculate_card_width(self) -> int:
        # Ancho aproximado basado en celdas (76px), separadores (8px) y padding del contenedor.
        data_columns = self.cols + 1  # incluye la columna de términos independientes
        index_width = 32
        cell_width = 76
        spacing = 8
        horizontal_padding = 40  # padding izquierdo + derecho (20 cada uno)
        gaps = (data_columns + 1) * spacing
        width = index_width + (data_columns * cell_width) + gaps + horizontal_padding
        return max(width, 360)

    def _update_layout_width(self) -> None:
        width = self._calculate_card_width()
        for control in (
            self._toolbar_container,
            self._matrix_container,
            self._placeholder_container,
            self._matrix_stack,
        ):
            if control is not None:
                control.width = width
                self._safe_update(control)
        if self._matrix_scroll_row:
            # Centrar cuando el ancho es menor al disponible aprovechando Container padre.
            self._matrix_scroll_row.controls = [self._matrix_stack] if self._matrix_stack else []
            self._safe_update(self._matrix_scroll_row)

    def _header_labels(self) -> List[str]:
        if self._analysis_context:
            prefix = self._variable_prefix or "x"
            labels = [f"{prefix}{idx}" for idx in range(1, self.cols + 1)]
            labels.append("0" if self._force_homogeneous else "b")
            return labels
        return matrix_header_labels(self.cols)

    def _solution_labels(self) -> List[str]:
        prefix = self._variable_prefix or "x"
        return [f"{prefix}{idx}" for idx in range(1, self.cols + 1)]

    def _format_variable_subset(self, indices: Sequence[int]) -> str:
        labels = self._solution_labels()
        selected = [labels[i] for i in indices if 0 <= i < len(labels)]
        return ", ".join(selected) if selected else "—"

    def _contextual_result_lines(self, result: ResultVM) -> List[str]:
        if not self._analysis_context:
            return []
        interpretation = MatrixCalculatorViewModel.interpret_result(
            result,
            context=self._analysis_context,
            is_homogeneous=self._force_homogeneous,
            variable_labels=self._solution_labels(),
        )
        lines = [f"Interpretación: {interpretation.summary}"]
        for detail in interpretation.details:
            lines.append(f"  - {detail}")
        return lines

    def _apply_method_constraints(self) -> None:
        if not self._cells:
            return
        last_index = self.cols
        for row_fields in self._cells:
            for col_idx, field in enumerate(row_fields):
                if self._force_homogeneous and col_idx == last_index:
                    if field.value != "0":
                        field.value = "0"
                    field.read_only = True
                    field.disabled = True
                    field.bgcolor = "#f8f1f0"
                else:
                    field.read_only = False
                    field.disabled = False
                    field.bgcolor = "#fff5f4"
                self._safe_update(field)

    # ------------------------------ Utilidad segura ------------------------------
    def _safe_update(self, control: Optional[ft.Control]) -> None:
        try:
            if control:
                control.update()
        except AssertionError:
            # Control aún no montado; ignorar actualización temprana.
            pass
