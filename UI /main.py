"""
User interface for the matrix calculator using PySide6.

This module defines a main window that allows the user to input a linear
system in augmented matrix form, choose a resolution method, and view
the solution along with an optional step-by-step breakdown of the
Gauss–Jordan elimination process. The UI is built using Qt widgets
provided by PySide6 and follows a modern, dark-themed aesthetic.

The interface is divided into two primary panels:

1. **Configuración** – Located on the left, this panel lets the user
   specify the number of equations and variables (within predefined
   limits), choose the solution method (currently only Gauss–Jordan),
   reset or fill example data, and initiate the calculation.
2. **Resultados** – On the right, this panel displays the matrix
   augmented input table, the solution (unique, infinite or inconsistent),
   and optionally the list of steps taken during the Gauss–Jordan
   algorithm. Each step shows the operation performed and the matrix
   state after the operation.

The window communicates with the `MatrixCalculatorViewModel` defined
in `UI/ViewModels/viewmodels.py` to perform the actual computation.

Note: This module depends on PySide6. If PySide6 is not installed in
the environment, importing this module will raise an ImportError. The
repository containing this file may not include PySide6 by default; to
run the UI, please ensure that PySide6 is installed in your Python
environment.
"""

import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # carpeta raíz
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
#from __future__ import annotations

import sys
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QMessageBox,
)

from ViewModels.viewmodels import MatrixCalculatorViewModel, ResultVM, StepVM


