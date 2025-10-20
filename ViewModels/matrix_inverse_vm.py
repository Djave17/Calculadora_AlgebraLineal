from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Sequence

from Models.matriz import Matriz
from Operadores.estrategia_pivoteo import PivoteoParcial
from Operadores.reductor_escalonado import ReductorEscalonado
from Operadores.registrador import PasoReduccion, RegistradorOperaciones
from ViewModels.resolucion_matriz_vm import StepVM


@dataclass
class PropertyCheckVM:
    code: str
    label: str
    holds: bool
    interpretation: str


@dataclass
class MatrixInverseResultVM:
    is_invertible: bool
    message: str
    initial_augmented: List[List[Fraction]]
    final_augmented: List[List[Fraction]]
    steps: List[StepVM]
    properties: List[PropertyCheckVM]
    inverse_matrix: Optional[List[List[Fraction]]] = None
    pivot_columns: List[int] = field(default_factory=list)


class MatrixInverseViewModel:
    """Calcula la inversa de una matriz cuadrada mostrando pasos Gauss-Jordan."""

    def __init__(self, eps: float = 1e-12) -> None:
        self._eps = eps
        self._reductor = ReductorEscalonado(eps=eps)
        self._pivoteo = PivoteoParcial()

    def compute(self, rows: Sequence[Sequence[Fraction | int | float]]) -> MatrixInverseResultVM:
        matrix = self._to_fraction_matrix(rows)
        n = len(matrix)
        if n == 0 or len(matrix[0]) == 0:
            raise ValueError("La matriz no puede ser vacía.")
        if any(len(row) != n for row in matrix):
            raise ValueError("La matriz debe ser cuadrada para poder invertirla.")

        identity = self._identity_matrix(n)
        augmented_data = [row[:] + identity[idx] for idx, row in enumerate(matrix)]
        original_augmented = self._copy_matrix(augmented_data)

        registrador = RegistradorOperaciones()
        resultado = self._reductor.a_forma_escalonada_reducida(
            matriz_aumentada=Matriz(augmented_data),
            num_variables=n,
            pivoteo=self._pivoteo,
            registrador=registrador,
        )

        rref = resultado.matriz_rref.como_lista()
        pivot_cols = list(resultado.columnas_pivote)
        full_rank = len(pivot_cols) == n
        left_block = [row[:n] for row in rref]
        right_block = [row[n:] for row in rref]
        is_identity_left = full_rank and left_block == self._identity_matrix(n)

        steps = self._build_steps(registrador.historial.pasos, original_augmented)
        message: str
        inverse_matrix: Optional[List[List[Fraction]]]
        if is_identity_left:
            inverse_matrix = right_block
            message = "Matriz invertible: se obtuvo [I | A⁻¹]."
        else:
            inverse_matrix = None
            message = "La matriz no es invertible porque no tiene pivote en cada fila."

        properties = self._build_properties(n, full_rank)

        return MatrixInverseResultVM(
            is_invertible=is_identity_left,
            message=message,
            initial_augmented=original_augmented,
            final_augmented=rref,
            steps=steps,
            properties=properties,
            inverse_matrix=inverse_matrix,
            pivot_columns=pivot_cols,
        )

    # ---------------------------- Internos ---------------------------- #
    def _build_steps(self, pasos: List[PasoReduccion], inicial: List[List[Fraction]]) -> List[StepVM]:
        steps: List[StepVM] = [
            StepVM(
                number=0,
                operation="CONSTRUCCION",
                description="Construcción de la matriz aumentada [A | I].",
                before_matrix=None,
                after_matrix=self._copy_matrix(inicial),
                affected_rows=[],
                factor=None,
                pivot_row=None,
                pivot_col=None,
            )
        ]
        for paso in pasos:
            steps.append(
                StepVM(
                    number=paso.numero,
                    operation=paso.operacion,
                    description=paso.descripcion or paso.operacion,
                    before_matrix=self._fraction_matrix(paso.antes),
                    after_matrix=self._fraction_matrix(paso.despues),
                    pivot_row=paso.pivote_fila,
                    pivot_col=paso.pivote_col,
                    affected_rows=list(paso.filas_afectadas or []),
                    factor=self._fraction_value(paso.factor),
                )
            )
        return steps

    def _build_properties(self, n: int, full_rank: bool) -> List[PropertyCheckVM]:
        interpretation_true = {
            "c": "A es invertible porque cada fila posee un pivote (rango completo).",
            "d": "El sistema homogéneo A x = 0 solo admite la solución trivial; existe A⁻¹.",
            "e": "Las columnas de A son linealmente independientes; conforman una base de ℝⁿ.",
        }
        interpretation_false = {
            "c": "Faltan pivotes en alguna fila; el rango es menor que n.",
            "d": "Existen soluciones no triviales para A x = 0; la inversa no existe.",
            "e": "Las columnas son dependientes lineales; no pueden generar ℝⁿ.",
        }
        properties_specs = [
            ("c", "La matriz A tiene n posiciones pivote."),
            ("d", "La ecuación A x = 0 tiene solamente la solución trivial."),
            ("e", "Las columnas de A forman un conjunto linealmente independiente."),
        ]
        return [
            PropertyCheckVM(
                code=code,
                label=label,
                holds=full_rank,
                interpretation=(interpretation_true if full_rank else interpretation_false)[code],
            )
            for code, label in properties_specs
        ]

    def _identity_matrix(self, size: int) -> List[List[Fraction]]:
        return [
            [Fraction(1 if i == j else 0) for j in range(size)]
            for i in range(size)
        ]

    def _to_fraction_matrix(self, rows: Sequence[Sequence[Fraction | int | float]]) -> List[List[Fraction]]:
        matrix: List[List[Fraction]] = []
        for row in rows:
            matrix.append([self._fraction_value(value) for value in row])
        if matrix and any(len(row) != len(matrix[0]) for row in matrix):
            raise ValueError("Todas las filas deben tener la misma longitud.")
        return matrix

    def _fraction_matrix(self, data: Optional[List[List[float | Fraction]]]) -> Optional[List[List[Fraction]]]:
        if data is None:
            return None
        return [[self._fraction_value(value) for value in row] for row in data]

    def _fraction_value(self, value: float | int | Fraction | None) -> Fraction:
        if value is None:
            return Fraction(0)
        if isinstance(value, Fraction):
            return value
        if isinstance(value, float):
            return Fraction(value).limit_denominator()
        if isinstance(value, int):
            return Fraction(value)
        return Fraction(str(value))

    def _copy_matrix(self, data: List[List[Fraction]]) -> List[List[Fraction]]:
        return [[cell for cell in row] for row in data]
