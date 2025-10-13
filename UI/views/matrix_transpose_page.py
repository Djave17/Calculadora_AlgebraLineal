"""Vista para calcular la traspuesta y explicar la propiedad (A^T)^T = A."""

from __future__ import annotations

from typing import List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QHeaderView,
)

from ViewModels.matrix_transpose_vm import MatrixTransposeViewModel, TransposeResult

from . import helpers


class MatrixTransposePage(QWidget):
    """Permite ingresar una matriz A, calcular A^T y verificar (A^T)^T = A."""

    MAX_ROWS = 10
    MAX_COLS = 10

    def __init__(
        self,
        view_model: MatrixTransposeViewModel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._vm = view_model
        self._last_steps: List[str] = []
        self._last_title: str = ""

        self._build_ui()
        self._wire_events()
        self._update_table_dimensions()

    # --------------------------- Construccion de la interfaz ---------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Calculo de la traspuesta")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Ingresa la matriz A y presiona Calcular matriz traspuesta. "
            "El panel inferior muestra A^T, explica como se intercambian filas por columnas "
            "y confirma la propiedad (A^T)^T = A."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        config_row = QHBoxLayout()
        config_row.setSpacing(12)

        config_row.addWidget(QLabel("Filas de A:"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, self.MAX_ROWS)
        self.rows_spin.setValue(3)
        config_row.addWidget(self.rows_spin)

        config_row.addWidget(QLabel("Columnas de A:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, self.MAX_COLS)
        self.cols_spin.setValue(3)
        config_row.addWidget(self.cols_spin)

        config_row.addStretch(1)
        layout.addLayout(config_row)

        self.matrix_group = QGroupBox("Matriz A")
        group_layout = QVBoxLayout(self.matrix_group)
        self.matrix_table = QTableWidget()
        self.matrix_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_table.verticalHeader().setVisible(False)
        group_layout.addWidget(self.matrix_table)
        layout.addWidget(self.matrix_group)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.compute_button = QPushButton("Calcular matriz traspuesta")
        self.compute_button.setFixedHeight(32)
        buttons_row.addWidget(self.compute_button)

        self.steps_button = QPushButton("Ver pasos detallados")
        self.steps_button.setFixedHeight(32)
        self.steps_button.setEnabled(False)
        buttons_row.addWidget(self.steps_button)

        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setFixedHeight(32)
        buttons_row.addWidget(self.clear_button)

        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        result_box = QGroupBox("Resultado y explicacion")
        result_layout = QVBoxLayout(result_box)
        result_layout.setContentsMargins(12, 12, 12, 12)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setMinimumHeight(220)
        self.result_output.setStyleSheet("background-color: #ffffff; color: #000000;")
        result_layout.addWidget(self.result_output)
        layout.addWidget(result_box, stretch=1)

    # ------------------------------ Conexion de eventos ------------------------------
    def _wire_events(self) -> None:
        self.rows_spin.valueChanged.connect(self._update_table_dimensions)
        self.cols_spin.valueChanged.connect(self._update_table_dimensions)
        self.compute_button.clicked.connect(self._handle_compute)
        self.steps_button.clicked.connect(self._handle_show_steps)
        self.clear_button.clicked.connect(self._handle_clear)

    # ------------------------------- Manejadores -------------------------------
    def _handle_compute(self) -> None:
        try:
            matrix_rows = helpers.table_to_matrix(self.matrix_table)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        result = self._vm.transpose(matrix_rows)
        self._display_result("Traspuesta de A", result, matrix_rows)

    def _handle_show_steps(self) -> None:
        if not self._last_steps:
            return
        QMessageBox.information(
            self,
            self._last_title or "Pasos detallados",
            "\n".join(self._last_steps),
        )

    def _handle_clear(self) -> None:
        helpers.fill_table_with_zero(self.matrix_table)
        self.result_output.clear()
        self._last_steps = []
        self._last_title = ""
        self.steps_button.setEnabled(False)

    # ------------------------------- Utilidades internas -------------------------------
    def _update_table_dimensions(self) -> None:
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        self.matrix_table.setRowCount(rows)
        self.matrix_table.setColumnCount(cols)
        self.matrix_table.setHorizontalHeaderLabels([f"c{j + 1}" for j in range(cols)])
        helpers.ensure_table_defaults(self.matrix_table)

    def _display_result(
        self,
        titulo: str,
        result: TransposeResult,
        matrix_rows: Sequence[Sequence],
    ) -> None:
        self._last_steps = result.steps
        self._last_title = titulo
        self.steps_button.setEnabled(bool(result.steps))

        lines: List[str] = [titulo, ""]
        lines.append("Matriz A ingresada:")
        lines.extend(helpers.matrix_lines(matrix_rows, indent="  "))
        lines.append("")

        lines.append(result.defined_message)
        lines.append(result.conclusion)
        lines.append("")
        lines.append(f"La traspuesta de A es:")
        lines.extend(helpers.matrix_lines(result.transpose, indent="  "))
        lines.append("")
        lines.append(f"Al aplicar la traspuesta nuevamente obtenemos (A^T)^T:")
        lines.extend(helpers.matrix_lines(result.double_transpose, indent="  "))
        lines.append("")
        lines.append(f"Propiedad aplicada: {result.property_name}")
        lines.append(f"  {result.property_statement}")
        lines.append("")
        lines.append("Pasos destacados:")
        lines.extend(result.steps)

        self.result_output.setPlainText("\n".join(lines).strip())

