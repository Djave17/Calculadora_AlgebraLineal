from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Sequence, Tuple

from .expression_evaluator import evaluate_expression

ClosedMethodName = Literal["bisection", "false_position"]


@dataclass(frozen=True)
class ClosedMethodIterationVM:
    iteration: int
    method: ClosedMethodName
    a: float
    b: float
    point: float
    fa: float
    fb: float
    fp: float
    error_percent: float | None
    next_interval: Tuple[float, float]


@dataclass(frozen=True)
class ClosedMethodResultVM:
    method: ClosedMethodName
    iterations: List[ClosedMethodIterationVM]
    approx_root: float
    final_error_percent: float | None
    final_interval: Tuple[float, float]
    converged: bool
    tolerance_percent: float
    final_function_value: float
    max_iterations: int
    plot_points: Sequence[Tuple[float, float]]


def solve_closed_root(
    method: ClosedMethodName,
    expression: str,
    a: float,
    b: float,
    desired_error: float,
    max_iterations: int = 50,
) -> ClosedMethodResultVM:
    tolerance_percent = _normalize_tolerance(desired_error)
    if max_iterations <= 0:
        raise ValueError("El máximo de iteraciones debe ser mayor a cero.")

    if method == "bisection":
        result = _bisection(expression, a, b, tolerance_percent, max_iterations)
    elif method == "false_position":
        result = _false_position(expression, a, b, tolerance_percent, max_iterations)
    else:
        raise ValueError(f"Metodo no soportado: {method}")

    final_value = evaluate_expression(expression, result.approx_root)
    plot_points = _build_plot_points(expression, a, b, result.approx_root)
    return ClosedMethodResultVM(
        method=result.method,
        iterations=result.iterations,
        approx_root=result.approx_root,
        final_error_percent=result.final_error_percent,
        final_interval=result.final_interval,
        converged=result.converged,
        tolerance_percent=result.tolerance_percent,
        final_function_value=final_value,
        max_iterations=max_iterations,
        plot_points=plot_points,
    )


def _bisection(
    expression: str,
    a: float,
    b: float,
    tolerance_percent: float,
    max_iterations: int,
) -> ClosedMethodResultVM:
    fa = evaluate_expression(expression, a)
    fb = evaluate_expression(expression, b)
    _ensure_sign_change(fa, fb, a, b)
    iterations: List[ClosedMethodIterationVM] = []
    prev_point: float | None = None
    approx_root = (a + b) / 2
    converged = False

    for iteration in range(1, max_iterations + 1):
        current_a, current_b = a, b
        current_fa, current_fb = fa, fb
        point = (current_a + current_b) / 2
        fp = evaluate_expression(expression, point)
        error_percent = _relative_error(prev_point, point)

        if fp == 0:
            converged = True
            error_percent = 0.0
            next_interval = (point, point)
            iterations.append(
                ClosedMethodIterationVM(
                    iteration=iteration,
                    method="bisection",
                    a=current_a,
                    b=current_b,
                    point=point,
                    fa=current_fa,
                    fb=current_fb,
                    fp=fp,
                    error_percent=error_percent,
                    next_interval=next_interval,
                )
            )
            approx_root = point
            break

        if current_fa * fp < 0:
            next_interval = (current_a, point)
            a, b = current_a, point
            fa, fb = current_fa, fp
        else:
            next_interval = (point, current_b)
            a, b = point, current_b
            fa, fb = fp, current_fb

        iterations.append(
            ClosedMethodIterationVM(
                iteration=iteration,
                method="bisection",
                a=current_a,
                b=current_b,
                point=point,
                fa=current_fa,
                fb=current_fb,
                fp=fp,
                error_percent=error_percent,
                next_interval=next_interval,
            )
        )

        approx_root = point
        prev_point = point
        if error_percent is not None and error_percent <= tolerance_percent:
            converged = True
            break

    final_error = iterations[-1].error_percent if iterations else None
    final_interval = iterations[-1].next_interval if iterations else (a, b)
    return ClosedMethodResultVM(
        method="bisection",
        iterations=iterations,
        approx_root=approx_root,
        final_error_percent=final_error,
        final_interval=final_interval,
        converged=converged,
        tolerance_percent=tolerance_percent,
        final_function_value=0.0,
        max_iterations=max_iterations,
        plot_points=[],
    )


