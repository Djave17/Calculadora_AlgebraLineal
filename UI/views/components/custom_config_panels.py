from __future__ import annotations

from typing import Callable

import flet as ft

from ...styles import PRIMARY_COLOR, SECONDARY_COLOR, SURFACE_COLOR, TEXT_DARK, TEXT_MUTED, BORDER_COLOR
from ...methods import MethodInfo


class _BaseConfigPanel:
    def __init__(self, method: MethodInfo) -> None:
        self.method = method
        self._container: ft.Container | None = None
        self._title_text: ft.Text | None = None
        self._description_text: ft.Text | None = None

    @property
    def view(self) -> ft.Control:
        if self._container is None:
            self._container = self._build()
        return self._container

    def _header(self) -> ft.Column:
        self._title_text = ft.Text(self.method.label, size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK)
        self._description_text = ft.Text(self.method.description, size=12, color=TEXT_MUTED)
        return ft.Column(
            spacing=4,
            controls=[
                self._title_text,
                self._description_text,
            ],
        )

    def _build(self) -> ft.Container:
        raise NotImplementedError

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass

    def set_method(self, method: MethodInfo) -> None:
        self.method = method
        if self._title_text:
            self._title_text.value = method.label
            self._safe_update(self._title_text)
        if self._description_text:
            self._description_text.value = method.description
            self._safe_update(self._description_text)


class CombinationConfigPanel(_BaseConfigPanel):
    MIN_DIM = 2
    MAX_DIM = 8
    MIN_VECT = 1
    MAX_VECT = 8

    def __init__(self, method: MethodInfo, on_change: Callable[[int, int], None]) -> None:
        super().__init__(method)
        self._dimension = 3
        self._vectors = 2
        self._on_change = on_change
        self._dim_field: ft.TextField | None = None
        self._vec_field: ft.TextField | None = None
        self._updating = False

    def _build(self) -> ft.Container:
        header = self._header()
        self._dim_field = ft.TextField(
            label="Dimensión n",
            value=str(self._dimension),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )
        self._vec_field = ft.TextField(
            label="Número de vectores",
            value=str(self._vectors),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )

        body = ft.Column(
            spacing=12,
            controls=[header, self._dim_field, self._vec_field],
        )

        container = ft.Container(
            width=None,
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=body,
        )
        return container

    def _handle_change(self, _event) -> None:
        if self._updating:
            return
        dimension = self._dimension
        vectors = self._vectors
        if self._dim_field:
            dimension = self._parse_int(self._dim_field.value, self.MIN_DIM, self.MAX_DIM, self._dimension)
        if self._vec_field:
            vectors = self._parse_int(self._vec_field.value, self.MIN_VECT, self.MAX_VECT, self._vectors)
        if (dimension, vectors) != (self._dimension, self._vectors):
            self._dimension = dimension
            self._vectors = vectors
            if self._on_change:
                self._on_change(dimension, vectors)
        self.set_values(dimension, vectors)

    def _parse_int(self, text: str | None, minimum: int, maximum: int, fallback: int) -> int:
        try:
            value = int((text or fallback))
        except (TypeError, ValueError):
            value = fallback
        return max(minimum, min(maximum, value))

    def set_values(self, dimension: int, vectors: int) -> None:
        self._dimension = dimension
        self._vectors = vectors
        self._updating = True
        if self._dim_field:
            self._dim_field.value = str(dimension)
            self._safe_update(self._dim_field)
        if self._vec_field:
            self._vec_field.value = str(vectors)
            self._safe_update(self._vec_field)
        self._updating = False

    def values(self) -> tuple[int, int]:
        return self._dimension, self._vectors


