from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from typing import List, Sequence, Tuple

from ..base import (
    DeterminantComputation,
    DeterminantStep,
    DeterminantTerm,
    compute_parity,
    ensure_square_matrix,
    to_fraction_matrix,
)

MAX_CRAMER_ORDER = 5


def compute_determinant_cramer(
    rows: Sequence[Sequence[Fraction | int | float]],
) -> DeterminantComputation:
    matrix = to_fraction_matrix(rows)
    ensure_square_matrix(matrix)
    order = len(matrix)
    if order > MAX_CRAMER_ORDER:
        raise ValueError(
            "El metodo de Cramer solo se recomienda hasta matrices de orden 5 por su complejidad factorial."
        )

    terms: List[DeterminantTerm] = []
    steps: List[DeterminantStep] = []
    determinant = Fraction(0)

    steps.append(
        DeterminantStep(
            label="Paso 0",
            description=(
                "Definición de Cramer-Leibniz: se recorren todas las permutaciones de columnas. "
                "Cada término aporta su signo (+/-) multiplicado por el producto de los factores seleccionados."
            ),
            snapshot=[row[:] for row in matrix],
        )
    )

    for idx, perm in enumerate(permutations(range(order)), start=1):
        sign = compute_parity(perm)
        factors: List[Fraction] = []
        positions: List[Tuple[int, int]] = []
        product = Fraction(1)
        for row_index, col_index in enumerate(perm):
            value = matrix[row_index][col_index]
            factors.append(value)
            positions.append((row_index, col_index))
            product *= value
        signed_value = product * sign
        determinant += signed_value
        mapping = ", ".join(f"fila {i + 1} -> columna {col + 1}" for i, col in enumerate(perm))
        sign_text = "+1" if sign > 0 else "-1"
        terms.append(
            DeterminantTerm(
                description=f"Permutación {idx}: {mapping}",
                sign=sign,
                product=signed_value,
                factors=tuple(factors),
                positions=tuple(positions),
                extra_detail=f"Signo algebraico {sign_text} y producto {format_factors(factors)} = {product}",
            )
        )
        steps.append(
            DeterminantStep(
                label=f"Paso {idx}",
                description=(
                    f"Permutación {idx} con paridad {'par' if sign > 0 else 'impar'} (signo {sign_text}). "
                    f"Producto parcial {format_factors(factors)} = {product}; "
                    f"aportación {sign_text} × {product} = {signed_value}. "
                    f"Acumulado: det(A) = {determinant}."
                ),
                subtotal=determinant,
            )
        )

    steps.append(
        DeterminantStep(
            label="Resultado",
            description=f"Suma de terminos: det(A) = {determinant}.",
            subtotal=determinant,
        )
    )

    return DeterminantComputation(
        method_id="cramer",
        determinant=determinant,
        terms=terms,
        steps=steps,
    )


def format_factors(factors: Sequence[Fraction]) -> str:
    return " * ".join(str(value) for value in factors)
