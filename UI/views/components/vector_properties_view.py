from __future__ import annotations

from typing import Optional

import flet as ft
from flet import Colors as colors

from ...styles import SURFACE_COLOR, BORDER_COLOR, PRIMARY_COLOR, TEXT_DARK, TEXT_MUTED

from ViewModels.linear_algebra_vm import LinearAlgebraViewModel


class VectorPropertiesView:
    """Permite analizar operaciones básicas en ℝⁿ reutilizando el ViewModel existente."""

    MIN_DIM = 2
    MAX_DIM = 8

    def __init__(self, page: ft.Page, view_model: LinearAlgebraViewModel) -> None:
        self._page = page
        self._vm = view_model

        self._dimension = 3
        self._alpha_text: str = ""
        self._alpha_label = ft.Text("α = —", color=colors.GREY_600)

        self._u_fields: list[ft.TextField] = []
        self._v_fields: list[ft.TextField] = []
        self._w_fields: list[ft.TextField] = []

        self._vectors_row = ft.ResponsiveRow(spacing=16, run_spacing=16)

        self._result_container = ft.Column(spacing=8, expand=True)
        self._result_container.controls.append(
            ft.Text("Introduce vectores para ver los resultados.", color=colors.GREY_600)
        )

        self._root = self._build()
        self._build_vector_cards()
        self._update_alpha_label()

    @property
    def view(self) -> ft.Control:
        return self._root

    # ------------------------------ Construcción ------------------------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Propiedades en ℝⁿ", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Calcula suma, producto por escalar y verifica axiomas básicos usando u, v y w.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=20,
            padding=ft.Padding(20, 20, 20, 20),
            shadow=ft.BoxShadow(blur_radius=18, color="#22000000", spread_radius=2),
            content=ft.Column(
                spacing=16,
                expand=True,
                controls=[
                    header,
                    self._vectors_row,
                    ft.Text("Resultados", size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Container(
                        bgcolor="#fff6f5",
                        border_radius=16,
                        padding=ft.Padding(16, 16, 16, 16),
                        content=self._result_container,
                    ),
                ],
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(12, 0, 12, 0),
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[card, self._alpha_label],
            ),
        )

    # ------------------------------ Operaciones ------------------------------
    def _handle_calculate(self, _event) -> None:
        data = {
            "u": self._vector_text(self._u_fields),
            "v": self._vector_text(self._v_fields),
            "w": self._vector_text(self._w_fields),
            "alpha": self._alpha_text,
        }
        try:
            resultado = self._vm.propiedades_Rn(data)
        except Exception as exc:  # pragma: no cover - propagación a UI
            self._show_error(str(exc))
            return

        self._update_alpha_label()
        self._render_result(resultado)

    def _handle_clear(self, _event) -> None:
        for fields in (self._u_fields, self._v_fields, self._w_fields):
            for field in fields:
                field.value = ""
                try:
                    field.update()
                except AssertionError:
                    pass
        self._result_container.controls.clear()
        self._result_container.controls.append(
            ft.Text("Introduce vectores para ver los resultados.", color=colors.GREY_600)
        )
        try:
            if self._result_container.page:
                self._result_container.update()
        except AssertionError:
            pass
        self._update_alpha_label()

    def resolve(self) -> None:
        self._handle_calculate(None)

    def clear_fields(self) -> None:
        self._handle_clear(None)

    # ------------------------------ Presentación ------------------------------
    def _render_result(self, data: dict) -> None:
        self._result_container.controls.clear()

        suma = data.get("suma")
        if suma:
            self._result_container.controls.append(ft.Text("Suma u + v", weight=ft.FontWeight.BOLD))
            self._result_container.controls.extend(ft.Text(line) for line in suma.get("pasos", []))
            self._result_container.controls.append(ft.Text(f"Resultado: {suma.get('resultado')}"))

        producto = data.get("producto_escalar")
        if producto:
            self._result_container.controls.append(ft.Divider())
            self._result_container.controls.append(ft.Text("Producto por escalar", weight=ft.FontWeight.BOLD))
            self._result_container.controls.extend(ft.Text(line) for line in producto.get("pasos", []))
            self._result_container.controls.append(ft.Text(f"Resultado: {producto.get('resultado')}"))

        propiedades = data.get("propiedades", [])
        if propiedades:
            self._result_container.controls.append(ft.Divider())
            self._result_container.controls.append(ft.Text("Verificación de axiomas", weight=ft.FontWeight.BOLD))
            for prop in propiedades:
                estado = "Sí" if prop.get("cumple") else "No"
                self._result_container.controls.append(ft.Text(f"{prop.get('propiedad')}: {estado}"))
                for paso in prop.get("pasos", []):
                    self._result_container.controls.append(ft.Text(f"  - {paso}", size=12))

        try:
            if self._result_container.page:
                self._result_container.update()
        except AssertionError:
            pass

    # ------------------------------ Utilidades ------------------------------
    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(
            bgcolor=colors.ERROR,
            content=ft.Text(message),
        )
        self._page.snack_bar.open = True
        self._page.update()

    def set_alpha(self, alpha_text: str) -> None:
        self._alpha_text = (alpha_text or "").strip()
        self._update_alpha_label()

    def alpha_text(self) -> str:
        return self._alpha_text

    def _update_alpha_label(self) -> None:
        display = self._alpha_text or "—"
        self._alpha_label.value = f"α = {display}"
        try:
            if self._alpha_label.page:
                self._alpha_label.update()
        except AssertionError:
            pass

    def set_dimension(self, dimension: int) -> None:
        dimension = max(self.MIN_DIM, min(self.MAX_DIM, dimension))
        if dimension == self._dimension:
            return
        self._dimension = dimension
        self._build_vector_cards()

    def dimension(self) -> int:
        return self._dimension

    def _vector_text(self, fields: list[ft.TextField]) -> str:
        return ",".join((field.value or "0") for field in fields)

    def _build_vector_cards(self) -> None:
        def ensure_fields(fields: list[ft.TextField]) -> list[ft.TextField]:
            if len(fields) < self._dimension:
                for _ in range(self._dimension - len(fields)):
                    fields.append(
                        ft.TextField(
                            width=80,
                            height=44,
                            text_align=ft.TextAlign.CENTER,
                            bgcolor="#fff5f4",
                            border_color=BORDER_COLOR,
                            focused_border_color=PRIMARY_COLOR,
                            content_padding=ft.Padding(0, 6, 0, 6),
                        )
                    )
            elif len(fields) > self._dimension:
                del fields[self._dimension :]
            return fields

        self._u_fields = ensure_fields(self._u_fields)
        self._v_fields = ensure_fields(self._v_fields)
        self._w_fields = ensure_fields(self._w_fields)

        def build_card(label: str, fields: list[ft.TextField]) -> ft.Container:
            rows = []
            for idx, field in enumerate(fields, start=1):
                rows.append(
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Text(str(idx), width=24, text_align=ft.TextAlign.CENTER, color=TEXT_MUTED),
                            field,
                        ],
                    )
                )
            return ft.Container(
                bgcolor=SURFACE_COLOR,
                border_radius=16,
                padding=ft.Padding(16, 16, 16, 16),
                border=ft.border.all(1, color=BORDER_COLOR),
                content=ft.Column(
                    spacing=8,
                    controls=[ft.Text(label, weight=ft.FontWeight.BOLD, color=TEXT_DARK), ft.Column(spacing=6, controls=rows)],
                ),
            )

        self._vectors_row.controls = [
            ft.Container(col={"xs": 12, "md": 4}, content=build_card("Vector u", self._u_fields)),
            ft.Container(col={"xs": 12, "md": 4}, content=build_card("Vector v", self._v_fields)),
            ft.Container(col={"xs": 12, "md": 4}, content=build_card("Vector w (opcional)", self._w_fields)),
        ]
        try:
            if self._vectors_row.page:
                self._vectors_row.update()
        except AssertionError:
            pass
