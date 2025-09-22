"""Página de bienvenida/introducción.

El diseño reproduce la idea de presentar un mensaje corto que recuerda
los objetivos del curso (ver Poole, *Linear Algebra: A Modern
Introduction*, prefacio). Se mantiene como widget aislado para que el
`MainWindow` solo se ocupe de la navegabilidad.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HomePage(QWidget):
    """Muestra un saludo centrado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addStretch(1)

        label = QLabel(
            "¡Bienvenido! Usa la barra lateral para navegar por las "
            "distintas herramientas de álgebra lineal."
        )
        label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        label.setWordWrap(True)
        layout.addWidget(label)

        layout.addStretch(1)
