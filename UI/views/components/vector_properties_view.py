from __future__ import annotations

from typing import Optional

import flet as ft
from flet import Colors as colors

from ViewModels.vector_propiedades_vm import VectorPropiedadesViewModel


class VectorPropertiesView:
    """Permite analizar operaciones básicas en ℝⁿ reutilizando el ViewModel existente."""

    def __init__(self, page: ft.Page, view_model: VectorPropiedadesViewModel) -> None:
        self._page = page
        self._vm = view_model

        self._u_field = ft.TextField(label="Vector u", hint_text="Ej: 1,2,3", expand=True)
        self._v_field = ft.TextField(label="Vector v", hint_text="Ej: 0,1,-1", expand=True)
        self._w_field = ft.TextField(label="Vector w (opcional)", hint_text="Ej: 1,1,1", expand=True)
        self._alpha_field = ft.TextField(label="Escalar α (opcional)", hint_text="Ej: 2/3", expand=True)

        self._result_container = ft.Column(spacing=8, expand=True)
        self._result_container.controls.append(
            ft.Text("Introduce vectores para ver los resultados.", color=colors.GREY_600)
        )

        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    # ------------------------------ Construcción ------------------------------
    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=2,
            controls=[
                ft.Text("Propiedades en ℝⁿ", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Calcula suma, producto por escalar y verifica axiomas básicos usando u, v y w.",
                    size=12,
                    color=colors.GREY_600,
                ),
            ],
        )

        inputs = ft.Column(
            spacing=12,
            controls=[
                self._u_field,
                self._v_field,
                self._w_field,
                self._alpha_field,
            ],
        )

        actions = ft.Row(
            spacing=12,
            controls=[
                ft.FilledButton("Calcular", icon=ft.icons.PLAY_ARROW, on_click=self._handle_calculate),
                ft.OutlinedButton("Limpiar", icon=ft.icons.CLEAR, on_click=self._handle_clear),
            ],
        )

        card = ft.Container(
            bgcolor=colors.WHITE,
            border_radius=20,
            padding=ft.Padding(20, 20, 20, 20),
            shadow=ft.BoxShadow(blur_radius=18, color="#22000000", spread_radius=2),
            content=ft.Column(
                spacing=16,
                expand=True,
                controls=[
                    header,
                    inputs,
                    actions,
                    ft.Text("Resultados", size=18, weight=ft.FontWeight.BOLD),
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
                controls=[card],
            ),
        )

    # ------------------------------ Acciones ------------------------------
    def _handle_calculate(self, _event) -> None:
        try:
            data = {
                "u": self._u_field.value or "",
                "v": self._v_field.value or "",
                "w": self._w_field.value or "",
                "alpha": self._alpha_field.value or "",
            }
            resultado = self._vm.propiedades_Rn(data)
        except Exception as exc:  # pragma: no cover - propagación a UI
            self._show_error(str(exc))
            return

        self._render_result(resultado)

    def _handle_clear(self, _event) -> None:
        for field in (self._u_field, self._v_field, self._w_field, self._alpha_field):
            field.value = ""
            field.update()
        self._result_container.controls.clear()
        self._result_container.controls.append(
            ft.Text("Introduce vectores para ver los resultados.", color=colors.GREY_600)
        )
        self._result_container.update()

    # ------------------------------ Presentación ------------------------------
    def _render_result(self, data: dict) -> None:
        self._result_container.controls.clear()

        suma = data.get("suma")
        if suma:
            self._result_container.controls.append(ft.Text("Suma u + v", weight=ft.FontWeight.BOLD))
            self._result_container.controls.extend(
                ft.Text(line) for line in suma.get("pasos", [])
            )
            self._result_container.controls.append(
                ft.Text(f"Resultado: {suma.get('resultado')}")
            )

        producto = data.get("producto_escalar")
        if producto:
            self._result_container.controls.append(ft.Divider())
            self._result_container.controls.append(ft.Text("Producto por escalar", weight=ft.FontWeight.BOLD))
            self._result_container.controls.extend(ft.Text(line) for line in producto.get("pasos", []))
            self._result_container.controls.append(
                ft.Text(f"Resultado: {producto.get('resultado')}")
            )

        propiedades = data.get("propiedades", [])
        if propiedades:
            self._result_container.controls.append(ft.Divider())
            self._result_container.controls.append(ft.Text("Verificación de axiomas", weight=ft.FontWeight.BOLD))
            for prop in propiedades:
                estado = "Sí" if prop.get("cumple") else "No"
                self._result_container.controls.append(
                    ft.Text(f"{prop.get('propiedad')}: {estado}")
                )
                for paso in prop.get("pasos", []):
                    self._result_container.controls.append(ft.Text(f"  - {paso}", size=12))

        self._result_container.update()

    # ------------------------------ Utilidades ------------------------------
    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(
            bgcolor=colors.ERROR,
            content=ft.Text(message),
        )
        self._page.snack_bar.open = True
        self._page.update()
