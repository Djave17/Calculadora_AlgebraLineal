from __future__ import annotations

from typing import Callable

import flet as ft
from flet import Colors as colors

from ...helpers import clamp, pluralize
from ...methods import MethodInfo
from ...styles import (
    BORDER_COLOR,
    PANEL_WIDTH,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SURFACE_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)

MIN_ROWS = 2
MAX_ROWS = 10
MIN_COLS = 3
MAX_COLS = 12


class RightConfigPanel:
    def __init__(
        self,
        rows: int,
        cols: int,
        method: MethodInfo,
        on_dimensions_change: Callable[[int, int], None],
        on_resolve: Callable[[], None],
        on_clear: Callable[[], None],
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.method = method
        self._on_dimensions_change = on_dimensions_change
        self._on_resolve = on_resolve
        self._on_clear = on_clear
        self._enabled = method.available

        self._rows_field: ft.TextField | None = None
        self._cols_field: ft.TextField | None = None
        self._method_label: ft.Text | None = None
        self._category_label: ft.Text | None = None
        self._description_label: ft.Text | None = None
        self._resolve_button: ft.ElevatedButton | None = None
        self._clear_button: ft.OutlinedButton | None = None
        self._stats_label: ft.Text | None = None
        self._container: ft.Container | None = None
        self._updating_fields: bool = False

        self._container = self._build()
        self._apply_enabled_state()

    def _build(self) -> ft.Control:
        self._method_label = ft.Text(
            self.method.label,
            size=18,
            weight=ft.FontWeight.BOLD,
            color=TEXT_DARK,
        )
        self._category_label = ft.Text(
            f"Configura los parámetros para: {self.method.label}",
            size=12,
            color=TEXT_MUTED,
        )
        self._description_label = ft.Text(
            self.method.description,
            size=12,
            color=TEXT_MUTED,
        )

        self._rows_field = ft.TextField(
            label="Filas",
            value=str(self.rows),
            helper_text=f"Entre {MIN_ROWS} y {MAX_ROWS} filas",
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_blur=self._handle_rows_blur,
            on_submit=self._handle_rows_blur,
            on_change=self._handle_rows_change,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self._cols_field = ft.TextField(
            label="Columnas",
            value=str(self.cols),
            helper_text=f"Entre {MIN_COLS} y {MAX_COLS} coeficientes",
            text_align=ft.TextAlign.CENTER,
            border_radius=12,
            border_color=PRIMARY_COLOR,
            focused_border_color=SECONDARY_COLOR,
            on_blur=self._handle_cols_blur,
            on_submit=self._handle_cols_blur,
            on_change=self._handle_cols_change,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        actions = ft.Row(
            spacing=12,
            controls=[
                ft.ElevatedButton(
                    "Resolver",
                    on_click=self._handle_resolve,
                    style=ft.ButtonStyle(
                        bgcolor={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                        color={ft.ControlState.DEFAULT: colors.WHITE},
                        padding=ft.Padding(20, 12, 20, 12),
                        shape=ft.RoundedRectangleBorder(radius=14),
                    ),
                    expand=True,
                ),
                ft.OutlinedButton(
                    "Limpiar",
                    on_click=self._handle_clear,
                    style=ft.ButtonStyle(
                        side={ft.ControlState.DEFAULT: ft.border.BorderSide(1, PRIMARY_COLOR)},
                        color={ft.ControlState.DEFAULT: PRIMARY_COLOR},
                        padding=ft.Padding(20, 12, 20, 12),
                        shape=ft.RoundedRectangleBorder(radius=14),
                    ),
                    expand=True,
                ),
            ],
        )
        self._resolve_button = actions.controls[0]
        self._clear_button = actions.controls[1]

        self._stats_label = ft.Text(
            self._dimension_summary(),
            size=12,
            color=TEXT_MUTED,
        )

        content = ft.Column(
            spacing=18,
            expand=True,
            controls=[
                self._method_label,
                self._category_label,
                self._description_label,
                ft.Divider(color=BORDER_COLOR),
                self._rows_field,
                self._cols_field,
                self._stats_label,
                actions,
            ],
        )

        container = ft.Container(
            width=PANEL_WIDTH,
            bgcolor=SURFACE_COLOR,
            border=ft.border.only(left=ft.border.BorderSide(width=1, color=BORDER_COLOR)),
            padding=ft.Padding(24, 24, 24, 24),
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[content],
            ),
        )
        return container

    @property
    def view(self) -> ft.Control:
        return self._container

    # ------------------------------ Eventos ------------------------------
    def _handle_rows_blur(self, event: ft.ControlEvent) -> None:
        if self._updating_fields:
            return
        value = event.control.value if isinstance(event.control, ft.TextField) else str(self.rows)
        self.rows = self._parse_dimension(value, MIN_ROWS, MAX_ROWS, self.rows)
        self._set_field_value(self._rows_field, str(self.rows))
        self._notify_dimensions()

    def _handle_cols_blur(self, event: ft.ControlEvent) -> None:
        if self._updating_fields:
            return
        value = event.control.value if isinstance(event.control, ft.TextField) else str(self.cols)
        self.cols = self._parse_dimension(value, MIN_COLS, MAX_COLS, self.cols)
        self._set_field_value(self._cols_field, str(self.cols))
        self._notify_dimensions()

    def _handle_resolve(self, _event) -> None:
        if self._enabled and self._on_resolve:
            self._on_resolve()

    def _handle_clear(self, _event) -> None:
        if self._enabled and self._on_clear:
            self._on_clear()

    # ------------------------------ API pública ------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._apply_enabled_state()
        if self._container:
            self._safe_update(self._container)

    def set_dimensions(self, rows: int, cols: int) -> None:
        self.rows = clamp(rows, MIN_ROWS, MAX_ROWS)
        self.cols = clamp(cols, MIN_COLS, MAX_COLS)
        self._set_field_value(self._rows_field, str(self.rows))
        self._set_field_value(self._cols_field, str(self.cols))
        self._update_stats_label()
        if self._container:
            self._safe_update(self._container)

    def update_method(self, method: MethodInfo) -> None:
        self.method = method
        if self._method_label:
            self._method_label.value = method.label
            self._safe_update(self._method_label)
        if self._category_label:
            self._category_label.value = f"Configura los parámetros para: {method.label}"
            self._safe_update(self._category_label)
        if self._description_label:
            self._description_label.value = method.description
            self._safe_update(self._description_label)
        self.set_enabled(method.available)
        self._update_stats_label()

    # ------------------------------ Utilidades ------------------------------
    def _notify_dimensions(self) -> None:
        self._update_stats_label()
        if self._on_dimensions_change:
            self._on_dimensions_change(self.rows, self.cols)

    def _set_field_value(self, field: ft.TextField | None, value: str) -> None:
        if field is None:
            return
        if field.value == value:
            return
        self._updating_fields = True
        field.value = value
        self._safe_update(field)
        self._updating_fields = False

    def _handle_rows_change(self, event: ft.ControlEvent) -> None:
        if self._updating_fields or not isinstance(event.control, ft.TextField):
            return
        value = (event.control.value or "").strip()
        if not value:
            return
        if not value.isdigit():
            return
        parsed = clamp(int(value), MIN_ROWS, MAX_ROWS)
        if str(parsed) != value:
            self._set_field_value(self._rows_field, str(parsed))
        if parsed != self.rows:
            self.rows = parsed
            self._notify_dimensions()

    def _handle_cols_change(self, event: ft.ControlEvent) -> None:
        if self._updating_fields or not isinstance(event.control, ft.TextField):
            return
        value = (event.control.value or "").strip()
        if not value:
            return
        if not value.isdigit():
            return
        parsed = clamp(int(value), MIN_COLS, MAX_COLS)
        if str(parsed) != value:
            self._set_field_value(self._cols_field, str(parsed))
        if parsed != self.cols:
            self.cols = parsed
            self._notify_dimensions()

    def _apply_enabled_state(self) -> None:
        disabled = not self._enabled
        for field in (self._rows_field, self._cols_field):
            if field:
                field.disabled = disabled
                self._safe_update(field)
        if self._resolve_button:
            self._resolve_button.disabled = disabled
            self._safe_update(self._resolve_button)
        if self._clear_button:
            self._clear_button.disabled = disabled
            self._safe_update(self._clear_button)

    def _parse_dimension(self, value: str, minimum: int, maximum: int, fallback: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = fallback
        return clamp(parsed, minimum, maximum)

    def _dimension_summary(self) -> str:
        filas = pluralize(self.rows, "fila")
        columnas = pluralize(self.cols, "columna")
        return f"Actual: {filas}, {columnas} + término independiente"

    def _update_stats_label(self) -> None:
        if self._stats_label:
            self._stats_label.value = self._dimension_summary()
            self._safe_update(self._stats_label)

    # ------------------------------ Utilidad segura ------------------------------
    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control is not None:
                control.update()
        except AssertionError:
            # El control aún no está agregado a la página; ignorar actualización temprana.
            pass
