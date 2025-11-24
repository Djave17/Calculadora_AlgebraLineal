from __future__ import annotations

import ast
import math
import re
from typing import Any, Callable, Dict


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


_NUMBER_VAR_PATTERN = re.compile(r"((?:\d+\.\d+)|\d+)\s*([A-Za-z\(])")
_PAREN_VAR_PATTERN = re.compile(r"(\))\s*([A-Za-z\(])")
_VAR_PAREN_PATTERN = re.compile(r"(x)\s*(\()")


def evaluate_expression(expr: str, x_value: float) -> float:
    """Evalua f(x) de manera segura para los metodos numericos."""

    expr = _normalize_expression(expr)
    if not expr:
        raise ValueError("Ingresa una funcion, por ejemplo sin(x) + x^2.")
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError as exc:
        raise ValueError("Expresion de funcion no valida.") from exc
    value = _eval_node(node, x_value)
    if not isinstance(value, (int, float)):
        raise ValueError("La expresion debe evaluar a un numero real.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("El resultado de la funcion no es finito.")
    return float(value)


def _eval_node(node: ast.AST, x_value: float) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constante no numerica.")
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
            raise ValueError("La expresion intenta llamar algo que no es funcion.")
        args = [_eval_node(arg, x_value) for arg in node.args]
        return func(*args)
    raise ValueError("Expresion no soportada.")


def _normalize_expression(expr: str) -> str:
    expr = expr.strip().replace("^", "**")
    expr = _NUMBER_VAR_PATTERN.sub(r"\1*\2", expr)
    expr = _PAREN_VAR_PATTERN.sub(r"\1*\2", expr)
    expr = _VAR_PAREN_PATTERN.sub(r"\1*\2", expr)
    return expr
