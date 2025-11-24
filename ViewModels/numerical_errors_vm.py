from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence


@dataclass(frozen=True)
class PositionalTermVM:
    digit: int
    exponent: int
    base: int

    @property
    def contribution(self) -> int:
        return self.digit * (self.base ** self.exponent)


@dataclass(frozen=True)
class BaseDecompositionVM:
    base: int
    value: int
    base_digits: str
    terms: List[PositionalTermVM]
    formatted_expression: str
    steps: List[str]


@dataclass(frozen=True)
class ErrorConceptVM:
    title: str
    description: str
    example: str


@dataclass(frozen=True)
class FloatingPointScenarioVM:
    expression: str
    computed: str
    expected: str
    explanation: str


@dataclass(frozen=True)
class ErrorAnalysisVM:
    true_value: float
    approx_value: float
    absolute_error: float
    relative_error: float | None
    propagated_error: float
    f_true: float
    f_approx: float
    function_expression: str
    interpretation: str


def _cot(x: float) -> float:
    sine = math.sin(x)
    if math.isclose(sine, 0.0, abs_tol=1e-12):
        raise ValueError("cot(x) indefinido para multiplos de pi.")
    return math.cos(x) / sine


def _sec(x: float) -> float:
    cosine = math.cos(x)
    if math.isclose(cosine, 0.0, abs_tol=1e-12):
        raise ValueError("sec(x) indefinido para pi/2 + k*pi.")
    return 1 / cosine


def _csc(x: float) -> float:
    sine = math.sin(x)
    if math.isclose(sine, 0.0, abs_tol=1e-12):
        raise ValueError("csc(x) indefinido para k*pi.")
    return 1 / sine


_ALLOWED_FUNCS: Dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "sen": math.sin,
    "seno": math.sin,
    "cos": math.cos,
    "coseno": math.cos,
    "tan": math.tan,
    "tangente": math.tan,
    "tg": math.tan,
    "ctg": _cot,
    "cot": _cot,
    "cotg": _cot,
    "sec": _sec,
    "csc": _csc,
    "cosec": _csc,
    "sqrt": math.sqrt,
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "asin": math.asin,
    "arcsin": math.asin,
    "acos": math.acos,
    "arccos": math.acos,
    "atan": math.atan,
    "arctan": math.atan,
    "sinh": math.sinh,
    "senh": math.sinh,
    "cosh": math.cosh,
    "cosenh": math.cosh,
    "tanh": math.tanh,
    "tgh": math.tanh,
}

_ALLOWED_CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "tau": math.tau,
    "e": math.e,
}

_ALLOWED_GLOBALS = {**_ALLOWED_FUNCS, **_ALLOWED_CONSTANTS}


def _parse_digits(value: int, base: int) -> List[int]:
    if value == 0:
        return [0]
    digits: List[int] = []
    remaining = abs(value)
    while remaining > 0:
        digits.append(remaining % base)
        remaining //= base
    digits.reverse()
    return digits


def decompose_number(value: int, base: int) -> BaseDecompositionVM:
    if base < 2 or base > 16:
        raise ValueError("La base debe estar entre 2 y 16.")
    digits = _parse_digits(value, base)
    sign = "-" if value < 0 else ""
    base_digits = sign + "".join(_digit_repr(d) for d in digits)
    terms: List[PositionalTermVM] = []
    expression_parts: List[str] = []
    steps: List[str] = []
    power = len(digits) - 1
    for index, digit in enumerate(digits):
        exponent = power - index
        term = PositionalTermVM(digit=digit, exponent=exponent, base=base)
        terms.append(term)
        expr = f"{digit}·{base}^{exponent}"
        expression_parts.append(expr)
        steps.append(f"{expr} = {digit * (base ** exponent)}")
    expression = " + ".join(expression_parts)
    if sign:
        expression = f"-({expression})"
    base_repr = f"{base_digits}_{base}"
    return BaseDecompositionVM(
        base=base,
        value=value,
        base_digits=base_repr,
        terms=terms,
        formatted_expression=expression,
        steps=steps,
    )


def _digit_repr(digit: int) -> str:
    if 0 <= digit <= 9:
        return str(digit)
    return chr(ord("A") + digit - 10)


