from __future__ import annotations

import flet as ft
from flet import Colors as colors

MER_CONTENT = """
### Método de Eliminación por Renglones (MER)

1. **Construye la matriz aumentada** `[A|b]` colocando el vector de términos independientes como última columna.
2. **Selecciona pivotes adecuados** en cada columna y permuta filas si el pivote es nulo.
3. **Normaliza el pivote** dividiendo la fila completa entre el valor del pivote.
4. **Anula los elementos sobre y debajo del pivote** mediante operaciones elementales de fila.
5. Repite el proceso para cada columna pivote hasta obtener la forma escalonada reducida (RREF).
6. Interpreta el sistema según la cantidad de pivotes y variables libres:
   - pivotes = número de variables → solución única.
   - pivotes < número de variables → infinitas soluciones (con parámetros).
   - aparece una fila `[0 … 0 | c]` con `c ≠ 0` → sistema inconsistente.

> Recuerda registrar las operaciones elementales; la vista de Gauss-Jordan te permite ver cada paso y replicarlo durante una demostración manual.
"""


class MerNotesView:
    """Muestra un resumen textual del MER."""

    def __init__(self) -> None:
        self._root = self._build()

    @property
    def view(self) -> ft.Control:
        return self._root

    def _build(self) -> ft.Control:
        card = ft.Container(
            bgcolor=colors.WHITE,
            border_radius=20,
            padding=ft.Padding(24, 24, 24, 24),
            shadow=ft.BoxShadow(blur_radius=18, color="#22000000", spread_radius=2),
            content=ft.Markdown(MER_CONTENT, selectable=True),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(24, 0, 24, 0),
            content=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[card],
            ),
        )
