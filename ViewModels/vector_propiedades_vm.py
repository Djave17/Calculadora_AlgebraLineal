"""Operaciones para la página de propiedades vectoriales.

Se apoya en la teoría de Grossman (2019, cap. 2) para verificar las
propiedades básicas de un espacio vectorial.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Tuple


@dataclass
class VectorResultVM:
    """Pequeña estructura para devolver resultado + pasos."""

    operation: str  # "sum", "scalar", ...
    result: List[Fraction]
    steps: List[str]


class VectorPropiedadesViewModel:
    """Lógica de operaciones y verificación de propiedades en R^n."""

    def __init__(self, tol: float = 1e-9) -> None:
        self.tol = tol

    def parse_vector(self, text: str) -> List[Fraction]:
        """Convierte una cadena en lista de fracciones exactas.

        Acepta formatos como ``1,2,3/5`` o ``(1/2  3)`` y genera mensajes
        claros si alguna componente no puede convertirse en número racional.
        """

        if text is None:
            raise ValueError(
                "Debes proporcionar componentes para el vector conforme a la definición de ℝⁿ (Lay, §1.2)."
            )
        s = text.strip()
        if s == "":
            raise ValueError(
                "Debes proporcionar componentes para el vector conforme a la definición de ℝⁿ (Lay, §1.2)."
            )
        s = s.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ")
        tokens = re.split(r"[\s,]+", s.strip())
        valores: List[Fraction] = []
        for token in tokens:
            if token == "":
                continue
            try:
                valores.append(Fraction(token))
            except ValueError as exc:
                raise ValueError(
                    f"El valor '{token}' no puede convertirse en fracción racional; "
                    "recuerda que en ℝ cada componente debe ser un número real (Grossman, cap. 1)."
                ) from exc
        if not valores:
            raise ValueError(
                "No se detectaron componentes numéricas; revisa el formato propuesto en clase."
            )
        return valores

    def parse_scalar(self, text: str) -> Fraction:
        """Interpreta el texto de la IU como un escalar (posible fracción)."""

        if text is None:
            raise ValueError("Debes proporcionar un valor para α.")
        normalized = text.strip().replace(" ", "")
        if normalized == "":
            raise ValueError("Debes proporcionar un valor para α.")
        try:
            return Fraction(normalized)
        except ValueError as exc:
            raise ValueError(
                f"El valor '{text}' no es un número racional válido para α; "
                "recuerda que la multiplicación por escalar requiere un elemento del cuerpo (Lay, §1.1)."
            ) from exc

    def _check_same_dim(self, *vecs: List[Fraction]) -> None:
        dims = [len(v) for v in vecs]
        if len(set(dims)) != 1:
            raise ValueError(
                "Todos los vectores deben compartir dimensión para operar en ℝⁿ "
                "(Lay, §1.2). Dimensiones detectadas: "
                f"{dims}"
            )

    def _approx_equal(self, a: List[Fraction], b: List[Fraction]) -> bool:
        if len(a) != len(b):
            return False
        return all(abs(x - y) <= self.tol for x, y in zip(a, b))

    def sum_vectors(self, u: List[Fraction], v: List[Fraction]) -> VectorResultVM:
        self._check_same_dim(u, v)
        steps = [f"Suma componente a componente (dim={len(u)})"]
        resultado: List[Fraction] = []
        for i, (ui, vi) in enumerate(zip(u, v), start=1):
            valor = ui + vi
            steps.append(f"x{i}: {ui} + {vi} = {valor}")
            resultado.append(valor)
        return VectorResultVM("sum", resultado, steps)

    def subtract_vectors(self, u: List[Fraction], v: List[Fraction]) -> VectorResultVM:
        self._check_same_dim(u, v)
        steps = [f"Resta componente a componente (dim={len(u)})"]
        resultado: List[Fraction] = []
        for i, (ui, vi) in enumerate(zip(u, v), start=1):
            valor = ui - vi
            steps.append(f"x{i}: {ui} - {vi} = {valor}")
            resultado.append(valor)
        return VectorResultVM("sub", resultado, steps)

    def scalar_mult(self, alpha: Fraction, u: List[Fraction]) -> VectorResultVM:
        steps = [f"Multiplicación por escalar α = {alpha}"]
        resultado: List[Fraction] = []
        for i, ui in enumerate(u, start=1):
            valor = alpha * ui
            steps.append(f"x{i}: {alpha} * {ui} = {valor}")
            resultado.append(valor)
        return VectorResultVM("scalar", resultado, steps)

    def verify_properties(
        self,
        u: List[Fraction],
        v: List[Fraction],
        w: Optional[List[Fraction]] = None,
    ) -> List[Tuple[str, bool, List[str]]]:
        """Verifica y detalla las propiedades básicas de ℝⁿ."""

        self._check_same_dim(u, v)
        n = len(u)
        if w is None:
            w = [Fraction(1) for _ in range(n)]
        else:
            self._check_same_dim(u, w)

        resultados: List[Tuple[str, bool, List[str]]] = []

        # Conmutativa
        suma_uv = self.sum_vectors(u, v).result
        suma_vu = self.sum_vectors(v, u).result
        ok = self._approx_equal(suma_uv, suma_vu)
        pasos = [
            f"u + v = {suma_uv}",
            f"v + u = {suma_vu}",
            "Comparación elemento a elemento.",
        ]
        resultados.append(("Conmutativa", ok, pasos))

        # Asociativa
        izquierda = self.sum_vectors(self.sum_vectors(u, v).result, w).result
        derecha = self.sum_vectors(u, self.sum_vectors(v, w).result).result
        ok = self._approx_equal(izquierda, derecha)
        pasos = [
            f"(u + v) + w = {izquierda}",
            f"u + (v + w) = {derecha}",
            f"w utilizado = {w}",
        ]
        resultados.append(("Asociativa", ok, pasos))

        # Vector cero
        cero = [Fraction(0) for _ in range(n)]
        suma_con_cero = self.sum_vectors(u, cero).result
        ok = self._approx_equal(suma_con_cero, u)
        pasos = [f"Vector cero = {cero}", f"u + 0 = {suma_con_cero}"]
        resultados.append(("Existencia de vector cero", ok, pasos))

        # Vector opuesto
        opuesto = [-x for x in u]
        suma_opuesto = self.sum_vectors(u, opuesto).result
        ok = self._approx_equal(suma_opuesto, cero)
        pasos = [f"-u = {opuesto}", f"u + (-u) = {suma_opuesto}"]
        resultados.append(("Existencia de vector opuesto", ok, pasos))

        return resultados
