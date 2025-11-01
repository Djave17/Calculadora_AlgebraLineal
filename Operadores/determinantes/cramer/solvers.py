# -*- coding: utf-8 -*-
from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

EPSILON = 1e-6
SARRUS_PASOS = [
    "Paso 1: Extender la matriz replicando las dos primeras columnas al final.",
    "Paso 2: Sumar los productos de las diagonales descendentes.",
    "Paso 3: Restar los productos de las diagonales ascendentes.",
    "Paso 4: Calcular Δ = suma_descendentes - suma_ascendentes.",
]


def resolver_cramer_2x2(
    a1: Fraction | int | float,
    b1: Fraction | int | float,
    c1: Fraction | int | float,
    a2: Fraction | int | float,
    b2: Fraction | int | float,
    c2: Fraction | int | float,
) -> Dict[str, object]:
    """Resolve a 2x2 linear system using Cramer's rule and show intermediate steps."""

    coeffs = [_to_fraction(value) for value in (a1, b1, c1, a2, b2, c2)]
    a1_f, b1_f, c1_f, a2_f, b2_f, c2_f = coeffs

    delta = a1_f * b2_f - b1_f * a2_f
    pasos_delta = [
        "Paso 1: Calcular Δ = (a1 * b2) - (b1 * a2).",
        f"Δ = ({_format_fraction(a1_f)} * {_format_fraction(b2_f)}) - "
        f"({_format_fraction(b1_f)} * {_format_fraction(a2_f)}) = {_format_fraction(delta)}.",
    ]

    if delta == 0:
        mensaje = "El sistema no tiene solución única (Δ = 0)."
        return {
            "mensaje": mensaje,
            "determinantes": {
                "delta": {
                    "valor": float(delta),
                    "valor_fraccion": delta,
                    "pasos": pasos_delta,
                },
            },
            "pasos": pasos_delta,
        }

    delta_x = c1_f * b2_f - b1_f * c2_f
    delta_y = a1_f * c2_f - c1_f * a2_f

    pasos_delta_x = [
        "Paso 2: Calcular Δx reemplazando la primera columna por los términos independientes.",
        f"Δx = ({_format_fraction(c1_f)} * {_format_fraction(b2_f)}) - "
        f"({_format_fraction(b1_f)} * {_format_fraction(c2_f)}) = {_format_fraction(delta_x)}.",
    ]
    pasos_delta_y = [
        "Paso 3: Calcular Δy reemplazando la segunda columna por los términos independientes.",
        f"Δy = ({_format_fraction(a1_f)} * {_format_fraction(c2_f)}) - "
        f"({_format_fraction(c1_f)} * {_format_fraction(a2_f)}) = {_format_fraction(delta_y)}.",
    ]

    x_value = delta_x / delta
    y_value = delta_y / delta

    pasos_soluciones = [
        "Paso 4: Calcular las soluciones dividiendo Δx y Δy entre Δ.",
        f"x = Δx / Δ = {_format_fraction(delta_x)} / {_format_fraction(delta)} = {_format_fraction(x_value)}.",
        f"y = Δy / Δ = {_format_fraction(delta_y)} / {_format_fraction(delta)} = {_format_fraction(y_value)}.",
    ]

    pasos = pasos_delta + pasos_delta_x + pasos_delta_y + pasos_soluciones

    return {
        "x": float(x_value),
        "y": float(y_value),
        "determinantes": {
            "delta": {
                "valor": float(delta),
                "valor_fraccion": delta,
                "pasos": pasos_delta,
            },
            "delta_x": {
                "valor": float(delta_x),
                "valor_fraccion": delta_x,
                "pasos": pasos_delta_x,
            },
            "delta_y": {
                "valor": float(delta_y),
                "valor_fraccion": delta_y,
                "pasos": pasos_delta_y,
            },
        },
        "pasos": pasos,
    }


