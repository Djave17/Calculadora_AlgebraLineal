from __future__ import annotations
from typing import List, Sequence, Optional

try:
    from Models.matriz import Matriz
except ModuleNotFoundError:  # Permite ejecutar el módulo directamente
    import os
    import sys

    PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from Models.matriz import Matriz


class SistemaLineal:
    """
    Representa un sistema A x = b.
    - A: Matriz de coeficientes (m x n)
    - b: vector independiente (m)
    """

    def __init__(self, A: Matriz, b: Sequence[float], nombres_variables: Optional[Sequence[str]] = None):
        if A.filas != len(b):
            raise ValueError("Dimensión inconsistente: filas(A) debe coincidir con len(b).")
        self._A = A
        self._b = list(float(x) for x in b)
        self._nombres = list(nombres_variables) if nombres_variables is not None else None

    @property
    def A(self) -> Matriz:
        return self._A

    @property
    def b(self) -> List[float]:
        return list(self._b)

    def num_ecuaciones(self) -> int:
        return self._A.filas

    def num_variables(self) -> int:
        return self._A.columnas

    def nombres_variables(self) -> Optional[List[str]]:
        if self._nombres is None:
            return None
        if len(self._nombres) != self.num_variables():
            raise ValueError("La longitud de nombres_variables no coincide con el número de variables.")
        return list(self._nombres)

    def como_matriz_aumentada(self) -> Matriz:
        """Devuelve la matriz [A|b] (m x (n+1))."""
        datos = []
        for i in range(self._A.filas):
            fila = self._A.obtener_fila(i)
            fila.append(self._b[i])
            datos.append(fila)
        return Matriz(datos)


class SistemaMatricial:
    """Representa una ecuación matricial A X = B con B de una o más columnas."""

    def __init__(
        self,
        A: Matriz,
        B: Sequence[Sequence[float]],
        nombres_variables: Optional[Sequence[str]] = None,
    ) -> None:
        if not B:
            raise ValueError("La matriz B no puede ser vacía.")
        if len(B) != A.filas:
            raise ValueError("Dimensión inconsistente entre A y B.")
        num_cols = len(B[0])
        for fila in B:
            if len(fila) != num_cols:
                raise ValueError("Todas las filas de B deben tener la misma longitud.")
        self._A = A
        self._B = [list(float(x) for x in fila) for fila in B]
        self._nombres = list(nombres_variables) if nombres_variables is not None else None

    @property
    def A(self) -> Matriz:
        return self._A

    @property
    def B(self) -> List[List[float]]:
        return [fila[:] for fila in self._B]

    def num_rhs(self) -> int:
        return len(self._B[0]) if self._B else 0

    def columna_b(self, indice: int) -> List[float]:
        if not (0 <= indice < self.num_rhs()):
            raise IndexError("Índice de columna de B fuera de rango.")
        return [fila[indice] for fila in self._B]

    def sistemas_individuales(self) -> List[SistemaLineal]:
        return [
            SistemaLineal(self._A, self.columna_b(i), nombres_variables=self._nombres)
            for i in range(self.num_rhs())
        ]
