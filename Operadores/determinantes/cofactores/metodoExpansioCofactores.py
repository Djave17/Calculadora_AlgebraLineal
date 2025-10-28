from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple

from ..base import (
    DeterminantComputation,
    DeterminantStep,
    DeterminantTerm,
    ensure_square_matrix,
    to_fraction_matrix,
)


def compute_determinant_cofactors(
    rows: Sequence[Sequence[Fraction | int | float]],
) -> DeterminantComputation:
    matrix = to_fraction_matrix(rows)
    ensure_square_matrix(matrix)

    steps: List[DeterminantStep] = []
    terms: List[DeterminantTerm] = []
    determinant = _expand_with_cofactors(matrix, depth=0, steps=steps, terms=terms, path=())
    steps.append(
        DeterminantStep(
            label="Resultado",
            description=f"Determinante por cofactores: det(A) = {determinant}.",
            subtotal=determinant,
        )
    )
    return DeterminantComputation(
        method_id="cofactors",
        determinant=determinant,
        terms=terms,
        steps=steps,
    )


def _expand_with_cofactors(
    matrix: Sequence[Sequence[Fraction]],
    depth: int,
    steps: List[DeterminantStep],
    terms: List[DeterminantTerm],
    path: Tuple[Tuple[int, int], ...],
) -> Fraction:
    order = len(matrix)
    if order == 1:
        value = matrix[0][0]
        steps.append(
            DeterminantStep(
                label=f"Nivel {depth}",
                description=f"Matriz 1x1, det = {value}.",
                subtotal=value,
                snapshot=[[matrix[0][0]]],
            )
        )
        return Fraction(value)

    selected_row = _select_expansion_row(matrix)
    zero_count = sum(1 for value in matrix[selected_row] if value == 0)
    steps.append(
        DeterminantStep(
            label=f"Nivel {depth}",
            description=(
                f"Expansion por la fila {selected_row + 1} (contiene {zero_count} "
                f"{'ceros' if zero_count != 1 else 'cero'})."
            ),
            snapshot=[list(row) for row in matrix],
        )
    )

    total = Fraction(0)
    for col, element in enumerate(matrix[selected_row]):
        sign = 1 if (selected_row + col) % 2 == 0 else -1
        cofactor_label = f"a[{selected_row + 1},{col + 1}]"
        if element == 0:
            steps.append(
                DeterminantStep(
                    label=f"Nivel {depth}",
                    description=f"El elemento {cofactor_label} es 0; su cofactor aporta 0.",
                    subtotal=total,
                )
            )
            continue

        minor_matrix = _minor(matrix, selected_row, col)
        minor_det = _expand_with_cofactors(
            minor_matrix, depth + 1, steps, terms, path + ((selected_row, col),)
        )
        contribution = sign * element * minor_det
        total += contribution
        sign_text = "+1" if sign > 0 else "-1"
        description = (
            f"Cofactor C{selected_row + 1}{col + 1}: (-1)^({selected_row + 1}+{col + 1}) = {sign_text}; "
            f"{cofactor_label} = {element}; det(M{selected_row + 1}{col + 1}) = {minor_det}. "
            f"Aporte: {sign_text} * {element} * {minor_det} = {contribution}. "
            f"Acumulado: {total}."
        )
        steps.append(
            DeterminantStep(
                label=f"Nivel {depth}",
                description=description,
                subtotal=total,
            )
        )
        terms.append(
            DeterminantTerm(
                description=f"Cofactor en {cofactor_label}",
                sign=sign,
                product=contribution,
                factors=(Fraction(element), Fraction(minor_det)),
                positions=path + ((selected_row, col),),
                level=depth,
                minor=[list(row) for row in minor_matrix],
                extra_detail=(
                    f"Signo {sign_text}, elemento {element}, menor con determinante {minor_det}."
                ),
            )
        )

    if total == 0:
        steps.append(
            DeterminantStep(
                label=f"Nivel {depth}",
                description="La suma de cofactores en este nivel es 0.",
                subtotal=total,
            )
        )
    return total


def _select_expansion_row(matrix: Sequence[Sequence[Fraction]]) -> int:
    zero_counts = [
        (index, sum(1 for value in row if value == 0))
        for index, row in enumerate(matrix)
    ]
    zero_counts.sort(key=lambda item: (-item[1], item[0]))
    return zero_counts[0][0]


def _minor(matrix: Sequence[Sequence[Fraction]], row_index: int, col_index: int) -> List[List[Fraction]]:
    minor: List[List[Fraction]] = []
    for i, row in enumerate(matrix):
        if i == row_index:
            continue
        minor_row: List[Fraction] = []
        for j, value in enumerate(row):
            if j == col_index:
                continue
            minor_row.append(value)
        minor.append(minor_row)
    return minor
