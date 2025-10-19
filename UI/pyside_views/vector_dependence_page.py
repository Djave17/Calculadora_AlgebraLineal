"""Vista para clasificar conjuntos de vectores como dependientes o independientes.

Se sigue el criterio de Lay (2012, §1.7): resolver el sistema homogéneo
A·c = 0 y analizar la presencia de soluciones no triviales.
"""

from __future__ import annotations

from typing import List

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

from ViewModels.vector_dependencia_vm import (
    DependenceResultVM,
    VectorDependenciaViewModel,
)

from . import dialogs, helpers
from .components import AlertBanner


class VectorDependencePage(QWidget):
    """Permite ingresar vectores y evaluar su dependencia lineal."""

    def __init__(
        self,
        view_model: VectorDependenciaViewModel,
        parent: QWidget | None = None,
        max_dim: int = 10,
        max_vectors: int = 12,
    ) -> None:
        super().__init__(parent)
        self._vm = view_model
        self._max_dim = max_dim
        self._max_vectors = max_vectors
        self._last_result: DependenceResultVM | None = None

        self._build_ui()
        self._wire_events()
        self._update_table()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Dependencia lineal en ℝⁿ")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        description = QLabel(
            "Introduce los vectores como columnas; la página resuelve el sistema homogéneo "
            "A·c = 0 para determinar si sólo existe la solución trivial."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Dimensión:"))
        self.dim_spin = QSpinBox()
        self.dim_spin.setRange(1, self._max_dim)
        self.dim_spin.setValue(3)
        config_row.addWidget(self.dim_spin)

        config_row.addSpacing(12)
        config_row.addWidget(QLabel("Número de vectores:"))
        self.vector_spin = QSpinBox()
        self.vector_spin.setRange(1, self._max_vectors)
        self.vector_spin.setValue(3)
        config_row.addWidget(self.vector_spin)
        config_row.addStretch(1)
        layout.addLayout(config_row)

        table_group = QGroupBox("Vectores (columnas)")
        table_layout = QVBoxLayout(table_group)
        self.vectors_table = QTableWidget()
        self.vectors_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.vectors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vectors_table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.vectors_table)
        layout.addWidget(table_group)

        buttons = QHBoxLayout()
        self.analyze_button = QPushButton("Analizar dependencia")
        self.steps_button = QPushButton("Ver pasos Gauss–Jordan")
        self.steps_button.setEnabled(False)
        self.clear_button = QPushButton("Limpiar")
        buttons.addWidget(self.analyze_button)
        buttons.addWidget(self.steps_button)
        buttons.addWidget(self.clear_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.alert_banner = AlertBanner()
        layout.addWidget(self.alert_banner)

        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setMinimumHeight(260)
        layout.addWidget(self.result_output)

    def _wire_events(self) -> None:
        self.dim_spin.valueChanged.connect(self._update_table)
        self.vector_spin.valueChanged.connect(self._update_table)
        self.analyze_button.clicked.connect(self._on_analyze)
        self.steps_button.clicked.connect(self._on_show_steps)
        self.clear_button.clicked.connect(self._on_clear)

    def _update_table(self) -> None:
        rows = self.dim_spin.value()
        cols = self.vector_spin.value()
        self.vectors_table.blockSignals(True)
        self.vectors_table.setRowCount(rows)
        self.vectors_table.setColumnCount(cols)
        self.vectors_table.setHorizontalHeaderLabels([f"v{j + 1}" for j in range(cols)])
        helpers.ensure_table_defaults(self.vectors_table)
        self.vectors_table.blockSignals(False)

    def _on_analyze(self) -> None:
        self._last_result = None
        try:
            rows = helpers.table_to_matrix(self.vectors_table)
            generadores = helpers.columns_from_rows(rows)
            resultado = self._vm.analizar(generadores)
            self._last_result = resultado
        except Exception as exc:
            self.alert_banner.show_message(str(exc), level="error")
            QMessageBox.critical(self, "Error", str(exc))
            return

        combination_terms = [
            f"{coef}{helpers.format_vector(vector)}"
            for coef, vector in zip(resultado.coefficient_labels, generadores)
        ]
        combination_expr = " + ".join(combination_terms)
        zero_vector = helpers.format_vector([0] * len(generadores[0]))
        status = resultado.solver_result.status
        has_unique_solution = status == "UNICA"
        are_dependent = status == "INFINITAS"
        solution_values = resultado.solver_result.solution
        trivial_only = (
            has_unique_solution
            and solution_values is not None
            and all(value == 0 for value in solution_values)
        )

        lines: List[str] = []
        lines.append("Matriz aumentada [A|0]:")
        lines.extend(helpers.matrix_lines(resultado.augmented_matrix, indent="  "))
        lines.append("")
        lines.append(f"Planteamiento: {combination_expr} = b, con b = {zero_vector}.")
        consistency_line = (
            "El sistema es consistente con una solución única."
            if has_unique_solution
            else "El sistema no es consistente con una solución única."
        )
        dependence_line = (
            "Los vectores ingresados son linealmente dependientes."
            if are_dependent
            else "Los vectores ingresados son linealmente independientes."
        )
        trivial_line = (
            "El sistema homogéneo solo tiene la solución trivial."
            if trivial_only
            else "El sistema homogéneo admite soluciones no triviales."
        )
        lines.append(f"• {consistency_line}")
        lines.append(f"• {dependence_line}")
        lines.append(f"• {trivial_line}")
        lines.append("")
        lines.extend(
            helpers.format_result_lines(
                resultado.solver_result,
                resultado.coefficient_labels,
                indent="",
                homogeneous=True,
            )
        )
        lines.append("")
        lines.extend(helpers.format_steps_lines(resultado.solver_result))

        self.result_output.setPlainText("\n".join(lines))
        self.alert_banner.show_message(
            resultado.interpretation.summary,
            level=resultado.interpretation.level,
        )
        self.steps_button.setEnabled(bool(resultado.solver_result.steps))

    def _on_show_steps(self) -> None:
        if not self._last_result or not self._last_result.solver_result.steps:
            return
        dialogs.show_steps_dialog(
            self,
            self._last_result.solver_result.steps,
            pivot_cols=self._last_result.solver_result.pivot_cols or [],
            title="Pasos Gauss–Jordan (dependencia)",
        )

    def _on_clear(self) -> None:
        helpers.fill_table_with_zero(self.vectors_table)
        self.result_output.clear()
        self.steps_button.setEnabled(False)
        self.alert_banner.clear()
        self._last_result = None