class MatrixCalculatorWindow(QMainWindow):
    """Main application window for the matrix calculator.

    This class sets up the user interface elements and connects them
    to the underlying view model. It reacts to user interactions
    (adjusting dimensions, entering matrix values, invoking the solver)
    and updates the display accordingly.
    """

    # Limits for the size of the matrix. These correspond to the
    # constraints shown in the left panel of the screenshot: 2–10 rows,
    # 3–12 columns.
    MIN_ROWS = 2
    MAX_ROWS = 10
    MIN_COLS = 3
    MAX_COLS = 12

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calculadora de Matrices")
        self.resize(1100, 700)

        # Instantiate the view model
        self.view_model = MatrixCalculatorViewModel()

        # Main container widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)

        # Create left configuration panel
        self.config_panel = self._create_config_panel()
        main_layout.addWidget(self.config_panel)

        # Create right result panel
        self.result_panel = self._create_result_panel()
        main_layout.addWidget(self.result_panel, stretch=1)

        # Apply dark style
        self._apply_dark_theme()

        # Initialize table with default sizes
        self._update_table_dimensions()

    # ------------------------------------------------------------------
    # UI Creation
    # ------------------------------------------------------------------
    def _create_config_panel(self) -> QWidget:
        panel = QGroupBox("Configuración")
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Title label (calculadora description) – similar to screenshot
        subtitle = QLabel(
            "Resuelve sistemas de ecuaciones lineales usando eliminación de Gauss y Gauss-Jordan"
        )
        subtitle.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        subtitle.setFont(font)
        layout.addWidget(subtitle)

        # Grid layout for inputs
        grid = QGridLayout()
        layout.addLayout(grid)

        # Rows spin box
        rows_label = QLabel("Filas")
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(self.MIN_ROWS)
        self.rows_spin.setMaximum(self.MAX_ROWS)
        self.rows_spin.setValue(self.view_model.rows)
        self.rows_spin.valueChanged.connect(self._on_dimensions_changed)
        rows_note = QLabel("2–10 filas")
        rows_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")

        grid.addWidget(rows_label, 0, 0)
        grid.addWidget(self.rows_spin, 0, 1)
        grid.addWidget(rows_note, 1, 0, 1, 2)

        # Columns spin box
        cols_label = QLabel("Columnas")
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(self.MIN_COLS)
        self.cols_spin.setMaximum(self.MAX_COLS)
        self.cols_spin.setValue(self.view_model.cols)
        self.cols_spin.valueChanged.connect(self._on_dimensions_changed)
        cols_note = QLabel("3–12 columnas")
        cols_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(cols_label, 2, 0)
        grid.addWidget(self.cols_spin, 2, 1)
        grid.addWidget(cols_note, 3, 0, 1, 2)

        # Method combobox
        method_label = QLabel("Método")
        self.method_combo = QComboBox()
        # Only Gauss–Jordan implemented but combobox allows extension
        self.method_combo.addItems(["Gauss-Jordan"])
        self.method_combo.setToolTip("Determinante")
        self.method_combo.setCurrentIndex(0)
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        method_note = QLabel("Método de resolución")
        method_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")

        grid.addWidget(method_label, 4, 0)
        grid.addWidget(self.method_combo, 4, 1)
        grid.addWidget(method_note, 5, 0, 1, 2)

        # Matrix dimension label
        self.dimension_label = QLabel()
        font_dim = QFont()
        font_dim.setPointSize(9)
        font_dim.setItalic(True)
        self.dimension_label.setFont(font_dim)
        grid.addWidget(self.dimension_label, 6, 0, 1, 2)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.solve_button = QPushButton("Resolver")
        self.solve_button.clicked.connect(self._on_solve_clicked)
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.example_button = QPushButton("Ejemplo")
        self.example_button.clicked.connect(self._on_example_clicked)
        buttons_layout.addWidget(self.solve_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.example_button)

        layout.addSpacing(10)
        layout.addLayout(buttons_layout)

        layout.addStretch()

        return panel

    def _create_result_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Augmented matrix table title
        title = QLabel("Matriz aumentada del sistema")
        font_title = QFont()
        font_title.setPointSize(11)
        font_title.setBold(True)
        title.setFont(font_title)
        layout.addWidget(title)

        # Table for augmented matrix [A|b]
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table.setFixedHeight(200)
        layout.addWidget(self.table)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Solution output area
        solution_title = QLabel("Resultado")
        font_solution = QFont()
        font_solution.setPointSize(11)
        font_solution.setBold(True)
        solution_title.setFont(font_solution)
        layout.addWidget(solution_title)

        # Label for state (UNICA, INFINITAS, INCONSISTENTE)
        self.state_label = QLabel()
        font_state = QFont()
        font_state.setPointSize(10)
        font_state.setBold(True)
        self.state_label.setFont(font_state)
        layout.addWidget(self.state_label)

        # Container for variable values or parametric solution
        self.solution_container = QVBoxLayout()
        layout.addLayout(self.solution_container)

        # Scroll area for steps
        steps_title = QLabel("Pasos Gauss-Jordan")
        steps_title.setFont(font_solution)
        layout.addWidget(steps_title)

        self.steps_scroll = QScrollArea()
        self.steps_scroll.setWidgetResizable(True)
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_container.setLayout(self.steps_layout)
        self.steps_scroll.setWidget(self.steps_container)
        layout.addWidget(self.steps_scroll)

        return panel

    def _apply_dark_theme(self) -> None:
        """Apply a custom dark theme to the entire application.

        This method sets a dark color palette and styles for commonly
        used widgets. It aims to approximate the aesthetic shown in
        the screenshot provided by the user, with deep background
        colours and muted accent tones.
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(19, 23, 34))
        palette.setColor(QPalette.WindowText, QColor(220, 229, 241))
        palette.setColor(QPalette.Base, QColor(29, 33, 48))
        palette.setColor(QPalette.AlternateBase, QColor(24, 27, 43))
        palette.setColor(QPalette.Text, QColor(220, 229, 241))
        palette.setColor(QPalette.Button, QColor(29, 33, 48))
        palette.setColor(QPalette.ButtonText, QColor(220, 229, 241))
        palette.setColor(QPalette.Highlight, QColor(68, 114, 196))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

        # Global style sheet
        self.setStyleSheet(
            """
            QLabel {
                color: #dde6f7;
            }
            QGroupBox {
                border: 1px solid #3b4252;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QSpinBox, QComboBox {
                background-color: #2e3448;
                border: 1px solid #465a7f;
                border-radius: 4px;
                padding: 2px 4px;
                color: #dde6f7;
            }
            QPushButton {
                background-color: #4c566a;
                border: 1px solid #5e81ac;
                border-radius: 4px;
                padding: 6px 12px;
                color: #e5e9f0;
            }
            QPushButton:hover {
                background-color: #5e81ac;
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
            QTableWidget {
                background-color: #2e3448;
                gridline-color: #434c6a;
                color: #dde6f7;
            }
            QHeaderView::section {
                background-color: #3b4252;
                color: #e5e9f0;
                padding: 4px;
                border: 1px solid #4c566a;
            }
            QScrollArea {
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #2e3448;
            }
            """
        )

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _on_dimensions_changed(self) -> None:
        """Handle changes to the number of rows or columns.

        When the user adjusts either spin box, update the internal
        dimension state and resize the table accordingly. Also update
        the dimension label to reflect the new matrix size.
        """
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        self.view_model.rows = m
        self.view_model.cols = n
        self._update_table_dimensions()
        self.dimension_label.setText(f"Matriz {m}×{n} (A|b)")

    def _on_method_changed(self) -> None:
        method_text = self.method_combo.currentText()
        self.view_model.method = method_text

    def _on_solve_clicked(self) -> None:
        """Read the matrix values from the table, invoke the solver and
        display the results. Invalid inputs trigger a message box.
        """
        try:
            augmented = []
            for i in range(self.table.rowCount()):
                row_values: List[float] = []
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    value_str = item.text() if item else "0"
                    # Empty cells are treated as zero; otherwise parse float
                    try:
                        value = float(value_str.strip()) if value_str.strip() != "" else 0.0
                    except ValueError:
                        raise ValueError(
                            f"Valor no numérico en fila {i+1}, columna {j+1}: '{value_str}'"
                        )
                    row_values.append(value)
                augmented.append(row_values)
            result = self.view_model.solve(augmented)
            self._update_result_display(result)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_clear_clicked(self) -> None:
        """Clear all entries in the matrix table and reset the result panel."""
        self._reset_table_to_zero()
        self.state_label.clear()
        self._clear_solution_display()
        self._clear_steps_display()

    def _on_example_clicked(self) -> None:
        """Fill the table with a simple example matrix and vector.

        The example uses small integer values so that the resulting
        solution is easy to verify manually. The number of rows and
        columns currently selected determine the size of the example.
        """
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        # Example: A is identity-like with sequential numbers; b is 1..m
        for i in range(m):
            for j in range(n):
                value = 1.0 if i == j else float((i + j) % 5 + 1)
                item = QTableWidgetItem(f"{value}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            # b vector: sequential integers starting from 1
            b_value = float(i + 1)
            b_item = QTableWidgetItem(f"{b_value}")
            b_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, n, b_item)

    # ------------------------------------------------------------------
    # UI Update Helpers
    # ------------------------------------------------------------------
    def _update_table_dimensions(self) -> None:
        """Resize the table to match the current rows and columns.

        The table will have `rows` rows and `cols + 1` columns (the
        extra column corresponds to the vector b). Column headers are
        labelled x1..xn and b. Existing items are preserved where
        possible; new cells are initialized empty.
        """
        m = self.view_model.rows
        n = self.view_model.cols
        current_rows = self.table.rowCount()
        current_cols = self.table.columnCount()

        # Adjust row count
        if current_rows != m:
            self.table.setRowCount(m)
        # Adjust column count (n variables + 1 for b)
        if current_cols != n + 1:
            self.table.setColumnCount(n + 1)
            # Set column headers
            headers = [f"x{j + 1}" for j in range(n)] + ["b"]
            self.table.setHorizontalHeaderLabels(headers)
        # Resize headers to fit contents
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Initialize new cells with empty text
        for i in range(m):
            for j in range(n + 1):
                if not self.table.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

    def _reset_table_to_zero(self) -> None:
        """Set all entries in the matrix table to zero."""
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if not item:
                    item = QTableWidgetItem()
                    self.table.setItem(i, j, item)
                item.setText("0")
                item.setTextAlignment(Qt.AlignCenter)

    def _clear_solution_display(self) -> None:
        """Remove existing solution widgets from the solution container."""
        while self.solution_container.count():
            child = self.solution_container.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

    def _clear_steps_display(self) -> None:
        """Remove existing step widgets from the steps container."""
        while self.steps_layout.count():
            child = self.steps_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

    def _update_result_display(self, result: ResultVM) -> None:
        """Update the solution and steps areas based on the result."""
        # Clear previous output
        self._clear_solution_display()
        self._clear_steps_display()

        # State label
        if result.status == "UNICA":
            self.state_label.setText("Solución única")
        elif result.status == "INFINITAS":
            self.state_label.setText("Infinitas soluciones")
        else:
            self.state_label.setText("Sistema inconsistente")

        # Solution or parametric
        if result.status == "UNICA" and result.solution is not None:
            for idx, value in enumerate(result.solution, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
        elif result.status == "INFINITAS" and result.parametric is not None:
            p = result.parametric
            # Particular solution
            particular_title = QLabel("Solución particular:")
            particular_title.setStyleSheet("font-size: 10pt; font-weight: bold;")
            self.solution_container.addWidget(particular_title)
            for idx, value in enumerate(p.particular, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
            # Direction vectors
            directions_title = QLabel("Direcciones asociadas a cada variable libre:")
            directions_title.setStyleSheet("font-size: 10pt; font-weight: bold; margin-top: 8px;")
            self.solution_container.addWidget(directions_title)
            for k, dir_vec in enumerate(p.directions):
                items = []
                for j, coef in enumerate(dir_vec):
                    if abs(coef) > 1e-12:
                        items.append(f"{coef:.6g}·x{j+1}")
                term = " + ".join(items) if items else "0"
                dir_label = QLabel(f"t{k+1}: {term}")
                dir_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(dir_label)
        else:
            # Inconsistent: no solution values to display
            inc_label = QLabel("No existe solución.")
            inc_label.setStyleSheet("font-size: 10pt; color: #e06c75;")
            self.solution_container.addWidget(inc_label)

        # Steps
        if result.steps:
            for step in result.steps:
                step_widget = self._create_step_widget(step)
                self.steps_layout.addWidget(step_widget)
            self.steps_layout.addStretch()

    def _create_step_widget(self, step: StepVM) -> QWidget:
        """Create a widget representing a single Gauss–Jordan step."""
        widget = QGroupBox(f"Paso {step.number} – {step.description}")
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Table showing the matrix after the operation
        matrix = step.after_matrix
        if not matrix:
            # If no after matrix provided, skip matrix display
            return widget
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        table = QTableWidget(rows, cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table.setFixedHeight(20 * rows + 2)
        # Populate table
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(f"{matrix[i][j]:.6g}")
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        # Resize columns proportionally
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        return widget


def main() -> None:
    app = QApplication(sys.argv)
    window = MatrixCalculatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()