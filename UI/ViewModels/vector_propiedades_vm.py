# UI/ViewModels/vector_properties_vm.py
from dataclasses import dataclass
from typing import List, Tuple, Optional
import re

@dataclass
class VectorResultVM:
    """Pequeña estructura para devolver resultado + pasos."""
    operation: str            # "sum", "scalar", ...
    result: List[float]
    steps: List[str]

class VectorPropiedadesViewModel:
    """Lógica de operaciones y verificación de propiedades en R^n."""
    def __init__(self, tol: float = 1e-9):
        self.tol = tol

    def parse_vector(self, text: str) -> List[float]:
        """Convierte una cadena en lista de floats.
        Permite: '1,2,3', '1 2 3', '(1, 2, 3)', '[1 2 3]'...
        Lanza ValueError con mensaje útil si falla.
        """
        if text is None:
            raise ValueError("Entrada vacía para vector.")
        s = text.strip()
        if s == "":
            raise ValueError("Entrada vacía para vector.")
        # quitar paréntesis/ corchetes y separar por comas/espacios
        s = s.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ")
        tokens = re.split(r'[,\s]+', s.strip())
        vals = []
        for t in tokens:
            if t == "":
                continue
            try:
                vals.append(float(t))
            except ValueError:
                raise ValueError(f"Valor no numérico en vector: '{t}'")
        if len(vals) == 0:
            raise ValueError("No se detectaron números en el vector.")
        return vals

    def _check_same_dim(self, *vecs: List[float]) -> None:
        dims = [len(v) for v in vecs]
        if len(set(dims)) != 1:
            raise ValueError(f"Los vectores deben tener la misma dimensión. Dimensiones detectadas: {dims}")

    def _approx_equal(self, a: List[float], b: List[float]) -> bool:
        if len(a) != len(b):
            return False
        return all(abs(x - y) <= self.tol for x, y in zip(a, b))

    def sum_vectors(self, u: List[float], v: List[float]) -> VectorResultVM:
        self._check_same_dim(u, v)
        steps = [f"Suma componente a componente (dim={len(u)})"]
        res = []
        for i, (ui, vi) in enumerate(zip(u, v), start=1):
            ri = ui + vi
            steps.append(f"x{i}: {ui} + {vi} = {ri}")
            res.append(ri)
        return VectorResultVM("sum", res, steps)

    def scalar_mult(self, alpha: float, u: List[float]) -> VectorResultVM:
        steps = [f"Multiplicación por escalar α = {alpha}"]
        res = []
        for i, ui in enumerate(u, start=1):
            ri = alpha * ui
            steps.append(f"x{i}: {alpha} * {ui} = {ri}")
            res.append(ri)
        return VectorResultVM("scalar", res, steps)

    def verify_properties(
        self,
        u: List[float],
        v: List[float],
        w: Optional[List[float]] = None
    ) -> List[Tuple[str, bool, List[str]]]:
        """
        Verifica (y explica) las propiedades:
          - Conmutativa de la suma
          - Asociativa de la suma (usa w si se proporciona; si no, usa w=(1,...,1))
          - Existencia del vector cero
          - Existencia del vector opuesto
        Devuelve lista de tuplas: (nombre_propiedad, cumple_bool, pasos_lista)
        """
        self._check_same_dim(u, v)
        n = len(u)
        if w is None:
            w = [1.0] * n
        else:
            self._check_same_dim(u, w)

        results = []

        # Conmutativa
        s_uv = self.sum_vectors(u, v).result
        s_vu = self.sum_vectors(v, u).result
        ok = self._approx_equal(s_uv, s_vu)
        steps = [f"u + v = {s_uv}", f"v + u = {s_vu}", "Comparación elemento a elemento."]
        results.append(("Conmutativa", ok, steps))

        # Asociativa
        left = self.sum_vectors(self.sum_vectors(u, v).result, w).result
        right = self.sum_vectors(u, self.sum_vectors(v, w).result).result
        ok = self._approx_equal(left, right)
        steps = [f"(u + v) + w = {left}", f"u + (v + w) = {right}", f"w utilizado = {w}"]
        results.append(("Asociativa", ok, steps))

        # Vector cero
        zero = [0.0] * n
        uzero = self.sum_vectors(u, zero).result
        ok = self._approx_equal(uzero, u)
        steps = [f"Vector cero = {zero}", f"u + 0 = {uzero}"]
        results.append(("Existencia de vector cero", ok, steps))

        # Vector opuesto
        neg_u = [-x for x in u]
        u_plus_neg = self.sum_vectors(u, neg_u).result
        ok = self._approx_equal(u_plus_neg, zero)
        steps = [f"-u = {neg_u}", f"u + (-u) = {u_plus_neg}"]
        results.append(("Existencia de vector opuesto", ok, steps))

        return results