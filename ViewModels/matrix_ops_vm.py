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


def rank(A: Sequence[Sequence[Fraction]], name: str = "A") -> MatrixOpResult:
    if not A or not A[0]:
        raise ValueError("La matriz no puede ser vacía.")
    m, n = len(A), len(A[0])
    if any(len(row) != n for row in A):
        raise ValueError("Todas las filas deben tener la misma longitud.")

    mat = [[Fraction(value) for value in row] for row in A]
    row = 0
    pivots = 0
    steps: List[str] = [f"Inicio del cálculo del rango de {name} ({m}x{n})."]

    for col in range(n):
        pivot_row = None
        for r in range(row, m):
            if mat[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            steps.append(f"Columna {col + 1}: sin pivote, continúa.")
            continue
        if pivot_row != row:
            mat[row], mat[pivot_row] = mat[pivot_row], mat[row]
            steps.append(f"Se intercambian filas {row + 1} y {pivot_row + 1}.")
        pivot_val = mat[row][col]
        steps.append(f"Pivote en ({row + 1}, {col + 1}) = {pivot_val}. Se normaliza la fila {row + 1}.")
        mat[row] = [value / pivot_val for value in mat[row]]
        for r in range(m):
            if r == row:
                continue
            factor = mat[r][col]
            if factor == 0:
                continue
            mat[r] = [mat[r][c] - factor * mat[row][c] for c in range(n)]
            steps.append(f"Se elimina la entrada ({r + 1}, {col + 1}) con factor {factor}.")
        pivots += 1
        row += 1
        if row == m:
            break
    steps.append(f"Rango de {name}: {pivots}.")
    return MatrixOpResult(f"r({name})", [[Fraction(pivots)]], steps)


def verify_properties(
    A: Sequence[Sequence[Fraction]],
    B: Sequence[Sequence[Fraction]] | None,
    alpha: Fraction | None,
) -> List[Dict[str, object]]:
    """Verifica propiedades básicas de la traspuesta y operaciones.

    Propiedades verificadas:
    - (A^T)^T = A
    - r(A) = r(A^T)
    - Si A y B compatibles: (A+B)^T = A^T + B^T
    - Si A y B compatibles: (A-B)^T = A^T - B^T
    - Si r especificado: (rA)^T = r(A^T)
    - Si r y B compatibles: (r(A+B))^T = r(A^T + B^T)
    - Si AB definido: (AB)^T = B^T A^T
    """

    props: List[Dict[str, object]] = []
    scalar_symbol = "r"

    original = [list(map(Fraction, row)) for row in A]
    tA_res = transpose(A)
    tA = tA_res.result
    ttA = transpose(tA).result
    props.append({
        "propiedad": "(A^T)^T = A",
        "cumple": ttA == original,
        "detalle": "Dos traspuestas devuelven la matriz original.",
    })

    try:
        rank_A = rank(A, "A")
        rank_AT = rank(tA, "A^T")
        rank_val = rank_A.result[0][0]
        rank_t_val = rank_AT.result[0][0]
        props.append({
            "propiedad": "r(A) = r(A^T)",
            "cumple": rank_val == rank_t_val,
            "detalle": f"r(A) = {rank_val}, r(A^T) = {rank_t_val}.",
        })
    except Exception as exc:
        props.append({
            "propiedad": "r(A) = r(A^T)",
            "cumple": False,
            "detalle": f"No evaluable: {exc}",
        })

    if B is not None:
        try:
            sumAB = add(A, B).result
            tSum = transpose(sumAB).result
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

        try:
            diffAB = subtract(A, B).result
            tDiff = transpose(diffAB).result
            tB = transpose(B).result
            diff_t = subtract(tA, tB).result
            props.append({
                "propiedad": "(A-B)^T = A^T - B^T",
                "cumple": tDiff == diff_t,
                "detalle": "La traspuesta distribuye sobre la resta si A y B son conformables.",
            })
        except Exception as exc:
            props.append({
                "propiedad": "(A-B)^T = A^T - B^T",
                "cumple": False,
                "detalle": f"No evaluable: {exc}",
            })

    if alpha is not None:
        left = transpose(scalar_mult(alpha, A).result).result
        right = scalar_mult(alpha, tA).result
        props.append({
            "propiedad": f"({scalar_symbol}A)^T = {scalar_symbol}(A^T)",
            "cumple": left == right,
            "detalle": "La traspuesta y el producto por escalar conmutan.",
        })

    if alpha is not None and B is not None:
        try:
            sumAB = add(A, B).result
            scaled_sum = scalar_mult(alpha, sumAB).result
            left = transpose(scaled_sum).result
            tB = transpose(B).result
            sum_t = add(tA, tB).result
            right = scalar_mult(alpha, sum_t).result
            props.append({
                "propiedad": f"({scalar_symbol}(A+B))^T = {scalar_symbol}(A^T + B^T)",
                "cumple": left == right,
                "detalle": "El escalar puede factorizarse tras tomar la traspuesta de la suma.",
            })
        except Exception as exc:
            props.append({
                "propiedad": f"({scalar_symbol}(A+B))^T = {scalar_symbol}(A^T + B^T)",
                "cumple": False,
                "detalle": f"No evaluable: {exc}",
            })

    if B is not None:
        try:
            AB = multiply(A, B).result
            tAB = transpose(AB).result
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
