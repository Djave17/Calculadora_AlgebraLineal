# algebra_lineal/fabrica/fabrica_matriz.py
from __future__ import annotations
from typing import Iterable
from Models.matriz import Matriz


class FabricaMatriz:
    """Fábrica de matrices (responsabilidad separada de la clase Matriz)."""

    @staticmethod
    def identidad(n: int) -> Matriz:
        if n <= 0:
            raise ValueError("El tamaño debe ser positivo.")
        datos = [[0.0] * n for _ in range(n)]
        for i in range(n):
            datos[i][i] = 1.0
        return Matriz(datos)

    @staticmethod
    def ceros(m: int, n: int) -> Matriz:
        if m <= 0 or n <= 0:
            raise ValueError("Dimensiones deben ser positivas.")
        return Matriz([[0.0] * n for _ in range(m)])

    @staticmethod
    def desde_filas(filas: Iterable[Iterable[float]]) -> Matriz:
        return Matriz([list(f) for f in filas])
