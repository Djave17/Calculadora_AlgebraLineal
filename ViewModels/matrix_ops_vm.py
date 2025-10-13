from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Sequence, Tuple, Dict


@dataclass
class MatrixOpResult:
    name: str
    result: List[List[Fraction]]
    steps: List[str]


def _check_same_shape(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> Tuple[int, int]:
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden ser vacías.")
    m, n = len(A), len(A[0])
    mb, nb = len(B), len(B[0])
    if any(len(row) != n for row in A):
        raise ValueError("Todas las filas de A deben tener la misma longitud.")
    if any(len(row) != nb for row in B):
        raise ValueError("Todas las filas de B deben tener la misma longitud.")
    if m != mb or n != nb:
        raise ValueError("Para suma/resta, A y B deben tener igual número de filas y columnas.")
    return m, n


def add(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> MatrixOpResult:
    m, n = _check_same_shape(A, B)
    C: List[List[Fraction]] = []
    steps: List[str] = [f"Suma elemento a elemento (dim {m}×{n})"]
    for i in range(m):
        row: List[Fraction] = []
        for j in range(n):
            val = Fraction(A[i][j]) + Fraction(B[i][j])
            steps.append(f"C[{i+1},{j+1}] = {A[i][j]} + {B[i][j]} = {val}")
            row.append(val)
        C.append(row)
    return MatrixOpResult("A + B", C, steps)


def subtract(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> MatrixOpResult:
    m, n = _check_same_shape(A, B)
    C: List[List[Fraction]] = []
    steps: List[str] = [f"Resta elemento a elemento (dim {m}×{n})"]
    for i in range(m):
        row: List[Fraction] = []
        for j in range(n):
            val = Fraction(A[i][j]) - Fraction(B[i][j])
            steps.append(f"C[{i+1},{j+1}] = {A[i][j]} - {B[i][j]} = {val}")
            row.append(val)
        C.append(row)
    return MatrixOpResult("A - B", C, steps)


def scalar_mult(alpha: Fraction, A: Sequence[Sequence[Fraction]]) -> MatrixOpResult:
    if not A or not A[0]:
        raise ValueError("La matriz A no puede ser vacía.")
    m, n = len(A), len(A[0])
    if any(len(row) != n for row in A):
        raise ValueError("Todas las filas de A deben tener la misma longitud.")
    C: List[List[Fraction]] = []
    steps: List[str] = [f"Multiplicación por escalar α = {alpha} (dim {m}×{n})"]
    for i in range(m):
        row: List[Fraction] = []
        for j in range(n):
            val = Fraction(alpha) * Fraction(A[i][j])
            steps.append(f"C[{i+1},{j+1}] = {alpha} · {A[i][j]} = {val}")
            row.append(val)
        C.append(row)
    return MatrixOpResult("α·A", C, steps)


def multiply(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> MatrixOpResult:
    if not A or not A[0] or not B or not B[0]:
        raise ValueError("Las matrices no pueden ser vacías.")
    m, n = len(A), len(A[0])
    n2, p = len(B), len(B[0])
    if any(len(row) != n for row in A):
        raise ValueError("Todas las filas de A deben tener la misma longitud.")
    if any(len(row) != p for row in B):
        raise ValueError("Todas las filas de B deben tener la misma longitud.")
    if n != n2:
        raise ValueError(
            "Para A·B, el número de columnas de A debe coincidir con el número de filas de B."
        )
    C: List[List[Fraction]] = []
    steps: List[str] = [f"Producto matricial A·B: A es {m}×{n}, B es {n2}×{p}"]
    for i in range(m):
        row: List[Fraction] = []
        for j in range(p):
            terms = [Fraction(A[i][k]) * Fraction(B[k][j]) for k in range(n)]
            val = sum(terms)
            expr = " + ".join(f"{A[i][k]}·{B[k][j]}" for k in range(n))
            steps.append(f"C[{i+1},{j+1}] = {expr} = {val}")
            row.append(val)
        C.append(row)
    return MatrixOpResult("A·B", C, steps)


def transpose(A: Sequence[Sequence[Fraction]]) -> MatrixOpResult:
    if not A or not A[0]:
        raise ValueError("La matriz no puede ser vacía.")
    m, n = len(A), len(A[0])
    if any(len(row) != n for row in A):
        raise ValueError("Todas las filas deben tener la misma longitud.")
    C: List[List[Fraction]] = [[Fraction(0) for _ in range(m)] for _ in range(n)]
    steps: List[str] = [f"Traspuesta: (A^T)[j,i] = A[i,j] (A es {m}×{n})"]
    for i in range(m):
        for j in range(n):
            C[j][i] = Fraction(A[i][j])
            steps.append(f"C[{j+1},{i+1}] = A[{i+1},{j+1}] = {A[i][j]}")
    return MatrixOpResult("A^T", C, steps)


def verify_properties(
    A: Sequence[Sequence[Fraction]],
    B: Sequence[Sequence[Fraction]] | None,
    alpha: Fraction | None,
) -> List[Dict[str, object]]:
    """Verifica propiedades básicas de la traspuesta y operaciones.

    Propiedades verificadas:
    - (A^T)^T = A
    - Si A y B compatibles: (A+B)^T = A^T + B^T
    - Si α especificado: (αA)^T = α(A^T)
    - Si AB definido: (AB)^T = B^T A^T
    """

    props: List[Dict[str, object]] = []

    # (A^T)^T = A
    tA = transpose(A).result
    ttA = transpose(tA).result
    ok = ttA == [list(map(Fraction, row)) for row in A]
    props.append({
        "propiedad": "(A^T)^T = A",
        "cumple": ok,
        "detalle": "Dos traspuestas devuelven la matriz original.",
    })

    # (A+B)^T = A^T + B^T
    if B is not None:
        try:
            sumAB = add(A, B).result
            tSum = transpose(sumAB).result
            tA = transpose(A).result
            tB = transpose(B).result
            sumt = add(tA, tB).result
            props.append({
                "propiedad": "(A+B)^T = A^T + B^T",
                "cumple": tSum == sumt,
                "detalle": "La traspuesta distribuye sobre la suma si A y B son conformables.",
            })
        except Exception as exc:
            props.append({
                "propiedad": "(A+B)^T = A^T + B^T",
                "cumple": False,
                "detalle": f"No evaluable: {exc}",
            })

    # (αA)^T = α(A^T)
    if alpha is not None:
        tA = transpose(A).result
        left = transpose(scalar_mult(alpha, A).result).result
        right = scalar_mult(alpha, tA).result
        props.append({
            "propiedad": "(αA)^T = α(A^T)",
            "cumple": left == right,
            "detalle": "La traspuesta con escalar conmute.",
        })

    # (AB)^T = B^T A^T
    if B is not None:
        try:
            AB = multiply(A, B).result
            tAB = transpose(AB).result
            tA = transpose(A).result
            tB = transpose(B).result
            right = multiply(tB, tA).result
            props.append({
                "propiedad": "(AB)^T = B^T A^T",
                "cumple": tAB == right,
                "detalle": "La traspuesta invierte el orden del producto.",
            })
        except Exception as exc:
            props.append({
                "propiedad": "(AB)^T = B^T A^T",
                "cumple": False,
                "detalle": f"No evaluable: {exc}",
            })

    return props

