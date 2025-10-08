"""Evaluación de dependencia lineal usando Gauss-Jordan.

La lógica aplica el criterio teórico: un conjunto \{v₁,…,vₖ\} es
independiente si el sistema homogéneo A·c = 0 (con A = [v₁ … vₖ]) sólo
admite la solución trivial (Lay, §1.7; Grossman, cap. 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List

from ViewModels.resolucion_matriz_vm import (
    InterpretationVM,
    MatrixCalculatorViewModel,
    ResultVM,
)


@dataclass
class DependenceResultVM:
    """Datos resumidos tras analizar un conjunto de vectores."""

    solver_result: ResultVM
    augmented_matrix: List[List[Fraction]]
    coefficient_labels: List[str]
    interpretation: InterpretationVM


class VectorDependenciaViewModel:
    """Prepara el sistema homogéneo asociado y lo interpreta."""

    def __init__(self) -> None:
        self._calculator = MatrixCalculatorViewModel()

    def analizar(self, generadores: List[List[Fraction]]) -> DependenceResultVM:
        if not generadores:
            raise ValueError(
                "Debes ingresar al menos un vector para evaluar dependencia "
                "(Lay, §1.7)."
            )

        dimension = len(generadores[0])
        if dimension == 0:
            raise ValueError(
                "Cada vector debe tener al menos una componente; de lo contrario "
                "no pertenece a ℝⁿ (Lay, §1.2)."
            )

        for idx, vec in enumerate(generadores, start=1):
            if len(vec) != dimension:
                raise ValueError(
                    "Todos los vectores deben compartir dimensión; es requisito "
                    "para definir correctamente el subespacio generado (Lay, §1.4)."
                )

        num_vectores = len(generadores)
        self._calculator.rows = dimension
        self._calculator.cols = num_vectores

        matriz_aumentada: List[List[Fraction]] = []
        for fila in range(dimension):
            coeficientes = [generadores[col][fila] for col in range(num_vectores)]
            coeficientes.append(Fraction(0))
            matriz_aumentada.append(coeficientes)

        resultado = self._calculator.solve(matriz_aumentada)
        etiquetas = [f"c{i + 1}" for i in range(num_vectores)]
        interpretacion = MatrixCalculatorViewModel.interpret_result(
            resultado,
            context="dependence",
            is_homogeneous=True,
            variable_labels=etiquetas,
        )

        return DependenceResultVM(
            solver_result=resultado,
            augmented_matrix=matriz_aumentada,
            coefficient_labels=etiquetas,
            interpretation=interpretacion,
        )