def error_concepts() -> Sequence[ErrorConceptVM]:
    return (
        ErrorConceptVM(
            "Error inherente",
            "Surge de la incertidumbre del dato físico antes de digitalizarlo.",
            "Medir 1.5 m con una cinta graduada a centímetros introduce ±0.005 m.",
        ),
        ErrorConceptVM(
            "Error de redondeo",
            "Proviene del límite de bits para representar fracciones en la computadora.",
            "0.1 en binario es periódico, por eso 0.1 + 0.2 difiere de 0.3.",
        ),
        ErrorConceptVM(
            "Error de truncamiento",
            "Aparece al cortar una serie infinita o aproximar una función.",
            "Usar 1 + x para aproximar e^x introduce un término faltante x^2/2.",
        ),
        ErrorConceptVM(
            "Overflow / Underflow",
            "La magnitud excede el rango del tipo flotante provocando infinito o cero.",
            "1e308 * 1e308 da inf; 1e-308 / 1e308 da 0 por underflow.",
        ),
        ErrorConceptVM(
            "Error de modelo",
            "Se selecciona una ecuación que no describe con precisión el fenómeno.",
            "Modelar el crecimiento poblacional solo con una función lineal.",
        ),
    )


def floating_point_scenarios() -> Sequence[FloatingPointScenarioVM]:
    scenarios: List[FloatingPointScenarioVM] = []
    scenarios.append(
        FloatingPointScenarioVM(
            expression="0.1 + 0.2",
            computed=str(0.1 + 0.2),
            expected="0.3",
            explanation="La suma es 0.30000000000000004 porque 0.1 y 0.2 no tienen representación binaria exacta.",
        )
    )
    huge = (1e16 + 1) - 1e16
    scenarios.append(
        FloatingPointScenarioVM(
            expression="(1e16 + 1) - 1e16",
            computed=str(huge),
            expected="1.0",
            explanation="La resta cancela los bits menos significativos y se pierde el 1.",
        )
    )
    harmonic = sum(0.1 for _ in range(10)) - 1.0
    scenarios.append(
        FloatingPointScenarioVM(
            expression="sum([0.1]*10) - 1.0",
            computed=str(harmonic),
            expected="0.0",
            explanation="La acumulación del redondeo produce -1.1102230246251565e-16 en lugar de cero exacto.",
        )
    )
    return scenarios


def compute_error_analysis(
    true_value: float,
    approx_value: float,
    function_expression: str,
    true_input: float,
    approx_input: float,
) -> ErrorAnalysisVM:
    absolute_error = abs(true_value - approx_value)
    relative_error = None if true_value == 0 else absolute_error / abs(true_value)
    f_true = _evaluate_expression(function_expression, true_input)
    f_approx = _evaluate_expression(function_expression, approx_input)
    propagated_error = abs(f_true - f_approx)
    interpretation = _build_interpretation(absolute_error, relative_error, propagated_error)
    return ErrorAnalysisVM(
        true_value=true_value,
        approx_value=approx_value,
        absolute_error=absolute_error,
        relative_error=relative_error,
        propagated_error=propagated_error,
        f_true=f_true,
        f_approx=f_approx,
        function_expression=function_expression,
        interpretation=interpretation,
    )


def _build_interpretation(
    absolute_error: float,
    relative_error: float | None,
    propagated_error: float,
) -> str:
    rel_msg = (
        f"El error relativo es del {relative_error * 100:.4f}%."
        if relative_error is not None
        else "El valor verdadero es cero; solo puede analizarse el error absoluto."
    )
    propagation_msg = (
        f"La función propaga la incertidumbre a {propagated_error:.4g} unidades."
    )
    return f"La diferencia entre mediciones es {absolute_error:.4g}. {rel_msg} {propagation_msg}"


def _evaluate_expression(expr: str, x_value: float) -> float:
    expr = expr.strip()
    if not expr:
        raise ValueError("Ingresa una función, por ejemplo sin(x) + x**2.")
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError as exc:
        raise ValueError("Expresión de función no válida.") from exc
    value = _eval_node(node, x_value)
    if not isinstance(value, (int, float)):
        raise ValueError("La expresión debe evaluar a un número real.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("El resultado de la función no es finito.")
    return float(value)


def _eval_node(node: ast.AST, x_value: float):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constante no numérica.")
    if isinstance(node, ast.Name):
        if node.id == "x":
            return x_value
        key = node.id.lower()
        if key in _ALLOWED_GLOBALS:
            return _ALLOWED_GLOBALS[key]
        raise ValueError(f"Nombre no permitido: {node.id}")
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, x_value)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Operador unario no soportado.")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, x_value)
        right = _eval_node(node.right, x_value)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Operador no soportado.")
    if isinstance(node, ast.Call):
        func = _eval_node(node.func, x_value)
        if not callable(func):
            raise ValueError("La expresión intenta llamar algo que no es función.")
        args = [_eval_node(arg, x_value) for arg in node.args]
        return func(*args)
    raise ValueError("Expresión no soportada.")
