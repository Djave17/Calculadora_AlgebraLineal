from __future__ import annotations

from fractions import Fraction
from typing import List

import flet as ft
from flet import Colors as colors, Icons as icons

from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED
from ViewModels import matrix_ops_vm as ops


class TransposeView:
    """Vista dedicada para calcular A^T y verificar propiedades básicas.

    - Permite definir dimensiones, capturar A y (opcional) un escalar α.
    - Muestra pasos de la traspuesta (intercambio de índices) y resultado final.
    - Verifica (A^T)^T = A y (αA)^T = α(A^T).
    """

    MIN = 1
    MAX = 8

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._rows = 2
        self._cols = 2
        self._a_cells: List[List[ft.TextField]] = []
        self._alpha_text: str = ""
        self._info_label = ft.Text("", color=TEXT_MUTED)
        self._last_steps: List[str] = []
        self._steps_button: ft.TextButton | None = None

        self._matrix_a_container = ft.Column(spacing=6, expand=True)
        self._result_container = ft.Column(spacing=8, expand=True)

        self._root = self._build()
        self._rebuild_table()
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
                ft.Text("Calcula A^T y verifica propiedades básicas.", size=12, color=TEXT_MUTED),
            ],
        )

        a_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=ft.Padding(20, 20, 20, 20),
            border=ft.border.all(1, color=PRIMARY_COLOR),
            content=ft.Column(spacing=12, controls=[ft.Text("Matriz A", weight=ft.FontWeight.BOLD, color=TEXT_DARK), self._matrix_a_container]),
        )

        actions = ft.Row(
            spacing=10,
            controls=[
                ft.FilledButton("Calcular A^T", icon=icons.SHUFFLE, on_click=lambda e: self._run_transpose()),
                ft.TextButton("Verificar propiedades", icon=icons.SCIENCE, on_click=lambda e: self._run_verify()),
                ft.OutlinedButton("Limpiar", icon=icons.CLEAR, on_click=lambda e: self._handle_clear()),
            ],
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
                controls=[header, self._info_label, a_card, actions, results_card],
            ),
        )

    # ---------------- acciones -----------------
    def _run_transpose(self) -> None:
        try:
            A = self._collect_matrix()
            res = ops.transpose(A)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._render_op(res)

    def _run_verify(self) -> None:
        try:
            A = self._collect_matrix()
            alpha = self._parse_alpha()
            props = ops.verify_properties(A, None, alpha)
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

    def _handle_clear(self) -> None:
        for row in self._a_cells:
            for f in row:
                f.value = "0"
                f.update()
        self._render_placeholder()

    # ---------------- presentación -----------------
    def _render_placeholder(self) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Introduce A y presiona ‘Calcular A^T’.", color=TEXT_MUTED))
        self._safe_update(self._result_container)
        self._set_steps([])

    def _render_op(self, res: ops.MatrixOpResult) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Pasos (intercambio de filas por columnas)", weight=ft.FontWeight.W_600))
        for line in res.steps:
            self._result_container.controls.append(ft.Text(line, size=12))
        self._result_container.controls.append(ft.Text("Resultado A^T", weight=ft.FontWeight.W_600))
        self._result_container.controls.append(self._render_matrix(res.result))
        self._safe_update(self._result_container)
        self._set_steps(res.steps)

    def _render_matrix(self, M: List[List[Fraction]]) -> ft.Control:
        col = ft.Column(spacing=4)
        for row in M:
            col.controls.append(ft.Row([
                ft.Container(width=70, height=36, alignment=ft.alignment.center,
                             border=ft.border.all(1, color=BORDER_COLOR), border_radius=8, bgcolor="#fff7f5",
                             content=ft.Text(str(val))) for val in row
            ], spacing=6))
        return col

    # ---------------- utilidades -----------------
    def _rebuild_table(self) -> None:
        self._matrix_a_container.controls.clear()
        self._a_cells.clear()
        for _ in range(self._rows):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for _c in range(self._cols):
                f = ft.TextField(value="0", width=70, height=44, text_align=ft.TextAlign.CENTER, bgcolor="#fff7f5",
                                 border_color=BORDER_COLOR, focused_border_color=PRIMARY_COLOR, content_padding=ft.Padding(0, 6, 0, 6), cursor_color=PRIMARY_COLOR)
                row_fields.append(f)
                row_controls.append(f)
            self._a_cells.append(row_fields)
            self._matrix_a_container.controls.append(ft.Row(row_controls, spacing=8))
        self._safe_update(self._matrix_a_container)
        self._update_info_label()

    def _collect_matrix(self) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in self._a_cells]
        return parse_matrix(raw)

    def _parse_alpha(self) -> Fraction | None:
        txt = self._alpha_text.strip()
        if not txt:
            return None
        try:
            return Fraction(txt)
        except ValueError as exc:
            raise ValueError(f"α inválido: '{txt}'") from exc

    def _update_info_label(self) -> None:
        alpha_display = self._alpha_text.strip() or "—"
        self._info_label.value = f"Dimensiones: A = {self._rows}×{self._cols} | α = {alpha_display}"
        self._safe_update(self._info_label)

    # ---------------- API pública -----------------
    def set_dimensions(self, rows: int, cols: int) -> None:
        rows = max(self.MIN, min(self.MAX, rows))
        cols = max(self.MIN, min(self.MAX, cols))
        changed = (rows, cols) != (self._rows, self._cols)
        self._rows = rows
        self._cols = cols
        if changed:
            self._rebuild_table()
            self._render_placeholder()
        else:
            self._update_info_label()

    def set_alpha(self, alpha_text: str) -> None:
        self._alpha_text = alpha_text or ""
        self._update_info_label()

    def parameters(self) -> tuple[int, int]:
        return self._rows, self._cols

    def alpha_text(self) -> str:
        return self._alpha_text

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
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dialog.actions = [
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: self._close_dialog(dialog),
                style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: PRIMARY_COLOR}),
            )
        ]
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
