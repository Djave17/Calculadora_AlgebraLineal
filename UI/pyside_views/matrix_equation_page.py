"""Resolución de ecuaciones matriciales AX = B con múltiples columnas.

La página replica la metodología propuesta por Strang (2016, cap. 3):
resolver AX = B columna a columna empleando eliminación de Gauss–Jordan
sobre cada vector independiente.
"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ViewModels.matrix_equation_vm import MatrixEquationViewModel
from ViewModels.resolucion_matriz_vm import MatrixEquationResultVM

from . import dialogs, helpers


class MatrixEquationPage(QWidget):
    """UI especializada para estudiar varias ecuaciones AX = b de forma paralela."""

    def __init__(
        self,
        view_model: MatrixEquationViewModel,
        parent: QWidget | None = None,
        max_rows: int = 10,
        max_cols: int = 12,
    ) -> None:
        super().__init__(parent)
        self._vm = view_model
        self._max_rows = max_rows
        self._max_cols = max_cols
        self._last_result: Optional[MatrixEquationResultVM] = None

        self._build_ui()
        self._wire_events()
        self._update_tables()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Ecuación matricial AX = B")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel(
            "Introduce la matriz A y la matriz B. El sistema resuelve AX = B "
            "columna a columna y explica el tipo de solución en cada caso."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Filas de A:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, self._max_rows)
        self.rows_spin.setValue(3)
        config_row.addWidget(self.rows_spin)

        config_row.addSpacing(10)
        config_row.addWidget(QLabel("Columnas (n):"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, self._max_cols)
        self.cols_spin.setValue(3)
        config_row.addWidget(self.cols_spin)

        config_row.addSpacing(10)
        config_row.addWidget(QLabel("Filas de B:"))
        self.b_rows_spin = QSpinBox()
        self.b_rows_spin.setRange(1, self._max_rows)
        self.b_rows_spin.setValue(3)
        config_row.addWidget(self.b_rows_spin)

        config_row.addSpacing(10)
        config_row.addWidget(QLabel("Columnas de B:"))
        self.b_cols_spin = QSpinBox()
        self.b_cols_spin.setRange(1, self._max_cols)
        self.b_cols_spin.setValue(1)
        config_row.addWidget(self.b_cols_spin)

        config_row.addStretch(1)
        layout.addLayout(config_row)

        matrices_row = QHBoxLayout()

        A_group = QGroupBox("Matriz A")
        A_layout = QVBoxLayout(A_group)
        self.A_table = QTableWidget()
        self.A_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.A_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.A_table.verticalHeader().setVisible(False)
        A_layout.addWidget(self.A_table)
        matrices_row.addWidget(A_group, stretch=3)

        B_group = QGroupBox("Matriz B")
        B_layout = QVBoxLayout(B_group)
        self.B_table = QTableWidget()
        self.B_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.B_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.B_table.verticalHeader().setVisible(False)
        B_layout.addWidget(self.B_table)
        matrices_row.addWidget(B_group, stretch=2)

        layout.addLayout(matrices_row)

        button_row = QHBoxLayout()
        self.solve_button = QPushButton("Resolver AX = B")
        self.steps_selector = QComboBox()
        self.steps_selector.setEnabled(False)
        self.steps_button = QPushButton("Ver pasos columna")
        self.steps_button.setEnabled(False)
        self.clear_button = QPushButton("Limpiar")
        button_row.addWidget(self.solve_button)
        button_row.addWidget(self.steps_selector)
        button_row.addWidget(self.steps_button)
        button_row.addWidget(self.clear_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setMinimumHeight(260)
        layout.addWidget(self.result_output)

    def _wire_events(self) -> None:
        self.rows_spin.valueChanged.connect(self._update_tables)
        self.cols_spin.valueChanged.connect(self._update_tables)
        self.b_rows_spin.valueChanged.connect(self._update_tables)
        self.b_cols_spin.valueChanged.connect(self._update_tables)
        self.solve_button.clicked.connect(self._on_solve)
        self.steps_button.clicked.connect(self._on_show_steps)
        self.clear_button.clicked.connect(self._on_clear)

    # --------------------------- Acciones principales ----------------------------
    def _update_tables(self) -> None:
        rows_a = self.rows_spin.value()
        rows_b = self.b_rows_spin.value()
        cols = self.cols_spin.value()
        rhs = self.b_cols_spin.value()

        self.A_table.blockSignals(True)
        self.A_table.setRowCount(rows_a)
        self.A_table.setColumnCount(cols)
        self.A_table.setHorizontalHeaderLabels([f"x{j + 1}" for j in range(cols)])
        helpers.ensure_table_defaults(self.A_table)
        self.A_table.blockSignals(False)

        self.B_table.blockSignals(True)
        self.B_table.setRowCount(rows_b)
        self.B_table.setColumnCount(rhs)
        self.B_table.setHorizontalHeaderLabels([f"b{j + 1}" for j in range(rhs)])
        helpers.ensure_table_defaults(self.B_table)
        self.B_table.blockSignals(False)

    def _on_solve(self) -> None:
        self._last_result = None
        try:
            A_rows = helpers.table_to_matrix(self.A_table)
            B_rows = helpers.table_to_matrix(self.B_table)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        if len(A_rows) != len(B_rows):
            QMessageBox.critical(
                self,
                "Dimensión incompatible",
                "La matriz B debe tener la misma cantidad de filas que A.",
            )
            return

        try:
            resultado = self._vm.resolver(A_rows, B_rows)
            self._last_result = resultado
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        var_labels = [f"x{j + 1}" for j in range(self.cols_spin.value())]
        lines: List[str] = []
        lines.append("Matriz A ingresada:")
        lines.extend(helpers.matrix_lines(A_rows, indent="  "))
        lines.append("")
        lines.append("Matriz B ingresada:")
        lines.extend(helpers.matrix_lines(B_rows, indent="  "))
        lines.append("")
        is_homogeneous = all(all(value == 0 for value in row) for row in B_rows)
        lines.append("AX = 0 (sistema homogéneo)" if is_homogeneous else "AX = b (sistema no homogéneo)")
        is_consistent = resultado.status in ("UNICA", "INFINITAS")
        lines.append("Sistema consistente." if is_consistent else "Sistema inconsistente.")
        summary_line = self._summarize_trivial_solution(resultado, is_homogeneous)
        if summary_line:
            lines.append(summary_line)
        lines.append(f"Estado global: {helpers.status_to_text(resultado.status)}")
        lines.append("")

        for column in resultado.columns:
            lines.append(f"Columna {column.label}: {helpers.status_to_text(column.result.status)}")
            lines.extend(helpers.format_result_lines(column.result, var_labels, indent="  ", homogeneous=is_homogeneous))
            lines.extend(helpers.format_steps_lines(column.result, indent="  "))
            lines.append("")

        self.result_output.setPlainText("\n".join(lines).strip())
        self._populate_steps_selector(resultado)

    def _on_clear(self) -> None:
        helpers.fill_table_with_zero(self.A_table)
        helpers.fill_table_with_zero(self.B_table)
        self.result_output.clear()
        self.steps_selector.clear()
        self.steps_selector.setEnabled(False)
        self.steps_button.setEnabled(False)
        self._last_result = None

    def _populate_steps_selector(self, result: MatrixEquationResultVM) -> None:
        self.steps_selector.blockSignals(True)
        self.steps_selector.clear()
        for column in result.columns:
            if column.result.steps:
                self.steps_selector.addItem(column.label, column.index)
        self.steps_selector.blockSignals(False)

        has_steps = self.steps_selector.count() > 0
        self.steps_selector.setEnabled(has_steps)
        self.steps_button.setEnabled(has_steps)
        if has_steps:
            self.steps_selector.setCurrentIndex(0)

    @staticmethod
    def _summarize_trivial_solution(result: MatrixEquationResultVM, is_homogeneous: bool) -> str:
        if not is_homogeneous:
            return ""

        status = result.status
        if status == "INCONSISTENTE":
            return "No existe solución; ni siquiera la trivial satisface las ecuaciones."

        has_free_vars = any(bool(column.result.free_vars) for column in result.columns)
        if status == "INFINITAS" or has_free_vars:
            return "Existen soluciones no triviales (hay al menos una variable libre)."

        if status == "UNICA" and MatrixEquationPage._all_solutions_zero(result):
            return "La solución trivial es la única."

        return "La solución trivial no es la única."

    @staticmethod
    def _all_solutions_zero(result: MatrixEquationResultVM) -> bool:
        for column in result.columns:
            solution = column.result.solution
            if not solution:
                return False
            if any(value != 0 for value in solution):
                return False
        return True

    def _on_show_steps(self) -> None:
        if not self._last_result:
            return
        current_index = self.steps_selector.currentIndex()
        if current_index < 0:
            return
        column_index = self.steps_selector.currentData()
        column = next((col for col in self._last_result.columns if col.index == column_index), None)
        if not column or not column.result.steps:
            return
        dialogs.show_steps_dialog(
            self,
            column.result.steps,
            pivot_cols=column.result.pivot_cols or [],
            title=f"Pasos Gauss–Jordan ({column.label})",
        )
