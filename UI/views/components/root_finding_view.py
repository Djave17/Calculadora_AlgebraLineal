from __future__ import annotations

from typing import cast
import math

import flet as ft
from flet import Colors as colors, Icons as icons

from ViewModels.root_finding_vm import MethodName, RootFindingResultVM, RootFindingIterationVM, solve_root
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class MetodosCerradosRaicesView:
    """Vista para los metodos cerrados de biseccion y regla falsa."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._method_field = ft.Dropdown(
            label="Metodo",
            value="bisection",
            options=[
                ft.dropdown.Option(key="bisection", text="Biseccion"),
                ft.dropdown.Option(key="false_position", text="Regla falsa"),
            ],
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
        )
        self._function_field = ft.TextField(
            label="f(x)",
            value="x^3 - x - 1",
            helper_text="Usa x como variable y ^ para potencias. Ej.: x^3 - x - 1",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_submit=self._handle_solve,
        )
        self._a_field = ft.TextField(
            label="Limite inferior a",
            value="1",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._b_field = ft.TextField(
            label="Limite superior b",
            value="2",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._error_field = ft.TextField(
            label="Error deseado (porcentaje o decimal)",
            value="0.01",
            helper_text="Ej.: 0.5 equivale a 0.5%, 0.0001 equivale a 0.01%.",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._solve_button = ft.FilledButton(
            "Calcular",
            icon=icons.PLAY_ARROW,
            style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE),
            on_click=self._handle_solve,
        )
        self._feedback_text = ft.Text("", color=TEXT_MUTED, size=12)
        self._iterations_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Iteracion", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("a", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("b", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Punto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nuevo intervalo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Error %", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            heading_row_color=colors.GREY_200,
            column_spacing=22,
            visible=False,
        )
        self._iterations_scroll = ft.Row(
            controls=[self._iterations_table],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
        )
        self._iterations_scroll.visible = False
        self._summary_container = ft.Container(visible=False)
        self._steps_tile = ft.ExpansionTile(
            title=ft.Text("Ver pasos", size=16, weight=ft.FontWeight.W_600, color=TEXT_DARK),
            subtitle=ft.Text(
                "Muestra las fórmulas del algoritmo exactamente como en la guía.",
                size=12,
                color=TEXT_MUTED,
            ),
            initially_expanded=False,
            controls=[],
            visible=False,
        )
        self._result: RootFindingResultVM | None = None

        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        hero = ft.Column(
            spacing=6,
            controls=[
                ft.Text("Metodos cerrados de busqueda de raices", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Selecciona Biseccion o Regla Falsa, ingresa f(x) con su intervalo [a,b] y el error deseado."
                    " El sistema valida f(a)*f(b) < 0 y documenta cada iteracion.",
                    size=13,
                    color=TEXT_MUTED,
                ),
            ],
        )

        form_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(24, 24, 24, 24),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Text("Configuracion del metodo", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=12,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 4}, content=self._method_field),
                            ft.Container(
                                col={"xs": 12, "md": 8},
                                content=self._function_field,
                                margin=ft.Margin(0, 0, 0, 10),
                            ),
                            ft.Container(col={"xs": 12, "md": 4}, content=self._a_field),
                            ft.Container(col={"xs": 12, "md": 4}, content=self._b_field),
                            ft.Container(
                                col={"xs": 12, "md": 4},
                                content=self._error_field,
                                margin=ft.Margin(0, 12, 0, 0),
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Recuerda: f(a) * f(b) debe ser negativo para garantizar una raiz en [a,b].",
                                size=12,
                                color=TEXT_MUTED,
                            ),
                            self._solve_button,
                        ],
                    ),
                    self._feedback_text,
                ],
            ),
        )

        table_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Iteraciones", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            ft.Icon(icons.TABLE_ROWS, color=PRIMARY_COLOR),
                        ],
                    ),
                    self._iterations_scroll,
                ],
            ),
        )

        summary_card = ft.Container(
            bgcolor="#fff6ed",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=self._summary_container,
        )

        steps_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(16, 16, 16, 16),
            content=self._steps_tile,
        )

        layout = ft.Column(
            spacing=20,
            controls=[hero, form_card, table_card, summary_card, steps_card],
        )
        return ft.Container(expand=True, padding=ft.Padding(12, 12, 12, 24), content=layout)

    def _handle_solve(self, _=None) -> None:
        try:
            expression = (self._function_field.value or "").strip()
            if not expression:
                raise ValueError("Ingresa una funcion f(x).")
            a = float(self._a_field.value)
            b = float(self._b_field.value)
            desired_error = float(self._error_field.value)
            method_value = cast(MethodName, self._method_field.value or "bisection")
            result = solve_root(method_value, expression, a, b, desired_error)
        except ValueError as exc:
            self._result = None
            self._iterations_table.visible = False
            self._iterations_scroll.visible = False
            self._summary_container.visible = False
            self._steps_tile.visible = False
            self._steps_tile.controls = []
            self._feedback_text.value = f"{exc}"
            self._feedback_text.color = colors.ERROR
            self._update_controls()
            return

        self._feedback_text.value = "Intervalo valido y calculo completado."
        self._feedback_text.color = colors.GREEN_700
        self._result = result
        self._render_iterations(result)
        self._render_summary(result)
        self._render_steps(result)
        self._update_controls()

    def _render_iterations(self, result: RootFindingResultVM) -> None:
        if result.method == "bisection":
            self._render_bisection_iterations(result)
        else:
            self._render_false_position_iterations(result)
        self._iterations_table.visible = True
        self._iterations_scroll.visible = True

    def _render_bisection_iterations(self, result: RootFindingResultVM) -> None:
        self._iterations_table.columns = [
            ft.DataColumn(ft.Text("Iteracion", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xₗ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xᵤ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xᵣ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Eₐ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vₗ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vᵤ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vᵣ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xᵤ − xₗ < E", weight=ft.FontWeight.BOLD)),
        ]
        rows: list[ft.DataRow] = []
        for iteration in result.iterations:
            interval_len = iteration.next_interval[1] - iteration.next_interval[0]
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(self._mono_line(f"+{iteration.iteration}")),
                        ft.DataCell(self._mono_line(self._fmt(iteration.a))),
                        ft.DataCell(self._mono_line(self._fmt(iteration.b))),
                        ft.DataCell(self._mono_line(self._fmt(iteration.point))),
                        ft.DataCell(
                            self._mono_line("-" if iteration.error_percent is None else f"{iteration.error_percent:.4f}")
                        ),
                        ft.DataCell(self._signed_cell(iteration.fa)),
                        ft.DataCell(self._signed_cell(iteration.fb)),
                        ft.DataCell(self._signed_cell(iteration.fp)),
                        ft.DataCell(self._mono_line(f"{interval_len:.4f}")),
                    ]
                )
            )
        self._iterations_table.rows = rows

    def _render_false_position_iterations(self, result: RootFindingResultVM) -> None:
        self._iterations_table.columns = [
            ft.DataColumn(ft.Text("Iteracion", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xₗ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xᵤ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("xᵣ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Eₐ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vₗ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vᵤ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("vᵣ", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Eₐ < E", weight=ft.FontWeight.BOLD)),
        ]
        rows: list[ft.DataRow] = []
        for iteration in result.iterations:
            ea_val = "-" if iteration.error_percent is None else f"{iteration.error_percent:.4f}"
            converged = (
                "-"
                if iteration.error_percent is None
                else ("True" if iteration.error_percent <= result.tolerance_percent else "False")
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(self._mono_line(f"+{iteration.iteration}")),
                        ft.DataCell(self._mono_line(self._fmt(iteration.a))),
                        ft.DataCell(self._mono_line(self._fmt(iteration.b))),
                        ft.DataCell(self._mono_line(self._fmt(iteration.point))),
                        ft.DataCell(self._mono_line(ea_val)),
                        ft.DataCell(self._signed_cell(iteration.fa)),
                        ft.DataCell(self._signed_cell(iteration.fb)),
                        ft.DataCell(self._signed_cell(iteration.fp)),
                        ft.DataCell(self._mono_line(converged)),
                    ]
                )
            )
        self._iterations_table.rows = rows

    def _render_summary(self, result: RootFindingResultVM) -> None:
        iterations_count = len(result.iterations)
        final_error = "-" if result.final_error_percent is None else f"{result.final_error_percent:.6f}%"
        status = "Convergio" if result.converged else "Maximo de iteraciones alcanzado"
        summary_column = ft.Column(
            spacing=6,
            controls=[
                ft.Text("Resumen final", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                ft.Text(f"Metodo: {'Biseccion' if result.method == 'bisection' else 'Regla falsa'}", color=TEXT_DARK),
                ft.Text(f"Raiz aproximada: {result.approx_root:.8f}", color=TEXT_DARK),
                ft.Text(f"Iteraciones: {iterations_count}", color=TEXT_DARK),
                ft.Text(
                    f"Error final: {final_error} (tolerancia <= {result.tolerance_percent:.6f}%)",
                    color=TEXT_DARK,
                ),
                ft.Text(
                    f"Intervalo final: [{result.final_interval[0]:.6f}, {result.final_interval[1]:.6f}]",
                    color=TEXT_DARK,
                ),
                ft.Text(status, color=TEXT_MUTED, size=12),
            ],
        )
        self._summary_container.content = summary_column
        self._summary_container.visible = True

    def _render_steps(self, result: RootFindingResultVM) -> None:
        sections = self._build_steps_sections(result)
        if sections:
            self._steps_tile.controls = sections
            self._steps_tile.visible = True
        else:
            self._steps_tile.controls = []
            self._steps_tile.visible = False

    def _build_steps_sections(self, result: RootFindingResultVM) -> list[ft.Control]:
        sections: list[ft.Control] = []
        if result.method == "bisection":
            overview = self._build_bisection_overview(result)
            if overview:
                sections.append(overview)
        elif result.method == "false_position":
            sections.append(self._build_false_position_overview())

        prev_point: float | None = None
        for iteration in result.iterations:
            sections.append(self._build_iteration_block(iteration, result.method, prev_point))
            prev_point = iteration.point
        return sections

    def _build_bisection_overview(self, result: RootFindingResultVM) -> ft.Control | None:
        if not result.iterations:
            return None
        first = result.iterations[0]
        tolerance = result.tolerance_percent / 100
        if tolerance <= 0:
            return None
        interval_length = abs(first.b - first.a)
        if interval_length <= 0:
            return None
        ratio = interval_length / tolerance
        n_estimate = math.log2(ratio)
        n_required = math.ceil(n_estimate)
        lines = [
            ft.Text("Estimacion de iteraciones (Biseccion)", weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
            self._formula_block("n", f"log₂((xᵤ - xₗ)/E) = log₂(({self._fmt(first.b)} - {self._fmt(first.a)}) / {self._fmt(tolerance)})"),
            self._formula_block("n", f"log₂({ratio:.4f}) ≈ {n_estimate:.2f}"),
            self._mono_line(f"Se requieren {n_required} iteraciones para que la semilongitud sea menor que E."),
        ]
        return ft.Column(spacing=4, controls=lines)

    def _build_false_position_overview(self) -> ft.Control:
        lines = [
            ft.Text("Formulas clave (Regla Falsa)", weight=ft.FontWeight.W_600, color=PRIMARY_COLOR),
            self._formula_block("xᵣ", "xᵤ - f(xᵤ) * (xₗ - xᵤ) / (f(xₗ) - f(xᵤ))"),
            self._formula_block("Eₐ", "|(xᵣ(k) - xᵣ(k-1)) / xᵣ(k)| * 100%"),
            self._mono_line("Evalua f(xₗ), f(xᵤ) y f(xᵣ) en cada iteracion para decidir el nuevo intervalo."),
        ]
        return ft.Column(spacing=6, controls=lines)

    def _build_iteration_block(
        self,
        iteration: RootFindingIterationVM,
        method: MethodName,
        prev_point: float | None,
    ) -> ft.Control:
        header = ft.Text(f"Iteracion {iteration.iteration}", weight=ft.FontWeight.W_600, color=PRIMARY_COLOR, size=15)
        lines: list[ft.Control] = []
        lines.append(self._formula_block("xₗ", f"{self._fmt(iteration.a)}"))
        lines.append(self._formula_block("xᵤ", f"{self._fmt(iteration.b)}"))
        if method == "bisection":
            xr_formula = f"xᵣ = (xₗ + xᵤ) / 2 = ({self._fmt(iteration.a)} + {self._fmt(iteration.b)}) / 2 = {self._fmt(iteration.point)}"
        else:
            xr_formula = (
                f"xᵣ = xᵤ - f(xᵤ) * (xₗ - xᵤ)/(f(xₗ) - f(xᵤ)) = {self._fmt(iteration.b)} - "
                f"{self._fmt(iteration.fb)} * ({self._fmt(iteration.a)} - {self._fmt(iteration.b)}) / "
                f"({self._fmt(iteration.fa)} - {self._fmt(iteration.fb)}) = {self._fmt(iteration.point)}"
            )
        lines.append(self._formula_block("xᵣ", xr_formula, highlight=True))
        lines.append(self._formula_block("f(xₗ)", f"f({self._fmt(iteration.a)}) = {self._fmt(iteration.fa)}"))
        lines.append(self._formula_block("f(xᵤ)", f"f({self._fmt(iteration.b)}) = {self._fmt(iteration.fb)}"))
        lines.append(self._formula_block("f(xᵣ)", f"f({self._fmt(iteration.point)}) = {self._fmt(iteration.fp)}", highlight=True))
        if prev_point is None or iteration.error_percent is None:
            lines.append(self._mono_line("Eₐ inicia sin calcular en la primera iteracion."))
        else:
            lines.append(
                self._formula_block(
                    "Eₐ",
                    f"|({self._fmt(iteration.point)} - {self._fmt(prev_point)}) / {self._fmt(iteration.point)}| * 100% = {iteration.error_percent:.6f}%",
                )
            )
        product = iteration.fa * iteration.fp
        relation = "< 0" if product < 0 else ("> 0" if product > 0 else "= 0")
        lines.append(self._mono_line(f"f(xₗ) · f(xᵣ) = {product:.6f} {relation}"))
        lines.append(
            self._mono_line(
                f"La raiz se ubica dentro de [{self._fmt(iteration.next_interval[0])}, {self._fmt(iteration.next_interval[1])}]."
            )
        )
        details = ft.Column(spacing=6, controls=lines)
        return ft.Container(padding=ft.Padding(8, 4, 8, 12), content=ft.Column(spacing=4, controls=[header, details]))

    def _fmt(self, value: float) -> str:
        return f"{value:.6f}"

    def _formula_block(self, label: str, expression: str, highlight: bool = False) -> ft.Text:
        color = PRIMARY_COLOR if highlight else TEXT_DARK
        return ft.Text(
            spans=[
                ft.TextSpan(f"{label}: ", style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=color)),
                ft.TextSpan(expression, style=ft.TextStyle(font_family="Consolas", color=TEXT_DARK)),
            ],
            size=13,
        )

    def _mono_line(self, text: str) -> ft.Text:
        return ft.Text(text, font_family="Consolas", size=13, color=TEXT_DARK)

    def _signed_cell(self, value: float) -> ft.Text:
        color = PRIMARY_COLOR if value > 0 else ("#0c7a43" if value < 0 else TEXT_DARK)
        prefix = "+" if value > 0 else ""
        return ft.Text(f"{prefix}{value:.4f}", font_family="Consolas", size=13, color=color)

    def _update_controls(self) -> None:
        for control in (
            self._iterations_table,
            self._iterations_scroll,
            self._summary_container,
            self._feedback_text,
            self._steps_tile,
        ):
            self._safe_update(control)

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
