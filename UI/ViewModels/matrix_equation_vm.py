from __future__ import annotations

from typing import List

from UI.ViewModels.resolucion_matriz_vm import (
    MatrixCalculatorViewModel,
    MatrixEquationResultVM,
)


class MatrixEquationViewModel:
    """Coordina la resolución de ecuaciones matriciales AX = B."""

    def __init__(self) -> None:
        self._calculator = MatrixCalculatorViewModel()

    def resolver(self, A_rows: List[List[float]], B_rows: List[List[float]]) -> MatrixEquationResultVM:
        return self._calculator.solve_matrix_equation(A_rows, B_rows)
