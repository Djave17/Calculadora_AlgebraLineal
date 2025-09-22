"""Herramientas de operaciones vectoriales en ℝⁿ.

Los ejercicios replican los que se discuten en Grossman (2019) y Lay
(2012): suma de vectores, multiplicación por escalar y verificación de
las propiedades básicas del espacio vectorial.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ViewModels.vector_propiedades_vm import VectorPropiedadesViewModel

from . import helpers


class VectorPropertiesPage(QWidget):
    """Vista que permite experimentar con operaciones elementales."""

    def __init__(self, view_model: VectorPropiedadesViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._vm = view_model

        self._build_ui()
        self._wire_events()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Propiedades algebraicas de ℝⁿ")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        explanation = QLabel(
            "Explora la suma u + v, la multiplicación α·u y verifica las "
            "propiedades conmutativa, asociativa, del vector cero y del "
            "vector opuesto."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        instructions = QLabel("Introduce vectores separados por comas o espacios. Ej: 1, 2, 3")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("u ="))
        self.vector_u_input = QLineEdit()
        self.vector_u_input.setPlaceholderText("Ej: 1, 2, 3")
        input_row.addWidget(self.vector_u_input)

        input_row.addWidget(QLabel("v ="))
        self.vector_v_input = QLineEdit()
        self.vector_v_input.setPlaceholderText("Ej: 4, 5, 6")
        input_row.addWidget(self.vector_v_input)

        input_row.addWidget(QLabel("w (opcional) ="))
        self.vector_w_input = QLineEdit()
        self.vector_w_input.setPlaceholderText("Vacío para usar w = (1, …, 1)")
        input_row.addWidget(self.vector_w_input)
        layout.addLayout(input_row)

        scalar_row = QHBoxLayout()
        scalar_row.addWidget(QLabel("Escalar α:"))
        self.scalar_input = QLineEdit()
        self.scalar_input.setMaximumWidth(120)
        self.scalar_input.setPlaceholderText("Ej: 2")
        scalar_row.addWidget(self.scalar_input)
        scalar_row.addStretch(1)
        layout.addLayout(scalar_row)

        button_row = QHBoxLayout()
        self.btn_sum = QPushButton("u + v")
        self.btn_scalar = QPushButton("α · u")
        self.btn_props = QPushButton("Verificar propiedades")
        self.btn_clear = QPushButton("Limpiar")
        button_row.addWidget(self.btn_sum)
        button_row.addWidget(self.btn_scalar)
        button_row.addWidget(self.btn_props)
        button_row.addWidget(self.btn_clear)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.vector_result_output = QTextEdit()
        self.vector_result_output.setReadOnly(True)
        self.vector_result_output.setMinimumHeight(240)
        layout.addWidget(self.vector_result_output)

    def _wire_events(self) -> None:
        self.btn_sum.clicked.connect(self._on_sum_vectors)
        self.btn_scalar.clicked.connect(self._on_scalar_mult)
        self.btn_props.clicked.connect(self._on_verify_properties)
        self.btn_clear.clicked.connect(self._on_clear)

    # --------------------------- event handlers -------------------------
    def _on_sum_vectors(self) -> None:
        try:
            u = self._vm.parse_vector(self.vector_u_input.text())
            v = self._vm.parse_vector(self.vector_v_input.text())
            res = self._vm.sum_vectors(u, v)
            lines = [f"Resultado: u + v = {helpers.format_vector(res.result)}", "", "Pasos:"]
            lines.extend(res.steps)
            self.vector_result_output.setPlainText("\n".join(lines))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_scalar_mult(self) -> None:
        try:
            u = self._vm.parse_vector(self.vector_u_input.text())
            alpha_str = self.scalar_input.text().strip()
            if not alpha_str:
                raise ValueError("Debes proporcionar un valor para α.")
            alpha = float(alpha_str)
            res = self._vm.scalar_mult(alpha, u)
            lines = [f"Resultado: α · u = {helpers.format_vector(res.result)}", "", "Pasos:"]
            lines.extend(res.steps)
            self.vector_result_output.setPlainText("\n".join(lines))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_verify_properties(self) -> None:
        try:
            u = self._vm.parse_vector(self.vector_u_input.text())
            v = self._vm.parse_vector(self.vector_v_input.text())
            w_text = self.vector_w_input.text().strip()
            w = self._vm.parse_vector(w_text) if w_text else None
            rows = ["Comprobación de propiedades:"]
            for prop, ok, steps in self._vm.verify_properties(u, v, w):
                estado = "OK" if ok else "X"
                rows.append(f"{prop}: {estado}")
                rows.extend(f"  {line}" for line in steps)
            self.vector_result_output.setPlainText("\n".join(rows))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_clear(self) -> None:
        self.vector_u_input.clear()
        self.vector_v_input.clear()
        self.vector_w_input.clear()
        self.scalar_input.clear()
        self.vector_result_output.clear()
