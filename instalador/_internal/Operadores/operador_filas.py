# algebra_lineal/Operadores/operador_filas.py
from __future__ import annotations
from typing import Optional
from Models.matriz import Matriz


class OperadorFilas:
    """
    Servicio de operaciones elementales de fila sobre una instancia de Matriz.
    Responsabilidad: aplicar intercambios, escalados y combinaciones lineales
    (útil para Gauss/Gauss-Jordan). Mantiene la Matriz desacoplada de la lógica.
    """

    def __init__(self, matriz: Matriz):
        self._m = matriz

    @property
    def matriz(self) -> Matriz:
        return self._m

    def intercambiar(self, i: int, j: int) -> None:
        if i == j:
            return
        fila_i = self._m.obtener_fila(i)
        fila_j = self._m.obtener_fila(j)
        self._m.asignar_fila(i, fila_j)
        self._m.asignar_fila(j, fila_i)

    def escalar(self, i: int, factor: float) -> None:
        if not (0 <= i < self._m.filas):
            raise IndexError("Índice de fila fuera de rango.")
        if factor == 0.0:
            # Permitimos, pero no es útil para normalizar pivote
            self._m.asignar_fila(i, [0.0] * self._m.columnas)
            return
        fila = self._m.obtener_fila(i)
        self._m.asignar_fila(i, [factor * x for x in fila])

    def combinar(self, destino: int, fuente: int, factor: float) -> None:
        """
        destino <- destino + factor * fuente
        """
        if not (0 <= destino < self._m.filas) or not (0 <= fuente < self._m.filas):
            raise IndexError("Índice de fila fuera de rango.")
        if destino == fuente and factor != 0.0:
            raise ValueError("No tiene sentido combinar una fila consigo misma con factor != 0.")
        fd = self._m.obtener_fila(destino)
        fs = self._m.obtener_fila(fuente)
        if len(fd) != len(fs):
            raise ValueError("Filas de distinta longitud.")
        self._m.asignar_fila(destino, [a + factor * b for a, b in zip(fd, fs)])

    def normalizar_pivote(self, fila: int, col_pivote: int, eps: float = 1e-12) -> None:
        """
        Escala la fila para que el elemento en col_pivote sea 1 (si |pivote|>eps).
        """
        pivote = self._m.obtener(fila, col_pivote)
        if abs(pivote) <= eps:
            raise ZeroDivisionError("Pivote numéricamente cero; requiere pivoteo o reordenamiento.")
        self.escalar(fila, 1.0 / pivote)
