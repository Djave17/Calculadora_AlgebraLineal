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
        layout.setContentsMargins(32, 32, 32, 32)
        layout.addStretch(1)

        titulo = QLabel("Calculadora de Álgebra Lineal")
        titulo.setAlignment(Qt.AlignCenter)
        fuente = QFont()
        fuente.setPointSize(18)
        fuente.setBold(True)
        titulo.setFont(fuente)
        titulo.setWordWrap(True)
        layout.addWidget(titulo)

        descripcion = QLabel(
            "Explora métodos fundamentales de álgebra lineal: resolución de sistemas "
            "con Gauss-Jordan, análisis de combinaciones lineales, verificación de "
            "propiedades vectoriales y ecuaciones matriciales AX = B. Cada vista "
            "incluye notas resumidas basadas en Lay (2012) y Grossman (2019) para "
            "acompañar el estudio."
        )
        descripcion.setAlignment(Qt.AlignJustify)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(descripcion)

        indicaciones = QLabel(
            "Usa el menú lateral para elegir un módulo y, si necesitas repasar los pasos "
            "de Gauss-Jordan, abre el diálogo de detalles que muestra cada operación."
        )
        indicaciones.setAlignment(Qt.AlignJustify)
        indicaciones.setWordWrap(True)
        indicaciones.setStyleSheet("font-size: 13px; margin-top: 12px; line-height: 1.5;")
        layout.addWidget(indicaciones)

        layout.addStretch(1)
