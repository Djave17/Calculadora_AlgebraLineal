from __future__ import annotations

from fractions import Fraction
from typing import List, Optional

import flet as ft
from flet import Icons as icons

from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED
from ViewModels import matrix_ops_vm as ops


class MatrixOpsView:
    """Vista para operaciones elementales con matrices y verificación de propiedades.

    Incluye:
    - Suma A + B, resta A - B
    - Producto por escalar α·A
    - Producto A·B
    - Traspuestas A^T y B^T
    - Verificación de propiedades de la traspuesta y compatibilidades
    """

    MIN = 1
    MAX = 8

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._rows_a = 2
        self._cols_a = 2
        self._rows_b = 2
        self._cols_b = 2
        self._alpha_text: str = ""

        self._a_cells: List[List[ft.TextField]] = []
        self._b_cells: List[List[ft.TextField]] = []
        self._result_container = ft.Column(spacing=8, expand=True)
        self._info_label = ft.Text("", color=TEXT_MUTED)
        self._operation_dropdown: ft.Dropdown | None = None
        self._execute_button: ft.FilledButton | None = None
        self._steps_button: ft.TextButton | None = None
        self._last_steps: List[str] = []

        self._matrix_a_container = ft.Column(spacing=6, expand=True)
        self._matrix_b_container = ft.Column(spacing=6, expand=True)

        self._root = self._build()
        self._rebuild_tables()
        self._render_placeholder()

    @property
    def view(self) -> ft.Control:
        return self._root

    # ---------------- construcción -----------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Operaciones con matrices", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text("Suma, resta, producto por escalar, producto y traspuestas con pasos.", size=12, color=TEXT_MUTED),
            ],
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
                        controls=[ft.Text("Matriz A", weight=ft.FontWeight.BOLD, color=TEXT_DARK), self._matrix_a_container],
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
                        controls=[ft.Text("Matriz B", weight=ft.FontWeight.BOLD, color=TEXT_DARK), self._matrix_b_container],
                    ),
                ),
            ],
        )

        operations = [
            ("add", "A + B"),
            ("sub", "A - B"),
            ("scalar", "α · A"),
            ("mul", "A · B"),
            ("at", "A^T"),
            ("bt", "B^T"),
            ("verify", "Verificar propiedades"),
        ]
        self._operation_dropdown = ft.Dropdown(
            label="Operación",
            value=operations[0][0],
            options=[ft.dropdown.Option(key, label) for key, label in operations],
            width=240,
        )
        self._execute_button = ft.FilledButton(
            "Aplicar",
            icon=icons.PLAY_ARROW,
            on_click=self._run_selected_operation,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                overlay_color={ft.ControlState.HOVERED: SECONDARY_COLOR},
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

        actions = ft.Row(
            spacing=12,
            controls=[self._operation_dropdown, self._execute_button],
        )

        self._steps_button = ft.TextButton(
            "Ver pasos",
            icon=icons.NAVIGATE_NEXT,
            visible=False,
            on_click=self._show_steps_dialog,
            style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: PRIMARY_COLOR}),
        )

        results_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            border=ft.border.all(1, color=BORDER_COLOR),
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Resultados", size=18, weight=ft.FontWeight.BOLD),
                    self._result_container,
                    self._steps_button,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Column(
                expand=True,
                controls=[header, self._info_label, matrices_row, actions, results_card],
            ),
        )

    # --------------- eventos / acciones ---------------
    def _run_add(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells)
            res = ops.add(A, B)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_sub(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells)
            res = ops.subtract(A, B)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_scalar(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            alpha = self._parse_alpha()
            if alpha is None:
                raise ValueError("Ingresa un valor para α (por ejemplo 2, -1/3).")
            res = ops.scalar_mult(alpha, A)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_mul(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells)
            res = ops.multiply(A, B)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_transpose(self, which: str) -> None:
        try:
            src = self._collect_matrix(self._a_cells if which == 'A' else self._b_cells)
            res = ops.transpose(src)
            res.name = f"{which}^T"
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_verify(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells)
            alpha = self._parse_alpha()
            props = ops.verify_properties(A, B, alpha)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Propiedades verificadas", weight=ft.FontWeight.BOLD))
        steps: List[str] = []
        for p in props:
            estado = "Cumple" if p.get("cumple") else "No cumple"
            linea = f"{p.get('propiedad')}: {estado}"
            self._result_container.controls.append(ft.Text(linea))
            steps.append(linea)
            detalle = p.get("detalle")
            if detalle:
                detalle_line = f"  - {detalle}"
                self._result_container.controls.append(ft.Text(detalle_line, size=12, color=TEXT_MUTED))
                steps.append(detalle_line)
        self._safe_update(self._result_container)
        self._set_steps(steps)

    def _run_selected_operation(self, _event) -> None:
        op = self._operation_dropdown.value if self._operation_dropdown else "add"
        mapping = {
            "add": self._run_add,
            "sub": self._run_sub,
            "scalar": self._run_scalar,
            "mul": self._run_mul,
            "at": lambda: self._run_transpose("A"),
            "bt": lambda: self._run_transpose("B"),
            "verify": self._run_verify,
        }
        action = mapping.get(op)
        if action is None:
            self._show_error("Selecciona una operación válida.")
            return
        action()

    # --------------- presentación ---------------
    def _render_placeholder(self) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Elige una operación para ver los pasos.", color=TEXT_MUTED))
        self._safe_update(self._result_container)
        self._set_steps([])

    def _render_op(self, res: ops.MatrixOpResult) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text(f"Operación: {res.name}", weight=ft.FontWeight.BOLD))
        self._result_container.controls.append(ft.Text("Pasos", weight=ft.FontWeight.W_600))
        for line in res.steps:
            self._result_container.controls.append(ft.Text(line, size=12))
        self._result_container.controls.append(ft.Text("Resultado", weight=ft.FontWeight.W_600))
        self._result_container.controls.append(self._render_matrix(res.result))
        self._safe_update(self._result_container)
        self._set_steps(res.steps)

    def _render_matrix(self, M: List[List[Fraction]]) -> ft.Control:
        col = ft.Column(spacing=4)
        for row in M:
            cells: List[ft.Control] = []
            for val in row:
                cells.append(
                    ft.Container(
                        width=70,
                        height=36,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, color=BORDER_COLOR),
                        border_radius=8,
                        bgcolor="#fff7f5",
                        content=ft.Text(str(val)),
                    )
                )
            col.controls.append(ft.Row(cells, spacing=6))
        return col

    # --------------- utilidades ---------------
    def _parse_alpha(self) -> Optional[Fraction]:
        txt = self._alpha_text.strip()
        if not txt:
            return None
        try:
            return Fraction(txt)
        except ValueError as exc:
            raise ValueError(f"α inválido: '{txt}'") from exc

    def _collect_matrix(self, cells: List[List[ft.TextField]]) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in cells]
        return parse_matrix(raw)

    def _rebuild_tables(self) -> None:
        def build_table(container: ft.Column, rows: int, cols: int, bucket: List[List[ft.TextField]]) -> None:
            container.controls.clear()
            bucket.clear()
            for _ in range(rows):
                row_fields: List[ft.TextField] = []
                row_controls: List[ft.Control] = []
                for _c in range(cols):
                    field = ft.TextField(value="0", width=70, height=44, text_align=ft.TextAlign.CENTER,
                                         bgcolor="#fff7f5", border_color=BORDER_COLOR, focused_border_color=PRIMARY_COLOR,
                                         content_padding=ft.Padding(0, 6, 0, 6), cursor_color=PRIMARY_COLOR)
                    row_fields.append(field)
                    row_controls.append(field)
                bucket.append(row_fields)
                container.controls.append(ft.Row(row_controls, spacing=8))
            self._safe_update(container)

        build_table(self._matrix_a_container, self._rows_a, self._cols_a, self._a_cells)
        build_table(self._matrix_b_container, self._rows_b, self._cols_b, self._b_cells)

        self._update_info_label()

    def _update_info_label(self) -> None:
        alpha_display = self._alpha_text.strip() or "—"
        self._info_label.value = (
            f"Dimensiones: A = {self._rows_a}×{self._cols_a}, B = {self._rows_b}×{self._cols_b} | α = {alpha_display}"
        )
        self._safe_update(self._info_label)

    # ---------------- API pública ----------------
    def set_dimensions(self, rows_a: int, cols_a: int, rows_b: int, cols_b: int) -> None:
        rows_a = max(self.MIN, min(self.MAX, rows_a))
        cols_a = max(self.MIN, min(self.MAX, cols_a))
        rows_b = max(self.MIN, min(self.MAX, rows_b))
        cols_b = max(self.MIN, min(self.MAX, cols_b))

        if (rows_a, cols_a, rows_b, cols_b) == (self._rows_a, self._cols_a, self._rows_b, self._cols_b):
            return
        self._rows_a = rows_a
        self._cols_a = cols_a
        self._rows_b = rows_b
        self._cols_b = cols_b
        self._rebuild_tables()
        self._render_placeholder()

    def set_alpha(self, alpha_text: str) -> None:
        self._alpha_text = alpha_text or ""
        self._update_info_label()

    def dimensions(self) -> tuple[int, int, int, int]:
        return self._rows_a, self._cols_a, self._rows_b, self._cols_b

    def alpha_text(self) -> str:
        return self._alpha_text

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass

    def _set_steps(self, steps: List[str]) -> None:
        self._last_steps = steps
        if self._steps_button:
            self._steps_button.visible = bool(steps)
            self._safe_update(self._steps_button)

    def _show_steps_dialog(self, _event=None) -> None:
        if not self._last_steps or not self._page:
            return
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Pasos"),
            content=ft.Container(
                width=420,
                content=ft.Column(controls=[ft.Text(line) for line in self._last_steps], scroll=ft.ScrollMode.AUTO),
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda e, dlg=dialog: self._close_dialog(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        try:
            self._page.open(dialog)
        except AttributeError:
            dialog.open = True
            dialog.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        try:
            self._page.close(dialog)
        except AttributeError:
            dialog.open = False
            dialog.update()

    def _show_error(self, message: str) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text(f"Error: {message}", color=TEXT_MUTED))
        self._safe_update(self._result_container)
        self._set_steps([])
