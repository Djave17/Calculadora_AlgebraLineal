from __future__ import annotations

import re
from typing import Iterable, cast

import flet as ft
from flet import Colors as colors, Icons as icons

from ViewModels.root_methods_open_vm import (
    OpenMethodIterationVM,
    OpenMethodName,
    OpenMethodResultVM,
    solve_open_root,
)
from ViewModels.expression_evaluator import evaluate_expression
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class NumericalMethodsOpenView:
    """Vista para metodos abiertos (Newton-Raphson y Secante)."""

    _SUPERSCRIPT_DIGITS: dict[str, str] = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
        "x": "ˣ",
        "X": "ˣ",
    }
    _SUPERSCRIPT_REVERSE: dict[str, str] = {v: k for k, v in _SUPERSCRIPT_DIGITS.items()}

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._method_field = ft.Dropdown(
            label="Metodo abierto",
            value="newton_raphson",
            options=[
                ft.dropdown.Option(key="newton_raphson", text="Newton-Raphson"),
                ft.dropdown.Option(key="secant", text="Secante"),
            ],
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_change=self._handle_method_change,
        )
        self._function_field = ft.TextField(
            label="f(x)",
            value="x^3 - x - 1",
            helper_text="Usa x como variable; admite pi/euler y sen, cos, tan, cotan. Usa ^ para potencias.",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.TEXT,
            on_change=self._handle_function_change,
            multiline=False,
            max_lines=1,
        )
        self._function_field.value = self._beautify_expression(self._function_field.value)
        self._x0_field = ft.TextField(
            label="x0 (punto inicial)",
            value="1.5",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._x1_field = ft.TextField(
            label="x1 (solo para Secante)",
            value="2",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            visible=False,
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
        self._max_iter_field = ft.TextField(
            label="Maximo de iteraciones",
            value="50",
            helper_text="Evita ciclos oscilantes o divergentes.",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._interval_a_field = ft.TextField(
            label="Intervalo a",
            value="0",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._interval_b_field = ft.TextField(
            label="Intervalo b",
            value="2",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._subintervals_field = ft.TextField(
            label="Numero de subintervalos",
            value="20",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._interval_row = ft.ResponsiveRow(
            columns=12,
            spacing=18,
            run_spacing=16,
            controls=[
                ft.Container(col={"xs": 12, "md": 4}, content=self._interval_a_field),
                ft.Container(col={"xs": 12, "md": 4}, content=self._interval_b_field),
                ft.Container(col={"xs": 12, "md": 4}, content=self._subintervals_field),
            ],
        )

        self._solve_button = ft.FilledButton(
            "Calcular",
            icon=icons.PLAY_ARROW,
            style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, color=colors.WHITE),
            on_click=self._handle_solve,
        )
        self._feedback_text = ft.Text("", color=TEXT_MUTED, size=12)
        self._iterations_table = ft.DataTable(
            columns=self._base_columns("newton_raphson"),
            rows=[],
            heading_row_color=colors.GREY_200,
            column_spacing=16,
            visible=False,
        )
        self._iterations_scroll = ft.Row(controls=[self._iterations_table], scroll=ft.ScrollMode.ALWAYS, expand=True)
        self._iterations_scroll.visible = False
        self._chart = self._build_chart([], None, None, None, 0, self._plain_expression(self._function_field.value or ""))
        self._chart_info = ft.Text("", size=12, color=TEXT_DARK)
        self._chart_container: ft.Container | None = None
        self._summary = ft.Text("", visible=False, color=TEXT_DARK)
        self._steps_tile = ft.ExpansionTile(
            title=ft.Text("Pasos del metodo", size=16, weight=ft.FontWeight.W_600, color=TEXT_DARK),
            subtitle=ft.Text("Formulas y calculos por iteracion.", size=12, color=TEXT_MUTED),
            initially_expanded=False,
            controls=[],
            visible=False,
        )

        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        hero = ft.Column(
            spacing=4,
            controls=[
                ft.Text("Metodos abiertos de raices", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Newton-Raphson y Secante con validacion de derivada, grafico y sustitucion final en f(x).",
                    size=13,
                    color=TEXT_MUTED,
                ),
            ],
        )

        form_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Text("Configuracion", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=16,
                        run_spacing=16,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 4}, content=self._method_field),
                            ft.Container(col={"xs": 12, "md": 8}, content=self._function_field, margin=ft.Margin(0, 0, 0, 10)),
                        ],
                    ),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=16,
                        run_spacing=16,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 6}, content=self._x0_field),
                            ft.Container(col={"xs": 12, "md": 6}, content=self._x1_field),
                        ],
                    ),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=16,
                        run_spacing=16,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 6}, content=self._error_field),
                            ft.Container(col={"xs": 12, "md": 6}, content=self._max_iter_field),
                        ],
                    ),
                    self._interval_row,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Alerta si f'(x) = 0 y se respeta el maximo de iteraciones.",
                                size=12,
                                color=PRIMARY_COLOR,
                                weight=ft.FontWeight.W_600,
                            ),
                            self._solve_button,
                        ],
                    ),
                    self._feedback_text,
                ],
            ),
        )

        chart_content = ft.Column(
            spacing=8,
            controls=[
                ft.Text("Grafica f(x) y raiz aproximada", size=17, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                self._chart,
                self._chart_info,
            ],
        )
        self._chart_container = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(12, 12, 12, 12),
            content=chart_content,
        )

        summary_card = ft.Container(
            bgcolor="#fff6ed",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(16, 16, 16, 16),
            content=self._summary,
        )

        table_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Iteraciones", size=17, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            ft.Icon(icons.TABLE_ROWS, color=PRIMARY_COLOR),
                        ],
                    ),
                    self._iterations_scroll,
                ],
            ),
        )

        return ft.Column(
            spacing=18,
            controls=[hero, form_card, self._chart_container, summary_card, table_card, self._build_steps_card()],
        )

    def _handle_method_change(self, _=None) -> None:
        method_value = cast(OpenMethodName, self._method_field.value or "newton_raphson")
        self._x1_field.visible = method_value == "secant"
        self._interval_row.visible = method_value != "secant"
        self._safe_update(self._x1_field)
        self._safe_update(self._interval_row)
        self._iterations_table.columns = self._base_columns(method_value)
        self._safe_update(self._iterations_table)

    def _handle_solve(self, _=None) -> None:
        interval_bounds: tuple[float, float] | None = None
        subints = 0
        try:
            expression = self._plain_expression((self._function_field.value or "").strip())
            if not expression:
                raise ValueError("Ingresa una funcion f(x).")
            x0 = self._parse_float(self._x0_field.value, "x0")
            desired_error = self._parse_float(self._error_field.value, "Error deseado")
            max_iterations = int(float(self._max_iter_field.value or "50"))
            method_value = cast(OpenMethodName, self._method_field.value or "newton_raphson")
            x1 = self._parse_float(self._x1_field.value, "x1") if method_value == "secant" else None
            if method_value != "secant":
                interval_a = self._parse_float(self._interval_a_field.value, "Intervalo a")
                interval_b = self._parse_float(self._interval_b_field.value, "Intervalo b")
                subints = int(float(self._subintervals_field.value or "20"))
                interval_bounds = (interval_a, interval_b) if subints > 0 else None
            result = solve_open_root(
                method_value,
                expression,
                x0,
                desired_error,
                x1=x1,
                max_iterations=max_iterations,
            )
        except ValueError as exc:
            self._feedback_text.value = f"{exc}"
            self._feedback_text.color = colors.ERROR
            self._iterations_table.visible = False
            self._iterations_scroll.visible = False
            self._summary.visible = False
            self._chart.visible = False
            self._steps_tile.visible = False
            self._update_controls()
            return

        self._feedback_text.value = "Calculo completado."
        self._feedback_text.color = colors.GREEN_700

        self._render_iterations(result)
        self._render_summary(result)
        self._render_chart(result, interval_bounds, subints, expression)
        self._render_steps(result)
        self._update_controls()

    def _render_iterations(self, result: OpenMethodResultVM) -> None:
        self._iterations_table.columns = self._base_columns(result.method)
        rows = []
        for it in result.iterations:
            cells = [
                ft.DataCell(self._mono(f"{it.iteration}")),
                ft.DataCell(self._mono(f"{it.xi:.6f}")),
            ]
            if result.method == "secant":
                cells.append(ft.DataCell(self._mono(f"{it.xi_minus_1:.6f}" if it.xi_minus_1 is not None else "-")))
            cells.extend(
                [
                    ft.DataCell(self._mono(f"{it.fx:.6f}")),
                    ft.DataCell(self._mono("-" if it.fprime is None else f"{it.fprime:.6f}")),
                    ft.DataCell(self._mono(f"{it.next_x:.6f}")),
                    ft.DataCell(self._mono("-" if it.error_percent is None else f"{it.error_percent:.6f}%")),
                ]
            )
            rows.append(ft.DataRow(cells=cells))
        self._iterations_table.rows = rows
        self._iterations_table.visible = True
        self._iterations_scroll.visible = True

    def _render_summary(self, result: OpenMethodResultVM) -> None:
        final_error = "-" if result.final_error_percent is None else f"{result.final_error_percent:.6f}%"
        warning_text = "Advertencia: f'(x) llego a 0." if result.derivative_warning else ""
        lines = [
            f"Metodo: {'Newton-Raphson' if result.method == 'newton_raphson' else 'Secante'}",
            f"Raiz aproximada: {result.approx_root:.8f}",
            f"f(raiz): {result.final_function_value:.8f} (sustitucion final)",
            f"Iteraciones: {len(result.iterations)} / maximo {result.max_iterations}",
            f"Error final: {final_error} (tolerancia <= {result.tolerance_percent:.6f}%)",
            "Estado: " + ("Convergio" if result.converged else "Maximo de iteraciones alcanzado"),
            warning_text,
        ]
        self._summary.value = "\n".join(line for line in lines if line)
        self._summary.visible = True

    def _render_chart(
        self,
        result: OpenMethodResultVM,
        interval_bounds: tuple[float, float] | None,
        subintervals: int,
        expression: str,
    ) -> None:
        self._chart = self._build_chart(result.plot_points, result.approx_root, result.final_function_value, interval_bounds, subintervals, expression)
        if self._chart_container and isinstance(self._chart_container.content, ft.Column):
            self._chart_container.content.controls[1] = self._chart
            self._chart_container.content.controls[2] = self._chart_info
            self._chart.visible = True
            self._safe_update(self._chart_container)
        self._chart_info.value = f"x = {result.approx_root:.6f} | f(x) = {result.final_function_value:.6g}"
        self._chart_info.visible = True

    def _render_steps(self, result: OpenMethodResultVM) -> None:
        sections = self._build_steps_sections(result)
        if sections:
            self._steps_tile.controls = sections
            self._steps_tile.visible = True
        else:
            self._steps_tile.controls = []
            self._steps_tile.visible = False

    def _base_columns(self, method: OpenMethodName) -> list[ft.DataColumn]:
        headers = ["Iteracion", "x_i"]
        if method == "secant":
            headers.append("x_{i-1}")
        headers.extend(["f(x_i)", "f'(x_i)", "x_{i+1}", "Error %"])
        return [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD)) for h in headers]

    def _mono(self, text: str) -> ft.Text:
        return ft.Text(text, font_family="Consolas", size=13, color=TEXT_DARK)

    def _parse_float(self, value: str | None, label: str) -> float:
        try:
            return float(value or "")
        except Exception as exc:
            raise ValueError(f"{label} invalido.") from exc

    def _build_chart(
        self,
        points: Iterable[tuple[float, float]],
        root: float | None,
        root_value: float | None,
        interval_bounds: tuple[float, float] | None,
        subintervals: int,
        expression: str,
    ) -> ft.Control:
        pts = list(points)
        if interval_bounds is not None and subintervals > 2:
            try:
                a, b = interval_bounds
                step = (b - a) / max(subintervals - 1, 1)
                pts = []
                x = a
                for _ in range(subintervals):
                    try:
                        y = evaluate_expression(expression, x)
                    except Exception:
                        y = 0.0
                    pts.append((x, y))
                    x += step
            except Exception:
                pts = list(points)
        if not pts:
            return ft.Text("Grafica disponible despues de un calculo valido.", color=TEXT_MUTED)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys + [0]), max(ys + [0])
        padding_x = max(abs(max_x - min_x) * 0.05, 1e-3)
        padding_y = max(abs(max_y - min_y) * 0.1, 0.5)
        data_series = [
            ft.LineChartData(
                data_points=[ft.LineChartDataPoint(x, y) for x, y in pts],
                stroke_width=2,
                color=PRIMARY_COLOR,
                curved=True,
                below_line_gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, colors=["#e6f3ff", "#fff"]),
            )
        ]
        if root is not None and root_value is not None:
            data_series.append(
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(root, root_value)
                    ],
                    stroke_width=2,
                    color="#0b5c36",
                )
            )
        return ft.LineChart(
            data_series=data_series,
            min_x=min_x - padding_x,
            max_x=max_x + padding_x,
            min_y=min_y - padding_y,
            max_y=max_y + padding_y,
            horizontal_grid_lines=ft.ChartGridLines(color="#f0f0f0"),
            vertical_grid_lines=ft.ChartGridLines(color="#f0f0f0"),
            interactive=True,
            expand=True,
        )

    def _build_steps_sections(self, result: OpenMethodResultVM) -> list[ft.Control]:
        if not result.iterations:
            return []
        header = ft.Text(
            "Formulas clave (Newton-Raphson)" if result.method == "newton_raphson" else "Formulas clave (Secante)",
            weight=ft.FontWeight.W_600,
            color=PRIMARY_COLOR,
        )
        formulas = [
            self._mono("Newton: x(i+1) = xi - f(xi)/f'(xi)") if result.method == "newton_raphson" else self._mono("Secante: x(i+1) = xi - f(xi)(xi-1 - xi)/(f(xi-1)-f(xi))"),
            self._mono("Ea% = |x(i+1) - x(i)| / |x(i+1)| * 100"),
        ]
        sections: list[ft.Control] = [header, ft.Column(spacing=2, controls=formulas)]
        prev_x: float | None = None
        for it in result.iterations:
            lines = [
                self._mono(f"x_i = {it.xi:.6f}" + (f", x_i-1 = {it.xi_minus_1:.6f}" if it.xi_minus_1 is not None else "")),
                self._mono(f"f(x_i) = {it.fx:.6f}" + ("" if it.fprime is None else f", f'(x_i) = {it.fprime:.6f}")),
                self._mono(f"x_{it.iteration+1} = {it.next_x:.6f}"),
            ]
            if prev_x is None or it.error_percent is None:
                lines.append(self._mono("Ea%: - (primera iteracion)"))
            else:
                lines.append(self._mono(f"Ea% = {it.error_percent:.6f}%"))
            sections.append(
                ft.ExpansionTile(
                    title=self._mono(f"Iteracion {it.iteration}"),
                    controls=[ft.Column(spacing=2, controls=lines)],
                    initially_expanded=False,
                )
            )
            prev_x = it.next_x
        return sections

    def _build_steps_card(self) -> ft.Container:
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(14, 12, 14, 12),
            content=self._steps_tile,
        )

    def _beautify_expression(self, expr: str) -> str:
        def repl_paren(match: re.Match[str]) -> str:
            sequence = match.group(1)
            return "".join(self._SUPERSCRIPT_DIGITS.get(ch, ch) for ch in sequence)

        expr = re.sub(r"\^\(([^)]+)\)", repl_paren, expr)

        def repl_simple(match: re.Match[str]) -> str:
            sequence = match.group(1)
            return "".join(self._SUPERSCRIPT_DIGITS.get(ch, ch) for ch in sequence)

        return re.sub(r"\^([0-9+\-xX]+)", repl_simple, expr)

    def _plain_expression(self, expr: str) -> str:
        def repl(match: re.Match[str]) -> str:
            base = match.group(1)
            supers = match.group(2)
            digits = "".join(self._SUPERSCRIPT_REVERSE.get(ch, ch) for ch in supers)
            return f"{base}^{digits}"

        superscript_chars = "".join(self._SUPERSCRIPT_DIGITS.values())
        pattern = re.compile(rf"([A-Za-z0-9\)\]])([{superscript_chars}]+)")
        expr = pattern.sub(repl, expr)
        return expr

    def _handle_function_change(self, e: ft.ControlEvent) -> None:
        current_value = e.control.value or ""
        plain_expr = self._plain_expression(current_value)
        beautified = self._beautify_expression(plain_expr)
        if beautified != current_value:
            self._function_field.value = beautified
            self._safe_update(self._function_field)

    def _clear_function(self, _=None) -> None:
        self._function_field.value = ""
        self._safe_update(self._function_field)

    def _update_controls(self) -> None:
        for control in (
            self._feedback_text,
            self._iterations_table,
            self._iterations_scroll,
            self._summary,
            self._chart,
            self._chart_container,
            self._steps_tile,
            self._interval_row,
        ):
            self._safe_update(control)

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
