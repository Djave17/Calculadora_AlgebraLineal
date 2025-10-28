from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple

from ..base import (
    DeterminantComputation,
    DeterminantStep,
    DeterminantTerm,
    ensure_square_matrix,
    extend_matrix_with_columns,
    to_fraction_matrix,
)

SARRUS_ORDER = 3


def compute_determinant_sarrus(
    rows: Sequence[Sequence[Fraction | int | float]],
) -> DeterminantComputation:
    matrix = to_fraction_matrix(rows)
    ensure_square_matrix(matrix)
    if len(matrix) != SARRUS_ORDER:
        raise ValueError("La regla de Sarrus solo aplica a matrices de 3x3.")

    extended = extend_matrix_with_columns(matrix, 2)
    steps: List[DeterminantStep] = [
        DeterminantStep(
            label="Paso 0",
            description=(
                "Se replica la matriz anexando las dos primeras columnas al final para visualizar diag. descendentes y ascendentes."
            ),
            snapshot=[row[:] for row in extended],
        )
    ]

    positive_terms, positive_sum, positive_steps = _diagonal_terms(
        matrix, extended, forward=True
    )
    negative_terms, negative_sum, negative_steps = _diagonal_terms(
        matrix, extended, forward=False
    )

    steps.extend(positive_steps)
    steps.extend(negative_steps)

    determinant = positive_sum - negative_sum

    steps.append(
        DeterminantStep(
            label="Resultado",
            description=(
                f"det(A) = suma(descendentes) - suma(ascendentes) = {positive_sum} - {negative_sum} = {determinant}."
            ),
            subtotal=determinant,
        )
    )

    terms = positive_terms + negative_terms
    return DeterminantComputation(
        method_id="sarrus",
        determinant=determinant,
        terms=terms,
        steps=steps,
    )


def _diagonal_terms(
    original: Sequence[Sequence[Fraction]],
    extended: Sequence[Sequence[Fraction]],
    forward: bool,
) -> Tuple[List[DeterminantTerm], Fraction, List[DeterminantStep]]:
    order = len(original)
    terms: List[DeterminantTerm] = []
    steps: List[DeterminantStep] = []
    total = Fraction(0)
    descriptor = "descendente" if forward else "ascendente"
    sign_value = 1 if forward else -1
    for start in range(order):
        product = Fraction(1)
        factors: List[Fraction] = []
        positions: List[Tuple[int, int]] = []
        for offset in range(order):
            row = offset if forward else (order - 1 - offset)
            col = start + offset
            value = extended[row][col]
            product *= value
            factors.append(value)
            original_col = col if col < len(original) else col - len(original)
            original_row = row if forward else order - 1 - offset
            positions.append((original_row, original_col))
        total += product
        label = f"Diagonal {descriptor} {start + 1}"
        sign_text = "+1" if forward else "-1"
        terms.append(
            DeterminantTerm(
                description=label,
                sign=sign_value,
                product=product if forward else -product,
                factors=tuple(factors),
                positions=tuple(positions),
                extra_detail=f"Signo {sign_text} con producto {format_factors(factors)} = {product}",
            )
        )
        note = "Se suma al acumulado." if forward else "Se restara del acumulado final."
        steps.append(
            DeterminantStep(
                label=label,
                description=(
                    f"Diagonal {descriptor} con factores {format_factors(factors)} = {product}. "
                    f"Signo {sign_text}; aporte {sign_text} * {product}. {note}"
                ),
                subtotal=total,
            )
        )
    return terms, total, steps


def format_factors(factors: Sequence[Fraction]) -> str:
    return " * ".join(str(value) for value in factors)
