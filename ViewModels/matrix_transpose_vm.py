"""Logica para calcular la traspuesta y verificar sus propiedades basicas."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Sequence

from Operadores.matrices import to_fraction_matrix


@dataclass
class TransposeResult:
    steps: List[str]
    transpose: List[List[Fraction]]
    double_transpose: List[List[Fraction]]
    property_name: str
    property_statement: str
    defined_message: str
    conclusion: str


class MatrixTransposeViewModel:
    """Calcula traspuestas sin librerias externas y valida (A^T)^T = A."""

    def transpose(self, matrix_rows: Sequence[Sequence]) -> TransposeResult:
        matrix = to_fraction_matrix(matrix_rows)
        steps: List[str] = []

        filas = len(matrix)
        columnas = len(matrix[0])
        steps.append(f"Paso 1: La matriz A tiene dimension {filas} x {columnas}.")

        transpose = self._transpose(matrix)
        steps.append("Paso 2: Intercambiando filas por columnas para obtener A^T:")
        for j, fila_transpuesta in enumerate(transpose, start=1):
            columna_original = [matrix[i][j - 1] for i in range(filas)]
            steps.append(
                f"  Columna {j} de A {self._format_vector(columna_original)} -> "
                f"Fila {j} de A^T {self._format_vector(fila_transpuesta)}."
            )

        double_transpose = self._transpose(transpose)
        steps.append("Paso 3: Calculando (A^T)^T para confirmar que recuperamos la matriz A original.")

        holds = self._equal_matrices(matrix, double_transpose)
        conclusion = (
            "La traspuesta de A es la mostrada y se verifica la propiedad (A^T)^T = A."
            if holds
            else "La traspuesta se calculo, pero (A^T)^T no coincide con A (revisa los datos)."
        )

        property_name = "Doble traspuesta"
        property_statement = "(A^T)^T = A"
        defined_message = (
            f"La traspuesta siempre esta definida: A es {filas}x{columnas} y A^T es {columnas}x{filas}."
        )

        return TransposeResult(
            steps=steps,
            transpose=transpose,
            double_transpose=double_transpose,
            property_name=property_name,
            property_statement=property_statement,
            defined_message=defined_message,
            conclusion=conclusion,
        )

    @staticmethod
    def _transpose(matrix: List[List[Fraction]]) -> List[List[Fraction]]:
        return [[row[i] for row in matrix] for i in range(len(matrix[0]))]

    @staticmethod
    def _equal_matrices(A: List[List[Fraction]], B: List[List[Fraction]]) -> bool:
        if len(A) != len(B):
            return False
        if A and B and len(A[0]) != len(B[0]):
            return False
        for fila_a, fila_b in zip(A, B):
            if fila_a != fila_b:
                return False
        return True

    @staticmethod
    def _format_vector(values: Sequence[Fraction]) -> str:
        return "[" + ", ".join(str(value) for value in values) + "]"
