"""ViewModel para resolver AX = B con Gauss-Jordan (Strang, 2016)."""

from __future__ import annotations

from fractions import Fraction
from typing import List

from ViewModels.resolucion_matriz_vm import (
    MatrixCalculatorViewModel,
    MatrixEquationResultVM,
)


class MatrixEquationViewModel:
    """Coordina la resolución de ecuaciones matriciales AX = B."""

    def __init__(self) -> None:
        self._calculator = MatrixCalculatorViewModel()

    def resolver(
        self,
        A_rows: List[List[Fraction]],
        B_rows: List[List[Fraction]],
    ) -> MatrixEquationResultVM:
        return self._calculator.solve_matrix_equation(A_rows, B_rows)
