from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Sequence, Tuple
import math

from .expression_evaluator import evaluate_expression

OpenMethodName = Literal["newton_raphson", "secant"]


@dataclass(frozen=True)
class OpenMethodIterationVM:
    iteration: int
    method: OpenMethodName
    xi: float
    xi_minus_1: float | None
    fx: float
    fprime: float | None
    next_x: float
    error_percent: float | None


@dataclass(frozen=True)
class OpenMethodResultVM:
    method: OpenMethodName
    iterations: List[OpenMethodIterationVM]
    approx_root: float
    final_error_percent: float | None
    converged: bool
    tolerance_percent: float
    final_function_value: float
    derivative_warning: bool
    max_iterations: int
    plot_points: Sequence[Tuple[float, float]]


def solve_open_root(
    method: OpenMethodName,
    expression: str,
    x0: float,
    desired_error: float,
    x1: float | None = None,
    max_iterations: int = 50,
) -> OpenMethodResultVM:
    tolerance_percent = _normalize_tolerance(desired_error)
    if max_iterations <= 0:
        raise ValueError("El máximo de iteraciones debe ser mayor a cero.")

    if method == "newton_raphson":
        result = _newton_raphson(expression, x0, tolerance_percent, max_iterations)
    elif method == "secant":
        if x1 is None:
            raise ValueError("La secante necesita dos valores iniciales.")
        result = _secant(expression, x0, x1, tolerance_percent, max_iterations)
    else:
        raise ValueError(f"Metodo no soportado: {method}")

    final_value = evaluate_expression(expression, result.approx_root)
    plot_points = _build_plot_points(expression, x0, x1, result.approx_root)
    return OpenMethodResultVM(
        method=result.method,
        iterations=result.iterations,
        approx_root=result.approx_root,
        final_error_percent=result.final_error_percent,
        converged=result.converged,
        tolerance_percent=result.tolerance_percent,
        final_function_value=final_value,
        derivative_warning=result.derivative_warning,
        max_iterations=max_iterations,
        plot_points=plot_points,
    )


def _newton_raphson(
    expression: str,
    x0: float,
    tolerance_percent: float,
    max_iterations: int,
) -> OpenMethodResultVM:
    iterations: List[OpenMethodIterationVM] = []
    prev_x: float | None = None
    xi = x0
    converged = False
    derivative_warning = False

    for iteration in range(1, max_iterations + 1):
        fx = evaluate_expression(expression, xi)
        fprime = _numeric_derivative(expression, xi)
        if abs(fprime) < 1e-10:
            derivative_warning = True
            raise ValueError("f'(x) es 0 o muy cercana a 0; el metodo puede fallar.")
        next_x = xi - fx / fprime
        error_percent = _relative_error(prev_x, next_x)

        iterations.append(
            OpenMethodIterationVM(
                iteration=iteration,
                method="newton_raphson",
                xi=xi,
                xi_minus_1=None,
                fx=fx,
                fprime=fprime,
                next_x=next_x,
                error_percent=error_percent,
            )
        )

        if error_percent is not None and error_percent <= tolerance_percent:
            converged = True
            xi = next_x
            break

        prev_x = xi
        xi = next_x

    approx_root = xi
    final_error = iterations[-1].error_percent if iterations else None
    return OpenMethodResultVM(
        method="newton_raphson",
        iterations=iterations,
        approx_root=approx_root,
        final_error_percent=final_error,
        converged=converged,
        tolerance_percent=tolerance_percent,
        final_function_value=0.0,
        derivative_warning=derivative_warning,
        max_iterations=max_iterations,
        plot_points=[],
    )


def _secant(
    expression: str,
    x0: float,
    x1: float,
    tolerance_percent: float,
    max_iterations: int,
) -> OpenMethodResultVM:
    iterations: List[OpenMethodIterationVM] = []
    xi_minus_1 = x0
    xi = x1
    converged = False
    derivative_warning = False

    for iteration in range(1, max_iterations + 1):
        f_xi_minus_1 = evaluate_expression(expression, xi_minus_1)
        f_xi = evaluate_expression(expression, xi)
        denominator = f_xi - f_xi_minus_1
        if denominator == 0:
            derivative_warning = True
            raise ValueError("El denominador de la secante es 0; intenta con otros valores iniciales.")
        next_x = xi - f_xi * (xi_minus_1 - xi) / denominator
        error_percent = _relative_error(xi, next_x)
        if not math.isfinite(next_x) or abs(next_x) > 1e6 or abs(f_xi) > 1e6:
            raise ValueError("La secante diverge con estos valores iniciales; prueba otros puntos.")
        if error_percent is not None and error_percent > 1e6:
            raise ValueError("La secante diverge (error crece); prueba otros puntos.")

        iterations.append(
            OpenMethodIterationVM(
                iteration=iteration,
                method="secant",
                xi=xi,
                xi_minus_1=xi_minus_1,
                fx=f_xi,
                fprime=None,
                next_x=next_x,
                error_percent=error_percent,
            )
        )

        if error_percent is not None and error_percent <= tolerance_percent:
            converged = True
            xi_minus_1 = xi
            xi = next_x
            break

        xi_minus_1, xi = xi, next_x

    approx_root = xi
    final_error = iterations[-1].error_percent if iterations else None
    return OpenMethodResultVM(
        method="secant",
        iterations=iterations,
        approx_root=approx_root,
        final_error_percent=final_error,
        converged=converged,
        tolerance_percent=tolerance_percent,
        final_function_value=0.0,
        derivative_warning=derivative_warning,
        max_iterations=max_iterations,
        plot_points=[],
    )


def _numeric_derivative(expression: str, x: float, h: float = 1e-5) -> float:
    forward = evaluate_expression(expression, x + h)
    backward = evaluate_expression(expression, x - h)
    return (forward - backward) / (2 * h)


def _relative_error(previous: float | None, current: float) -> float | None:
    if previous is None:
        return None
    if current == 0:
        return abs(current - previous) * 100
    return abs((current - previous) / current) * 100


def _normalize_tolerance(value: float) -> float:
    if value <= 0:
        raise ValueError("El error deseado debe ser positivo.")
    return value * 100 if value <= 1 else value


def _build_plot_points(
    expression: str,
    x0: float,
    x1: float | None,
    root: float,
    samples: int = 60,
) -> list[Tuple[float, float]]:
    refs = [x0, root]
    if x1 is not None:
        refs.append(x1)
    left = min(refs)
    right = max(refs)
    margin = max(abs(right - left) * 0.25, 1.0)
    start = left - margin
    end = right + margin
    step = (end - start) / max(samples - 1, 1)
    points: list[Tuple[float, float]] = []
    x = start
    for _ in range(samples):
        try:
            y = evaluate_expression(expression, x)
        except Exception:
            x += step
            continue
        points.append((x, y))
        x += step
    return points
