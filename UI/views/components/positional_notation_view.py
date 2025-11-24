from __future__ import annotations

from typing import List

import flet as ft
from flet import Icons as icons

from ViewModels.numerical_errors_vm import BaseDecompositionVM, decompose_number
from ...styles import BORDER_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED


class PositionalNotationView:
    """Vista dedicada a la descomposición en base 10 y base 2 del Programa 8."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page
        self._number_field = ft.TextField(
            label="Número entero",
            value="84506",
            helper_text="Acepta signo +/- y espacios como separador de miles.",
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_submit=self._refresh_decomposition,
        )
        self._results_column = ft.Column(spacing=12)
        self._root = self._build()
        self._refresh_decomposition(silent=True)

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        hero = ft.Column(
            spacing=6,
            controls=[
                ft.Text("Programa 8 · Notación posicional", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Expón cada cifra usando potencias de 10 y 2 para explicar cómo se construye un número en distintas bases.",
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
                    ft.Text("¿Qué debes documentar?", weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.Text("• Mostrar la multiplicación de cada cifra por su posición (potencias de 10 o 2).", size=12, color=TEXT_MUTED),
                    ft.Text("• Incluir un ejemplo base 10 (p.ej. 84 506) y uno base 2 (p.ej. 1111001).", size=12, color=TEXT_MUTED),
                    ft.Text("• Presentar los pasos individuales y la suma final que reconstruye el número original.", size=12, color=TEXT_MUTED),
                ],
            ),
        )
        example_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=20,
            padding=ft.Padding(24, 24, 24, 24),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Descomposición paso a paso", size=18, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                            ft.Text(
                                "Escribe el número e identifica los aportes posicionales. Ideal para capturas de pantalla del reporte.",
                                size=12,
                                color=TEXT_MUTED,
                            ),
                            ft.Text(
                                "Pulsa el botón rojo de la derecha para recalcular la descomposición.",
                                size=11,
                                color=TEXT_MUTED,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            self._number_field,
                            ft.Container(
                                bgcolor="#fff1e5",
                                border_radius=12,
                                padding=ft.Padding(12, 12, 12, 12),
                                expand=True,
                                content=ft.Text(
                                    "Ejemplos sugeridos:\n84 506 = 8·10⁴ + 4·10³ + ... + 6·10⁰\n1111001 = 1·2⁶ + … + 1·2⁰",
                                    size=12,
                                    color=TEXT_MUTED,
                                ),
                            ),
                        ],
                    ),
                    self._results_column,
                ],
            ),
        )
        floating_refresh = ft.Container(
            alignment=ft.alignment.top_right,
            padding=ft.Padding(0, 0, 0, 0),
            content=ft.FilledButton(
                "Calcular",
                icon=icons.AUTO_AWESOME,
                style=ft.ButtonStyle(
                    bgcolor={ft.ControlState.DEFAULT: SECONDARY_COLOR},
                    color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                on_click=self._refresh_decomposition,
            ),
        )
        example_section = ft.Stack(
            controls=[
                example_card,
                floating_refresh,
            ],
        )

        layout = ft.Column(
            spacing=20,
            controls=[
                hero,
                requirements,
                example_section,
            ],
        )
        return ft.Container(expand=True, padding=ft.Padding(12, 12, 12, 24), content=layout)

    # ---------------- Actions ---------------- #
    def _refresh_decomposition(self, _event=None, *, silent: bool = False) -> None:
        try:
            number = self._parse_integer_input()
            self._number_field.error_text = None
        except ValueError as exc:
            if not silent:
                message = str(exc)
                self._number_field.error_text = message
                self._safe_update(self._number_field)
                self._show_error(message)
            return
        try:
            base10_vm = decompose_number(number, 10)
            base2_vm = decompose_number(number, 2)
        except ValueError as exc:
            if not silent:
                self._show_error(str(exc))
            return
        self._results_column.controls = [
            self._build_decomposition_tile(base10_vm, "Base 10", icons.CALCULATE, True),
            self._build_decomposition_tile(base2_vm, "Base 2", icons.DEVICE_HUB, True),
        ]
        self._safe_update(self._results_column)
        self._safe_update(self._number_field)

    def _build_decomposition_tile(self, vm: BaseDecompositionVM, title: str, icon_name: str, expanded: bool) -> ft.Control:
        rows = []
        for term in vm.terms:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(term.digit))),
                        ft.DataCell(ft.Text(f"{vm.base}^{term.exponent}")),
                        ft.DataCell(ft.Text(str(term.contribution))),
                    ],
                )
            )
        steps = ft.Column(spacing=2, controls=[ft.Text(step, size=11, color=TEXT_MUTED) for step in vm.steps])
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cifra")),
                ft.DataColumn(ft.Text("Posición")),
                ft.DataColumn(ft.Text("Aporte")),
            ],
            rows=rows,
            divider_thickness=0.6,
            column_spacing=24,
        )
        header = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon_name, color=PRIMARY_COLOR),
                ft.Text(title, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                ft.Container(
                    bgcolor="#fff1e5",
                    border_radius=10,
                    padding=ft.Padding(8, 4, 8, 4),
                    content=ft.Text(vm.base_digits, size=11, weight=ft.FontWeight.BOLD),
                ),
            ],
        )
        body = ft.Container(
            bgcolor="#fefcfa",
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(16, 16, 16, 16),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        f"Expresión posicional: {vm.formatted_expression}",
                        size=12,
                        color=TEXT_MUTED,
                    ),
                    table,
                    ft.Text(f"Suma final: {vm.value}", size=12, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                    ft.Container(
                        bgcolor="#fff6ed",
                        border_radius=12,
                        padding=ft.Padding(10, 10, 10, 10),
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Pasos mostrados al usuario", size=11, weight=ft.FontWeight.W_600, color=TEXT_DARK),
                                steps,
                            ],
                        ),
                    ),
                ],
            ),
        )
        return ft.ExpansionTile(
            title=header,
            subtitle=ft.Text(f"Suma final: {vm.value}", size=12, color=TEXT_MUTED),
            initially_expanded=expanded,
            controls=[body],
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

    def _parse_integer_input(self) -> int:
        raw_value = (self._number_field.value or "").strip()
        if not raw_value:
            raise ValueError("Ingresa un numero entero (puede ser negativo).")
        normalized = "".join(ch for ch in raw_value if not ch.isspace())
        normalized = normalized.replace("_", "")
        if not normalized:
            raise ValueError("Ingresa un numero entero (puede ser negativo).")
        sign = ""
        if normalized[0] in "+-":
            sign = normalized[0]
            normalized = normalized[1:]
        if not normalized or not normalized.isdigit():
            raise ValueError("Solo se permiten digitos y un signo inicial.")
        return int(f"{sign}{normalized}")


