from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Sequence

_MAX_DENOMINATOR = 10_000

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
class MultiplicationTermVM:
    left: Fraction
    right: Fraction
    product: Fraction


@dataclass
class MultiplicationCellVM:
    row: int
    col: int
    terms: List[MultiplicationTermVM]
    result: Fraction
    expected: Fraction


@dataclass
class VerificationResultVM:
    can_verify: bool
    holds: bool
    message: str
    product: Optional[List[List[Fraction]]] = None
    identity: Optional[List[List[Fraction]]] = None
    steps: List[MultiplicationCellVM] = field(default_factory=list)


@dataclass
class MatrixInverseResultVM:
    is_invertible: bool
    message: str
    original_matrix: List[List[Fraction]]
    initial_augmented: List[List[Fraction]]
    final_augmented: List[List[Fraction]]
    steps: List[StepVM]
    properties: List[PropertyCheckVM]
    verification: VerificationResultVM
    determinant: Fraction
    determinant_steps: List[StepVM]
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
        original_matrix = self._copy_matrix(matrix)
        n = len(matrix)
        if n == 0 or len(matrix[0]) == 0:
            raise ValueError("La matriz no puede ser vacia.")
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

        steps = self._build_steps(
            registrador.historial.pasos,
            original_augmented,
            "Construccion de la matriz aumentada [A | I].",
        )
        if is_identity_left:
            inverse_matrix = right_block
            message = "Matriz invertible (no singular): se obtuvo [I | A^-1]."
        else:
            inverse_matrix = None
            message = "Matriz no invertible (singular): faltan pivotes para obtener identidad."

        determinant_value, determinant_steps = self._compute_determinant(original_matrix)
        verification = self._build_verification(original_matrix, inverse_matrix, n, is_identity_left)
        properties = self._build_properties(full_rank, verification)

        return MatrixInverseResultVM(
            is_invertible=is_identity_left,
            message=message,
            original_matrix=original_matrix,
            initial_augmented=original_augmented,
            final_augmented=rref,
            steps=steps,
            properties=properties,
            verification=verification,
            determinant=determinant_value,
            determinant_steps=determinant_steps,
            inverse_matrix=inverse_matrix,
            pivot_columns=pivot_cols,
        )

    # ---------------------------- Internos ---------------------------- #
    def _build_steps(
        self,
        pasos: List[PasoReduccion],
        inicial: List[List[Fraction]],
        initial_description: str,
        initial_operation: str = "CONSTRUCCION",
    ) -> List[StepVM]:
        steps: List[StepVM] = [
            StepVM(
                number=0,
                operation=initial_operation,
                description=initial_description,
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

    def _build_properties(self, full_rank: bool, verification: VerificationResultVM) -> List[PropertyCheckVM]:
        interpretation_true = {
            "c": "A es invertible porque cada fila posee un pivote (rango completo).",
            "d": "El sistema homogeneo A x = 0 solo admite la solucion trivial; existe A^-1.",
            "e": "Las columnas de A son linealmente independientes; conforman una base de R^n.",
        }
        interpretation_false = {
            "c": "Faltan pivotes en alguna fila; el rango es menor que n.",
            "d": "Existen soluciones no triviales para A x = 0; la inversa no existe.",
            "e": "Las columnas son dependientes lineales; no pueden generar R^n.",
        }
        properties_specs = [
            ("c", "La matriz A tiene n posiciones pivote."),
            ("d", "La ecuacion A x = 0 tiene solamente la solucion trivial."),
            ("e", "Las columnas de A forman un conjunto linealmente independiente."),
        ]
        props = [
            PropertyCheckVM(
                code=code,
                label=label,
                holds=full_rank,
                interpretation=(interpretation_true if full_rank else interpretation_false)[code],
            )
            for code, label in properties_specs
        ]

        if verification.can_verify:
            interpretation = (
                "El producto A * A^-1 devuelve la matriz identidad."
                if verification.holds
                else "Se obtuvo una matriz distinta de I al multiplicar A por su inversa."
            )
            props.append(
                PropertyCheckVM(
                    code="f",
                    label="A * A^-1 = I",
                    holds=verification.holds,
                    interpretation=interpretation,
                )
            )
        else:
            props.append(
                PropertyCheckVM(
                    code="f",
                    label="A * A^-1 = I",
                    holds=False,
                    interpretation=verification.message,
                )
            )
        return props

    def _compute_determinant(self, matrix: List[List[Fraction]]) -> tuple[Fraction, List[StepVM]]:
        n = len(matrix)
        if n == 0:
            return Fraction(1), []
        matriz = Matriz(self._copy_matrix(matrix))
        registrador = RegistradorOperaciones()
        reductor = ReductorEscalonado(eps=self._eps)
        resultado = reductor.a_forma_escalonada_reducida(
            matriz_aumentada=matriz,
            num_variables=n,
            pivoteo=self._pivoteo,
            registrador=registrador,
        )
        pasos = registrador.historial.pasos
        pivot_values: List[Fraction] = []
        swap_count = 0
        for paso in pasos:
            if paso.operacion == "INTERCAMBIO_FILAS":
                swap_count += 1
            elif paso.operacion == "NORMALIZAR_PIVOTE":
                if (
                    paso.antes is not None
                    and paso.pivote_fila is not None
                    and paso.pivote_col is not None
                ):
                    valor = self._fraction_value(paso.antes[paso.pivote_fila][paso.pivote_col])
                    pivot_values.append(valor)
        if len(pivot_values) < n:
            determinante = Fraction(0)
        else:
            determinante = Fraction(-1 if swap_count % 2 else 1)
            for valor in pivot_values:
                determinante *= valor
        det_steps = self._build_steps(
            pasos,
            self._copy_matrix(matrix),
            "Matriz original A.",
            "MATRIZ_INICIAL",
        )
        if len(resultado.columnas_pivote) < n:
            determinante = Fraction(0)
        return determinante, det_steps

    def _build_verification(
        self,
        original: List[List[Fraction]],
        inverse_matrix: Optional[List[List[Fraction]]],
        n: int,
        is_identity_left: bool,
    ) -> VerificationResultVM:
        if inverse_matrix is None or not is_identity_left:
            return VerificationResultVM(
                can_verify=False,
                holds=False,
                message="No es posible verificar A * A^-1 = I porque A no es invertible.",
            )
        product = self._matrix_multiply(original, inverse_matrix)
        identity = self._identity_matrix(n)
        holds = product == identity
        if holds:
            message = "La multiplicacion A * A^-1 devolvio exactamente la matriz identidad."
        else:
            message = "La multiplicacion A * A^-1 produjo una matriz distinta de I; no se verifica la propiedad de inversa."
        steps = self._compute_multiplication_steps(original, inverse_matrix, product)
        return VerificationResultVM(
            can_verify=True,
            holds=holds,
            message=message,
            product=product,
            identity=identity,
            steps=steps,
        )

    def _compute_multiplication_steps(
        self,
        original: List[List[Fraction]],
        inverse_matrix: List[List[Fraction]],
        product: List[List[Fraction]],
    ) -> List[MultiplicationCellVM]:
        steps: List[MultiplicationCellVM] = []
        if not original or not inverse_matrix:
            return steps
        rows_a = len(original)
        cols_b = len(inverse_matrix[0]) if inverse_matrix and inverse_matrix[0] else 0
        for i in range(rows_a):
            for j in range(cols_b):
                terms: List[MultiplicationTermVM] = []
                subtotal = Fraction(0)
                for k in range(len(inverse_matrix)):
                    left = original[i][k]
                    right = inverse_matrix[k][j]
                    product_term = left * right
                    subtotal += product_term
                    terms.append(MultiplicationTermVM(left=left, right=right, product=product_term))
                expected = Fraction(1 if i == j else 0)
                result_value = product[i][j]
                if result_value != subtotal:
                    result_value = subtotal
                steps.append(
                    MultiplicationCellVM(
                        row=i,
                        col=j,
                        terms=terms,
                        result=result_value,
                        expected=expected,
                    )
                )
        return steps

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
            return Fraction(value).limit_denominator(_MAX_DENOMINATOR)
        if isinstance(value, int):
            return Fraction(value)
        return Fraction(str(value))

    def _copy_matrix(self, data: List[List[Fraction]]) -> List[List[Fraction]]:
        return [[cell for cell in row] for row in data]

    def _matrix_multiply(
        self,
        A: Sequence[Sequence[Fraction]],
        B: Sequence[Sequence[Fraction]],
    ) -> List[List[Fraction]]:
        rows_a = len(A)
        cols_a = len(A[0]) if rows_a else 0
        rows_b = len(B)
        cols_b = len(B[0]) if rows_b else 0
        if cols_a != rows_b:
            raise ValueError("Dimensiones incompatibles para multiplicacion.")
        result: List[List[Fraction]] = []
        for i in range(rows_a):
            row: List[Fraction] = []
            for j in range(cols_b):
                total = Fraction(0)
                for k in range(cols_a):
                    total += Fraction(A[i][k]) * Fraction(B[k][j])
                row.append(total)
            result.append(row)
        return result
