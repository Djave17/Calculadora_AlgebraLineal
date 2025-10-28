from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple

from ..base import ensure_square_matrix, to_fraction_matrix
from ..cofactores.metodoExpansioCofactores import compute_determinant_cofactors


@dataclass
class DeterminantPropertyResult:
    code: str
    label: str
    holds: bool
    verified: bool
    message: str
    examples: Dict[str, List[List[Fraction]]] = field(default_factory=dict)


def evaluate_determinant_properties(
    rows: Sequence[Sequence[Fraction | int | float]],
    determinant: Fraction,
) -> List[DeterminantPropertyResult]:
    matrix = to_fraction_matrix(rows)
    ensure_square_matrix(matrix)

    return [
        _property_zero_row_or_column(matrix, determinant),
        _property_proportional_rows_or_cols(matrix, determinant),
        _property_row_swap_sign(matrix, determinant),
        _property_row_scaling(matrix, determinant),
        _property_multiplicative(matrix, determinant),
    ]


def _property_zero_row_or_column(matrix: Sequence[Sequence[Fraction]], det_a: Fraction) -> DeterminantPropertyResult:
    zero_row = next((idx for idx, row in enumerate(matrix) if _is_zero_vector(row)), None)
    zero_col = next((idx for idx, col in enumerate(_columns(matrix)) if _is_zero_vector(col)), None)
    if zero_row is not None or zero_col is not None:
        location = f"fila {zero_row + 1}" if zero_row is not None else f"columna {zero_col + 1}"
        holds = det_a == 0
        message = (
            f"Se detectó {location} compuesta solo por ceros. El determinante calculado es {det_a}, "
            "confirmando que det(A) = 0."
        )
        return DeterminantPropertyResult(
            code="P1",
            label="Fila/columna nula implica det(A)=0",
            holds=holds,
            verified=True,
            message=message,
            examples={"A": _copy_matrix(matrix)},
        )

    example = [
        [Fraction(1), Fraction(0), Fraction(2)],
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(3), Fraction(-1), Fraction(1)],
    ]
    example_det = compute_determinant_cofactors(example).determinant
    message = (
        "A no posee filas ni columnas nulas, por lo que no se verifica directamente. "
        "Se muestra la matriz B con una fila nula; su determinante es 0."
    )
    return DeterminantPropertyResult(
        code="P1",
        label="Fila/columna nula implica det(A)=0",
        holds=example_det == 0,
        verified=False,
        message=message,
        examples={"B": example},
    )


def _property_proportional_rows_or_cols(matrix: Sequence[Sequence[Fraction]], det_a: Fraction) -> DeterminantPropertyResult:
    proportional_info = _find_proportional_vectors(matrix)
    if proportional_info:
        (kind, idx1, idx2, factor) = proportional_info
        holds = det_a == 0
        place = "filas" if kind == "row" else "columnas"
        message = (
            f"Se detectaron {place} {idx1 + 1} y {idx2 + 1} proporcionales (factor {factor}). "
            f"El determinante calculado es {det_a}, por lo que se confirma la propiedad."
        )
        return DeterminantPropertyResult(
            code="P2",
            label="Filas/columnas proporcionales hacen det(A)=0",
            holds=holds,
            verified=True,
            message=message,
            examples={"A": _copy_matrix(matrix)},
        )

    example = [
        [Fraction(1), Fraction(2), Fraction(3)],
        [Fraction(2), Fraction(4), Fraction(6)],
        [Fraction(0), Fraction(1), Fraction(1)],
    ]
    example_det = compute_determinant_cofactors(example).determinant
    message = (
        "No se hallaron filas o columnas proporcionales en A. "
        "La matriz B exhibe dos filas proporcionales y su determinante es 0."
    )
    return DeterminantPropertyResult(
        code="P2",
        label="Filas/columnas proporcionales hacen det(A)=0",
        holds=example_det == 0,
        verified=False,
        message=message,
        examples={"B": example},
    )


def _property_row_swap_sign(matrix: Sequence[Sequence[Fraction]], det_a: Fraction) -> DeterminantPropertyResult:
    if len(matrix) < 2:
        return DeterminantPropertyResult(
            code="P3",
            label="Intercambio de filas cambia el signo",
            holds=True,
            verified=False,
            message="En matrices 1x1 el intercambio de filas es trivial; se recuerda la propiedad teórica.",
            examples={"A": _copy_matrix(matrix)},
        )

    swapped = _swap_rows(matrix, 0, 1)
    det_swapped = compute_determinant_cofactors(swapped).determinant
    holds = det_swapped == -det_a
    message = (
        f"Se intercambiaron las filas 1 y 2. El nuevo determinante es {det_swapped}. "
        f"Comparando con det(A) = {det_a}, se verifica det(B) = -det(A)."
    )
    return DeterminantPropertyResult(
        code="P3",
        label="Intercambio de filas cambia el signo",
        holds=holds,
        verified=True,
        message=message,
        examples={"A": _copy_matrix(matrix), "B": swapped},
    )


