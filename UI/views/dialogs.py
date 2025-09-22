"""Reusable dialogs to present Gauss–Jordan traces.

The visual layout follows the step-by-step presentations suggested by
Grossman, *Álgebra Lineal*, 8ª ed., cap. 2, where each row operation is
paired with the updated matrix. Keeping the construction here prevents
code duplication across the different feature pages.
"""

from __future__ import annotations

from typing import Iterable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHeaderView,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ViewModels.resolucion_matriz_vm import StepVM


PIVOT_COLOR = QColor(64, 125, 188)
TEXT_COLOR = QColor(255, 255, 255)


def create_step_widget(step: StepVM) -> QWidget:
    """Create a compact widget that shows one Gauss–Jordan operation."""

    pivot_txt = ""
    if step.pivot_row is not None and step.pivot_col is not None:
        pivot_txt = f"  |  pivote x{step.pivot_col + 1} en ({step.pivot_row + 1},{step.pivot_col + 1})"

    widget = QGroupBox(f"Paso {step.number} – {step.description}{pivot_txt}")
    widget.setStyleSheet("QGroupBox { color: #ffffff; }")
    layout = QVBoxLayout()
    widget.setLayout(layout)

    matrix = step.after_matrix
    if not matrix:
        return widget

    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    table = QTableWidget(rows, cols)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setVisible(False)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    table.setFixedHeight(20 * max(rows, 1) + 2)

    for i in range(rows):
        for j in range(cols):
            item = QTableWidgetItem(str(matrix[i][j]))
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(TEXT_COLOR)
            if step.pivot_row is not None and step.pivot_col is not None and i == step.pivot_row and j == step.pivot_col:
                item.setBackground(PIVOT_COLOR)
            table.setItem(i, j, item)

    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    layout.addWidget(table)
    return widget


def show_steps_dialog(
    parent: QWidget,
    steps: Sequence[StepVM],
    pivot_cols: Iterable[int] = (),
    title: str = "Pasos Gauss–Jordan",
) -> None:
    """Open a modal dialog containing all recorded steps."""

    if not steps:
        return

    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.resize(700, 500)
    vbox = QVBoxLayout(dialog)

    def _fmt_vars(indices: Iterable[int]) -> str:
        data = [f"x{idx + 1}" for idx in indices]
        return ", ".join(data) if data else "—"

    header = QLabel(f"Columnas pivote: {_fmt_vars(pivot_cols)}")
    header.setStyleSheet("color: #ffffff; font-weight: bold; margin-bottom: 6px;")
    vbox.addWidget(header)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    container = QWidget()
    container_layout = QVBoxLayout()
    container.setLayout(container_layout)

    for step in steps:
        container_layout.addWidget(create_step_widget(step))

    container_layout.addStretch(1)
    scroll.setWidget(container)
    vbox.addWidget(scroll)

    dialog.exec()
