"""Página que estudia combinaciones lineales de vectores.

La interfaz sigue el planteamiento estándar: escribir los generadores como
columnas y resolver A*c = b mediante Gauss–Jordan (Lay, 2012, cap. 1.7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
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

from ViewModels.combinacion_lineal_vm import CombinacionLinealViewModel, CombinationResultVM

from . import dialogs, helpers


@dataclass
class _StoredResult:
    explanation: CombinationResultVM


class CombinationPage(QWidget):
    """Analiza si b pertenece al subespacio generado por {v1,...,vk}."""

    def __init__(
        self,
        view_model: CombinacionLinealViewModel,
        parent: QWidget | None = None,
        max_rows: int = 10,
        max_cols: int = 12,
    ) -> None:
        super().__init__(parent)
        self._vm = view_model
        self._max_rows = max_rows
        self._max_cols = max_cols
        self._last_result: Optional[_StoredResult] = None

        self._build_ui()
        self._wire_events()
        self._update_tables()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Combinación lineal de vectores")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel(
            "Determina si el vector objetivo se puede expresar como combinación "
            "lineal de los generadores."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Dimensión:"))
        self.combo_dim_spin = QSpinBox()
        self.combo_dim_spin.setRange(1, self._max_rows)
        self.combo_dim_spin.setValue(3)
        config_row.addWidget(self.combo_dim_spin)

        config_row.addSpacing(12)
        config_row.addWidget(QLabel("Número de vectores:"))
        self.combo_vectors_spin = QSpinBox()
        self.combo_vectors_spin.setRange(1, self._max_cols)
        self.combo_vectors_spin.setValue(2)
        config_row.addWidget(self.combo_vectors_spin)
        config_row.addStretch(1)
        layout.addLayout(config_row)

        tables_row = QHBoxLayout()

        basis_group = QGroupBox("Vectores generadores (columnas)")
        basis_layout = QVBoxLayout(basis_group)
        self.combo_basis_table = QTableWidget()
        self.combo_basis_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.combo_basis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.combo_basis_table.verticalHeader().setVisible(False)
        basis_layout.addWidget(self.combo_basis_table)
        tables_row.addWidget(basis_group, stretch=2)

        target_group = QGroupBox("Vector objetivo b")
        target_layout = QVBoxLayout(target_group)
        self.combo_target_table = QTableWidget()
        self.combo_target_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.combo_target_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.combo_target_table.verticalHeader().setVisible(False)
        target_layout.addWidget(self.combo_target_table)
        tables_row.addWidget(target_group, stretch=1)

        layout.addLayout(tables_row)

        button_row = QHBoxLayout()
        self.combo_resolve_button = QPushButton("Analizar combinación")
        self.combo_steps_button = QPushButton("Ver pasos detallados")
        self.combo_steps_button.setEnabled(False)
        self.combo_clear_button = QPushButton("Limpiar")
        button_row.addWidget(self.combo_resolve_button)
        button_row.addWidget(self.combo_steps_button)
        button_row.addWidget(self.combo_clear_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.combo_result_output = QTextEdit()
        self.combo_result_output.setReadOnly(True)
        self.combo_result_output.setMinimumHeight(260)
        layout.addWidget(self.combo_result_output)

    def _wire_events(self) -> None:
        self.combo_dim_spin.valueChanged.connect(self._update_tables)
        self.combo_vectors_spin.valueChanged.connect(self._update_tables)
        self.combo_resolve_button.clicked.connect(self._on_resolve)
        self.combo_steps_button.clicked.connect(self._on_show_steps)
        self.combo_clear_button.clicked.connect(self._on_clear)

    # --------------------------- interaction -----------------------------
    def _update_tables(self) -> None:
        rows = self.combo_dim_spin.value()
        cols = self.combo_vectors_spin.value()

        self.combo_basis_table.blockSignals(True)
        self.combo_basis_table.setRowCount(rows)
        self.combo_basis_table.setColumnCount(cols)
        self.combo_basis_table.setHorizontalHeaderLabels([f"v{j + 1}" for j in range(cols)])
        helpers.ensure_table_defaults(self.combo_basis_table)
        self.combo_basis_table.blockSignals(False)

        self.combo_target_table.blockSignals(True)
        self.combo_target_table.setRowCount(rows)
        self.combo_target_table.setColumnCount(1)
        self.combo_target_table.setHorizontalHeaderLabels(["b"])
        helpers.ensure_table_defaults(self.combo_target_table)
        self.combo_target_table.blockSignals(False)

    def _on_resolve(self) -> None:
        self._last_result = None
        try:
            basis_rows = helpers.table_to_matrix(self.combo_basis_table)
            generadores = helpers.columns_from_rows(basis_rows)
            target_rows = helpers.table_to_matrix(self.combo_target_table)
            objetivo = [row[0] for row in target_rows]

            resultado = self._vm.analizar(generadores, objetivo)
            self._last_result = _StoredResult(resultado)

            lines: List[str] = []
            lines.append("Matriz aumentada [A|b]:")
            lines.extend(helpers.matrix_lines(resultado.augmented_matrix, indent="  "))
            lines.append("")
            lines.extend(helpers.format_result_lines(resultado.solver_result, resultado.coefficient_labels))
            lines.append("")
            lines.extend(helpers.format_steps_lines(resultado.solver_result))

            self.combo_result_output.setPlainText("\n".join(lines))
            self.combo_steps_button.setEnabled(bool(resultado.solver_result.steps))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_clear(self) -> None:
        helpers.fill_table_with_zero(self.combo_basis_table)
        helpers.fill_table_with_zero(self.combo_target_table)
        self.combo_result_output.clear()
        self.combo_steps_button.setEnabled(False)
        self._last_result = None

    def _on_show_steps(self) -> None:
        if not self._last_result:
            return
        steps = self._last_result.explanation.solver_result.steps
        if not steps:
            return
        dialogs.show_steps_dialog(
            self,
            steps,
            pivot_cols=self._last_result.explanation.solver_result.pivot_cols or [],
            title="Pasos Gauss–Jordan (combinación lineal)",
        )
