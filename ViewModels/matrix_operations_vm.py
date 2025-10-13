"""Logica de operaciones basicas entre matrices sin usar NumPy ni SciPy."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Sequence

from Operadores.matrices import to_fraction_matrix


@dataclass
class OperationResult:
    """Contiene los pasos descriptivos y la matriz resultante de una operacion."""

    compatible: bool
    steps: List[str]
    result_matrix: List[List[Fraction]] | None
    property_name: str = ""
    property_statement: str = ""
    defined_message: str = ""


class MatrixOperationsViewModel:
    """Ejecuta validaciones y operaciones elementales sobre matrices densas."""

    def add_multiple(self, matrices_rows: Sequence[Sequence[Sequence]]) -> OperationResult:
        if len(matrices_rows) < 2:
            raise ValueError("Se requieren al menos dos matrices para la suma.")

        matrices = [to_fraction_matrix(rows) for rows in matrices_rows]
        steps: List[str] = []
        steps.append(
            f"Paso 1: Verificando dimensiones para la suma de {len(matrices)} matrices."
        )

        base_rows = len(matrices[0])
        base_cols = len(matrices[0][0])
        compatible = True
        for idx, matriz in enumerate(matrices[1:], start=2):
            if len(matriz) != base_rows or len(matriz[0]) != base_cols:
                steps.append(
                    f"La matriz {idx} no coincide en dimension con la primera "
                    f"({base_rows}x{base_cols})."
                )
                compatible = False
                break

        property_name = "Ley conmutativa de la suma"
        property_statement = "A + B = B + A"

        if not compatible:
            steps.append("Las matrices NO son compatibles para la suma.")
            defined_message = "Operacion no definida: existen matrices con dimensiones distintas."
            return OperationResult(False, steps, None, property_name, property_statement, defined_message)

        steps.append("Las matrices son compatibles para la suma.")
        result: List[List[Fraction]] = []
        for i in range(base_rows):
            fila_resultado: List[Fraction] = []
            for j in range(base_cols):
                componentes = [matriz[i][j] for matriz in matrices]
                valor = sum(componentes, Fraction(0))
                componentes_str = " + ".join(str(comp) for comp in componentes)
                steps.append(
                    f"Paso 2.{i + 1}.{j + 1}: c{i + 1}{j + 1} = {componentes_str} = {valor}"
                )
                fila_resultado.append(valor)
            result.append(fila_resultado)

        steps.append("Paso 3: Resultado final de la suma calculado.")
        defined_message = f"Operacion definida: todas las matrices son de dimension {base_rows}x{base_cols}."
        return OperationResult(True, steps, result, property_name, property_statement, defined_message)

    def add(self, A_rows: Sequence[Sequence], B_rows: Sequence[Sequence]) -> OperationResult:
        return self.add_multiple([A_rows, B_rows])

    def subtract(self, A_rows: Sequence[Sequence], B_rows: Sequence[Sequence]) -> OperationResult:
        A = to_fraction_matrix(A_rows)
        B = to_fraction_matrix(B_rows)
        steps: List[str] = []
        steps.append(
            "Paso 1: Verificando dimensiones para la resta. "
            f"A es {self._format_dimensions(A)} y B es {self._format_dimensions(B)}."
        )

        property_name = "Relacion con la suma"
        property_statement = "A - B = A + (-B)"

        if not self._same_shape(A, B):
            steps.append("Las matrices NO son compatibles para la resta (dimensiones distintas).")
            defined_message = "Operacion no definida: la resta requiere matrices de igual dimension."
            return OperationResult(False, steps, None, property_name, property_statement, defined_message)

        steps.append("Las matrices son compatibles para la resta.")
        result: List[List[Fraction]] = []
        for i, (row_a, row_b) in enumerate(zip(A, B), start=1):
            fila: List[Fraction] = []
            for j, (a_ij, b_ij) in enumerate(zip(row_a, row_b), start=1):
                valor = a_ij - b_ij
                steps.append(f"Paso 2.{i}.{j}: c{i}{j} = {a_ij} - {b_ij} = {valor}")
                fila.append(valor)
            result.append(fila)

        steps.append("Paso 3: Resultado final de la resta calculado.")
        filas = len(A)
        columnas = len(A[0])
        defined_message = f"Operacion definida: A y B son de dimension {filas}x{columnas}."
        return OperationResult(True, steps, result, property_name, property_statement, defined_message)

    def scalar_multiply(self, scalar: str, A_rows: Sequence[Sequence]) -> OperationResult:
        escalar = self._parse_number(scalar)
        A = to_fraction_matrix(A_rows)
        steps: List[str] = []
        steps.append(
            f"Paso 1: Preparando multiplicacion escalar. k = {escalar}. "
            f"A es {self._format_dimensions(A)}."
        )

        property_name = "Escalar aplicado a la matriz"
        property_statement = "kA multiplica cada entrada de A por k"

        resultado: List[List[Fraction]] = []
        for i, fila in enumerate(A, start=1):
            fila_resultado: List[Fraction] = []
            for j, valor in enumerate(fila, start=1):
                producto = escalar * valor
                steps.append(f"Paso 2.{i}.{j}: c{i}{j} = {escalar} * {valor} = {producto}")
                fila_resultado.append(producto)
            resultado.append(fila_resultado)

        steps.append("Paso 3: Resultado final de k * A calculado.")
        defined_message = f"Operacion definida: cualquier matriz puede multiplicarse por el escalar {escalar}."
        return OperationResult(True, steps, resultado, property_name, property_statement, defined_message)

    def multiply(self, A_rows: Sequence[Sequence], B_rows: Sequence[Sequence]) -> OperationResult:
        A = to_fraction_matrix(A_rows)
        B = to_fraction_matrix(B_rows)
        steps: List[str] = []
        steps.append(
            "Paso 1: Verificando compatibilidad para la multiplicacion AB. "
            f"A es {self._format_dimensions(A)} y B es {self._format_dimensions(B)}."
        )

        property_name = "Condicion de producto"
        property_statement = "Si columnas(A) = filas(B), entonces AB esta definido"

        if len(A[0]) != len(B):
            steps.append(
                "El producto AB NO es posible porque el numero de columnas de A no coincide "
                "con el numero de filas de B."
            )
            defined_message = (
                "Operacion no definida: se requiere que las columnas de A coincidan con las filas de B."
            )
            return OperationResult(False, steps, None, property_name, property_statement, defined_message)

        steps.append(
            "El producto AB es posible. Calculando cada entrada como suma de productos fila-columna."
        )

        resultado: List[List[Fraction]] = []
        for i, fila_a in enumerate(A, start=1):
            fila_resultado: List[Fraction] = []
            for j in range(len(B[0])):
                columna_b = [B[k][j] for k in range(len(B))]
                productos = [fila_a[k] * columna_b[k] for k in range(len(columna_b))]
                valor = sum(productos, Fraction(0))
                detalle = " + ".join(f"({fila_a[k]}*{columna_b[k]})" for k in range(len(productos)))
                steps.append(f"Paso 2.{i}.{j + 1}: c{i}{j + 1} = {detalle} = {valor}")
                fila_resultado.append(valor)
            resultado.append(fila_resultado)

        steps.append("Paso 3: Resultado final de AB calculado.")
        defined_message = (
            f"Operacion definida: A es {len(A)}x{len(A[0])}, B es {len(B)}x{len(B[0])} y el resultado es "
            f"{len(A)}x{len(B[0])}."
        )
        return OperationResult(True, steps, resultado, property_name, property_statement, defined_message)

    @staticmethod
    def _format_dimensions(matrix: Sequence[Sequence[Fraction]]) -> str:
        return f"{len(matrix)}x{len(matrix[0])}" if matrix and matrix[0] else "0x0"

    @staticmethod
    def _same_shape(A: Sequence[Sequence[Fraction]], B: Sequence[Sequence[Fraction]]) -> bool:
        return len(A) == len(B) and len(A[0]) == len(B[0])

    @staticmethod
    def _parse_number(value: str | Fraction | int | float) -> Fraction:
        if isinstance(value, Fraction):
            return value
        if isinstance(value, (int, float)):
            return Fraction(value)

        normalizado = str(value).strip()
        if normalizado == "":
            return Fraction(0)
        try:
            return Fraction(normalizado)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"El escalar '{value}' no es un numero valido.") from exc