class MatrixOpsConfigPanel(_BaseConfigPanel):
    MIN = 1
    MAX = 8

    def __init__(self, method: MethodInfo, on_change: Callable[[int, int, int, int, str], None]) -> None:
        super().__init__(method)
        self._rows_a = 2
        self._cols_a = 2
        self._rows_b = 2
        self._cols_b = 2
        self._alpha = ""
        self._on_change = on_change
        self._updating = False
        self._fields: dict[str, ft.TextField] = {}

    def _build(self) -> ft.Container:
        header = self._header()
        def make_field(label: str, key: str, value: str, numeric: bool = True) -> ft.TextField:
            field = ft.TextField(
                label=label,
                value=value,
                text_align=ft.TextAlign.CENTER,
                border_radius=12,
                border_color=PRIMARY_COLOR,
                focused_border_color=SECONDARY_COLOR,
                keyboard_type=ft.KeyboardType.NUMBER if numeric else ft.KeyboardType.TEXT,
                on_blur=self._handle_change,
                on_submit=self._handle_change,
            )
            self._fields[key] = field
            return field

        rows_a = make_field("Filas A", "rows_a", str(self._rows_a))
        cols_a = make_field("Columnas A", "cols_a", str(self._cols_a))
        rows_b = make_field("Filas B", "rows_b", str(self._rows_b))
        cols_b = make_field("Columnas B", "cols_b", str(self._cols_b))
        alpha = make_field("Escalar α (opcional)", "alpha", self._alpha, numeric=False)

        body = ft.Column(
            spacing=12,
            controls=[header, rows_a, cols_a, rows_b, cols_b, alpha],
        )

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=body,
        )

    def _handle_change(self, _event) -> None:
        if self._updating:
            return
        rows_a = self._parse_int(self._fields.get("rows_a"), self._rows_a)
        cols_a = self._parse_int(self._fields.get("cols_a"), self._cols_a)
        rows_b = self._parse_int(self._fields.get("rows_b"), self._rows_b)
        cols_b = self._parse_int(self._fields.get("cols_b"), self._cols_b)
        alpha = (self._fields.get("alpha").value if self._fields.get("alpha") else self._alpha) or ""

        changed = (rows_a, cols_a, rows_b, cols_b, alpha) != (self._rows_a, self._cols_a, self._rows_b, self._cols_b, self._alpha)
        self.set_values(rows_a, cols_a, rows_b, cols_b, alpha)
        if changed and self._on_change:
            self._on_change(self._rows_a, self._cols_a, self._rows_b, self._cols_b, self._alpha)

    def _parse_int(self, field: ft.TextField | None, fallback: int) -> int:
        if field is None:
            return fallback
        try:
            value = int(field.value or fallback)
        except (TypeError, ValueError):
            value = fallback
        return max(self.MIN, min(self.MAX, value))

    def set_values(self, rows_a: int, cols_a: int, rows_b: int, cols_b: int, alpha: str) -> None:
        self._rows_a = rows_a
        self._cols_a = cols_a
        self._rows_b = rows_b
        self._cols_b = cols_b
        self._alpha = alpha or ""
        self._updating = True
        mapping = {
            "rows_a": str(rows_a),
            "cols_a": str(cols_a),
            "rows_b": str(rows_b),
            "cols_b": str(cols_b),
            "alpha": self._alpha,
        }
        for key, value in mapping.items():
            field = self._fields.get(key)
            if field:
                field.value = value
                self._safe_update(field)
        self._updating = False

    def values(self) -> tuple[int, int, int, int, str]:
        return self._rows_a, self._cols_a, self._rows_b, self._cols_b, self._alpha


