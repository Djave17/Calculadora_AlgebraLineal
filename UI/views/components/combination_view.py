from __future__ import annotations

from fractions import Fraction
from typing import List, Optional

import flet as ft
from flet import Colors as colors, Icons as icons

from ViewModels.combinacion_lineal_vm import CombinacionLinealViewModel, CombinationResultVM
from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class CombinationView:
    """Vista específica para analizar combinación lineal b ∈ span{v₁,…,vₖ}.

    Permite definir:
    - Dimensión (n)
    - Cantidad de vectores generadores (k)
    - Columnas v1..vk y el vector objetivo b (columna aparte)
    Muestra el planteamiento [A|b], interpretación y permite abrir los pasos.
    """

    MIN_DIM = 2
    MAX_DIM = 8
    MIN_VECT = 1
    MAX_VECT = 8

    def __init__(self, page: ft.Page, on_show_steps) -> None:
        self._page = page
        self._vm = CombinacionLinealViewModel()
        self._on_show_steps = on_show_steps

        self._dim = 3
        self._count = 2

        self._gen_cells: List[List[ft.TextField]] = []  # n × k
        self._b_cells: List[ft.TextField] = []          # n × 1
        self._dimension_label = ft.Text("")

        # Containers
        self._generators_container = ft.Column(spacing=6, expand=True)
        self._b_container = ft.Column(spacing=6, expand=True)
        self._result_container = ft.Column(spacing=8, expand=True)

        self._btn_steps = ft.TextButton("Ver pasos detallados", disabled=True, on_click=self._open_steps)
        self._latest: Optional[CombinationResultVM] = None

        self._root = self._build()
        self._rebuild_tables()
        self._render_placeholder()
        self._update_dimension_label()

    @property
    def view(self) -> ft.Control:
        return self._root

    # -------------------- construcción --------------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Combinación lineal de vectores", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Determina si b puede escribirse como combinación lineal de {v₁,…,vₖ}.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        gen_card = ft.Container(
            col={"xs": 12, "md": 8},
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=ft.Padding(20, 20, 20, 20),
            border=ft.border.all(1, color=PRIMARY_COLOR),
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Vectores generadores (columnas)", weight=ft.FontWeight.BOLD, color=TEXT_DARK), self._generators_container],
            ),
        )
        b_card = ft.Container(
            col={"xs": 12, "md": 4},
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            padding=ft.Padding(20, 20, 20, 20),
            border=ft.border.all(1, color=BORDER_COLOR),
            content=ft.Column(
                spacing=12,
                controls=[ft.Text("Vector objetivo b", weight=ft.FontWeight.BOLD, color=TEXT_DARK), self._b_container],
            ),
        )

        actions = ft.Row(
            spacing=12,
            controls=[
                ft.FilledButton("Analizar combinación", icon=icons.PLAY_ARROW, on_click=self._handle_analyze),
                self._btn_steps,
                ft.OutlinedButton("Limpiar", icon=icons.CLEAR, on_click=self._handle_clear),
            ],
        )

        results_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=16,
            border=ft.border.all(1, color=BORDER_COLOR),
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(spacing=12, controls=[ft.Text("Resultado", size=18, weight=ft.FontWeight.BOLD), self._result_container]),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Column(
                expand=True,
                controls=[header, self._dimension_label, ft.ResponsiveRow(controls=[gen_card, b_card], spacing=16, run_spacing=16), actions, results_card],
            ),
        )

    # -------------------- eventos --------------------
    def _handle_analyze(self, _event) -> None:
        try:
            gen = self._collect_generators()
            b = self._collect_b()
            result = self._vm.analizar(gen, b)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._latest = result
        self._btn_steps.disabled = not (result.solver_result.steps)
        self._btn_steps.update()
        self._render_result(result)

    def _open_steps(self, _event) -> None:
        if not self._latest or not self._latest.solver_result.steps:
            self._show_error("No hay pasos disponibles.")
            return
        self._on_show_steps(self._latest.solver_result.steps, self._latest.solver_result.pivot_cols or [])

    def _handle_clear(self, _event) -> None:
        for row in self._gen_cells:
            for c in row:
                c.value = "0"
                c.update()
        for c in self._b_cells:
            c.value = "0"
            c.update()
        self._latest = None
        self._btn_steps.disabled = True
        self._btn_steps.update()
        self._render_placeholder()

    # -------------------- presentación --------------------
    def _render_placeholder(self) -> None:
        self._result_container.controls.clear()
        self._result_container.controls.append(ft.Text("Configura n y k; captura vᵢ como columnas y b a la derecha.", color=TEXT_MUTED))
        self._result_container.update()

    def _render_result(self, vm: CombinationResultVM) -> None:
        from ...helpers import format_result_lines

        self._result_container.controls.clear()
        A_aug = ["[" + ", ".join(str(x) for x in row) + "]" for row in vm.augmented_matrix]
        self._result_container.controls.append(ft.Text("Matriz aumentada [A|b]:", weight=ft.FontWeight.W_600))
        for line in A_aug:
            self._result_container.controls.append(ft.Text(line, size=12))

        labels = vm.coefficient_labels
        for line in format_result_lines(vm.solver_result, labels):
            self._result_container.controls.append(ft.Text(line, size=12))

        self._result_container.controls.append(ft.Text("Interpretación:", weight=ft.FontWeight.W_600))
        self._result_container.controls.append(ft.Text(vm.interpretation.summary))
        for detail in vm.interpretation.details:
            self._result_container.controls.append(ft.Text(f"  - {detail}", size=12, color=TEXT_MUTED))

        self._result_container.update()

    # -------------------- utilidades --------------------
    def _rebuild_tables(self) -> None:
        # Generadores como columnas: generamos una malla n×k
        self._generators_container.controls.clear()
        self._gen_cells.clear()
        for _ in range(self._dim):
            row_fields: List[ft.TextField] = []
            row_controls: List[ft.Control] = []
            for _c in range(self._count):
                f = ft.TextField(
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
                row_fields.append(f)
                row_controls.append(f)
            self._gen_cells.append(row_fields)
            self._generators_container.controls.append(ft.Row(row_controls, spacing=8))
        self._safe_update(self._generators_container)

        # Vector b (n×1)
        self._b_container.controls.clear()
        self._b_cells.clear()
        for _ in range(self._dim):
            f = ft.TextField(
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
            self._b_cells.append(f)
            self._b_container.controls.append(ft.Row([f]))
        self._safe_update(self._b_container)

    def _collect_generators(self) -> List[List[Fraction]]:
        # Extrae columnas v1..vk a partir de la malla n×k (self._gen_cells almacena por filas)
        raw = [[cell.value or "0" for cell in row] for row in self._gen_cells]
        matrix = parse_matrix(raw)  # n × k en filas
        # convertir filas a columnas: generadores = lista de columnas
        if not matrix or not matrix[0]:
            raise ValueError("Los vectores generadores no pueden ser vacíos.")
        n, k = len(matrix), len(matrix[0])
        cols: List[List[Fraction]] = []
        for j in range(k):
            cols.append([matrix[i][j] for i in range(n)])
        return cols

    def _collect_b(self) -> List[Fraction]:
        raw = [[cell.value or "0"] for cell in self._b_cells]
        matrix = parse_matrix(raw)
        return [row[0] for row in matrix]

    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(bgcolor=colors.ERROR, content=ft.Text(message))
        self._page.snack_bar.open = True
        self._page.update()

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass

    # -------------------- API pública --------------------
    def set_parameters(self, dimension: int, vector_count: int) -> None:
        dimension = max(self.MIN_DIM, min(self.MAX_DIM, dimension))
        vector_count = max(self.MIN_VECT, min(self.MAX_VECT, vector_count))
        changed = (dimension, vector_count) != (self._dim, self._count)
        self._dim = dimension
        self._count = vector_count
        if changed:
            self._rebuild_tables()
            self._render_placeholder()
        self._update_dimension_label()

    def parameters(self) -> tuple[int, int]:
        return self._dim, self._count

    def _update_dimension_label(self) -> None:
        self._dimension_label.value = f"Dimensión n = {self._dim}, vectores generadores = {self._count}"
        self._dimension_label.color = TEXT_MUTED
        try:
            self._dimension_label.update()
        except AssertionError:
            pass
