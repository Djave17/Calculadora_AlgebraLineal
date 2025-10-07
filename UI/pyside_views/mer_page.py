"""Página informativa del Método de Eliminación por Renglones (MER)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MerPage(QWidget):
    """Describe los pasos conceptuales del MER utilizados en la aplicación."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        titulo = QLabel("Método de Eliminación por Renglones (MER)")
        fuente = QFont()
        fuente.setPointSize(17)
        fuente.setBold(True)
        titulo.setFont(fuente)
        titulo.setAlignment(Qt.AlignLeft)
        titulo.setWordWrap(True)
        layout.addWidget(titulo)

        descripcion = QLabel(
            "El MER aplica operaciones elementales por renglón hasta obtener una forma "
            "escalonada o reducida. Es la base teórica del algoritmo de Gauss-Jordan "
            "que emplea la calculadora para clasificar sistemas lineales."
        )
        descripcion.setAlignment(Qt.AlignJustify)
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(descripcion)

        pasos = QLabel(
            "Pasos habituales:\n"
            "1. Identificar un pivote distinto de cero en la columna actual.\n"
            "2. Intercambiar renglones si es necesario para colocar el pivote.\n"
            "3. Escalar el renglón pivote hasta que el pivote valga 1.\n"
            "4. Anular los elementos por encima y por debajo del pivote usando combinaciones lineales.\n"
            "5. Repetir para cada columna pivote hasta alcanzar la forma escalonada reducida."
        )
        pasos.setAlignment(Qt.AlignLeft)
        pasos.setWordWrap(True)
        pasos.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(pasos)

        referencias = QLabel(
            "Referencias recomendadas: Lay (2012, cap. 1-2) y Grossman (2019, cap. 2)."
        )
        referencias.setAlignment(Qt.AlignLeft)
        referencias.setWordWrap(True)
        referencias.setStyleSheet("font-size: 12px; color: #cbd7ea;")
        layout.addWidget(referencias)

        layout.addStretch(1)