def _property_row_scaling(matrix: Sequence[Sequence[Fraction]], det_a: Fraction) -> DeterminantPropertyResult:
    scalar = Fraction(2)
    scaled = _scale_row(matrix, 0, scalar)
    det_scaled = compute_determinant_cofactors(scaled).determinant
    holds = det_scaled == det_a * scalar
    message = (
        f"Se multiplicó la fila 1 por k={scalar}. det(A') = {det_scaled} y k·det(A) = {scalar * det_a}."
    )
    return DeterminantPropertyResult(
        code="P4",
        label="Escalar una fila escala det(A)",
        holds=holds,
        verified=True,
        message=message,
        examples={"A": _copy_matrix(matrix), "A'": scaled},
    )


def _property_multiplicative(matrix: Sequence[Sequence[Fraction]], det_a: Fraction) -> DeterminantPropertyResult:
    identity = _identity_matrix(len(matrix))
    product = _matrix_multiply(matrix, identity)
    det_product = compute_determinant_cofactors(product).determinant
    det_identity = compute_determinant_cofactors(identity).determinant
    holds = det_product == det_a * det_identity
    message = (
        "Se utilizó B = I para ejemplificar. det(A·I) = "
        f"{det_product} y det(A)·det(I) = {det_a * det_identity}."
    )
    return DeterminantPropertyResult(
        code="P5",
        label="det(AB) = det(A)·det(B)",
        holds=holds,
        verified=True,
        message=message,
        examples={"A": _copy_matrix(matrix), "B": identity, "AB": product},
    )


def _is_zero_vector(vector: Sequence[Fraction]) -> bool:
    return all(value == 0 for value in vector)


def _columns(matrix: Sequence[Sequence[Fraction]]) -> List[List[Fraction]]:
    return [
        [row[col_index] for row in matrix]
        for col_index in range(len(matrix[0]))
    ]


def _find_proportional_vectors(
    matrix: Sequence[Sequence[Fraction]],
) -> Tuple[str, int, int, Fraction] | None:
    for idx1 in range(len(matrix)):
        for idx2 in range(idx1 + 1, len(matrix)):
            factor = _proportional_factor(matrix[idx1], matrix[idx2])
            if factor is not None:
                return "row", idx1, idx2, factor
    cols = _columns(matrix)
    for idx1 in range(len(cols)):
        for idx2 in range(idx1 + 1, len(cols)):
            factor = _proportional_factor(cols[idx1], cols[idx2])
            if factor is not None:
                return "column", idx1, idx2, factor
    return None


def _proportional_factor(vec1: Sequence[Fraction], vec2: Sequence[Fraction]) -> Fraction | None:
    factor: Fraction | None = None
    for a, b in zip(vec1, vec2):
        if a == 0 and b == 0:
            continue
        if a == 0 or b == 0:
            return None
        current = Fraction(a) / Fraction(b)
        if factor is None:
            factor = current
        elif factor != current:
            return None
    return factor


def _swap_rows(matrix: Sequence[Sequence[Fraction]], i: int, j: int) -> List[List[Fraction]]:
    swapped = _copy_matrix(matrix)
    swapped[i], swapped[j] = swapped[j], swapped[i]
    return swapped


def _scale_row(matrix: Sequence[Sequence[Fraction]], index: int, scalar: Fraction) -> List[List[Fraction]]:
    scaled = _copy_matrix(matrix)
    scaled[index] = [scalar * value for value in scaled[index]]
    return scaled


def _identity_matrix(size: int) -> List[List[Fraction]]:
    return [
        [Fraction(1 if i == j else 0) for j in range(size)]
        for i in range(size)
    ]


def _matrix_multiply(
    A: Sequence[Sequence[Fraction]],
    B: Sequence[Sequence[Fraction]],
) -> List[List[Fraction]]:
    rows_a = len(A)
    cols_a = len(A[0]) if rows_a else 0
    rows_b = len(B)
    cols_b = len(B[0]) if rows_b else 0
    if cols_a != rows_b:
        raise ValueError("Dimensiones incompatibles para el producto AB.")
    result: List[List[Fraction]] = []
    for i in range(rows_a):
        row: List[Fraction] = []
        for j in range(cols_b):
            total = Fraction(0)
            for k in range(cols_a):
                total += A[i][k] * B[k][j]
            row.append(total)
        result.append(row)
    return result


def _copy_matrix(matrix: Sequence[Sequence[Fraction]]) -> List[List[Fraction]]:
    return [list(row) for row in matrix]
