from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class DeterminantStep:
    """Describe un paso textual dentro del cálculo de un determinante."""

    label: str
    description: str
    subtotal: Fraction | None = None
    snapshot: List[List[Fraction]] | None = None


@dataclass(frozen=True)
class DeterminantTerm:
    """Representa un término parcial del determinante."""

    description: str
    sign: int
    product: Fraction
    factors: Tuple[Fraction, ...]
    positions: Tuple[Tuple[int, int], ...]
    level: int = 0
    minor: List[List[Fraction]] | None = None
    extra_detail: str | None = None


@dataclass
class DeterminantComputation:
    """Resultado detallado de un método de determinante."""

    method_id: str
    determinant: Fraction
    terms: List[DeterminantTerm] = field(default_factory=list)
    steps: List[DeterminantStep] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def to_fraction_matrix(rows: Sequence[Sequence[Fraction | int | float]]) -> List[List[Fraction]]:
    matrix: List[List[Fraction]] = []
    for row in rows:
        matrix.append([_fraction_value(value) for value in row])
    if matrix:
        width = len(matrix[0])
        for row in matrix:
            if len(row) != width:
                raise ValueError("Todas las filas deben tener la misma longitud.")
    return matrix


def ensure_square_matrix(matrix: Sequence[Sequence[Fraction]]) -> None:
    if not matrix or not matrix[0]:
        raise ValueError("La matriz no puede ser vacía.")
    rows = len(matrix)
    cols = len(matrix[0])
    if rows != cols:
        raise ValueError("La matriz debe ser cuadrada.")
    for row in matrix:
        if len(row) != cols:
            raise ValueError("Todas las filas deben tener la misma longitud.")


def extend_matrix_with_columns(matrix: Sequence[Sequence[Fraction]], extra_columns: int) -> List[List[Fraction]]:
    if extra_columns <= 0:
        return [list(row) for row in matrix]
    return [list(row) + list(row[:extra_columns]) for row in matrix]


def extend_matrix_with_rows(matrix: Sequence[Sequence[Fraction]], extra_rows: int) -> List[List[Fraction]]:
    """Append the first ``extra_rows`` rows at the end to visualize Sarrus by rows."""
    if extra_rows <= 0:
        return [list(row) for row in matrix]
    base = [list(row) for row in matrix]
    return base + [list(matrix[i]) for i in range(min(extra_rows, len(matrix)))]


def _fraction_value(value: Fraction | int | float) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(value).limit_denominator(10_000)
    raise TypeError("Solo se admiten valores numéricos reales.")


def compute_parity(permutation: Iterable[int]) -> int:
    perm = list(permutation)
    visited = [False] * len(perm)
    transpositions = 0
    for i in range(len(perm)):
        if visited[i]:
            continue
        cycle_length = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            cycle_length += 1
        if cycle_length > 0:
            transpositions += cycle_length - 1
    return 1 if transpositions % 2 == 0 else -1
