"""Utilidades para mantener las vistas de PySide ligeras y comprobables.

Los helpers de este módulo reúnen piezas pequeñas reutilizadas en varias
pantallas:

* El formateo de matrices sigue a Lay, *Linear Algebra and its Applications*
  (5ª ed., 2012, §1.2), donde la matriz aumentada se presenta fila por fila.
* El resumen textual de los pasos de Gauss-Jordan cita a Poole, *Linear Algebra:
  A Modern Introduction* (4ª ed., 2015, §1.4), referencia indicada en clase
  para documentar la eliminación.

Separar estas rutinas evita que la ventana principal se convierta en un
"objeto Dios" y respeta la separación propuesta por MVVM (MSDN, 2009).
"""

from __future__ import annotations

from fractions import Fraction

from typing import Iterable, List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from ViewModels.resolucion_matriz_vm import ResultVM


def matrix_lines(matrix: Sequence[Sequence[Fraction | float]] | None, indent: str = "") -> List[str]:
    """Renderiza una matriz aumentada fila por fila.

    El formato replica los ejemplos vistos en clase: cada fila se envuelve
    entre corchetes y se respeta una sangría opcional ``indent``.
    """

    if not matrix:
        return [f"{indent}—"]
    return [f"{indent}[{', '.join(str(value) for value in row)}]" for row in matrix]


def status_to_text(status: str) -> str:
    """Traduce el estado del solucionador a mensajes legibles."""

    mapping = {
        "UNICA": "Solución única",
        "INFINITAS": "Infinitas soluciones",
        "INCONSISTENTE": "Sistema inconsistente",
    }
    return mapping.get(status, status)


def format_result_lines(
    result: ResultVM,
    variable_labels: Sequence[str],
    indent: str = "",
    homogeneous: bool = False,
) -> List[str]:
    """Genera un resumen textual en varias líneas del resultado obtenido."""

    lines = [f"{indent}Estado: {status_to_text(result.status)}"]

    if result.status == "UNICA" and result.solution is not None:
        lines.append(f"{indent}Solución:")
        for label, value in zip(variable_labels, result.solution):
            lines.append(f"{indent}  {label} = {value}")
    elif result.status == "INFINITAS" and result.parametric is not None:
        lines.append(f"{indent}Solución particular:")
        for label, value in zip(variable_labels, result.parametric.particular):
            lines.append(f"{indent}  {label} = {value}")
        if result.parametric.direcciones:
            lines.append(f"{indent}Direcciones asociadas:")
            for idx, direction in enumerate(result.parametric.direcciones, start=1):
                direction_str = ", ".join(str(value) for value in direction)
                lines.append(f"{indent}  t{idx}: ({direction_str})")
    elif result.status == "INCONSISTENTE":
        lines.append(f"{indent}No existe solución compatible con B.")

    pivote_labels = ", ".join(variable_labels[idx] for idx in (result.pivot_cols or [])) or "—"
    libre_labels = ", ".join(variable_labels[idx] for idx in (result.free_vars or [])) or "—"
    lines.append(f"{indent}Columnas pivote: {pivote_labels}")
    lines.append(f"{indent}Variables libres: {libre_labels}")

    if homogeneous:
        lines.append(_homogeneous_solution_statement(result, indent))

    return lines


def format_steps_lines(result: ResultVM, indent: str = "") -> List[str]:
    """Devuelve una vista rápida de los pasos de Gauss-Jordan apta para estudio."""

    if not result.steps:
        return [f"{indent}No se registraron pasos."]
    lines = [f"{indent}Pasos Gauss–Jordan:"]
    for step in result.steps:
        lines.append(f"{indent}  [{step.number}] {step.description}")
        if step.after_matrix:
            lines.extend(matrix_lines(step.after_matrix, indent + "    "))
    return lines


def ensure_table_defaults(table: QTableWidget) -> None:
    """Garantiza que cada celda almacene un número en texto (por defecto 0)."""

    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            item = table.item(i, j)
            if item is None:
                item = QTableWidgetItem("0")
                table.setItem(i, j, item)
            if item.text().strip() == "":
                item.setText("0")
            item.setTextAlignment(Qt.AlignCenter)


def fill_table_with_zero(table: QTableWidget) -> None:
    """Reinicia todas las celdas de la tabla al valor cero."""

    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            item = table.item(i, j)
            if item is None:
                item = QTableWidgetItem("0")
                table.setItem(i, j, item)
            else:
                item.setText("0")
            item.setTextAlignment(Qt.AlignCenter)


def _parse_number(text: str) -> Fraction:
    """Convierte cadenas como ``3/5`` o ``2.75`` en fracciones exactas."""

    normalized = text.replace(" ", "")
    if normalized == "":
        return Fraction(0)
    try:
        return Fraction(normalized)
    except ValueError as exc:
        raise ValueError(f"Valor no numérico: '{text}'") from exc


def table_to_matrix(table: QTableWidget) -> List[List[Fraction]]:
    """Convierte un ``QTableWidget`` en una matriz de fracciones.

    La transformación sigue el flujo descrito por Strang, *Linear Algebra and
    its Applications* (4ª ed., 2016, §3.2): la IU captura coeficientes y el
    ViewModel opera con arreglos numéricos.
    """

    data: List[List[Fraction]] = []
    for i in range(table.rowCount()):
        row_vals: List[Fraction] = []
        for j in range(table.columnCount()):
            item = table.item(i, j)
            text = item.text().strip() if item and item.text() else "0"
            try:
                row_vals.append(_parse_number(text))
            except ValueError as exc:
                raise ValueError(
                    f"Valor no numérico en fila {i + 1}, columna {j + 1}: '{text}'"
                ) from exc
        data.append(row_vals)
    return data


def columns_from_rows(rows: Sequence[Sequence[Fraction | float]]) -> List[List[Fraction]]:
    """Transpone una matriz dada por filas para obtener sus vectores columna."""

    if not rows:
        return []
    num_cols = len(rows[0])
    for fila in rows:
        if len(fila) != num_cols:
            raise ValueError("Todas las filas deben tener la misma longitud.")
    return [[Fraction(rows[i][j]) for i in range(len(rows))] for j in range(num_cols)]


def format_vector(values: Iterable[Fraction | float]) -> str:
    """Devuelve una representación tipo tupla ``(v1, v2, ...)``."""

    return "(" + ", ".join(str(x) for x in values) + ")"


def _homogeneous_solution_statement(result: ResultVM, indent: str) -> str:
    """Redacta si la soluci?n trivial es ?nica en sistemas homog?neos."""
    status = result.status

    if status == "INCONSISTENTE":
        return f"{indent}Ni siquiera la soluci?n trivial satisface el sistema (inconsistente)."

    if status == "UNICA":
        if result.solution is None:
            return f"{indent}La soluci?n trivial es la ?nica."
        if all(value == 0 for value in result.solution):
            return f"{indent}La soluci?n trivial es la ?nica."
        return f"{indent}La soluci?n trivial no es la ?nica."

    if status == "INFINITAS":
        return f"{indent}Existen soluciones no triviales; la soluci?n trivial no es la ?nica."

    if result.free_vars:
        return f"{indent}Existen soluciones no triviales; la soluci?n trivial no es la ?nica."

    parametric = result.parametric
    if parametric and (parametric.direcciones or parametric.free_vars):
        return f"{indent}Existen soluciones no triviales; la soluci?n trivial no es la ?nica."

    return f"{indent}La soluci?n trivial no es la ?nica."
