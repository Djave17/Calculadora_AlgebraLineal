from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

from Operadores.determinantes import (
    DeterminantComputation,
    DeterminantStep,
    DeterminantTerm,
    evaluate_determinant_properties,
    compute_determinant_cofactors,
    compute_determinant_cramer,
    compute_determinant_sarrus,
    ensure_square_matrix,
    to_fraction_matrix,
    DeterminantPropertyResult,
)


@dataclass
class DeterminantTermVM:
    description: str
    sign: int
    product: Fraction
    factors: Tuple[Fraction, ...]
    positions: Tuple[Tuple[int, int], ...]
    level: int
    extra_detail: str | None = None
    minor: List[List[Fraction]] | None = None


@dataclass
class DeterminantStepVM:
    label: str
    description: str
    subtotal: Fraction | None
    snapshot: List[List[Fraction]] | None


@dataclass
class MatrixMultiplicationTermVM:
    left: Fraction
    right: Fraction
    product: Fraction


@dataclass
class MatrixMultiplicationCellVM:
    row: int
    col: int
    terms: List[MatrixMultiplicationTermVM]
    result: Fraction
    expected: Fraction


@dataclass
class DeterminantMultiplicativeDetailVM:
    left_label: str
    right_label: str
    product_label: str
    expected_label: str
    left_matrix: List[List[Fraction]]
    right_matrix: List[List[Fraction]]
    product_matrix: List[List[Fraction]]
    expected_matrix: List[List[Fraction]]
    det_left: Fraction
    det_right: Fraction
    det_product: Fraction
    det_expected: Fraction
    steps: List[MatrixMultiplicationCellVM] = field(default_factory=list)


@dataclass
class DeterminantMethodResultVM:
    method_id: str
    label: str
    justification: str
    determinant: Fraction | None
    terms: List[DeterminantTermVM] = field(default_factory=list)
    steps: List[DeterminantStepVM] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and self.determinant is not None


@dataclass
class DeterminantPropertyVM:
    code: str
    label: str
    holds: bool
    verified: bool
    message: str
    examples: Dict[str, List[List[Fraction]]]
    steps: List[str]
    multiplication: DeterminantMultiplicativeDetailVM | None = None


@dataclass
class DeterminantSummaryVM:
    determinant: Fraction
    is_invertible: bool
    message: str


@dataclass
class DeterminantAnalysisVM:
    matrix: List[List[Fraction]]
    methods: List[DeterminantMethodResultVM]
    properties: List[DeterminantPropertyVM]
    summary: DeterminantSummaryVM


METHOD_METADATA: Dict[str, Tuple[str, str]] = {
    "cofactors": (
        "Expansión por Cofactores",
        "Aplicable a cualquier matriz cuadrada; permite rastrear los signos de los cofactores y los productos parciales.",
    ),
    "cramer": (
        "Método de Cramer",
        "Orientado a matrices de orden reducido, mostrando cada combinación de factores (signo ± y producto).",
    ),
    "sarrus": (
        "Regla de Sarrus",
        "Solo matrices 3×3: suma diagonales principales y resta las secundarias con detalle de cada producto.",
    ),
}


