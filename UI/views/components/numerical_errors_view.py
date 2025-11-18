from __future__ import annotations

from typing import List

import flet as ft
from flet import Icons as icons

from ViewModels.numerical_errors_vm import (
    ErrorAnalysisVM,
    ErrorConceptVM,
    FloatingPointScenarioVM,
    compute_error_analysis,
    error_concepts,
    floating_point_scenarios,
)
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class NumericalErrorsView:
    """Módulo Program 8: errores numéricos, ejemplos flotantes y propagación."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._true_value_field = ft.TextField(
            label="xᵥ (valor verdadero)",
            value="2.1738",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._approx_value_field = ft.TextField(
            label="xₐ (valor aproximado)",
            value="2.15",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._function_field = ft.TextField(
            label="Función f(x)",
            value="sin(x) + x**2",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            helper_text="Puedes usar funciones trigonométricas de math y el símbolo ** para potencias.",
        )
        self._true_input_field = ft.TextField(
            label="xᵥ para f(x)",
            value="1.2",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._approx_input_field = ft.TextField(
            label="xₐ aproximado",
            value="1.18",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self._error_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Magnitud", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Resultado", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            visible=False,
            heading_row_color=ft.Colors.GREY_200,
            divider_thickness=0.6,
            column_spacing=30,
        )
        self._interpretation_text = ft.Text("", size=12, color=TEXT_MUTED)

        self._root = self._build()
        self._refresh_error_analysis(silent=True)

    @property
    def view(self) -> ft.Control:
        return self._root

    # ------------------------------- build ------------------------------- #
    def _build(self) -> ft.Control:
        hero = ft.Column(
            spacing=8,
            controls=[
                ft.Text("Programa 8 · Errores numéricos", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Trabaja con xᵥ, xₐ y f(x) para calcular Eₐ = |xᵥ − xₐ|, Eᵣ = |xᵥ − xₐ| / |xᵥ| y Eₚ = |f(xᵥ) − f(xₐ)|.",
                    size=13,
                    color=TEXT_MUTED,
                ),
            ],
        )

        requirements = ft.Container(
            bgcolor="#fff6ed",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text("Checklist del reporte:", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.Text("• Introducir xᵥ y xₐ proporcionados por el docente o un sensor para calcular errores.", size=12, color=TEXT_MUTED),
                    ft.Text("• Demostrar por qué 0.1 + 0.2 != 0.3 y documentar otros escenarios de redondeo.", size=12, color=TEXT_MUTED),
                    ft.Text("• Explicar con palabras los resultados tabulares (interpretación final).", size=12, color=TEXT_MUTED),
                ],
            ),
        )

        layout = ft.Column(
            spacing=20,
            controls=[
                hero,
                requirements,
                self._build_concepts_card(),
                self._build_float_examples_card(),
                self._build_error_lab_card(),
            ],
        )
        return ft.Container(expand=True, padding=ft.Padding(12, 12, 12, 24), content=layout)

    def _build_concepts_card(self) -> ft.Control:
        concept_cards: List[ft.Control] = []
        for concept in error_concepts():
            concept_cards.append(self._concept_chip(concept))

        expansion = ft.ExpansionTile(
            title=ft.Text("Conceptos de error numérico", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
            subtitle=ft.Text(
                "Refuerza la teoría solicitada en la guía (inherente, redondeo, truncamiento, overflow y error de modelo).",
                size=12,
                color=TEXT_MUTED,
            ),
            initially_expanded=False,
            controls=[
                ft.ResponsiveRow(
                    spacing=12,
                    run_spacing=12,
                    controls=[ft.Container(col={"xs": 12, "md": 6}, content=chip) for chip in concept_cards],
                )
            ],
        )
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(22, 22, 22, 22),
            content=ft.Column(
                spacing=12,
                controls=[expansion],
            ),
        )

    def _build_float_examples_card(self) -> ft.Control:
        scenarios = floating_point_scenarios()

        scenario_cards = []
        for scene in scenarios:
            scenario_cards.append(
                ft.Container(
                    bgcolor="#fffaf3",
                    border_radius=14,
                    padding=ft.Padding(16, 12, 16, 12),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(f"Expresión: {scene.expression}", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            ft.Text(f"Esperado: {scene.expected}", size=12, color=TEXT_MUTED),
                            ft.Text(f"Computadora: {scene.computed}", size=12, color=TEXT_MUTED),
                            ft.Text("Interpretación:", size=12, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            ft.Text(scene.explanation, size=12, color=TEXT_DARK),
                        ],
                    ),
                )
            )

        expansion = ft.ExpansionTile(
            title=ft.Text("Ejemplos con punto flotante", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
            subtitle=ft.Text(
                "Uso obligatorio: print(0.1 + 0.2 == 0.3). Aquí mostramos el resultado falso, más dos escenarios adicionales.",
                size=12,
                color=TEXT_MUTED,
            ),
            initially_expanded=False,
            controls=[ft.Column(spacing=12, controls=scenario_cards)],
        )
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(22, 22, 22, 22),
            content=ft.Column(
                spacing=12,
                controls=[
                    expansion,
                ],
            ),
        )

    def _build_error_lab_card(self) -> ft.Control:
        inputs = ft.ResponsiveRow(
            spacing=12,
            run_spacing=12,
            controls=[
                ft.Container(col={"xs": 12, "md": 6}, content=self._true_value_field),
                ft.Container(col={"xs": 12, "md": 6}, content=self._approx_value_field),
                ft.Container(col={"xs": 12, "md": 6}, content=self._true_input_field),
                ft.Container(col={"xs": 12, "md": 6}, content=self._approx_input_field),
                ft.Container(col={"xs": 12}, content=self._function_field),
            ],
        )
        run_button = ft.FilledButton(
            "Calcular errores",
            icon=icons.ANALYTICS,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: SECONDARY_COLOR},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=self._refresh_error_analysis,
        )
        interpretation_box = ft.Container(
            bgcolor="#eef7ff",
            border_radius=16,
            padding=ft.Padding(12, 12, 12, 12),
            content=self._interpretation_text,
        )
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(22, 22, 22, 22),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Laboratorio de errores", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            run_button,
                        ],
                    ),
                    ft.Text(
                        "Ingresa xᵥ, xₐ y los argumentos usados en f(x) (p. ej. xᵥ = 1.2, xₐ = 1.18). "
                        "El panel devuelve automáticamente Eₐ, Eᵣ y Eₚ para el reporte.",
                        size=12,
                        color=TEXT_MUTED,
                    ),
                    inputs,
                    self._error_table,
                    ft.Text("Interpretación", size=12, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    interpretation_box,
                ],
            ),
        )

    def _concept_chip(self, concept: ErrorConceptVM) -> ft.Control:
        return ft.Container(
            bgcolor="#fffaf6",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=16,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(concept.title, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Text(concept.description, size=12, color=TEXT_MUTED),
                    ft.Container(
                        bgcolor="#ffe6d5",
                        border_radius=12,
                        padding=ft.Padding(8, 8, 8, 8),
                        content=ft.Text(concept.example, size=11, color=TEXT_DARK),
                    ),
                ],
            ),
        )

    def _refresh_error_analysis(self, _event=None, *, silent: bool = False) -> None:
        try:
            true_value = self._parse_float(self._true_value_field.value, "xᵥ (valor verdadero)")
            approx_value = self._parse_float(self._approx_value_field.value, "xₐ (valor aproximado)")
            true_input = self._parse_float(self._true_input_field.value, "xᵥ para f(x)")
            approx_input = self._parse_float(self._approx_input_field.value, "xₐ para f(x)")
        except ValueError as exc:
            if not silent:
                self._show_error(str(exc))
            return
        try:
            vm = compute_error_analysis(
                true_value=true_value,
                approx_value=approx_value,
                function_expression=self._function_field.value or "",
                true_input=true_input,
                approx_input=approx_input,
            )
        except ValueError as exc:
            if not silent:
                self._show_error(str(exc))
            return
        self._render_error_analysis(vm)

    def _render_error_analysis(self, vm: ErrorAnalysisVM) -> None:
        rows = [
            {"title": "xᵥ (verdadero)", "value": self._format_number(vm.true_value)},
            {"title": "xₐ (aproximado)", "value": self._format_number(vm.approx_value)},
            {
                "title": "Error absoluto",
                "formula": "Eₐ = |xᵥ − xₐ|",
                "value": self._format_number(vm.absolute_error),
            },
            {
                "title": "Error relativo",
                "formula": "Eᵣ = |xᵥ − xₐ| / |xᵥ|",
                "value": "No definido (xᵥ = 0)" if vm.relative_error is None else self._format_number(vm.relative_error),
            },
            {
                "title": f"f(xᵥ) con f(x) = {vm.function_expression}",
                "value": self._format_number(vm.f_true),
            },
            {
                "title": "f(xₐ)",
                "value": self._format_number(vm.f_approx),
            },
            {
                "title": "Propagación",
                "formula": "Eₚ = |f(xᵥ) − f(xₐ)|",
                "value": self._format_number(vm.propagated_error),
            },
        ]
        self._error_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(self._metric_label(row["title"], row.get("formula"))),
                    ft.DataCell(ft.Text(row["value"])),
                ]
            )
            for row in rows
        ]
        self._error_table.visible = True
        self._interpretation_text.value = vm.interpretation
        self._safe_update(self._error_table)
        self._safe_update(self._interpretation_text)

    # ------------------------------ helpers ------------------------------ #
    def _parse_float(self, text: str | None, label: str) -> float:
        raw = (text or "").strip()
        if raw == "":
            raise ValueError(f"Ingresa el {label}.")
        try:
            return float(raw)
        except ValueError as exc:
            raise ValueError(f"'{text}' no es un número válido para {label}.") from exc

    def _format_number(self, value: float) -> str:
        return f"{value:.8g}"

    def _metric_label(self, title: str, formula: str | None = None) -> ft.Control:
        if not formula:
            return ft.Text(title)
        return ft.Column(
            spacing=2,
            controls=[
                ft.Text(title, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                ft.Text(formula, size=11, color=TEXT_MUTED),
            ],
        )

    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#f77373")
        self._page.snack_bar.open = True
        self._page.update()

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
