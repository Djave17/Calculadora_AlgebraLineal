from __future__ import annotations
from typing import List, Sequence, Optional
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
