from __future__ import annotations

from dataclasses import dataclass
from typing import List

from UI.ViewModels.resolucion_matriz_vm import (
    MatrixCalculatorViewModel,
    ResultVM,
)


@dataclass
class CombinationResultVM:
    """Datos generados al analizar si un vector es combinación lineal."""

    coefficient_labels: List[str]
    solver_result: ResultVM
    augmented_matrix: List[List[float]]


class CombinacionLinealViewModel:
    """Gestiona el planteamiento y resolución de combinaciones lineales."""

    def __init__(self) -> None:
        self._calculator = MatrixCalculatorViewModel()

    def analizar(
        self,
        generadores: List[List[float]],
        objetivo: List[float],
    ) -> CombinationResultVM:
        if not generadores:
            raise ValueError("Debes proporcionar al menos un vector generador.")
        if not objetivo:
            raise ValueError("El vector objetivo no puede ser vacío.")
        dimension = len(objetivo)
        for idx, vec in enumerate(generadores, start=1):
            if len(vec) != dimension:
                raise ValueError(
                    f"El vector v{idx} tiene dimensión {len(vec)} y se esperaba {dimension}."
                )

        # Matriz A formada con los vectores como columnas
        filas_a = [
            [vec[i] for vec in generadores]
            for i in range(dimension)
        ]
        matriz_aumentada = [fila + [objetivo[i]] for i, fila in enumerate(filas_a)]

        self._calculator.rows = dimension
        self._calculator.cols = len(generadores)
        resultado = self._calculator.solve(matriz_aumentada)

        etiquetas = [f"c{i + 1}" for i in range(len(generadores))]
        return CombinationResultVM(
            coefficient_labels=etiquetas,
            solver_result=resultado,
            augmented_matrix=matriz_aumentada,
        )
