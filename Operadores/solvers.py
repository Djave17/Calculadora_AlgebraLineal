from __future__ import annotations

from typing import List, Sequence, Tuple

from fractions import Fraction

from Models.matriz import Matriz
from Operadores.matrices import matriz_from_rows
from Operadores.sistema_lineal import SistemaLineal, SistemaMatricial
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.SolucionGaussJordan.solucion import Solucion


def solve_Ax_b(
    A_rows: Sequence[Sequence],
    b_vector: Sequence,
    registrar: bool = True,
) -> Solucion:
    matriz = matriz_from_rows(A_rows)
    sistema = SistemaLineal(matriz, b_vector)
    solver = SolucionadorGaussJordan()
    return solver.resolver(sistema, registrar_pasos=registrar)


def solve_AX_B(
    A_rows: Sequence[Sequence],
    B_rows: Sequence[Sequence],
    registrar: bool = True,
) -> List[Tuple[int, Solucion]]:
    matriz = matriz_from_rows(A_rows)
    sistema_matricial = SistemaMatricial(matriz, B_rows)
    solver = SolucionadorGaussJordan()
    soluciones: List[Tuple[int, Solucion]] = []
    for idx, sistema in enumerate(sistema_matricial.sistemas_individuales()):
        solucion = solver.resolver(sistema, registrar_pasos=registrar)
        soluciones.append((idx, solucion))
    return soluciones


def classify_solution(solucion: Solucion) -> str:
    return solucion.estado


def null_space_from_rref(
    rref: Matriz,
    pivot_cols: List[int],
    num_variables: int,
) -> List[List[Fraction]]:
    free_vars = [j for j in range(num_variables) if j not in pivot_cols]
    if not free_vars:
        return []
    vectors: List[List[Fraction]] = []
    for free in free_vars:
        direction = [Fraction(0) for _ in range(num_variables)]
        direction[free] = Fraction(1)
        for pivot_col in pivot_cols:
            fila = _find_pivot_row(rref, pivot_col)
            coef = rref.obtener(fila, free)
            if coef != 0:
                direction[pivot_col] = -coef
        vectors.append(direction)
    return vectors


def _find_pivot_row(matriz: Matriz, pivot_col: int) -> int:
    for i in range(matriz.filas):
        if matriz.obtener(i, pivot_col) == Fraction(1):
            return i
    for i in range(matriz.filas):
        if matriz.obtener(i, pivot_col) != 0:
            return i
    raise RuntimeError("No se encontró fila de pivote.")