def verificar_solucion_2x2(
    a1: Fraction | int | float,
    b1: Fraction | int | float,
    c1: Fraction | int | float,
    a2: Fraction | int | float,
    b2: Fraction | int | float,
    c2: Fraction | int | float,
    x: Fraction | int | float,
    y: Fraction | int | float,
) -> Dict[str, object]:
    """Verify a candidate solution for a 2x2 system within a tolerance."""

    coeffs = [_to_fraction(value) for value in (a1, b1, c1, a2, b2, c2, x, y)]
    a1_f, b1_f, c1_f, a2_f, b2_f, c2_f, x_f, y_f = coeffs

    ecuacion_1 = a1_f * x_f + b1_f * y_f
    ecuacion_2 = a2_f * x_f + b2_f * y_f

    detalle_1 = (
        f"a1 * x + b1 * y = {_format_fraction(a1_f)} * {_format_fraction(x_f)} + "
        f"{_format_fraction(b1_f)} * {_format_fraction(y_f)} = {_format_fraction(ecuacion_1)}."
    )
    detalle_2 = (
        f"a2 * x + b2 * y = {_format_fraction(a2_f)} * {_format_fraction(x_f)} + "
        f"{_format_fraction(b2_f)} * {_format_fraction(y_f)} = {_format_fraction(ecuacion_2)}."
    )

    coincide_1 = _casi_igual(ecuacion_1, c1_f)
    coincide_2 = _casi_igual(ecuacion_2, c2_f)

    mensaje = (
        "Verificación Exitosa"
        if (coincide_1 and coincide_2)
        else "Error de Verificación (Revisar cálculos)"
    )

    return {
        "mensaje": mensaje,
        "evaluaciones": [
            {
                "ecuacion": 1,
                "resultado": float(ecuacion_1),
                "esperado": float(c1_f),
                "detalle": detalle_1,
                "diferencia": float(ecuacion_1 - c1_f),
            },
            {
                "ecuacion": 2,
                "resultado": float(ecuacion_2),
                "esperado": float(c2_f),
                "detalle": detalle_2,
                "diferencia": float(ecuacion_2 - c2_f),
            },
        ],
        "tolerancia": EPSILON,
        "valido": coincide_1 and coincide_2,
    }


def calcular_determinante_sarrus(
    matriz_A: Sequence[Sequence[Fraction | int | float]],
) -> Dict[str, object]:
    """Compute the determinant of a 3x3 matrix via Sarrus' rule with detailed steps."""

    matriz = _to_fraction_matrix_3x3(matriz_A)
    detalle = _sarrus_core(matriz)

    positivos = [
        {
            "diagonal": idx + 1,
            "terminos": [_format_fraction(valor) for valor in item["factores"]],
            "producto": float(item["producto"]),
            "expresion": " * ".join(_format_fraction(valor) for valor in item["factores"])
            + f" = {_format_fraction(item['producto'])}",
        }
        for idx, item in enumerate(detalle["positivos"])
    ]
    negativos = [
        {
            "diagonal": idx + 1,
            "terminos": [_format_fraction(valor) for valor in item["factores"]],
            "producto": float(item["producto"]),
            "expresion": " * ".join(_format_fraction(valor) for valor in item["factores"])
            + f" = {_format_fraction(item['producto'])}",
        }
        for idx, item in enumerate(detalle["negativos"])
    ]

    return {
        "determinante": float(detalle["determinante"]),
        "valor_fraccion": detalle["determinante"],
        "matriz_extendida": [
            [_format_fraction(valor) for valor in fila]
            for fila in detalle["extendida"]
        ],
        "positivos": positivos,
        "negativos": negativos,
        "suma_positivos": float(detalle["suma_positivos"]),
        "suma_negativos": float(detalle["suma_negativos"]),
        "pasos": SARRUS_PASOS[:],
    }


