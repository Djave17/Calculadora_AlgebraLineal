"""Utilities that keep PySide views lightweight and testable.

The helpers from this module encapsulate small building blocks that are
shared by multiple screens:

* Matrix pretty-printing follows Lay, *Linear Algebra and its
  Applications* (5ª ed., 2012, §1.2) where augmented matrices are shown
  row by row.
* The textual summary for Gauss–Jordan steps references Poole,
  *Linear Algebra: A Modern Introduction* (4ª ed., 2015, §1.4), which is
  the material suggested in class for tracking elimination steps.

Keeping these routines isolated prevents the main window from turning
into a "God object" and aligns with MVVM recommendations (MSDN, 2009).
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from ViewModels.resolucion_matriz_vm import ResultVM


def matrix_lines(matrix: Sequence[Sequence[float]] | None, indent: str = "") -> List[str]:
    """Render an augmented matrix row by row.

    The format mirrors the way we present examples in class: each row is
    wrapped in brackets and aligned using the optional ``indent``.
    """

    if not matrix:
        return [f"{indent}—"]
    return [f"{indent}[{', '.join(str(value) for value in row)}]" for row in matrix]


def status_to_text(status: str) -> str:
    """Map solver status codes to human-readable messages."""

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
) -> List[str]:
    """Create a multi-line textual summary for solver results."""

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
    return lines


def format_steps_lines(result: ResultVM, indent: str = "") -> List[str]:
    """Produce a short, study-friendly preview of Gauss–Jordan steps."""

    if not result.steps:
        return [f"{indent}No se registraron pasos."]
    lines = [f"{indent}Pasos Gauss–Jordan:"]
    for step in result.steps:
        lines.append(f"{indent}  [{step.number}] {step.description}")
        if step.after_matrix:
            lines.extend(matrix_lines(step.after_matrix, indent + "    "))
    return lines


def ensure_table_defaults(table: QTableWidget) -> None:
    """Guarantee that every cell has a numeric string, defaulting to 0."""

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
    """Reset every cell in the table back to zero."""

    for i in range(table.rowCount()):
        for j in range(table.columnCount()):
            item = table.item(i, j)
            if item is None:
                item = QTableWidgetItem("0")
                table.setItem(i, j, item)
            else:
                item.setText("0")
            item.setTextAlignment(Qt.AlignCenter)


def table_to_matrix(table: QTableWidget) -> List[List[float]]:
    """Convert a ``QTableWidget`` into a float matrix.

    This mirrors the data flow explained in Strang, *Linear Algebra and
    Its Applications* (4ª ed., 2016, §3.2): the UI captures coefficients
    while the ViewModel works with numeric arrays.
    """

    data: List[List[float]] = []
    for i in range(table.rowCount()):
        row_vals: List[float] = []
        for j in range(table.columnCount()):
            item = table.item(i, j)
            text = item.text().strip() if item and item.text() else "0"
            try:
                row_vals.append(float(text))
            except ValueError as exc:
                raise ValueError(
                    f"Valor no numérico en fila {i + 1}, columna {j + 1}: '{text}'"
                ) from exc
        data.append(row_vals)
    return data


def columns_from_rows(rows: Sequence[Sequence[float]]) -> List[List[float]]:
    """Transpose a matrix expressed as rows into its column vectors."""

    if not rows:
        return []
    num_cols = len(rows[0])
    for fila in rows:
        if len(fila) != num_cols:
            raise ValueError("Todas las filas deben tener la misma longitud.")
    return [[rows[i][j] for i in range(len(rows))] for j in range(num_cols)]


def format_vector(values: Iterable[float]) -> str:
    """Return a textbook-style tuple representation ``(v1, v2, …)``."""

    return "(" + ", ".join(str(x) for x in values) + ")"
