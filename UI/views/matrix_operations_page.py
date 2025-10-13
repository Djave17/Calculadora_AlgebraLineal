"""Vista para operaciones basicas entre matrices siguiendo la plantilla indicada."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QHeaderView,
)

from ViewModels.matrix_operations_vm import MatrixOperationsViewModel, OperationResult

from . import helpers


class MatrixOperationsPage(QWidget):
    """Permite sumar, restar, escalar y multiplicar matrices mostrando los pasos."""

    MAX_ROWS = 8
    MAX_COLS = 8
    MAX_MATRICES = 4

    def __init__(
        self,
        view_model: MatrixOperationsViewModel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._vm = view_model
        self._matrix_tables: List[QTableWidget] = []
        self._matrix2_rows_custom = False
        self._matrix2_cols_custom = False
        self._last_steps: List[str] = []
        self._last_title: str = ""

        self._build_ui()
        self._wire_events()
        self._update_matrix_count()
        self._sync_matrix2_spins()
        self._update_table_dimensions()

    # --------------------------- Construccion de la interfaz ---------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Operaciones con matrices")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Configura el tamano de las matrices y el numero de matrices a sumar. "
            "Selecciona la operacion deseada para ver los pasos detallados y la interpretacion."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        config_row = QHBoxLayout()
        config_row.setSpacing(12)

        config_row.addWidget(QLabel("Filas:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, self.MAX_ROWS)
        self.rows_spin.setValue(3)
        config_row.addWidget(self.rows_spin)

        config_row.addWidget(QLabel("Columnas:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, self.MAX_COLS)
        self.cols_spin.setValue(3)
        config_row.addWidget(self.cols_spin)

        config_row.addWidget(QLabel("Numero de matrices:"))
        self.matrices_spin = QSpinBox()
        self.matrices_spin.setRange(2, self.MAX_MATRICES)
        self.matrices_spin.setValue(2)
        config_row.addWidget(self.matrices_spin)

        self.matrix2_rows_label = QLabel("Filas matriz 2:")
        config_row.addWidget(self.matrix2_rows_label)
        self.matrix2_rows_spin = QSpinBox()
        self.matrix2_rows_spin.setRange(1, self.MAX_COLS)
        config_row.addWidget(self.matrix2_rows_spin)

        self.matrix2_cols_label = QLabel("Columnas matriz 2:")
        config_row.addWidget(self.matrix2_cols_label)
        self.matrix2_cols_spin = QSpinBox()
        self.matrix2_cols_spin.setRange(1, self.MAX_COLS)
        config_row.addWidget(self.matrix2_cols_spin)

        config_row.addStretch(1)
        layout.addLayout(config_row)

        self.matrices_group = QGroupBox("Matrices de entrada")
        matrices_layout = QHBoxLayout(self.matrices_group)
        matrices_layout.setContentsMargins(12, 12, 12, 12)
        matrices_layout.setSpacing(12)
        self._matrices_layout = matrices_layout
        layout.addWidget(self.matrices_group)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.scalar_label = QLabel("Escalar k:")
        buttons_row.addWidget(self.scalar_label)
        self.scalar_input = QLineEdit("1")
        self.scalar_input.setFixedWidth(80)
        buttons_row.addWidget(self.scalar_input)

        self.sum_button = QPushButton("Sumar")
        self.sum_button.setFixedHeight(32)
        buttons_row.addWidget(self.sum_button)

        self.subtract_button = QPushButton("Restar")
        self.subtract_button.setFixedHeight(32)
        buttons_row.addWidget(self.subtract_button)

        self.scalar_button = QPushButton("k * A")
        self.scalar_button.setFixedHeight(32)
        buttons_row.addWidget(self.scalar_button)

        self.multiply_button = QPushButton("Producto AB")
        self.multiply_button.setFixedHeight(32)
        buttons_row.addWidget(self.multiply_button)

        self.steps_button = QPushButton("Ver pasos detallados")
        self.steps_button.setFixedHeight(32)
        self.steps_button.setEnabled(False)
        buttons_row.addWidget(self.steps_button)

        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setFixedHeight(32)
        buttons_row.addWidget(self.clear_button)

        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        self.result_box = QGroupBox("Interpretacion y pasos")
        result_layout = QVBoxLayout(self.result_box)
        result_layout.setContentsMargins(12, 12, 12, 12)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setMinimumHeight(220)
        self.result_output.setStyleSheet("background-color: #ffffff; color: #000000;")
        result_layout.addWidget(self.result_output)
        layout.addWidget(self.result_box, stretch=1)

    # ------------------------------ Conexion de eventos ------------------------------
    def _wire_events(self) -> None:
        self.rows_spin.valueChanged.connect(self._on_base_rows_changed)
        self.cols_spin.valueChanged.connect(self._on_base_cols_changed)
        self.matrices_spin.valueChanged.connect(self._on_matrix_count_changed)

        self.sum_button.clicked.connect(self._handle_sum)
        self.subtract_button.clicked.connect(self._handle_subtract)
        self.scalar_button.clicked.connect(self._handle_scalar)
        self.multiply_button.clicked.connect(self._handle_multiply)
        self.clear_button.clicked.connect(self._handle_clear)
        self.steps_button.clicked.connect(self._handle_show_steps)
        self.matrix2_rows_spin.valueChanged.connect(self._on_matrix2_rows_changed)
        self.matrix2_cols_spin.valueChanged.connect(self._on_matrix2_cols_changed)

    # ------------------------------- Manejadores -------------------------------
    def _handle_sum(self) -> None:
        try:
            matrices = self._collect_all_matrices()
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        result = self._vm.add_multiple(matrices)
        titulo = "Suma de matrices"
        self._display_result(titulo, matrices, result)

    def _handle_subtract(self) -> None:
        if self.matrices_spin.value() != 2:
            QMessageBox.warning(
                self,
                "Dimensiones invalidas",
                "Para la resta deben capturarse exactamente dos matrices.",
            )
            return
        try:
            matrices = self._collect_all_matrices()
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        A_rows, B_rows = matrices[0], matrices[1]
        result = self._vm.subtract(A_rows, B_rows)
        titulo = "Resta A - B"
        self._display_result(titulo, matrices[:2], result)

    def _handle_scalar(self) -> None:
        try:
            A_rows = helpers.table_to_matrix(self._matrix_tables[0])
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        try:
            result = self._vm.scalar_multiply(self.scalar_input.text(), A_rows)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        titulo = "Multiplicacion escalar k * A"
        self._display_result(titulo, [A_rows], result)

    def _handle_multiply(self) -> None:
        if self.matrices_spin.value() != 2:
            QMessageBox.warning(
                self,
                "Dimensiones invalidas",
                "Para el producto AB deben capturarse exactamente dos matrices.",
            )
            return
        if not self._matrix2_rows_custom:
            self.matrix2_rows_spin.blockSignals(True)
            self.matrix2_rows_spin.setValue(self.cols_spin.value())
            self.matrix2_rows_spin.blockSignals(False)
            self._update_table_dimensions()
        try:
            matrices = self._collect_all_matrices()
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        A_rows, B_rows = matrices[0], matrices[1]
        result = self._vm.multiply(A_rows, B_rows)
        titulo = "Producto AB"
        self._display_result(titulo, matrices[:2], result)

    def _handle_clear(self) -> None:
        for table in self._matrix_tables:
            helpers.fill_table_with_zero(table)
        self.scalar_input.setText("1")
        self.result_output.clear()
        self._last_steps = []
        self._last_title = ""
        self.steps_button.setEnabled(False)

    def _handle_show_steps(self) -> None:
        if not self._last_steps:
            return
        QMessageBox.information(
            self,
            self._last_title or "Pasos detallados",
            "\n".join(self._last_steps),
        )

    # ------------------------------- Utilidades internas -------------------------------
    def _on_base_rows_changed(self, value: int) -> None:
        self._sync_matrix2_spins()
        self._update_table_dimensions()

    def _on_base_cols_changed(self, value: int) -> None:
        self._sync_matrix2_spins()
        self._update_table_dimensions()

    def _on_matrix2_rows_changed(self, value: int) -> None:
        if self.matrices_spin.value() == 2:
            self._matrix2_rows_custom = True
        self._update_table_dimensions()

    def _on_matrix2_cols_changed(self, value: int) -> None:
        if self.matrices_spin.value() == 2:
            self._matrix2_cols_custom = True
        self._update_table_dimensions()

    def _sync_matrix2_spins(self) -> None:
        visible = self.matrices_spin.value() == 2
        for widget in (
            self.matrix2_rows_label,
            self.matrix2_rows_spin,
            self.matrix2_cols_label,
            self.matrix2_cols_spin,
        ):
            widget.setVisible(visible)

        if not visible:
            return

        if not self._matrix2_rows_custom:
            self.matrix2_rows_spin.blockSignals(True)
            self.matrix2_rows_spin.setValue(self.rows_spin.value())
            self.matrix2_rows_spin.blockSignals(False)

        if not self._matrix2_cols_custom:
            self.matrix2_cols_spin.blockSignals(True)
            self.matrix2_cols_spin.setValue(self.cols_spin.value())
            self.matrix2_cols_spin.blockSignals(False)

    def _on_matrix_count_changed(self) -> None:
        self._update_matrix_count()
        if self.matrices_spin.value() != 2:
            self._matrix2_rows_custom = False
            self._matrix2_cols_custom = False
        self._sync_matrix2_spins()
        self._update_table_dimensions()

    def _update_matrix_count(self) -> None:
        desired = self.matrices_spin.value()
        current = len(self._matrix_tables)

        if desired < current:
            for _ in range(current - desired):
                table = self._matrix_tables.pop()
                widget = table.parentWidget()
                if widget:
                    self._matrices_layout.removeWidget(widget)
                    widget.setParent(None)
            return

        for index in range(current, desired):
            group = QGroupBox(f"Matriz {index + 1}")
            group_layout = QVBoxLayout(group)
            table = QTableWidget()
            table.setEditTriggers(QAbstractItemView.AllEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            group_layout.addWidget(table)
            self._matrices_layout.addWidget(group)
            self._matrix_tables.append(table)

    def _update_table_dimensions(self) -> None:
        base_rows = self.rows_spin.value()
        base_cols = self.cols_spin.value()
        matrix2_rows = self.matrix2_rows_spin.value()
        matrix2_cols = self.matrix2_cols_spin.value()

        for index, table in enumerate(self._matrix_tables):
            if index == 0:
                rows = base_rows
                cols = base_cols
            elif index == 1 and self.matrices_spin.value() == 2:
                rows = matrix2_rows
                cols = matrix2_cols
            else:
                rows = base_rows
                cols = base_cols

            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels([f"c{j + 1}" for j in range(cols)])
            helpers.ensure_table_defaults(table)

    def _collect_all_matrices(self) -> List[List[List[Fraction]]]:
        matrices: List[List[List[Fraction]]] = []
        for table in self._matrix_tables:
            matrices.append(helpers.table_to_matrix(table))
        return matrices

    def _display_result(
        self,
        titulo: str,
        matrices: Sequence[Sequence[Sequence]],
        result: OperationResult,
    ) -> None:
        self._last_steps = result.steps
        self._last_title = titulo
        self.steps_button.setEnabled(bool(result.steps))

        lines: List[str] = [titulo, ""]
        for idx, matriz in enumerate(matrices, start=1):
            lines.append(f"Matriz {idx}:")
            lines.extend(helpers.matrix_lines(matriz, indent="  "))
            lines.append("")

        compat_text = (
            "La operacion es compatible con las dimensiones ingresadas."
            if result.compatible
            else "La operacion no es compatible con las dimensiones ingresadas."
        )
        lines.append(compat_text)
        lines.append("")
        lines.extend(result.steps)

        if result.result_matrix is not None:
            lines.append("")
            lines.append("Resultado:")
            lines.extend(helpers.matrix_lines(result.result_matrix, indent="  "))

        self.result_output.setPlainText("\n".join(lines).strip())