def resolver_cramer_3x3(
    A: Sequence[Sequence[Fraction | int | float]],
    B: Sequence[Fraction | int | float],
) -> Dict[str, object]:
    """Resolve a 3x3 system using Cramer's rule with Sarrus' rule for determinants."""

    matriz_A = _to_fraction_matrix_3x3(A)
    vector_B = _to_fraction_vector_3(B)

    detalle_delta = _sarrus_core(matriz_A)
    delta = detalle_delta["determinante"]

    pasos_generales = [
        "Paso 1: Calcular Δ usando la matriz de coeficientes A.",
    ]

    determinantes: Dict[str, Dict[str, object]] = {
        "delta": {
            "valor": float(delta),
            "valor_fraccion": delta,
            "pasos": SARRUS_PASOS[:],
            "detalle": _formatear_detalle_sarrus(detalle_delta),
        }
    }

    if delta == 0:
        mensaje = "El sistema no tiene solución única (Δ = 0)."
        pasos_generales.append("Δ = 0, se detiene el proceso de Cramer.")
        return {
            "mensaje": mensaje,
            "determinantes": determinantes,
            "pasos": pasos_generales,
        }

    matrices_reemplazadas = [
        _reemplazar_columna(matriz_A, vector_B, 0),
        _reemplazar_columna(matriz_A, vector_B, 1),
        _reemplazar_columna(matriz_A, vector_B, 2),
    ]

    etiquetas = ["delta_x", "delta_y", "delta_z"]
    soluciones: List[Fraction] = []
    determinantes_parciales: List[Fraction] = []
    pasos_generales.append("Paso 2: Calcular Δx, Δy y Δz reemplazando columnas por el vector B.")

    for etiqueta, matriz in zip(etiquetas, matrices_reemplazadas):
        detalle_det = _sarrus_core(matriz)
        determinantes[etiqueta] = {
            "valor": float(detalle_det["determinante"]),
            "valor_fraccion": detalle_det["determinante"],
            "pasos": SARRUS_PASOS[:],
            "detalle": _formatear_detalle_sarrus(detalle_det),
        }
        determinantes_parciales.append(detalle_det["determinante"])
        soluciones.append(detalle_det["determinante"] / delta)

    pasos_generales.append("Paso 3: Obtener x, y, z dividiendo cada determinante parcial entre Δ.")

    x_value, y_value, z_value = soluciones
    pasos_soluciones = [
        f"x = Δx / Δ = {_format_fraction(determinantes_parciales[0])} / {_format_fraction(delta)} = {_format_fraction(x_value)}.",
        f"y = Δy / Δ = {_format_fraction(determinantes_parciales[1])} / {_format_fraction(delta)} = {_format_fraction(y_value)}.",
        f"z = Δz / Δ = {_format_fraction(determinantes_parciales[2])} / {_format_fraction(delta)} = {_format_fraction(z_value)}.",
    ]

    pasos = pasos_generales + pasos_soluciones

    return {
        "x": float(x_value),
        "y": float(y_value),
        "z": float(z_value),
        "determinantes": determinantes,
        "pasos": pasos,
    }


def verificar_solucion_3x3(
    A: Sequence[Sequence[Fraction | int | float]],
    B: Sequence[Fraction | int | float],
    x: Fraction | int | float,
    y: Fraction | int | float,
    z: Fraction | int | float,
) -> Dict[str, object]:
    """Verify a candidate solution for a 3x3 system."""

    matriz_A = _to_fraction_matrix_3x3(A)
    vector_B = _to_fraction_vector_3(B)
    soluciones = [_to_fraction(value) for value in (x, y, z)]

    evaluaciones = []
    coincide_todo = True

    for idx, (fila, esperado) in enumerate(zip(matriz_A, vector_B), start=1):
        total = sum(factor * valor for factor, valor in zip(fila, soluciones))
        coincide = _casi_igual(total, esperado)
        coincide_todo = coincide_todo and coincide
        detalle = (
            f"a{idx}1 * x + a{idx}2 * y + a{idx}3 * z = "
            f"{_format_fraction(fila[0])} * {_format_fraction(soluciones[0])} + "
            f"{_format_fraction(fila[1])} * {_format_fraction(soluciones[1])} + "
            f"{_format_fraction(fila[2])} * {_format_fraction(soluciones[2])} = {_format_fraction(total)}."
        )
        evaluaciones.append(
            {
                "ecuacion": idx,
                "resultado": float(total),
                "esperado": float(esperado),
                "detalle": detalle,
                "diferencia": float(total - esperado),
                "valido": coincide,
            }
        )

    mensaje = (
        "Verificación Exitosa"
        if coincide_todo
        else "Error de Verificación (Revisar cálculos)"
    )

    return {
        "mensaje": mensaje,
        "evaluaciones": evaluaciones,
        "tolerancia": EPSILON,
        "valido": coincide_todo,
    }


