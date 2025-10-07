"""Página principal de resolución de sistemas lineales.

La vista sigue la secuencia mostrada en Lay, *Álgebra Lineal y sus
Aplicaciones* (5ª ed., 2012, cap. 1–2): primero se fijan dimensiones,
se captura la matriz aumentada y finalmente se ejecuta Gauss–Jordan.
El objetivo del refactor es encapsular la lógica de la UI en un widget
reutilizable y dejar que la ventana principal se enfoque en la
navegación.
"""

from __future__ import annotations

from typing import List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel, ResultVM, StepVM

from . import dialogs, helpers


class CalculatorPage(QWidget):
    """Widget autónomo para gestionar la captura y resolución de A|b."""

    MIN_ROWS = 2
    MAX_ROWS = 10
    MIN_COLS = 3
    MAX_COLS = 12
    MAX_DISPLAY_STEPS = 10

    def __init__(self, view_model: MatrixCalculatorViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.view_model = view_model
        self._last_steps: List[StepVM] | None = None
        self._last_pivot_cols: List[int] | None = None
        self._last_free_vars: List[int] | None = None

        self._build_ui()
        self._wire_events()
        self._update_table_dimensions()
        self.dimension_label.setText(f"Matriz {self.view_model.rows}×{self.view_model.cols} (A|b)")

    # ------------------------------ Construcción de UI ------------------------------
    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self._config_panel = self._build_config_panel()
        layout.addWidget(self._config_panel, stretch=1)

        result_panel = self._build_result_panel()
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setWidget(result_panel)
        layout.addWidget(result_scroll, stretch=3)

    def _build_config_panel(self) -> QWidget:
        panel = QGroupBox("Configuración")
        layout = QVBoxLayout(panel)

        subtitle = QLabel(
            "Resuelve sistemas mediante eliminación de Gauss-Jordan. "
            "La matriz aumentada se transforma hasta alcanzar la forma escalonada reducida (RREF)."
        )
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        subtitle.setStyleSheet("margin-bottom: 6px;")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        layout.addLayout(grid)

        # Filas (ecuaciones)
        grid.addWidget(QLabel("Filas"), 0, 0)
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(self.MIN_ROWS, self.MAX_ROWS)
        self.rows_spin.setValue(self.view_model.rows)
        grid.addWidget(self.rows_spin, 0, 1)
        rows_note = QLabel("2–10 filas")
        rows_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(rows_note, 1, 0, 1, 2)

        # Columnas (variables)
        grid.addWidget(QLabel("Columnas"), 2, 0)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(self.MIN_COLS, self.MAX_COLS)
        self.cols_spin.setValue(self.view_model.cols)
        grid.addWidget(self.cols_spin, 2, 1)
        cols_note = QLabel("3–12 columnas")
        cols_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(cols_note, 3, 0, 1, 2)

        # Método (placeholder por si se añaden más métodos)
        grid.addWidget(QLabel("Método"), 4, 0)
        self.method_display = QLineEdit("Gauss-Jordan")
        self.method_display.setReadOnly(True)
        self.method_display.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.method_display, 4, 1)
        grid.addWidget(QLabel("Resolución por pivoteo parcial."), 5, 0, 1, 2)

        self.dimension_label = QLabel()
        font_dim = QFont()
        font_dim.setPointSize(9)
        font_dim.setItalic(True)
        self.dimension_label.setFont(font_dim)
        grid.addWidget(self.dimension_label, 6, 0, 1, 2)

        button_row = QHBoxLayout()
        self.solve_button = QPushButton("Resolver")
        self.clear_button = QPushButton("Limpiar")
        self.example_button = QPushButton("Ejemplo")
        button_row.addWidget(self.solve_button)
        button_row.addWidget(self.clear_button)
        button_row.addWidget(self.example_button)
        layout.addLayout(button_row)
        layout.addStretch(1)
        return panel

    def _build_result_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(2)

        title = QLabel("Matriz aumentada del sistema")
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        title.setFont(font_title)
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setMinimumHeight(260)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionsClickable(True)
        layout.addWidget(self.table, stretch=2)

        layout.addWidget(self._make_separator())

        solution_title = QLabel("Resultado")
        font_solution = QFont()
        font_solution.setPointSize(13)
        font_solution.setBold(True)
        solution_title.setFont(font_solution)
        layout.addWidget(solution_title)

        self.state_label = QLabel()
        font_state = QFont()
        font_state.setPointSize(11)
        font_state.setBold(True)
        self.state_label.setFont(font_state)
        layout.addWidget(self.state_label)

        self.consistency_label = QLabel()
        self.consistency_label.setStyleSheet("color: #cbd7ea;")
        layout.addWidget(self.consistency_label)

        self.pivots_label = QLabel()
        self.pivots_label.setStyleSheet("color: #cbd7ea; margin-bottom: 2px;")
        layout.addWidget(self.pivots_label)

        self.solution_widget = QWidget()
        self.solution_container = QVBoxLayout(self.solution_widget)
        self.solution_container.setContentsMargins(0, 0, 0, 0)
        self.solution_container.setSpacing(2)

        self.solution_scroll = QScrollArea()
        self.solution_scroll.setWidgetResizable(True)
        self.solution_scroll.setMinimumHeight(240)
        self.solution_scroll.setWidget(self.solution_widget)
        layout.addWidget(self.solution_scroll, stretch=3)

        self.btn_show_steps = QPushButton("Ver pasos Gauss–Jordan")
        self.btn_show_steps.setVisible(False)
        layout.addWidget(self.btn_show_steps)

        layout.addStretch(1)
        return panel

    def _make_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator

    # ----------------------------- Conexiones -----------------------------
    def _wire_events(self) -> None:
        self.rows_spin.valueChanged.connect(self._on_dimensions_changed)
        self.cols_spin.valueChanged.connect(self._on_dimensions_changed)
        self.solve_button.clicked.connect(self._on_solve_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.example_button.clicked.connect(self._on_example_clicked)
        self.btn_show_steps.clicked.connect(self._handle_show_steps)

    # ---------------------------- Manejadores de eventos -------------------------
    def _on_dimensions_changed(self) -> None:
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        self.view_model.rows = m
        self.view_model.cols = n
        self._update_table_dimensions()
        self.dimension_label.setText(f"Matriz {m}×{n} (A|b)")

    def _on_solve_clicked(self) -> None:
        try:
            augmented = helpers.table_to_matrix(self.table)
            result = self.view_model.solve(augmented)
            self._update_result_display(result)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_clear_clicked(self) -> None:
        helpers.fill_table_with_zero(self.table)
        self.state_label.clear()
        self.consistency_label.clear()
        self.pivots_label.clear()
        self._clear_solution_display()
        self._last_steps = None
        self.btn_show_steps.setVisible(False)

    def _on_example_clicked(self) -> None:
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        for i in range(m):
            for j in range(n):
                value = 1.0 if i == j else float((i + j) % 5 + 1)
                item = QTableWidgetItem(f"{value}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            b_value = float(i + 1)
            b_item = QTableWidgetItem(f"{b_value}")
            b_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, n, b_item)

    def _handle_show_steps(self) -> None:
        if not self._last_steps:
            return
        dialogs.show_steps_dialog(self, self._last_steps, self._last_pivot_cols or [])

    # --------------------------- Actualización de la vista ----------------------------
    def _update_table_dimensions(self) -> None:
        rows = self.view_model.rows
        cols = self.view_model.cols + 1
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels([f"x{j + 1}" for j in range(cols - 1)] + ["b"])
        helpers.ensure_table_defaults(self.table)

    def _update_result_display(self, result: ResultVM) -> None:
        self._last_steps = result.steps
        self._last_pivot_cols = result.pivot_cols or []
        self._last_free_vars = result.free_vars or []

        self.state_label.setText(helpers.status_to_text(result.status))
        is_consistent = result.status in ("UNICA", "INFINITAS")
        self.consistency_label.setText("Sistema: Consistente" if is_consistent else "Sistema: Inconsistente")

        piv_text = ", ".join([f"x{j + 1}" for j in (self._last_pivot_cols or [])]) or "—"
        self.pivots_label.setText(f"Columnas pivote: {piv_text}")

        self._clear_solution_display()
        labels = [f"x{idx + 1}" for idx in range(self.view_model.cols)]
        for line in helpers.format_result_lines(result, labels):
            label = QLabel(line)
            label.setWordWrap(True)
            self.solution_container.addWidget(label)

        if result.steps:
            self.btn_show_steps.setVisible(True)
        else:
            self.btn_show_steps.setVisible(False)

    def _clear_solution_display(self) -> None:
        while self.solution_container.count():
            item = self.solution_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ----------------------------- Utilidades -----------------------------
    def export_state(self) -> dict:
        """Expose a snapshot for debugging or future persistence."""

        return {
            "rows": self.view_model.rows,
            "cols": self.view_model.cols,
            "augmented": helpers.table_to_matrix(self.table),
            "last_steps": self._last_steps,
        }
