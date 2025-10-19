from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, List, Tuple
import re


def _parse_tokens(raw: str) -> List[Fraction]:
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("No se proporcionó ningún número para el vector.")
    cleaned = cleaned.replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ")
    tokens = [tok for tok in re.split(r"[\s,]+", cleaned) if tok]
    if not tokens:
        raise ValueError("No se detectaron componentes en el vector.")
    componentes: List[Fraction] = []
    for tok in tokens:
        try:
            componentes.append(Fraction(tok))
        except ValueError as exc:
            raise ValueError(f"Componente inválida en vector: '{tok}'") from exc
    return componentes


@dataclass(frozen=True)
class Vector:
    componentes: Tuple[Fraction, ...]

    @staticmethod
    def from_iter(values: Iterable) -> "Vector":
        comps = tuple(Fraction(v) for v in values)
        if not comps:
            raise ValueError("Un vector no puede ser vacío.")
        return Vector(comps)

    @property
    def dim(self) -> int:
        return len(self.componentes)

    def is_zero(self) -> bool:
        return all(c == 0 for c in self.componentes)

    def opuesto(self) -> "Vector":
        return Vector(tuple(-c for c in self.componentes))

    def scale(self, escalar) -> "Vector":
        factor = Fraction(escalar)
        return Vector(tuple(factor * c for c in self.componentes))

    def __add__(self, other: "Vector") -> "Vector":
        self._assert_same_dim(other)
        return Vector(tuple(a + b for a, b in zip(self.componentes, other.componentes)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.componentes == other.componentes

    def _assert_same_dim(self, other: "Vector") -> None:
        if self.dim != other.dim:
            raise ValueError("Los vectores deben tener la misma dimensión.")

    def __iter__(self):
        return iter(self.componentes)

    def __repr__(self) -> str:
        return f"Vector({list(self.componentes)!r})"


def parse_vector(texto: str) -> Vector:
    componentes = _parse_tokens(texto)
    return Vector.from_iter(componentes)


def parse_vector_set(texto: str) -> List[Vector]:
    bloques = [segmento.strip() for segmento in texto.split(";") if segmento.strip()]
    if not bloques:
        raise ValueError("No se proporcionaron vectores.")
    vectores = [parse_vector(segmento) for segmento in bloques]
    dim = vectores[0].dim
    for idx, vec in enumerate(vectores[1:], start=2):
        if vec.dim != dim:
            raise ValueError(
                f"Todos los vectores deben tener dimensión {dim}. El vector {idx} tiene {vec.dim}."
            )
    return vectores


def check_conmutativa(u: Vector, v: Vector) -> Tuple[bool, List[str]]:
    u._assert_same_dim(v)
    suma_uv = u + v
    suma_vu = v + u
    cumplimiento = suma_uv == suma_vu
    pasos = [
        f"u + v = { _format_vector(suma_uv) }",
        f"v + u = { _format_vector(suma_vu) }",
        "Comparación componente a componente realizada.",
    ]
    return cumplimiento, pasos


def check_asociativa(u: Vector, v: Vector, w: Vector) -> Tuple[bool, List[str]]:
    u._assert_same_dim(v)
    u._assert_same_dim(w)
    izquierda = (u + v) + w
    derecha = u + (v + w)
    cumplimiento = izquierda == derecha
    pasos = [
        f"(u + v) + w = { _format_vector(izquierda) }",
        f"u + (v + w) = { _format_vector(derecha) }",
    ]
    return cumplimiento, pasos


def check_neutro(u: Vector) -> Tuple[bool, List[str]]:
    cero = Vector(tuple(Fraction(0) for _ in u))
    suma = u + cero
    cumplimiento = suma == u
    pasos = [
        f"Vector cero = { _format_vector(cero) }",
        f"u + 0 = { _format_vector(suma) }",
    ]
    return cumplimiento, pasos


def check_inverso(u: Vector) -> Tuple[bool, List[str]]:
    opuesto = u.opuesto()
    suma = u + opuesto
    cumplimiento = suma.is_zero()
    pasos = [
        f"-u = { _format_vector(opuesto) }",
        f"u + (-u) = { _format_vector(suma) }",
    ]
    return cumplimiento, pasos


def _format_vector(vector: Vector) -> str:
    return "[" + ", ".join(_format_fraction(value) for value in vector.componentes) + "]"


def _format_fraction(value: Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else f"{value.numerator}"