class DeterminantViewModel:
    """Calcula determinantes mediante múltiples métodos y verifica propiedades teóricas."""

    def compute(self, rows: Sequence[Sequence[Fraction | int | float]]) -> DeterminantAnalysisVM:
        matrix = to_fraction_matrix(rows)
        ensure_square_matrix(matrix)

        method_results: List[DeterminantMethodResultVM] = []

        # Cofactors as baseline (always applicable)
        cofactors_result = self._run_method("cofactors", matrix, compute_determinant_cofactors)
        method_results.append(cofactors_result)
        if not cofactors_result.success or cofactors_result.determinant is None:
            raise ValueError("No fue posible calcular el determinante por cofactores.")

        determinant_value = cofactors_result.determinant

        # Attempt Cramer (limited to order <= MAX_CRAMER_ORDER)
        method_results.append(self._safe_run_method("cramer", matrix, compute_determinant_cramer))

        # Attempt Sarrus (only for 3x3)
        method_results.append(self._safe_run_method("sarrus", matrix, compute_determinant_sarrus))

        properties = self._build_properties(matrix, determinant_value)
        summary = self._build_summary(determinant_value)

        return DeterminantAnalysisVM(
            matrix=[row[:] for row in matrix],
            methods=method_results,
            properties=properties,
            summary=summary,
        )

    # --------------------------- Helpers --------------------------- #
    def _run_method(
        self,
        method_id: str,
        matrix: Sequence[Sequence[Fraction]],
        solver,
    ) -> DeterminantMethodResultVM:
        label, justification = METHOD_METADATA[method_id]
        computation = solver(matrix)
        return self._to_method_vm(method_id, label, justification, computation)

    def _safe_run_method(
        self,
        method_id: str,
        matrix: Sequence[Sequence[Fraction]],
        solver,
    ) -> DeterminantMethodResultVM:
        label, justification = METHOD_METADATA[method_id]
        try:
            computation = solver(matrix)
        except ValueError as exc:
            return DeterminantMethodResultVM(
                method_id=method_id,
                label=label,
                justification=justification,
                determinant=None,
                error=str(exc),
            )
        return self._to_method_vm(method_id, label, justification, computation)

    def _to_method_vm(
        self,
        method_id: str,
        label: str,
        justification: str,
        computation: DeterminantComputation,
    ) -> DeterminantMethodResultVM:
        terms = [
            DeterminantTermVM(
                description=term.description,
                sign=term.sign,
                product=term.product,
                factors=term.factors,
                positions=term.positions,
                level=term.level,
                extra_detail=term.extra_detail,
                minor=[row[:] for row in term.minor] if term.minor else None,
            )
            for term in computation.terms
        ]
        steps = [
            DeterminantStepVM(
                label=step.label,
                description=step.description,
                subtotal=step.subtotal,
                snapshot=[row[:] for row in step.snapshot] if step.snapshot else None,
            )
            for step in computation.steps
        ]
        return DeterminantMethodResultVM(
            method_id=method_id,
            label=label,
            justification=justification,
            determinant=computation.determinant,
            terms=terms,
            steps=steps,
            warnings=list(computation.warnings),
        )

    def _build_properties(
        self,
        matrix: Sequence[Sequence[Fraction]],
        determinant: Fraction,
    ) -> List[DeterminantPropertyVM]:
        property_results: List[DeterminantPropertyResult] = evaluate_determinant_properties(matrix, determinant)
        properties: List[DeterminantPropertyVM] = []
        for result in property_results:
            multiplication_detail: DeterminantMultiplicativeDetailVM | None = None
            detail = result.multiplication_detail
            if detail is not None:
                multiplication_detail = DeterminantMultiplicativeDetailVM(
                    left_label=detail.left_label,
                    right_label=detail.right_label,
                    product_label=detail.product_label,
                    expected_label=detail.expected_label,
                    left_matrix=[row[:] for row in detail.left_matrix],
                    right_matrix=[row[:] for row in detail.right_matrix],
                    product_matrix=[row[:] for row in detail.product_matrix],
                    expected_matrix=[row[:] for row in detail.expected_matrix],
                    det_left=detail.det_left,
                    det_right=detail.det_right,
                    det_product=detail.det_product,
                    det_expected=detail.det_expected,
                    steps=[
                        MatrixMultiplicationCellVM(
                            row=cell.row,
                            col=cell.col,
                            terms=[
                                MatrixMultiplicationTermVM(
                                    left=term.left,
                                    right=term.right,
                                    product=term.product,
                                )
                                for term in cell.terms
                            ],
                            result=cell.result,
                            expected=cell.expected,
                        )
                        for cell in detail.steps
                    ],
                )
            properties.append(
                DeterminantPropertyVM(
                    code=result.code,
                    label=result.label,
                    holds=result.holds,
                    verified=result.verified,
                    message=result.message,
                    examples={key: [row[:] for row in value] for key, value in result.examples.items()},
                    steps=list(result.steps),
                    multiplication=multiplication_detail,
                )
            )
        return properties

    def _build_summary(self, determinant: Fraction) -> DeterminantSummaryVM:
        is_invertible = determinant != 0
        message = (
            "El determinante es distinto de cero, por lo tanto A es invertible."
            if is_invertible
            else "El determinante es cero, la matriz no tiene inversa."
        )
        return DeterminantSummaryVM(
            determinant=determinant,
            is_invertible=is_invertible,
            message=message,
        )