class TransposeConfigPanel(_BaseConfigPanel):
    MIN = 1
    MAX = 8

    def __init__(self, method: MethodInfo, on_change: Callable[[int, int, str], None]) -> None:
        super().__init__(method)
        self._rows = 2
        self._cols = 2
        self._alpha = ""
        self._on_change = on_change
        self._updating = False
        self._rows_field: ft.TextField | None = None
        self._cols_field: ft.TextField | None = None
        self._alpha_field: ft.TextField | None = None

    def _build(self) -> ft.Container:
        header = self._header()
        self._rows_field = ft.TextField(
            label="Filas",
            value=str(self._rows),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )
        self._cols_field = ft.TextField(
            label="Columnas",
            value=str(self._cols),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )
        self._alpha_field = ft.TextField(
            label="Escalar α (opcional)",
            value=self._alpha,
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.TEXT,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )

        body = ft.Column(
            spacing=12,
            controls=[header, self._rows_field, self._cols_field, self._alpha_field],
        )

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=body,
        )

    def _handle_change(self, _event) -> None:
        if self._updating:
            return
        rows = self._parse_int(self._rows_field, self._rows)
        cols = self._parse_int(self._cols_field, self._cols)
        alpha = (self._alpha_field.value if self._alpha_field else self._alpha) or ""
        changed = (rows, cols, alpha) != (self._rows, self._cols, self._alpha)
        self.set_values(rows, cols, alpha)
        if changed and self._on_change:
            self._on_change(self._rows, self._cols, self._alpha)

    def _parse_int(self, field: ft.TextField | None, fallback: int) -> int:
        if field is None:
            return fallback
        try:
            value = int(field.value or fallback)
        except (TypeError, ValueError):
            value = fallback
        return max(self.MIN, min(self.MAX, value))

    def set_values(self, rows: int, cols: int, alpha: str) -> None:
        self._rows = rows
        self._cols = cols
        self._alpha = alpha or ""
        self._updating = True
        if self._rows_field:
            self._rows_field.value = str(rows)
            self._safe_update(self._rows_field)
        if self._cols_field:
            self._cols_field.value = str(cols)
            self._safe_update(self._cols_field)
        if self._alpha_field:
            self._alpha_field.value = self._alpha
            self._safe_update(self._alpha_field)
        self._updating = False

    def values(self) -> tuple[int, int, str]:
        return self._rows, self._cols, self._alpha


class MatrixIdentitiesConfigPanel(_BaseConfigPanel):
    MIN = 1
    MAX = 8

    def __init__(
        self,
        method: MethodInfo,
        on_dimensions_change: Callable[[int, int], None],
        on_resolve: Callable[[], None],
        on_clear: Callable[[], None],
    ) -> None:
        super().__init__(method)
        self._rows = 3
        self._cols = 3
        self._on_dimensions_change = on_dimensions_change
        self._on_resolve = on_resolve
        self._on_clear = on_clear
        self._rows_field: ft.TextField | None = None
        self._cols_field: ft.TextField | None = None
        self._rows_label = "Filas"
        self._cols_label = "Columnas"
        self._updating = False

    def _build(self) -> ft.Container:
        header = self._header()
        self._rows_field = ft.TextField(
            label=self._rows_label,
            value=str(self._rows),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )
        self._cols_field = ft.TextField(
            label=self._cols_label,
            value=str(self._cols),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_change,
            on_submit=self._handle_change,
        )

        actions = ft.Row(
            spacing=10,
            controls=[
                ft.FilledButton("Resolver", on_click=lambda _: self._on_resolve()),
                ft.OutlinedButton("Limpiar", on_click=lambda _: self._on_clear()),
            ],
        )

        body = ft.Column(
            spacing=12,
            controls=[header, self._rows_field, self._cols_field, actions],
        )

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=body,
        )

    def _handle_change(self, _event) -> None:
        if self._updating:
            return
        rows = self._parse_int(self._rows_field, self._rows)
        cols = self._parse_int(self._cols_field, self._cols)
        changed = (rows, cols) != (self._rows, self._cols)
        self.set_values(rows, cols)
        if changed and self._on_dimensions_change:
            self._on_dimensions_change(self._rows, self._cols)

    def _parse_int(self, field: ft.TextField | None, fallback: int) -> int:
        if field is None:
            return fallback
        try:
            value = int(field.value or fallback)
        except (TypeError, ValueError):
            value = fallback
        return max(self.MIN, min(self.MAX, value))

    def set_values(self, rows: int, cols: int) -> None:
        self._rows = rows
        self._cols = cols
        self._updating = True
        if self._rows_field:
            self._rows_field.value = str(rows)
            self._safe_update(self._rows_field)
        if self._cols_field:
            self._cols_field.value = str(cols)
            self._safe_update(self._cols_field)
        self._updating = False

    def set_labels(self, rows_label: str, cols_label: str) -> None:
        self._rows_label = rows_label
        self._cols_label = cols_label
        if self._rows_field:
            self._rows_field.label = rows_label
            self._safe_update(self._rows_field)
        if self._cols_field:
            self._cols_field.label = cols_label
            self._safe_update(self._cols_field)