# ---------------------------- Helpers ---------------------------- #

def _to_fraction(value: Fraction | int | float) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(str(value))


def _to_fraction_matrix_3x3(
    matriz: Sequence[Sequence[Fraction | int | float]],
) -> List[List[Fraction]]:
    filas = [_convert_row(row, 3) for row in matriz]
    if len(filas) != 3:
        raise ValueError("La matriz debe ser de tamaño 3x3.")
    return filas


def _to_fraction_vector_3(
    vector: Sequence[Fraction | int | float],
) -> List[Fraction]:
    if len(vector) != 3:
        raise ValueError("El vector independiente debe tener exactamente 3 entradas.")
    return [_to_fraction(valor) for valor in vector]


def _convert_row(
    row: Sequence[Fraction | int | float],
    expected: int,
) -> List[Fraction]:
    valores = [_to_fraction(valor) for valor in row]
    if len(valores) != expected:
        raise ValueError(f"Cada fila debe tener exactamente {expected} columnas para el modo 3x3.")
    return valores


def _reemplazar_columna(
    matriz: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
    indice_columna: int,
) -> List[List[Fraction]]:
    nueva_matriz: List[List[Fraction]] = []
    for fila_idx, fila in enumerate(matriz):
        nueva_fila = list(fila)
        nueva_fila[indice_columna] = vector[fila_idx]
        nueva_matriz.append(nueva_fila)
    return nueva_matriz


def _sarrus_core(matriz: Sequence[Sequence[Fraction]]) -> Dict[str, object]:
    if len(matriz) != 3 or any(len(fila) != 3 for fila in matriz):
        raise ValueError("La regla de Sarrus requiere una matriz 3x3.")

    extendida = [fila + fila[:2] for fila in matriz]

    diagonales_positivas = [
        ((0, 0), (1, 1), (2, 2)),
        ((0, 1), (1, 2), (2, 0)),
        ((0, 2), (1, 0), (2, 1)),
    ]
    diagonales_negativas = [
        ((2, 0), (1, 1), (0, 2)),
        ((2, 1), (1, 2), (0, 0)),
        ((2, 2), (1, 0), (0, 1)),
    ]

    positivos = [_extraer_diagonal(matriz, indices) for indices in diagonales_positivas]
    negativos = [_extraer_diagonal(matriz, indices) for indices in diagonales_negativas]

    suma_positivos = sum(item["producto"] for item in positivos)
    suma_negativos = sum(item["producto"] for item in negativos)
    determinante = suma_positivos - suma_negativos

    return {
        "extendida": extendida,
        "positivos": positivos,
        "negativos": negativos,
        "suma_positivos": suma_positivos,
        "suma_negativos": suma_negativos,
        "determinante": determinante,
    }


def _extraer_diagonal(
    matriz: Sequence[Sequence[Fraction]],
    indices: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]],
) -> Dict[str, object]:
    factores = [matriz[i][j] for i, j in indices]
    producto = Fraction(1)
    for valor in factores:
        producto *= valor
    return {
        "indices": indices,
        "factores": factores,
        "producto": producto,
    }


def _formatear_detalle_sarrus(detalle: Dict[str, object]) -> Dict[str, object]:
    return {
        "positivos": [
            {
                "indices": item["indices"],
                "factores": [_format_fraction(valor) for valor in item["factores"]],
                "producto": _format_fraction(item["producto"]),
            }
            for item in detalle["positivos"]
        ],
        "negativos": [
            {
                "indices": item["indices"],
                "factores": [_format_fraction(valor) for valor in item["factores"]],
                "producto": _format_fraction(item["producto"]),
            }
            for item in detalle["negativos"]
        ],
        "suma_positivos": _format_fraction(detalle["suma_positivos"]),
        "suma_negativos": _format_fraction(detalle["suma_negativos"]),
        "determinante": _format_fraction(detalle["determinante"]),
    }


def _casi_igual(left: Fraction, right: Fraction, tol: float = EPSILON) -> bool:
    return abs(float(left - right)) <= tol


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return f"{value.numerator}"
    return f"{value.numerator}/{value.denominator}"
