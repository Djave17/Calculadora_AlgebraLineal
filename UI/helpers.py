from __future__ import annotations

from fractions import Fraction
from typing import Iterable, List, Sequence

from ViewModels.resolucion_matriz_vm import ResultVM


def parse_number(text: str) -> Fraction:
    normalized = (text or "").strip().replace(" ", "")
    if normalized == "":
        return Fraction(0)
    try:
        return Fraction(normalized)
    except ValueError as exc:
        raise ValueError(f"Valor no numérico: '{text}'") from exc


def parse_matrix(rows: Sequence[Sequence[str]]) -> List[List[Fraction]]:
    matrix: List[List[Fraction]] = []
    for i, raw_row in enumerate(rows, start=1):
        converted_row: List[Fraction] = []
        for j, cell in enumerate(raw_row, start=1):
            try:
                converted_row.append(parse_number(cell))
            except ValueError as exc:
                raise ValueError(
                    f"Valor no numérico en fila {i}, columna {j}: '{cell}'"
                ) from exc
        matrix.append(converted_row)
    return matrix


def status_to_text(status: str) -> str:
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
        lines.append(f"{indent}No existe solución compatible con b.")

    pivot_labels = ", ".join(variable_labels[idx] for idx in (result.pivot_cols or [])) or "—"
    free_labels = ", ".join(variable_labels[idx] for idx in (result.free_vars or [])) or "—"
    lines.append(f"{indent}Columnas pivote: {pivot_labels}")
    lines.append(f"{indent}Variables libres: {free_labels}")
    return lines


def format_steps_lines(result: ResultVM, indent: str = "") -> List[str]:
    if not result.steps:
        return [f"{indent}No se registraron pasos."]
    lines = [f"{indent}Pasos Gauss–Jordan:"]
    for step in result.steps:
        lines.append(f"{indent}  [{step.number}] {step.description}")
        if step.after_matrix:
            lines.append(f"{indent}    Matriz resultante:")
            for row in step.after_matrix:
                row_txt = ", ".join(str(value) for value in row)
                lines.append(f"{indent}      [{row_txt}]")
    return lines


def matrix_header_labels(variable_count: int) -> List[str]:
    labels = [f"x{idx}" for idx in range(1, variable_count + 1)]
    labels.append("b")
    return labels


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def pluralize(value: int, singular: str, plural: str | None = None) -> str:
    if value == 1:
        return f"{value} {singular}"
    label = plural if plural is not None else f"{singular}s"
    return f"{value} {label}"


def build_matrix_rows_from_values(values: Sequence[Sequence[str]]) -> List[List[str]]:
    return [[cell if cell.strip() != "" else "0" for cell in row] for row in values]

