from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import flet as ft
from flet import Icons as icons

from ...methods import MethodInfo
from ...styles import SURFACE_COLOR, BORDER_COLOR, PRIMARY_COLOR, TEXT_DARK, TEXT_MUTED
from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel
from .matrix_editor import MatrixEditor
from .custom_config_panels import MatrixIdentitiesConfigPanel


@dataclass
class ModeConfig:
    method: MethodInfo
    rows_label: str
    cols_label: str
    description: str
    default_rows: int
    default_cols: int


class MatrixIdentitiesView:
    """Vista unificada para AX = B, combinacion lineal y sistema homogeneo."""

    def __init__(
        self,
        page: ft.Page,
        view_model: MatrixCalculatorViewModel,
        on_show_steps,
    ) -> None:
        self._page = page
        self._view_model = view_model
        self._on_show_steps = on_show_steps

        self._modes: Dict[str, ModeConfig] = {
            "ax_b": ModeConfig(
                method=MethodInfo(
                    id="identities_axb",
                    label="Ecuacion AX = B",
                    icon="TABLE_ROWS",
                    available=True,
                    description="Resuelve A*x = b registrando pasos Gauss-Jordan.",
                    category="Identidades de matrices",
                    analysis_context=None,
                    force_homogeneous=False,
                    variable_prefix="x",
                ),
                rows_label="Filas (m)",
                cols_label="Columnas de A (n)",
                description="Cada columna de A corresponde a una variable xi; la ultima columna es el vector b.",
                default_rows=3,
                default_cols=3,
            ),
            "combination": ModeConfig(
                method=MethodInfo(
                    id="identities_combination",
                    label="Combinacion lineal",
                    icon="FUNCTIONS",
                    available=True,
                    description="Determina si b pertenece al span de {v1,...,vk}.",
                    category="Identidades de matrices",
                    analysis_context="combination",
                    force_homogeneous=False,
                    variable_prefix="c",
                ),
                rows_label="Dimension (n)",
                cols_label="Numero de vectores (k)",
                description="Introduce los vectores generadores como columnas y b en la ultima columna.",
                default_rows=3,
                default_cols=2,
            ),
            "homogeneous": ModeConfig(
                method=MethodInfo(
                    id="identities_homogeneous",
                    label="Sistema homogeneo A*c = 0",
                    icon="HUB",
                    available=True,
                    description="Verifica independencia lineal y soluciones no triviales.",
                    category="Identidades de matrices",
                    analysis_context="dependence",
                    force_homogeneous=True,
                    variable_prefix="c",
                ),
                rows_label="Filas (m)",
                cols_label="Columnas de A (n)",
                description="La ultima columna se mantiene en 0; identifica soluciones no triviales.",
                default_rows=3,
                default_cols=3,
            ),
        }

        self._mode = "ax_b"
        self._mode_dimensions: Dict[str, Tuple[int, int]] = {
            key: (cfg.default_rows, cfg.default_cols) for key, cfg in self._modes.items()
        }

        current_cfg = self._modes[self._mode]
        self._view_model.rows = current_cfg.default_rows
        self._view_model.cols = current_cfg.default_cols

        self._matrix_editor = MatrixEditor(
            page=self._page,
            rows=current_cfg.default_rows,
            cols=current_cfg.default_cols,
            method=current_cfg.method,
            on_request_steps=self._on_show_steps,
        )
        self._matrix_editor.update_method_category("Identidades de matrices")

        self._info_text = ft.Text(current_cfg.description, size=12, color=TEXT_MUTED)

        self._mode_buttons = ft.SegmentedButton(
            selected={self._mode},
            allow_empty_selection=False,
            segments=[
                ft.Segment(value="ax_b", label=ft.Text("AX = B"), icon=ft.Icon(icons.TABLE_ROWS)),
                ft.Segment(value="combination", label=ft.Text("Combinacion"), icon=ft.Icon(icons.FUNCTIONS)),
                ft.Segment(value="homogeneous", label=ft.Text("A*c = 0"), icon=ft.Icon(icons.HUB)),
            ],
            on_change=self._handle_mode_change,
        )

        self._config_panel = MatrixIdentitiesConfigPanel(
            current_cfg.method,
            on_dimensions_change=self._handle_dimensions_change,
            on_resolve=self._handle_resolve,
            on_clear=self._handle_clear,
        )
        self._config_panel.set_values(current_cfg.default_rows, current_cfg.default_cols)
        self._config_panel.set_labels(current_cfg.rows_label, current_cfg.cols_label)

        self._root = self._build()

    def _build(self) -> ft.Control:
        header = ft.Column(
            spacing=4,
            controls=[
                ft.Text("Identidades de matrices", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Explora AX = B, combinacion lineal y sistemas homogeneos con la misma matriz aumentada.",
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        )

        card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border_radius=20,
            padding=ft.Padding(20, 20, 20, 20),
            border=ft.border.all(1, color=BORDER_COLOR),
            content=ft.Column(
                spacing=16,
                controls=[
                    self._mode_buttons,
                    self._info_text,
                    self._matrix_editor.view,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            padding=ft.Padding(16, 0, 16, 0),
            content=ft.Column(
                expand=True,
                spacing=18,
                controls=[header, card],
            ),
        )

    @property
    def view(self) -> ft.Control:
        return self._root

    @property
    def config_view(self) -> ft.Control:
        return self._config_panel.view

    # ---------------------- Mode management ----------------------
    def _handle_mode_change(self, event: ft.ControlEvent) -> None:
        selected = self._extract_selected_mode(
            getattr(event.control, "selected", None) if event and event.control else None
        )
        if selected is None and event and event.control:
            selected = self._extract_selected_mode(getattr(event.control, "value", None))
        self._switch_mode(selected or self._mode)

    def _switch_mode(self, mode: str) -> None:
        if mode not in self._modes or mode == self._mode:
            return
        self._mode = mode
        cfg = self._modes[self._mode]
        if self._mode_buttons:
            self._mode_buttons.selected = {self._mode}
            self._safe_update(self._mode_buttons)
        self._config_panel.set_method(cfg.method)
        self._config_panel.set_labels(cfg.rows_label, cfg.cols_label)
        self._info_text.value = cfg.description
        self._safe_update(self._info_text)
        rows, cols = self._mode_dimensions.get(self._mode, (cfg.default_rows, cfg.default_cols))
        self._apply_dimensions(rows, cols, update_panel=True)
        self._matrix_editor.update_method(cfg.method)
        self._matrix_editor.update_method_category("Identidades de matrices")

    def _apply_dimensions(self, rows: int, cols: int, update_panel: bool = False) -> None:
        rows = max(1, min(8, rows))
        cols = max(1, min(12, cols))
        self._mode_dimensions[self._mode] = (rows, cols)
        self._view_model.rows = rows
        self._view_model.cols = cols
        self._matrix_editor.set_dimensions(rows, cols)
        if update_panel:
            self._config_panel.set_values(rows, cols)

    # ---------------------- Callbacks ----------------------
    def _handle_dimensions_change(self, rows: int, cols: int) -> None:
        cfg = self._modes[self._mode]
        rows = max(cfg.default_rows if rows <= 0 else rows, 1)
        self._apply_dimensions(rows, cols)

    def _handle_resolve(self) -> None:
        try:
            augmented = self._matrix_editor.get_augmented_matrix()
        except ValueError as exc:
            self._show_error(str(exc))
            return
        try:
            result = self._view_model.solve(augmented)
        except Exception as exc:
            self._show_error(str(exc))
            return
        self._matrix_editor.show_result(result)

    def _handle_clear(self) -> None:
        cfg = self._modes[self._mode]
        rows, cols = cfg.default_rows, cfg.default_cols
        self._apply_dimensions(rows, cols, update_panel=True)
        self._matrix_editor.clear_matrix()

    # ---------------------- Public API ----------------------
    def parameters(self) -> Tuple[int, int]:
        return self._mode_dimensions[self._mode]

    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode in self._modes and mode != self._mode:
            self._mode_buttons.selected = {mode}
            self._safe_update(self._mode_buttons)
            self._switch_mode(mode)

    def _show_error(self, message: str) -> None:
        self._page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#f48f8f")
        self._page.snack_bar.open = True
        self._page.update()

    def _safe_update(self, control: ft.Control | None) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass

    def _extract_selected_mode(self, raw_value: Iterable[str] | str | None) -> str | None:
        if isinstance(raw_value, (set, tuple, list)):
            return next(iter(raw_value), None)
        return str(raw_value) if raw_value else None
