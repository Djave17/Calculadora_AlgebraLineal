from __future__ import annotations

from typing import Optional

import flet as ft

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel

from ..helpers import clamp
from ..methods import METHOD_CATEGORIES, MethodCategory, MethodInfo, find_method, first_available_method
from ..styles import BACKGROUND_COLOR, PANEL_WIDTH, PRIMARY_COLOR, SURFACE_COLOR
from .components import (
    LeftMethodsMenu,
    MatrixEditor,
    MatrixEquationView,
    MerNotesView,
    RightConfigPanel,
    VectorPropertiesView,
)
from .components.steps_dialog import show_steps_dialog


class MainShell:
    MIN_ROWS = 2
    MAX_ROWS = 8
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

        self.view_model.rows = clamp(max(self.view_model.rows, self.DEFAULT_ROWS), self.MIN_ROWS, self.MAX_ROWS)
        self.view_model.cols = clamp(max(self.view_model.cols, self.DEFAULT_COLS), self.MIN_COLS, self.MAX_COLS)
        self._config_visible = True

        self._left_menu: Optional[LeftMethodsMenu] = None
        self._matrix_editor: Optional[MatrixEditor] = None
        self._matrix_editors: dict[str, tuple[MatrixCalculatorViewModel, MatrixEditor]] = {}
        self._matrix_equation_view: Optional[MatrixEquationView] = None
        self._vector_properties_view: Optional[VectorPropertiesView] = None
        self._mer_view: Optional[MerNotesView] = None

        self._config_panel: Optional[RightConfigPanel] = None
        self._config_container: Optional[ft.Container] = None
        self._center_container: Optional[ft.Container] = None
        self._root: Optional[ft.Column] = None

        self._root = self._build()
        self._activate_method(self.active_method)

    def _build(self) -> ft.Column:
        self._left_menu = LeftMethodsMenu(
            categories=self.categories,
            active_method_id=self.active_method.id,
            on_method_selected=self._handle_method_selected,
        )

        initial_vm, initial_editor = self._ensure_matrix_editor(self.active_method)
        self.view_model = initial_vm
        self._matrix_editor = initial_editor

        self._config_panel = RightConfigPanel(
            rows=initial_vm.rows,
            cols=initial_vm.cols,
            method=self.active_method,
            on_dimensions_change=self._handle_dimensions_change,
            on_resolve=self._handle_resolve,
            on_clear=self._handle_clear,
        )

        self._config_container = ft.Container(
            col={"xs": 12, "md": 12, "lg": 3},
            bgcolor=SURFACE_COLOR,
            padding=ft.Padding(0, 0, 0, 0),
            animate=ft.Animation(300, "ease"),
            content=self._config_panel.view,
            visible=self._config_visible,
        )

        self._center_container = ft.Container(
            col={"xs": 12, "md": 12, "lg": 6},
            expand=True,
        )

        body = ft.ResponsiveRow(
            expand=True,
            spacing=16,
            run_spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(col={"xs": 12, "md": 4, "lg": 3}, content=self._left_menu.view),
                self._center_container,
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
        if not self._config_container or self.active_method.view_type != "matrix_solver":
            return
        self._config_visible = not self._config_visible
        self._config_container.visible = self._config_visible
        self._safe_update(self._config_container)

    def _handle_method_selected(self, method_id: str) -> None:
        match = find_method(method_id)
        if match is None:
            return
        category, method = match
        self.active_category = category
        self.active_method = method
        self._activate_method(method)

    def _handle_dimensions_change(self, rows: int, cols: int) -> None:
        if self.active_method.view_type != "matrix_solver":
            return
        rows = clamp(rows, self.MIN_ROWS, self.MAX_ROWS)
        cols = clamp(cols, self.MIN_COLS, self.MAX_COLS)
        self.view_model.rows = rows
        self.view_model.cols = cols
        if self._matrix_editor:
            self._matrix_editor.set_dimensions(rows, cols)
        if self._config_panel:
            self._config_panel.set_dimensions(rows, cols)

    def _handle_resolve(self) -> None:
        if self.active_method.view_type != "matrix_solver":
            return
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
        if self.active_method.view_type != "matrix_solver":
            return
        default_rows = clamp(self.active_method.default_rows, self.MIN_ROWS, self.MAX_ROWS)
        default_cols = clamp(self.active_method.default_cols, self.MIN_COLS, self.MAX_COLS)
        self.view_model.rows = default_rows
        self.view_model.cols = default_cols
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

    # ------------------------------ Gestión de vistas ------------------------------
    def _ensure_matrix_editor(self, method: MethodInfo) -> tuple[MatrixCalculatorViewModel, MatrixEditor]:
        if method.id not in self._matrix_editors:
            vm = MatrixCalculatorViewModel()
            vm.rows = clamp(method.default_rows, self.MIN_ROWS, self.MAX_ROWS)
            vm.cols = clamp(method.default_cols, self.MIN_COLS, self.MAX_COLS)
            editor = MatrixEditor(
                page=self.page,
                rows=vm.rows,
                cols=vm.cols,
                method=method,
                on_request_steps=self._handle_show_steps,
                on_toggle_settings=self._toggle_config_panel,
            )
            self._matrix_editors[method.id] = (vm, editor)
        vm, editor = self._matrix_editors[method.id]
        vm.method = method.id
        return vm, editor

    def _ensure_matrix_equation_view(self) -> MatrixEquationView:
        if self._matrix_equation_view is None:
            vm = MatrixCalculatorViewModel()
            vm.rows = clamp(self.DEFAULT_ROWS, self.MIN_ROWS, self.MAX_ROWS)
            vm.cols = clamp(self.DEFAULT_COLS, self.MIN_COLS, self.MAX_COLS)
            self._matrix_equation_view = MatrixEquationView(self.page, vm, self._handle_show_steps)
        return self._matrix_equation_view

    def _ensure_vector_properties_view(self) -> VectorPropertiesView:
        if self._vector_properties_view is None:
            from ViewModels.linear_algebra_vm import LinearAlgebraViewModel

            self._vector_properties_view = VectorPropertiesView(self.page, LinearAlgebraViewModel())
        return self._vector_properties_view

    def _ensure_mer_view(self) -> MerNotesView:
        if self._mer_view is None:
            self._mer_view = MerNotesView()
        return self._mer_view

    def _activate_method(self, method: MethodInfo) -> None:
        if self._left_menu:
            self._left_menu.set_active_method(method.id)

        # Conmutar entre tipos de vista de forma segura y sin variables no definidas
        if method.view_type == "matrix_solver":
            vm, editor = self._ensure_matrix_editor(method)
            self.view_model = vm
            self.view_model.method = method.id
            self._matrix_editor = editor
            self._matrix_editor.update_method(method)
            self._matrix_editor.update_method_category(self.active_category.label)

            if self._center_container:
                self._center_container.content = editor.view
                self._safe_update(self._center_container)
            if self._config_panel:
                self._config_panel.set_dimensions(vm.rows, vm.cols)
                self._config_panel.update_method(method)
            if self._config_container:
                self._config_container.visible = self._config_visible
                self._safe_update(self._config_container)

        elif method.view_type == "matrix_equation":
            view = self._ensure_matrix_equation_view()
            if self._center_container:
                self._center_container.content = view.view
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.visible = False
                self._safe_update(self._config_container)

        elif method.view_type == "vector_properties":
            view = self._ensure_vector_properties_view()
            if self._center_container:
                self._center_container.content = view.view
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.visible = False
                self._safe_update(self._config_container)

        elif method.view_type == "mer_notes":
            view = self._ensure_mer_view()
            if self._center_container:
                self._center_container.content = view.view
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.visible = False
                self._safe_update(self._config_container)

        else:
            if self._center_container:
                self._center_container.content = None
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.visible = False
                self._safe_update(self._config_container)

    def _safe_update(self, control: Optional[ft.Control]) -> None:
        try:
            if control and control.page:
                control.update()
        except AssertionError:
            pass