def _false_position(
    expression: str,
    a: float,
    b: float,
    tolerance_percent: float,
    max_iterations: int,
) -> ClosedMethodResultVM:
    fa = evaluate_expression(expression, a)
    fb = evaluate_expression(expression, b)
    _ensure_sign_change(fa, fb, a, b)
    iterations: List[ClosedMethodIterationVM] = []
    prev_point: float | None = None
    approx_root = a
    converged = False

    for iteration in range(1, max_iterations + 1):
        current_a, current_b = a, b
        current_fa, current_fb = fa, fb
        denominator = current_fb - current_fa
        if abs(denominator) < 1e-14:
            raise ValueError("Division por cero o denominador muy pequeño en regla falsa; ajusta el intervalo.")
        point = current_b - current_fb * (current_b - current_a) / denominator
        fp = evaluate_expression(expression, point)
        error_percent = _relative_error(prev_point, point)
        if prev_point is not None and abs(point - prev_point) < 1e-14:
            raise ValueError("El método de Regla Falsa se estancó (xr no cambia); intenta otro intervalo.")

        if fp == 0:
            converged = True
            error_percent = 0.0
            next_interval = (point, point)
            iterations.append(
                ClosedMethodIterationVM(
                    iteration=iteration,
                    method="false_position",
                    a=current_a,
                    b=current_b,
                    point=point,
                    fa=current_fa,
                    fb=current_fb,
                    fp=fp,
                    error_percent=error_percent,
                    next_interval=next_interval,
                )
            )
            approx_root = point
            break

        if current_fa * fp < 0:
            next_interval = (current_a, point)
            a, b = current_a, point
            fa, fb = current_fa, fp
        else:
            next_interval = (point, current_b)
            a, b = point, current_b
            fa, fb = fp, current_fb

        iterations.append(
            ClosedMethodIterationVM(
                iteration=iteration,
                method="false_position",
                a=current_a,
                b=current_b,
                point=point,
                fa=current_fa,
                fb=current_fb,
                fp=fp,
                error_percent=error_percent,
                next_interval=next_interval,
            )
        )

        approx_root = point
        prev_point = point
        if error_percent is not None and error_percent <= tolerance_percent:
            converged = True
            break

    final_error = iterations[-1].error_percent if iterations else None
    final_interval = iterations[-1].next_interval if iterations else (a, b)
    return ClosedMethodResultVM(
        method="false_position",
        iterations=iterations,
        approx_root=approx_root,
        final_error_percent=final_error,
        final_interval=final_interval,
        converged=converged,
        tolerance_percent=tolerance_percent,
        final_function_value=0.0,
        max_iterations=max_iterations,
        plot_points=[],
    )


def _ensure_sign_change(fa: float, fb: float, a: float | None = None, b: float | None = None) -> None:
    if fa * fb >= 0:
        a_label = f"f({a})={fa:.6g}" if a is not None else f"f(a)={fa:.6g}"
        b_label = f"f({b})={fb:.6g}" if b is not None else f"f(b)={fb:.6g}"
        raise ValueError(
            f"El intervalo no es valido: {a_label}, {b_label}. Ajusta a,b para que f(a) y f(b) tengan signos opuestos."
        )


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
    a: float,
    b: float,
    root: float,
    samples: int = 60,
) -> list[Tuple[float, float]]:
    left = min(a, b, root)
    right = max(a, b, root)
    margin = max(abs(right - left) * 0.15, 1.0)
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