class VectorPropertiesConfigPanel(_BaseConfigPanel):
    MIN_DIM = 2
    MAX_DIM = 8

    def __init__(
        self,
        method: MethodInfo,
        on_dimension_change: Callable[[int], None],
        on_alpha_change: Callable[[str], None],
        on_resolve: Callable[[], None],
        on_clear: Callable[[], None],
    ) -> None:
        super().__init__(method)
        self._dimension = 3
        self._alpha = ""
        self._on_dimension_change = on_dimension_change
        self._on_alpha_change = on_alpha_change
        self._on_resolve = on_resolve
        self._on_clear = on_clear
        self._dim_field: ft.TextField | None = None
        self._alpha_field: ft.TextField | None = None
        self._updating = False

    def _build(self) -> ft.Container:
        header = self._header()
        self._dim_field = ft.TextField(
            label="Dimensión n",
            value=str(self._dimension),
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_blur=self._handle_dimension_change,
            on_submit=self._handle_dimension_change,
        )
        self._alpha_field = ft.TextField(
            label="Escalar α",
            value=self._alpha,
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_blur=self._handle_alpha_change,
            on_submit=self._handle_alpha_change,
        )
        actions = ft.Column(
            spacing=10,
            controls=[
                ft.FilledButton("Resolver", on_click=lambda _: self._on_resolve()),
                ft.OutlinedButton("Limpiar", on_click=lambda _: self._on_clear()),
            ],
        )

        body = ft.Column(
            spacing=12,
            controls=[header, self._dim_field, self._alpha_field, actions],
        )

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.border.all(1, color=BORDER_COLOR),
            border_radius=18,
            padding=ft.Padding(20, 20, 20, 20),
            content=body,
        )

    def _handle_dimension_change(self, _event) -> None:
        if self._updating:
            return
        value = self._parse_dimension(self._dim_field.value if self._dim_field else None)
        changed = value != self._dimension
        self.set_dimension(value)
        if changed and self._on_dimension_change:
            self._on_dimension_change(value)

    def _handle_alpha_change(self, _event) -> None:
        if self._updating:
            return
        alpha = self._alpha_field.value if self._alpha_field else ""
        self.set_alpha(alpha)
        if self._on_alpha_change:
            self._on_alpha_change(self._alpha)

    def _parse_dimension(self, text: str | None) -> int:
        try:
            value = int(text or self._dimension)
        except (TypeError, ValueError):
            value = self._dimension
        return max(self.MIN_DIM, min(self.MAX_DIM, value))

    def set_dimension(self, dimension: int) -> None:
        self._dimension = dimension
        self._updating = True
        if self._dim_field:
            self._dim_field.value = str(dimension)
            self._safe_update(self._dim_field)
        self._updating = False

    def dimension(self) -> int:
        return self._dimension

    def set_alpha(self, alpha: str) -> None:
        self._alpha = (alpha or "").strip()
        self._updating = True
        if self._alpha_field:
            self._alpha_field.value = self._alpha
            self._safe_update(self._alpha_field)
        self._updating = False

    def value_alpha(self) -> str:
        return self._alpha

