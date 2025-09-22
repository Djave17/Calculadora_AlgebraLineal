from __future__ import annotations

from fractions import Fraction
from typing import Iterable, List, Sequence

from Models.matriz import Matriz


def to_fraction_matrix(rows: Sequence[Sequence]) -> List[List[Fraction]]:
    matrix: List[List[Fraction]] = []
    for fila in rows:
        matrix.append([Fraction(elem) for elem in fila])
    if not matrix or not matrix[0]:
        raise ValueError("La matriz no puede ser vacía.")
    num_cols = len(matrix[0])
    for fila in matrix:
        if len(fila) != num_cols:
            raise ValueError("Todas las filas deben tener la misma longitud.")
    return matrix


def matriz_from_rows(rows: Sequence[Sequence]) -> Matriz:
    return Matriz(to_fraction_matrix(rows))


def construir_matriz_aumentada(
    A_rows: Sequence[Sequence],
    b_columns: Sequence[Sequence],
) -> Matriz:
    A = to_fraction_matrix(A_rows)
    B = to_fraction_matrix(b_columns)
    if len(A) != len(B):
        raise ValueError("A y B deben tener el mismo número de filas para formar [A|B].")
    for fila_a, fila_b in zip(A, B):
        fila_a.extend(fila_b)
    return Matriz(A)


def rango(matriz: Matriz) -> int:
    count = 0
    for i in range(matriz.filas):
        if any(matriz.obtener(i, j) != 0 for j in range(matriz.columnas)):
            count += 1
    return count
