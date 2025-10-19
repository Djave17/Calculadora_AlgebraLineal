from __future__ import annotations

from fractions import Fraction
from typing import Dict, List

import flet as ft
from flet import Colors as colors, Icons as icons

from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED
from ViewModels import matrix_ops_vm as ops

ALPHA = "α"


class TransposeView:
    """Vista para explorar la traspuesta y sus propiedades clásicas."""

    MIN = 1
    MAX = 8
    OPERATIONS: tuple[Dict[str, object], ...] = (
        {
            "key": "at",
            "label": "A^T",
            "description": "Calcula la traspuesta de A.",
            "requires_b": False,
            "requires_alpha": False,
        },
        {
            "key": "sum",
            "label": "(A + B)^T",
            "description": "Evalúa la propiedad distributiva sobre la suma.",
            "requires_b": True,
            "requires_alpha": False,
        },
        {
            "key": "diff",
            "label": "(A - B)^T",
            "description": "Evalúa la traspuesta de una resta.",
            "requires_b": True,
            "requires_alpha": False,
        },
        {
            "key": "scalar",
            "label": f"({ALPHA} * A)^T",
            "description": f"Comprueba que la traspuesta conmute con el escalar {ALPHA}.",
            "requires_b": False,
            "requires_alpha": True,
        },
        {
            "key": "product",
            "label": "(A * B)^T",
            "description": "Muestra que la traspuesta invierte el orden del producto.",
            "requires_b": True,
            "requires_alpha": False,
        },
    )

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._rows_a = 2
        self._cols_a = 2
        self._rows_b = 2
        self._cols_b = 2
        self._alpha_text: str = ""

        self._a_cells: List[List[ft.TextField]] = []
        self._b_cells: List[List[ft.TextField]] = []

        self._operation_dropdown: ft.Dropdown | None = None
        self._operation_hint = ft.Text("", size=12, color=TEXT_MUTED)
        self._info_label = ft.Text("", color=TEXT_MUTED)
        self._alpha_hint = ft.Text("", size=12, color=TEXT_MUTED)
        self._matrix_a_container = ft.Column(spacing=6, expand=True)
        self._matrix_b_container = ft.Column(spacing=6, expand=True)
        self._result_container = ft.Column(spacing=8, expand=True)
        self._steps_button = ft.TextButton(
            "Ver pasos",
            icon=icons.NAVIGATE_NEXT,
            visible=False,
            on_click=self._show_steps_dialog,
            style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: PRIMARY_COLOR}),
        )
        self._last_steps: List[str] = []

        self._operation_map = {item["key"]: item for item in self.OPERATIONS}

        self._root = self._build()
        self._rebuild_tables()
        self._handle_operation_change()
        self._render_placeholder()

    @property
    def view(self) -> ft.Control:
        return self._root

    # ---------------- construcción -----------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Matriz traspuesta", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    f"Calcula A^T y propiedades como (A ± B)^T, ({ALPHA} * A)^T y (A * B)^T.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        matrices_row = ft.ResponsiveRow(
            spacing=16,
            run_spacing=16,
            controls=[
                self._build_matrix_card("Matriz A", self._matrix_a_container, PRIMARY_COLOR),
                self._build_matrix_card(
                    "Matriz B",
                    self._matrix_b_container,
                    BORDER_COLOR,
                    footer=ft.Text(
                        "Se usa en las propiedades con B: suma, resta y producto.",
                        size=11,
                        color=TEXT_MUTED,
                    ),
                ),
            ],
        )

        self._operation_dropdown = ft.Dropdown(
            label="Operación",
            value=self.OPERATIONS[0]["key"],
            options=[ft.dropdown.Option(item["key"], item["label"]) for item in self.OPERATIONS],
            width=220,
            on_change=lambda _: self._handle_operation_change(),
        )

        action_row = ft.Row(
            spacing=10,
            wrap=True,
            controls=[
                self._operation_dropdown,
                ft.FilledButton("Calcular operación", icon=icons.PLAY_ARROW, on_click=lambda _: self._run_operation()),
                ft.TextButton("Verificar propiedades", icon=icons.SCIENCE, on_click=lambda _: self._run_verify()),
                ft.OutlinedButton("Limpiar", icon=icons.CLEAR, on_click=lambda _: self._handle_clear()),
            ],
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
                controls=[
                    header,
                    self._info_label,
                    self._alpha_hint,
                    matrices_row,
                    action_row,
                    self._operation_hint,
                    results_card,
                ],
            ),
        )

    def _build_matrix_card(self, title: str, container: ft.Column, border_color: str, footer: ft.Control | None = None) -> ft.Container:
        controls: List[ft.Control] = [ft.Text(title, weight=ft.FontWeight.BOLD, color=TEXT_DARK), container]
        if footer is not None:
            controls.append(footer)
        return ft.Container(
            col={"xs": 12, "md": 6},
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=ft.Padding(20, 20, 20, 20),
            border=ft.border.all(1, color=border_color),
            content=ft.Column(spacing=12, controls=controls),
        )

    # ---------------- acciones -----------------
    def _handle_operation_change(self) -> None:
        if not self._operation_dropdown:
            return
        meta = self._operation_map.get(self._operation_dropdown.value or "at")
        description = meta.get("description") if meta else ""
        self._operation_hint.value = description or ""
        self._safe_update(self._operation_hint)

    def _run_operation(self) -> None:
        op_key = self._operation_dropdown.value if self._operation_dropdown else "at"
        meta = self._operation_map.get(op_key, self._operation_map["at"])
        requires_b = bool(meta.get("requires_b"))
        requires_alpha = bool(meta.get("requires_alpha"))
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells) if requires_b else None
            alpha = self._parse_alpha(required=requires_alpha)
        except Exception as exc:
            self._show_error(str(exc))
            return

        try:
            if op_key == "at":
                result = ops.transpose(A)
                result.name = "A^T"
                self._render_simple_op(result)
            elif op_key == "sum":
                self._handle_sum_operation(A, B)
            elif op_key == "diff":
                self._handle_diff_operation(A, B)
            elif op_key == "scalar":
                self._handle_scalar_operation(A, alpha)
            elif op_key == "product":
                self._handle_product_operation(A, B)
            else:
                self._show_error("Operación no soportada.")
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_sum_operation(self, A: List[List[Fraction]], B: List[List[Fraction]] | None) -> None:
        if B is None:
            raise ValueError("Define la matriz B para evaluar (A + B)^T.")
        sum_res = ops.add(A, B)
        t_sum = ops.transpose(sum_res.result)
        tA = ops.transpose(A)
        tB = ops.transpose(B)
        sum_transposes = ops.add(tA.result, tB.result)
        holds = t_sum.result == sum_transposes.result
        self._render_transpose_property(
            "(A + B)^T",
            [
                ("Pasos de A + B", sum_res.steps),
                ("Pasos de la traspuesta", t_sum.steps),
                ("Pasos de A^T + B^T", sum_transposes.steps),
            ],
            [
                ("(A + B)^T", t_sum.result),
                ("A^T", tA.result),
                ("B^T", tB.result),
                ("A^T + B^T", sum_transposes.result),
            ],
            holds,
            "(A + B)^T = A^T + B^T",
        )

    def _handle_diff_operation(self, A: List[List[Fraction]], B: List[List[Fraction]] | None) -> None:
        if B is None:
            raise ValueError("Define la matriz B para evaluar (A - B)^T.")
        diff_res = ops.subtract(A, B)
        t_diff = ops.transpose(diff_res.result)
        tA = ops.transpose(A)
        tB = ops.transpose(B)
        diff_transposes = ops.subtract(tA.result, tB.result)
        holds = t_diff.result == diff_transposes.result
        self._render_transpose_property(
            "(A - B)^T",
            [
                ("Pasos de A - B", diff_res.steps),
                ("Pasos de la traspuesta", t_diff.steps),
                ("Pasos de A^T - B^T", diff_transposes.steps),
            ],
            [
                ("(A - B)^T", t_diff.result),
                ("A^T", tA.result),
                ("B^T", tB.result),
                ("A^T - B^T", diff_transposes.result),
            ],
            holds,
            "(A - B)^T = A^T - B^T",
        )

    def _handle_scalar_operation(self, A: List[List[Fraction]], alpha: Fraction | None) -> None:
        if alpha is None:
            raise ValueError(f"Define {ALPHA} para evaluar la propiedad.")
        scalar_res = ops.scalar_mult(alpha, A)
        t_scalar = ops.transpose(scalar_res.result)
        tA = ops.transpose(A)
        scalar_transpose = ops.scalar_mult(alpha, tA.result)
        holds = t_scalar.result == scalar_transpose.result
        self._render_transpose_property(
            f"({ALPHA} * A)^T",
            [
                (f"Pasos de {ALPHA} * A", scalar_res.steps),
                ("Pasos de la traspuesta", t_scalar.steps),
                (f"Pasos de {ALPHA} * A^T", scalar_transpose.steps),
            ],
            [
                (f"({ALPHA} * A)^T", t_scalar.result),
                ("A^T", tA.result),
                (f"{ALPHA} * A^T", scalar_transpose.result),
            ],
            holds,
            f"({ALPHA} * A)^T = {ALPHA} * A^T",
        )

    def _handle_product_operation(self, A: List[List[Fraction]], B: List[List[Fraction]] | None) -> None:
        if B is None:
            raise ValueError("Define la matriz B para evaluar (A * B)^T.")
        product_res = ops.multiply(A, B)
        t_product = ops.transpose(product_res.result)
        tA = ops.transpose(A)
        tB = ops.transpose(B)
        reversed_product = ops.multiply(tB.result, tA.result)
        holds = t_product.result == reversed_product.result
        self._render_transpose_property(
            "(A * B)^T",
            [
                ("Pasos de A * B", product_res.steps),
                ("Pasos de la traspuesta", t_product.steps),
                ("Pasos de B^T * A^T", reversed_product.steps),
            ],
            [
                ("(A * B)^T", t_product.result),
                ("B^T", tB.result),
                ("A^T", tA.result),
                ("B^T * A^T", reversed_product.result),
            ],
            holds,
            "(A * B)^T = B^T * A^T",
        )

    def _run_verify(self) -> None:
        try:
            A = self._collect_matrix(self._a_cells)
            B = self._collect_matrix(self._b_cells)
            alpha = self._parse_alpha(required=False)
            props = ops.verify_properties(A, B, alpha)
        except Exception as exc:
            self._show_error(str(exc))
            return

        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Verificación de propiedades", weight=ft.FontWeight.BOLD))
        steps: List[str] = []
        for prop in props:
            cumple = prop.get("cumple", False)
            estado = "Cumple" if cumple else "No cumple"
            color = colors.GREEN_600 if cumple else colors.RED_400
            label = prop.get("propiedad", "")
            detalle = prop.get("detalle")
            line = f"{label}: {estado}"
            self._result_container.controls.append(ft.Text(line, color=color))
            steps.append(line)
            if detalle:
                detalle_line = f"  - {detalle}"
                self._result_container.controls.append(ft.Text(detalle_line, size=12, color=TEXT_MUTED))
                steps.append(detalle_line)
        self._safe_update(self._result_container)
        self._set_steps(steps)

    def _handle_clear(self) -> None:
        for bucket in (self._a_cells, self._b_cells):
            for row in bucket:
                for field in row:
                    field.value = "0"
                    self._safe_update(field)
        self._render_placeholder()

    # ---------------- presentación -----------------
    def _render_placeholder(self) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Introduce las matrices y elige una operación para ver los pasos.", color=TEXT_MUTED))
        self._safe_update(self._result_container)
        self._set_steps([])

    def _render_simple_op(self, res: ops.MatrixOpResult) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text(f"Operación: {res.name}", weight=ft.FontWeight.BOLD))
        self._result_container.controls.append(ft.Text("Pasos", weight=ft.FontWeight.W_600))
        for line in res.steps:
            self._result_container.controls.append(ft.Text(line, size=12))
        self._result_container.controls.append(ft.Text("Resultado", weight=ft.FontWeight.W_600))
        self._result_container.controls.append(self._render_matrix(res.result))
        self._safe_update(self._result_container)
        self._set_steps(res.steps)

    def _render_transpose_property(
        self,
        title: str,
        step_sections: List[tuple[str, List[str]]],
        matrices: List[tuple[str, List[List[Fraction]]]],
        holds: bool,
        message: str,
    ) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text(f"Operación: {title}", weight=ft.FontWeight.BOLD))
        log: List[str] = []
        for heading, steps in step_sections:
            self._result_container.controls.append(ft.Text(heading, weight=ft.FontWeight.W_600))
            log.append(heading)
            for step in steps:
                self._result_container.controls.append(ft.Text(step, size=12))
                log.append(f"  {step}")
        for heading, matrix in matrices:
            self._result_container.controls.append(ft.Text(heading, weight=ft.FontWeight.W_600))
            self._result_container.controls.append(self._render_matrix(matrix))
        status_text = message if holds else f"No se cumple: {message}"
        status_color = colors.GREEN_600 if holds else colors.RED_400
        self._result_container.controls.append(ft.Text(status_text, weight=ft.FontWeight.W_600, color=status_color))
        self._safe_update(self._result_container)
        log.append(status_text)
        self._set_steps(log)

    def _render_matrix(self, M: List[List[Fraction]]) -> ft.Control:
        col = ft.Column(spacing=4)
        for row in M:
            col.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            width=70,
                            height=36,
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, color=BORDER_COLOR),
                            border_radius=8,
                            bgcolor="#fff7f5",
                            content=ft.Text(str(val)),
                        )
                        for val in row
                    ],
                    spacing=6,
                )
            )
        return col

    # ---------------- utilidades -----------------
    def _rebuild_tables(self) -> None:
        self._build_table(self._matrix_a_container, self._a_cells, self._rows_a, self._cols_a)
        self._build_table(self._matrix_b_container, self._b_cells, self._rows_b, self._cols_b)
        self._update_info_label()

    def _build_table(self, container: ft.Column, bucket: List[List[ft.TextField]], rows: int, cols: int) -> None:
        container.controls.clear()
        bucket.clear()
        for _ in range(rows):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for _ in range(cols):
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
            bucket.append(row_fields)
            container.controls.append(ft.Row(row_controls, spacing=8))
        self._safe_update(container)

    def _collect_matrix(self, cells: List[List[ft.TextField]]) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in cells]
        return parse_matrix(raw)

    def _parse_alpha(self, *, required: bool) -> Fraction | None:
        txt = self._alpha_text.strip()
        if not txt:
            if required:
                raise ValueError(f"Define {ALPHA} en el panel derecho.")
            return None
        try:
            return Fraction(txt)
        except ValueError as exc:
            raise ValueError(f"{ALPHA} inválido: '{txt}'") from exc

    def _update_info_label(self) -> None:
        alpha_display = self._alpha_text.strip() or "sin definir"
        self._info_label.value = (
            f"Dimensiones: A = {self._rows_a}x{self._cols_a}, B = {self._rows_b}x{self._cols_b}"
        )
        self._alpha_hint.value = f"Escalar {ALPHA}: {alpha_display}"
        self._safe_update(self._info_label)
        self._safe_update(self._alpha_hint)

    # ---------------- API pública -----------------
    def set_parameters(self, rows_a: int, cols_a: int, rows_b: int, cols_b: int) -> None:
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
        self._alpha_text = (alpha_text or "").strip()
        self._update_info_label()

    def parameters(self) -> tuple[int, int, int, int]:
        return self._rows_a, self._cols_a, self._rows_b, self._cols_b

    def alpha_text(self) -> str:
        return self._alpha_text

    # ---------------- utilidades extra -----------------
    def _set_steps(self, steps: List[str]) -> None:
        self._last_steps = steps
        if self._steps_button:
            self._steps_button.visible = bool(steps)
            self._safe_update(self._steps_button)

    def _show_steps_dialog(self, _event) -> None:
        if not self._last_steps:
            return
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Pasos"),
            content=ft.Container(
                width=420,
                content=ft.Column(controls=[ft.Text(line) for line in self._last_steps], scroll=ft.ScrollMode.AUTO),
            ),
            actions=[ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        if self._page:
            self._page.open(dialog)

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        try:
            if self._page:
                self._page.close(dialog)
        except AttributeError:
            dialog.open = False
            dialog.update()

    def _show_error(self, message: str) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text(f"Error: {message}", color=TEXT_MUTED))
        self._safe_update(self._result_container)
        self._set_steps([])

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
