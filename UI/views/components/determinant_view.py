from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Sequence

import flet as ft
from flet import Icons as icons

from ViewModels.determinant_vm import (
    DeterminantAnalysisVM,
    DeterminantMultiplicativeDetailVM,
    DeterminantMethodResultVM,
    DeterminantPropertyVM,
    DeterminantStepVM,
    DeterminantTermVM,
    DeterminantViewModel,
    MatrixMultiplicationCellVM,
)

from ...helpers import parse_matrix
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


METHOD_META: Dict[str, Dict[str, str]] = {
    "cofactors": {
        "icon": icons.TABLE_ROWS,
        "tagline": "Expansion por Cofactores (para cualquier matriz cuadrada).",
    },
    "cramer": {
        "icon": icons.FUNCTIONS,
        "tagline": "Metodo de Cramer (para sistemas lineales pequenos o ilustrativos).",
    },
    "sarrus": {
        "icon": icons.FILTER_3,
        "tagline": "Regla de Sarrus (solo aplicable a matrices de 3x3).",
    },
}

METHOD_STEPS_META: Dict[str, Dict[str, str]] = {
    "cofactors": {
        "icon": icons.TABLE_ROWS,
        "title": "Desarrollo por cofactores",
        "subtitle": "Se muestran los cofactores evaluados y el acumulado por nivel.",
    },
    "cramer": {
        "icon": icons.FORMAT_LIST_NUMBERED,
        "title": "Permutaciones evaluadas (metodo de Cramer)",
        "subtitle": "Cada permutacion aporta un producto firmado al determinante.",
    },
    "sarrus": {
        "icon": icons.FILTER_3,
        "title": "Diagonales calculadas (regla de Sarrus)",
        "subtitle": "Se detallan las diagonales descendentes y ascendentes con sus productos.",
    },
}




def recommend_method(order: int) -> str:
    if order == 3:
        return "sarrus"
    if order <= 2:
        return "cramer"
    return "cofactors"


