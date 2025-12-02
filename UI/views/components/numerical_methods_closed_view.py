from __future__ import annotations

import re
from typing import Iterable, cast

import flet as ft
from flet import Colors as colors, Icons as icons

from ViewModels.root_methods_closed_vm import (
    ClosedMethodName,
    ClosedMethodResultVM,
    solve_closed_root,
)
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class NumericalMethodsClosedView:
    """Vista para metodos cerrados (Biseccion y Regla Falsa)."""

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
            label="Metodo cerrado",
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
            helper_text="Usa x como variable; admite pi/euler y sen, cos, tan, cotan. Usa ^ para potencias.",
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.TEXT,
            on_change=self._handle_function_change,
        )
        self._function_field.value = self._beautify_expression(self._function_field.value)
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
        self._max_iter_field = ft.TextField(
            label="Maximo de iteraciones",
            value="50",
            helper_text="Protege contra convergencia lenta u oscilante.",
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
            columns=self._base_columns(),
            rows=[],
            heading_row_color=colors.GREY_200,
            column_spacing=16,
            visible=False,
        )
        self._iterations_scroll = ft.Row(controls=[self._iterations_table], scroll=ft.ScrollMode.ALWAYS, expand=True)
        self._iterations_scroll.visible = False
        self._chart = self._build_chart([])
        self._chart_info = ft.Text("", size=12, color=TEXT_DARK)
        self._summary = ft.Text("", visible=False, color=TEXT_DARK)
        self._steps_tile = ft.ExpansionTile(
            title=ft.Text("Pasos del metodo", size=16, weight=ft.FontWeight.W_600, color=TEXT_DARK),
            subtitle=ft.Text("Formulas y calculos por iteracion.", size=12, color=TEXT_MUTED),
            initially_expanded=False,
            controls=[],
            visible=False,
        )
        self._chart_container: ft.Container | None = None

        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        hero = ft.Column(
            spacing=4,
            controls=[
                ft.Text("Metodos cerrados de busqueda de raices", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Selecciona Biseccion o Regla Falsa, ingresa f(x) con [a,b], error deseado y limite de iteraciones.",
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
                spacing=18,
                controls=[
                    ft.Text("Configuracion", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=20,
                        run_spacing=18,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 4}, content=self._method_field),
                            ft.Container(col={"xs": 12, "md": 8}, content=self._function_field, margin=ft.Margin(0, 0, 0, 12)),
                        ],
                    ),
                    ft.ResponsiveRow(
                        columns=12,
                        spacing=20,
                        run_spacing=18,
                        controls=[
                            ft.Container(col={"xs": 12, "md": 3}, content=self._a_field, padding=ft.Padding(0, 2, 0, 2)),
                            ft.Container(col={"xs": 12, "md": 3}, content=self._b_field, padding=ft.Padding(0, 2, 0, 2)),
                            ft.Container(col={"xs": 12, "md": 3}, content=self._error_field, padding=ft.Padding(0, 2, 0, 2)),
                            ft.Container(col={"xs": 12, "md": 3}, content=self._max_iter_field, padding=ft.Padding(0, 2, 0, 2)),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Recuerda: f(a) * f(b) debe ser negativo para garantizar raiz en [a,b].",
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

        summary_card = ft.Container(
            bgcolor="#fff6ed",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(16, 16, 16, 16),
            content=self._summary,
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

        return ft.Column(
            spacing=18,
            controls=[hero, form_card, self._chart_container, summary_card, table_card, self._build_steps_card()],
        )

    def _handle_solve(self, _=None) -> None:
        try:
            expression = self._plain_expression((self._function_field.value or "").strip())
            if not expression:
                raise ValueError("Ingresa una funcion f(x).")
            a = self._parse_float(self._a_field.value, "Limite inferior a")
            b = self._parse_float(self._b_field.value, "Limite superior b")
            desired_error = self._parse_float(self._error_field.value, "Error deseado")
            max_iterations = int(float(self._max_iter_field.value or "50"))
            method_value = cast(ClosedMethodName, self._method_field.value or "bisection")
            result = solve_closed_root(method_value, expression, a, b, desired_error, max_iterations=max_iterations)
        except ValueError as exc:
            self._feedback_text.value = f"{exc}"
            self._feedback_text.color = colors.ERROR
            self._iterations_table.visible = False
            self._summary.visible = False
            self._chart.visible = False
            self._update_controls()
            return

        self._feedback_text.value = "Intervalo valido y calculo completado."
        self._feedback_text.color = colors.GREEN_700

        self._render_iterations(result)
        self._render_summary(result)
        self._render_chart(result)
        self._render_steps(result)
        self._update_controls()

    def _render_iterations(self, result: ClosedMethodResultVM) -> None:
        self._iterations_table.columns = self._base_columns()
        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(self._mono(f"{it.iteration}")),
                    ft.DataCell(self._mono(f"{it.a:.6f}")),
                    ft.DataCell(self._mono(f"{it.b:.6f}")),
                    ft.DataCell(self._mono(f"{it.point:.6f}")),
                    ft.DataCell(self._mono(f"{it.fa:.6f}")),
                    ft.DataCell(self._mono(f"{it.fb:.6f}")),
                    ft.DataCell(self._mono(f"{it.fp:.6f}")),
                    ft.DataCell(self._mono("-" if it.error_percent is None else f"{it.error_percent:.6f}%")),
                ]
            )
            for it in result.iterations
        ]
        self._iterations_table.rows = rows
        self._iterations_table.visible = True
        self._iterations_scroll.visible = True

    def _render_summary(self, result: ClosedMethodResultVM) -> None:
        final_error = "-" if result.final_error_percent is None else f"{result.final_error_percent:.6f}%"
        lines = [
            f"Metodo: {'Biseccion' if result.method == 'bisection' else 'Regla falsa'}",
            f"Raiz aproximada: {result.approx_root:.8f}",
            f"f(raiz): {result.final_function_value:.8f} (cerca de 0)",
            f"Iteraciones: {len(result.iterations)} / maximo {result.max_iterations}",
            f"Error final: {final_error} (tolerancia <= {result.tolerance_percent:.6f}%)",
            f"Intervalo final: [{result.final_interval[0]:.6f}, {result.final_interval[1]:.6f}]",
            "Estado: " + ("Convergio" if result.converged else "Maximo de iteraciones alcanzado"),
        ]
        self._summary.value = "\n".join(lines)
        self._summary.visible = True

    def _render_chart(self, result: ClosedMethodResultVM) -> None:
        self._chart = self._build_chart(result.plot_points, result.approx_root, result.final_function_value)
        if self._chart_container and isinstance(self._chart_container.content, ft.Column):
            self._chart_container.content.controls[1] = self._chart
            self._chart_container.content.controls[2] = self._chart_info
            self._chart.visible = True
            self._safe_update(self._chart_container)
        self._chart_info.value = f"x = {result.approx_root:.6f} | f(x) = {result.final_function_value:.6g}"
        self._chart_info.visible = True

    def _render_steps(self, result: ClosedMethodResultVM) -> None:
        sections = self._build_steps_sections(result)
        if sections:
            self._steps_tile.controls = sections
            self._steps_tile.visible = True
        else:
            self._steps_tile.controls = []
            self._steps_tile.visible = False

    def _base_columns(self) -> list[ft.DataColumn]:
        headers = ["Iteracion", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Error %"]
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
        root: float | None = None,
        root_value: float | None = None,
    ) -> ft.Control:
        pts = list(points)
        if not pts:
            return ft.Text("Grafica disponible despues de un calculo valido.", color=TEXT_MUTED)
        if root is not None and root_value is not None:
            pts.append((root, root_value))
            pts.sort(key=lambda p: p[0])
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
                below_line_gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["#ffe6e6", "#fff"],
                ),
            )
        ]
        if root is not None and root_value is not None:
            data_series.append(
                ft.LineChartData(
                    data_points=[ft.LineChartDataPoint(root, root_value, tooltip=f"x = {root:.8f}\\nf(x) = {root_value:.8g}")],
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

    def _build_steps_sections(self, result: ClosedMethodResultVM) -> list[ft.Control]:
        if not result.iterations:
            return []
        header = ft.Text(
            "Formulas clave" if result.method == "bisection" else "Formulas clave (Regla falsa)",
            weight=ft.FontWeight.W_600,
            color=PRIMARY_COLOR,
        )
        formulas = [
            self._mono("Biseccion: xr = (a + b) / 2")
            if result.method == "bisection"
            else self._mono("Regla falsa: xr = b - f(b)(b-a)/(f(b)-f(a))"),
            self._mono("Ea% = |xr(k) - xr(k-1)| / |xr(k)| * 100"),
        ]
        sections: list[ft.Control] = [header, ft.Column(spacing=2, controls=formulas)]
        prev_point: float | None = None
        for it in result.iterations:
            xr_formula = (
                f"xr = (a + b)/2 = ({it.a:.6f} + {it.b:.6f})/2 = {it.point:.6f}"
                if result.method == "bisection"
                else f"xr = b - f(b)(b-a)/(f(b)-f(a)) = {it.point:.6f}"
            )
            body = [
                self._mono(f"a = {it.a:.6f}, b = {it.b:.6f}"),
                self._mono(xr_formula),
                self._mono(f"f(a) = {it.fa:.6f}, f(b) = {it.fb:.6f}, f(xr) = {it.fp:.6f}"),
            ]
            if prev_point is None or it.error_percent is None:
                body.append(self._mono("Ea%: - (primera iteracion)"))
            else:
                body.append(self._mono(f"Ea% = |xr(k) - xr(k-1)| / |xr(k)| = {it.error_percent:.6f}%"))
            sections.append(
                ft.ExpansionTile(
                    title=self._mono(f"Iteracion {it.iteration}"),
                    controls=[ft.Column(spacing=2, controls=body)],
                    initially_expanded=False,
                )
            )
            prev_point = it.point
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
        # Prioriza ^(...) para soportar e^(-x) y luego ^123
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

    def _update_controls(self) -> None:
        for control in (
            self._feedback_text,
            self._iterations_table,
            self._iterations_scroll,
            self._summary,
            self._chart,
            self._solve_button,
            self._chart_container,
            self._steps_tile,
        ):
            self._safe_update(control)

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
