from __future__ import annotations

from typing import Optional

import flet as ft

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel

from ..helpers import clamp
from ..methods import METHOD_CATEGORIES, MethodCategory, MethodInfo, find_method, first_available_method
from ..styles import (
    BACKGROUND_COLOR,
    PANEL_WIDTH,
    PRIMARY_COLOR,
    SURFACE_COLOR,
)
from .components import LeftMethodsMenu, MatrixEditor, RightConfigPanel
from .components.steps_dialog import show_steps_dialog


class MainShell:
    MIN_ROWS = 2
    MAX_ROWS = 10
    MIN_COLS = 3
    MAX_COLS = 12
    DEFAULT_ROWS = 3
    DEFAULT_COLS = 3

    def __init__(
        self,
        page: ft.Page,
        view_model: MatrixCalculatorViewModel,
        categories: tuple[MethodCategory, ...] = METHOD_CATEGORIES,
    ) -> None:
        self.page = page
        self.view_model = view_model
        self.categories = categories

        category, method = first_available_method()
        self.active_category: MethodCategory = category
        self.active_method: MethodInfo = method
        # Garantizar dimensiones iniciales dentro de los límites y con un tamaño cómodo por defecto.
        self.view_model.rows = clamp(max(self.view_model.rows, self.DEFAULT_ROWS), self.MIN_ROWS, self.MAX_ROWS)
        self.view_model.cols = clamp(max(self.view_model.cols, self.DEFAULT_COLS), self.MIN_COLS, self.MAX_COLS)
        self._config_visible = True

        self._left_menu: Optional[LeftMethodsMenu] = None
        self._matrix_editor: Optional[MatrixEditor] = None
        self._config_panel: Optional[RightConfigPanel] = None
        self._config_container: Optional[ft.AnimatedContainer] = None
        self._root: Optional[ft.Column] = None

        self._root = self._build()

    def _build(self) -> ft.Column:

        self._left_menu = LeftMethodsMenu(
            categories=self.categories,
            active_method_id=self.active_method.id,
            on_method_selected=self._handle_method_selected,
        )

        self._matrix_editor = MatrixEditor(
            on_toggle_settings=self._toggle_config_panel,
            page=self.page,
            rows=self.view_model.rows,
            cols=self.view_model.cols,
            method=self.active_method,
            on_request_steps=self._handle_show_steps,
        )

        self._config_panel = RightConfigPanel(
            rows=self.view_model.rows,
            cols=self.view_model.cols,
            method=self.active_method,
            on_dimensions_change=self._handle_dimensions_change,
            on_resolve=self._handle_resolve,
            on_clear=self._handle_clear,
        )

        self._config_container = ft.Container(
            width=PANEL_WIDTH,
            content=self._config_panel.view,
            animate=ft.Animation(300, "ease"),
            bgcolor=SURFACE_COLOR,
        )

        body = ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                self._left_menu.view,
                ft.Container(expand=True, content=self._matrix_editor.view),
                self._config_container,
            ],
        )

        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=BACKGROUND_COLOR,
                    content=body,
                ),
            ],
        )

    @property
    def view(self) -> ft.Control:
        return self._root

    # ------------------------------ Eventos ------------------------------
    def _toggle_config_panel(self) -> None:
        if not self._config_container:
            return
        self._config_visible = not self._config_visible
        self._config_container.width = PANEL_WIDTH if self._config_visible else 0
        self._config_container.update()

    def _handle_method_selected(self, method_id: str) -> None:
        match = find_method(method_id)
        if match is None:
            return
        category, method = match
        self.active_category = category
        self.active_method = method
        self.view_model.method = method.id
        if self._left_menu:
            self._left_menu.set_active_method(method.id)
        if self._matrix_editor:
            self._matrix_editor.update_method(method)
            self._matrix_editor.update_method_category(category.label)
        if self._config_panel:
            self._config_panel.update_method(method)
        if not method.available:
            self._show_snackbar("Este método aún no está disponible. Usa Gauss-Jordan para resolver.")

    def _handle_dimensions_change(self, rows: int, cols: int) -> None:
        rows = clamp(rows, self.MIN_ROWS, self.MAX_ROWS)
        cols = clamp(cols, self.MIN_COLS, self.MAX_COLS)
        self.view_model.rows = rows
        self.view_model.cols = cols
        if self._matrix_editor:
            self._matrix_editor.set_dimensions(rows, cols)
        if self._config_panel:
            self._config_panel.set_dimensions(rows, cols)

    def _handle_resolve(self) -> None:
        if not self.active_method.available:
            self._show_snackbar("El método seleccionado no tiene resolución interactiva todavía.")
            return
        if not self._matrix_editor:
            return
        try:
            augmented = self._matrix_editor.get_augmented_matrix()
        except ValueError as exc:
            self._show_snackbar(str(exc), error=True)
            return
        try:
            result = self.view_model.solve(augmented)
        except Exception as exc:  # pragma: no cover - propagación defensiva
            self._show_snackbar(str(exc), error=True)
            return
        self._matrix_editor.show_result(result)

    def _handle_clear(self) -> None:
        self.view_model.rows = self.DEFAULT_ROWS
        self.view_model.cols = self.DEFAULT_COLS
        if self._config_panel:
            self._config_panel.set_dimensions(self.view_model.rows, self.view_model.cols)
        if self._matrix_editor:
            self._matrix_editor.set_dimensions(self.view_model.rows, self.view_model.cols)
            self._matrix_editor.clear_matrix()

    def _handle_show_steps(self, steps, pivot_cols) -> None:
        show_steps_dialog(self.page, steps, pivot_cols)

    # ------------------------------ Utilidades ------------------------------
    def _show_snackbar(self, message: str, error: bool = False) -> None:
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=PRIMARY_COLOR if not error else "#f77373",
        )
        self.page.snack_bar.open = True
        self.page.update()
