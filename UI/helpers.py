from __future__ import annotations

import ast
import math
import re
from fractions import Fraction
from typing import Iterable, List, Sequence

from ViewModels.resolucion_matriz_vm import ResultVM

_MAX_DENOMINATOR = 10_000

_SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
}


def _cot(x: float) -> float:
    return 1.0 / math.tan(x)


def _sec(x: float) -> float:
    return 1.0 / math.cos(x)


def _csc(x: float) -> float:
    return 1.0 / math.sin(x)


_EXTRA_FUNCTIONS = {
    "cot": _cot,
    "ctg": _cot,
    "cotg": _cot,
    "sec": _sec,
    "csc": _csc,
}

_SAFE_CONSTANTS = {
    "pi": math.pi,
    "π": math.pi,
    "tau": math.tau,
    "e": math.e,
}

_SAFE_NAMES = {**_SAFE_FUNCTIONS, **_EXTRA_FUNCTIONS, **_SAFE_CONSTANTS}

_ALIAS_MAP = {
    "sen": "sin",
    "tg": "tan",
    "ctg": "cot",
    "cotg": "cot",
}

_ALIAS_PATTERN = re.compile(
    r"\b(" + "|".join(sorted(_ALIAS_MAP, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE,
) if _ALIAS_MAP else None


def _normalize_expression(expr: str) -> str:
    cleaned = expr.replace("^", "**").replace("√", "sqrt").replace("·", "*").replace("π", "pi")
    if _ALIAS_PATTERN:
        cleaned = _ALIAS_PATTERN.sub(lambda m: _ALIAS_MAP[m.group(0).lower()], cleaned)
    return cleaned


def _ensure_fraction(value) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        return Fraction(int(value))
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("El resultado no es finito.")
        return Fraction(value).limit_denominator(_MAX_DENOMINATOR)
    raise ValueError("Valor no numérico.")


def _resolve_name(name: str):
    key = name.lower()
    if key in _SAFE_NAMES:
        return _SAFE_NAMES[key]
    raise ValueError(f"Nombre no permitido: {name}")


def _eval_node(node):
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, (int, float)):
            return value
        raise ValueError("Constante no numérica.")
    if isinstance(node, ast.Name):
        return _resolve_name(node.id)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Operador unario no soportado.")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            exponent = right
            base = left
            if isinstance(exponent, Fraction) and exponent.denominator == 1:
                exponent = exponent.numerator
            if isinstance(base, Fraction) and isinstance(exponent, int):
                return base ** exponent
            base_val = float(base if not isinstance(base, Fraction) else float(base))
            exp_val = float(exponent if not isinstance(exponent, Fraction) else float(exponent))
            result = base_val ** exp_val
            if not math.isfinite(result):
                raise ValueError("Resultado no finito en potencia.")
            return result
        raise ValueError("Operador no soportado.")
    if isinstance(node, ast.Call):
        func = _eval_node(node.func)
        if not callable(func):
            raise ValueError("Se intentó llamar a un elemento no funcional.")
        if node.keywords:
            raise ValueError("Argumentos con nombre no soportados.")
        args = [_eval_node(arg) for arg in node.args]
        numeric_args = [float(arg) if isinstance(arg, Fraction) else arg for arg in args]
        result = func(*numeric_args)
        if isinstance(result, complex):
            raise ValueError("Resultado complejo no soportado.")
        if isinstance(result, (int, float, Fraction)):
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("Resultado no finito.")
            return result
        raise ValueError("La función devolvió un tipo no numérico.")
    raise ValueError("Expresión no soportada.")


def _eval_expression(expr: str):
    prepared = _normalize_expression(expr)
    try:
        tree = ast.parse(prepared, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Expresión no válida.") from exc
    return _eval_node(tree.body)


def parse_number(text: str) -> Fraction:
    raw = (text or "").strip()
    normalized = raw.replace(" ", "")
    if normalized == "":
        return Fraction(0)
    try:
        return Fraction(normalized)
    except ValueError:
        try:
            value = _eval_expression(raw)
            return _ensure_fraction(value)
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

    pivot_labels = ", ".join(variable_labels[idx] for idx in (result.pivot_cols or [])) or "∅"
    free_labels = ", ".join(variable_labels[idx] for idx in (result.free_vars or [])) or "∅"
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