class DeterminantView:
    MIN_ORDER = 1
    MAX_ORDER = 6

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._order = 3
        self._view_model = DeterminantViewModel()

        self._analysis: Optional[DeterminantAnalysisVM] = None
        self._selected_method: str = recommend_method(self._order)

        self._cells: List[List[ft.TextField]] = []
        self._matrix_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self._matrix_preview_title = ft.Text(
            "Matriz ingresada",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=TEXT_DARK,
            visible=False,
        )
        self._matrix_preview_container = ft.Container(
            visible=False,
            bgcolor="#fff6ed",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(12, 12, 12, 12),
        )

        self._summary_title = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=TEXT_DARK)
        self._summary_message = ft.Text("", size=12, color=TEXT_MUTED)
        self._summary_container = ft.Container(
            visible=False,
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(14, 14, 14, 14),
            content=ft.Column(
                spacing=6,
                controls=[self._summary_title, self._summary_message],
            ),
        )

        self._methods_title = ft.Text(
            "Método seleccionado",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=TEXT_DARK,
            visible=False,
        )
        self._methods_container = ft.Column(spacing=16, visible=False)

        self._properties_title = ft.Text(
            "Propiedades del determinante",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=TEXT_DARK,
            visible=False,
        )
        self._properties_container = ft.Column(spacing=12, visible=False)

        self._placeholder = ft.Container(
            bgcolor="#faf8ff",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text("Determinante de una matriz", size=16, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.Text(
                        "Ingresa A y la aplicación elegirá Cramer, Sarrus o cofactors según la dimensión para mostrar los pasos completos.",
                        size=12,
                        color=TEXT_MUTED,
                    ),
                ],
            ),
        )

        self._root = ft.Column(
            spacing=18,
            expand=True,
            controls=[
                self._build_header(),
                self._matrix_container,
                self._placeholder,
                self._matrix_preview_title,
                self._matrix_preview_container,
                self._summary_container,
                self._methods_title,
                self._methods_container,
                self._properties_title,
                self._properties_container,
            ],
        )

        self._rebuild_table()

    @property
    def view(self) -> ft.Control:
        return self._root

    # --------------------------- Public API --------------------------- #
    def order(self) -> int:
        return self._order

    def set_order(self, order: int) -> None:
        order = max(self.MIN_ORDER, min(self.MAX_ORDER, order))
        if order == self._order:
            return
        self._order = order
        self._selected_method = recommend_method(order)
        self._rebuild_table()
        self._clear_results()
        self._render_placeholder()

    def set_recommended_method(self, method_id: str) -> None:
        normalized = method_id or recommend_method(self._order)
        if normalized == self._selected_method:
            return
        self._selected_method = normalized
        if self._analysis:
            self._render_method_card(self._analysis.methods)

    def resolve(self) -> None:
        try:
            matrix = self._collect_matrix()
        except ValueError as exc:
            self._show_error(str(exc))
            return
        try:
            analysis = self._view_model.compute(matrix)
        except ValueError as exc:
            self._show_error(str(exc))
            return
        self._analysis = analysis
        if not any(method.method_id == self._selected_method for method in analysis.methods):
            self._selected_method = recommend_method(self._order)
        self._render_analysis(analysis)

    def clear_fields(self) -> None:
        for row in self._cells:
            for cell in row:
                cell.value = "0"
                self._safe_update(cell)
        self._analysis = None
        self._selected_method = recommend_method(self._order)
        self._clear_results()
        self._render_placeholder()

    # --------------------------- Build helpers --------------------------- #
    def _build_header(self) -> ft.Control:
        return ft.Column(
            spacing=4,
            controls=[
                ft.Text("Determinante de A", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Comparación de los métodos clásicos del determinante con signos, productos parciales y verificación teórica.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

    def _rebuild_table(self) -> None:
        self._cells = []
        rows: List[ft.Control] = []
        for _ in range(self._order):
            current_row: List[ft.TextField] = []
            inputs: List[ft.Control] = []
            for _ in range(self._order):
                field = ft.TextField(
                    value="0",
                    width=68,
                    height=44,
                    text_align=ft.TextAlign.CENTER,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border_color=BORDER_COLOR,
                    focused_border_color=PRIMARY_COLOR,
                    content_padding=ft.Padding(8, 0, 8, 0),
                )
                current_row.append(field)
                inputs.append(ft.Container(width=70, content=field))
            self._cells.append(current_row)
            rows.append(ft.Row(inputs, spacing=8, alignment=ft.MainAxisAlignment.CENTER))
        self._matrix_container.controls = rows
        self._safe_update(self._matrix_container)

    # --------------------------- Rendering --------------------------- #
    def _render_placeholder(self) -> None:
        self._placeholder.visible = True
        self._matrix_preview_title.visible = False
        self._matrix_preview_container.visible = False
        self._summary_container.visible = False
        self._methods_title.visible = False
        self._methods_container.visible = False
        self._properties_title.visible = False
        self._properties_container.visible = False
        self._safe_update(self._placeholder)
        self._safe_update(self._matrix_preview_title)
        self._safe_update(self._matrix_preview_container)
        self._safe_update(self._summary_container)
        self._safe_update(self._methods_title)
        self._safe_update(self._methods_container)
        self._safe_update(self._properties_title)
        self._safe_update(self._properties_container)

    def _clear_results(self) -> None:
        self._summary_title.value = ""
        self._summary_message.value = ""
        self._methods_container.controls = []
        self._properties_container.controls = []
        self._matrix_preview_container.content = None
        self._summary_container.visible = False
        self._methods_container.visible = False
        self._methods_title.visible = False
        self._properties_container.visible = False
        self._properties_title.visible = False
        self._matrix_preview_container.visible = False
        self._matrix_preview_title.visible = False

    def _render_analysis(self, analysis: DeterminantAnalysisVM) -> None:
        self._placeholder.visible = False
        self._safe_update(self._placeholder)

        self._matrix_preview_container.content = self._build_matrix_grid(analysis.matrix)
        self._matrix_preview_title.visible = True
        self._matrix_preview_container.visible = True
        self._safe_update(self._matrix_preview_title)
        self._safe_update(self._matrix_preview_container)

        summary = analysis.summary
        self._summary_title.value = f"det(A) = {summary.determinant}"
        self._summary_title.color = PRIMARY_COLOR if summary.is_invertible else "#d32f2f"
        self._summary_message.value = summary.message
        self._summary_container.visible = True
        self._safe_update(self._summary_title)
        self._safe_update(self._summary_message)
        self._safe_update(self._summary_container)

        self._render_method_card(analysis.methods)

        property_controls = self._build_properties_section(analysis.properties)
        self._properties_container.controls = property_controls
        has_properties = bool(property_controls)
        self._properties_title.visible = has_properties
        self._properties_container.visible = has_properties
        self._safe_update(self._properties_title)
        self._safe_update(self._properties_container)

    def _render_method_card(self, methods: Sequence[DeterminantMethodResultVM]) -> None:
        selected: Optional[DeterminantMethodResultVM] = next(
            (method for method in methods if method.method_id == self._selected_method),
            None,
        )
        if selected is None and methods:
            selected = methods[0]
            self._selected_method = selected.method_id
        if selected is None:
            self._methods_container.controls = []
            self._methods_title.visible = False
            self._methods_container.visible = False
            self._safe_update(self._methods_title)
            self._safe_update(self._methods_container)
            return

        self._methods_container.controls = [self._build_method_card_content(selected)]
        self._methods_title.visible = True
        self._methods_container.visible = True
        self._safe_update(self._methods_title)
        self._safe_update(self._methods_container)

    def _build_method_card_content(self, method: DeterminantMethodResultVM) -> ft.Control:
        meta = METHOD_META.get(method.method_id, {"icon": icons.ANALYTICS, "tagline": method.justification})

        header = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=44,
                    height=44,
                    border_radius=12,
                    bgcolor=PRIMARY_COLOR,
                    content=ft.Icon(meta["icon"], color=ft.Colors.WHITE, size=24),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(method.label, size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Text(meta["tagline"], size=12, color=TEXT_MUTED),
                    ],
                ),
            ],
        )

        if not method.success:
            body = ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        "Este método no está disponible para la dimensión elegida.",
                        weight=ft.FontWeight.BOLD,
                        color="#d32f2f",
                        size=13,
                    ),
                    ft.Text(method.error or "Selecciona otro método disponible.", size=12, color=TEXT_MUTED),
                ],
            )
        else:
            warning_cards: List[ft.Control] = [
                ft.Container(
                    bgcolor="#fff0e6",
                    border=ft.border.all(1, color="#ffa726"),
                    border_radius=12,
                    padding=ft.Padding(10, 10, 10, 10),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(icons.WARNING_AMBER, color="#ffa726", size=18),
                            ft.Text(warning, size=12, color="#bf7100"),
                        ],
                    ),
                )
                for warning in method.warnings
            ]

            body = ft.Column(
                spacing=14,
                controls=[
                    ft.Container(
                        bgcolor="#fff4f6",
                        border=ft.border.all(1, color=PRIMARY_COLOR),
                        border_radius=14,
                        padding=ft.Padding(14, 14, 14, 14),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(icons.CALCULATE, color=PRIMARY_COLOR, size=20),
                                        ft.Text(
                                            f"det(A) = {method.determinant}",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_COLOR,
                                        ),
                                    ],
                                ),
                                ft.Text(method.justification, size=12, color=TEXT_MUTED),
                                ft.Text(
                                    "Términos con signo y producto parcial:",
                                    size=12,
                                    color=TEXT_MUTED,
                                ),
                                self._build_terms_section(method.terms),
                            ],
                        ),
                    ),
                    self._build_method_operations(method),
                    *warning_cards,
                ],
            )

        return ft.Container(
            bgcolor="#ffffff",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=14,
                controls=[header, body],
            ),
        )

    def _build_properties_section(self, properties: Sequence[DeterminantPropertyVM]) -> List[ft.Control]:
        items: List[ft.Control] = []
        for prop in properties:
            icon_name = icons.CHECK_CIRCLE if prop.holds else icons.ERROR_OUTLINE
            icon_color = PRIMARY_COLOR if prop.holds else "#d32f2f"
            badge_text = "Verificado con esta matriz" if prop.verified else "Ejemplo ilustrativo"
            header = ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon_name, color=icon_color, size=20),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(prop.label, weight=ft.FontWeight.W_600, color=TEXT_DARK, size=13),
                            ft.Text(badge_text, size=10, color=TEXT_MUTED),
                        ],
                    ),
                    ft.Container(
                        bgcolor="#eef0ff" if prop.holds else "#fdecea",
                        border_radius=10,
                        padding=ft.Padding(6, 4, 6, 4),
                        content=ft.Text(prop.code, size=10, color=icon_color, weight=ft.FontWeight.BOLD),
                    ),
                ],
            )
            body_controls: List[ft.Control] = [ft.Text(prop.message, size=12, color=TEXT_MUTED)]
            if prop.steps:
                step_texts = [
                    ft.Text(f"{index}. {step}", size=12, color=TEXT_DARK)
                    for index, step in enumerate(prop.steps, start=1)
                ]
                body_controls.append(
                    ft.ExpansionTile(
                        title=ft.Text("Verificación paso a paso", size=12, color=TEXT_DARK),
                        controls=[ft.Column(spacing=4, controls=step_texts)],
                        icon_color=PRIMARY_COLOR,
                    )
                )
            if prop.multiplication:
                body_controls.append(
                    ft.Container(
                        bgcolor="#f2f6ff",
                        border=ft.border.all(1, color="#8da2ff"),
                        border_radius=12,
                        padding=ft.Padding(12, 12, 12, 12),
                        content=self._build_property_multiplication_detail(prop.multiplication),
                    )
                )

            if prop.examples:
                example_tiles: List[ft.Control] = []
                for label, matrix in prop.examples.items():
                    example_tiles.append(
                        ft.ExpansionTile(
                            title=ft.Text(f"Matriz {label}", size=12, color=TEXT_DARK),
                            controls=[self._build_matrix_grid(matrix)],
                            icon_color=PRIMARY_COLOR,
                        )
                    )
                body_controls.append(ft.Column(spacing=6, controls=example_tiles))
            items.append(
                ft.Container(
                    bgcolor="#f3fbf5" if prop.holds else "#fff7f7",
                    border=ft.border.all(1, color=PRIMARY_COLOR if prop.holds else "#f8b4b4"),
                    border_radius=14,
                    padding=ft.Padding(14, 14, 14, 14),
                    content=ft.Column(spacing=10, controls=[header, *body_controls]),
                )
            )
        return items

    def _build_method_operations(self, method: DeterminantMethodResultVM) -> ft.Control:
        meta = METHOD_STEPS_META.get(
            method.method_id,
            {
                "icon": icons.FORMAT_LIST_NUMBERED,
                "title": "Desarrollo paso a paso",
                "subtitle": "Detalle de cada operación realizada por el método seleccionado.",
            },
        )
        header_controls: List[ft.Control] = [
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(meta["icon"], color=PRIMARY_COLOR, size=20),
                    ft.Text(meta["title"], size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ],
            )
        ]
        subtitle_text = meta.get("subtitle")
        if subtitle_text:
            header_controls.append(ft.Text(subtitle_text, size=12, color=TEXT_MUTED))
        header_controls.append(self._build_steps_section(method.steps))
        return ft.Container(
            bgcolor="#f2f6ff",
            border=ft.border.all(1, color="#8da2ff"),
            border_radius=14,
            padding=ft.Padding(14, 14, 14, 14),
            content=ft.Column(spacing=8, controls=header_controls),
        )

    def _build_terms_section(self, terms: Sequence[DeterminantTermVM]) -> ft.Control:
        if not terms:
            return ft.Text("No se registraron términos.", color=TEXT_MUTED, size=12)
        cards: List[ft.Control] = []
        for index, term in enumerate(terms, start=1):
            sign_text = "+1" if term.sign >= 0 else "-1"
            factors_text = " · ".join(str(value) for value in term.factors) if term.factors else "-"
            detail_controls: List[ft.Control] = [
                ft.Text(f"Término {index}: {term.description}", weight=ft.FontWeight.W_600, color=TEXT_DARK, size=12),
                ft.Text(f"Signo algebraico: {sign_text}", size=12, color=TEXT_MUTED),
                ft.Text(f"Producto parcial: {term.product}", size=12, color=TEXT_MUTED),
                ft.Text(f"Factores: {factors_text}", size=12, color=TEXT_MUTED),
            ]
            if term.extra_detail:
                detail_controls.append(ft.Text(term.extra_detail, size=12, color=TEXT_MUTED))
            if term.minor:
                detail_controls.append(
                    ft.ExpansionTile(
                        title=ft.Text("Menor asociado", size=12, color=TEXT_DARK),
                        controls=[self._build_matrix_grid(term.minor)],
                        icon_color=PRIMARY_COLOR,
                    )
                )
            cards.append(
                ft.Container(
                    bgcolor="#f4f7ff" if term.sign >= 0 else "#fff5f5",
                    border=ft.border.all(1, color=PRIMARY_COLOR if term.sign >= 0 else "#f8b4b4"),
                    border_radius=12,
                    padding=ft.Padding(12, 12, 12, 12),
                    content=ft.Column(spacing=6, controls=detail_controls),
                )
            )
        return ft.Column(spacing=10, controls=cards)

    def _build_steps_section(self, steps: Sequence[DeterminantStepVM]) -> ft.Control:
        if not steps:
            return ft.Text("No se registraron pasos para este método.", color=TEXT_MUTED, size=12)
        tiles: List[ft.Control] = []
        for index, step in enumerate(steps, start=1):
            tile_body: List[ft.Control] = [ft.Text(step.description, size=12, color=TEXT_MUTED)]
            if step.subtotal is not None:
                tile_body.append(ft.Text(f"Acumulado: {step.subtotal}", size=12, color=PRIMARY_COLOR))
            if step.snapshot:
                tile_body.append(
                    ft.Container(
                        bgcolor="#ffffff",
                        border=ft.border.all(1, color=BORDER_COLOR),
                        border_radius=10,
                        padding=ft.Padding(8, 8, 8, 8),
                        content=self._build_matrix_grid(step.snapshot),
                    )
                )
            tiles.append(
                ft.ExpansionTile(
                    title=ft.Text(f"{index}. {step.label}", size=12, color=TEXT_DARK),
                    icon_color=PRIMARY_COLOR,
                    controls=[ft.Column(spacing=6, controls=tile_body)],
                )
            )
        return ft.Column(spacing=6, controls=tiles)

    def _build_matrix_grid(self, matrix: Sequence[Sequence[Fraction]]) -> ft.Column:
        rows: List[ft.Control] = []
        for row in matrix:
            cells = [
                ft.Container(
                    width=64,
                    height=34,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, color=BORDER_COLOR),
                    border_radius=8,
                    content=ft.Text(str(value), size=12, color=TEXT_DARK),
                )
                for value in row
            ]
            rows.append(ft.Row(cells, spacing=6))
        return ft.Column(spacing=4, controls=rows)


    def _build_property_multiplication_detail(
        self,
        detail: DeterminantMultiplicativeDetailVM,
    ) -> ft.Control:
        det_matches = detail.det_product == detail.det_expected
        message_color = PRIMARY_COLOR if det_matches else "#c62828"
        rows_a = len(detail.left_matrix)
        cols_a = len(detail.left_matrix[0]) if detail.left_matrix and detail.left_matrix[0] else 0
        rows_b = len(detail.right_matrix)
        cols_b = len(detail.right_matrix[0]) if detail.right_matrix and detail.right_matrix[0] else 0
        dimension_text = ft.Text(
            f"Producto {detail.left_label} * {detail.right_label}: dimensiones {rows_a}x{cols_a} y {rows_b}x{cols_b}.",
            size=12,
            color=TEXT_MUTED,
        )
        matrix_cards: List[ft.Control] = [
            self._build_labeled_matrix_card(f"Matriz {detail.left_label}", detail.left_matrix),
            self._build_labeled_matrix_card(f"Matriz {detail.right_label}", detail.right_matrix),
            self._build_labeled_matrix_card(detail.product_label, detail.product_matrix, emphasize=det_matches),
            self._build_labeled_matrix_card(detail.expected_label, detail.expected_matrix),
        ]
        matrices_column = ft.Container(
            height=220,
            content=ft.Column(
                spacing=12,
                controls=matrix_cards,
                scroll=ft.ScrollMode.AUTO,
            ),
        )
        det_summary = ft.Text(
            f"det({detail.product_label}) = {self._format_fraction(detail.det_product)} y det({detail.left_label}) * det({detail.right_label}) = {self._format_fraction(detail.det_expected)}",
            color=message_color,
            weight=ft.FontWeight.W_600,
            size=12,
        )
        return ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Verificacion del producto AB para det(AB) = det(A) * det(B)",
                    weight=ft.FontWeight.W_600,
                    color=TEXT_DARK,
                    size=12,
                ),
                det_summary,
                dimension_text,
                matrices_column,
                self._build_multiplication_text_summary(detail.steps, detail.expected_label),
            ],
        )

    def _build_multiplication_text_summary(
        self,
        steps: Sequence[MatrixMultiplicationCellVM],
        expected_label: str,
    ) -> ft.Control:
        if not steps:
            return ft.Text("No hay detalles de multiplicacion disponibles.", color=TEXT_MUTED, size=12)
        lines: List[ft.Control] = [
            ft.Text("Detalle de cada entrada C(i, j):", weight=ft.FontWeight.W_600, color=TEXT_DARK),
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
            expected_color = PRIMARY_COLOR if cell.result == cell.expected else "#c62828"
            lines.append(
                ft.Text(
                    f"{expected_label}({cell.row + 1}, {cell.col + 1}) = {self._format_fraction(cell.expected)}",
                    size=12,
                    color=expected_color,
                )
            )
        return ft.Column(spacing=4, controls=lines)

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

    def _build_matrix_card(
        self,
        matrix: Sequence[Sequence[Fraction]],
        emphasize: bool = False,
    ) -> ft.Control:
        return ft.Container(
            bgcolor="#fffaf6" if emphasize else "#fff7f5",
            border=ft.border.all(1, color=PRIMARY_COLOR if emphasize else BORDER_COLOR),
            border_radius=14,
            padding=ft.Padding(12, 12, 12, 12),
            content=self._build_matrix_grid(matrix),
        )

    def _format_fraction(self, value: Fraction) -> str:
        if isinstance(value, Fraction):
            if value.denominator == 1:
                return f"{value.numerator}"
            return f"{value.numerator}/{value.denominator}"
        return str(value)

    # --------------------------- Utilities --------------------------- #
    def _collect_matrix(self) -> List[List[Fraction]]:
        raw = [[cell.value or "0" for cell in row] for row in self._cells]
        matrix = parse_matrix(raw)
        if len(matrix) != len(matrix[0]):
            raise ValueError("La matriz A debe ser cuadrada.")
        return matrix

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
