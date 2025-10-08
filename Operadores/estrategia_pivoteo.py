from __future__ import annotations
from typing import Protocol, Optional
from Models.matriz import Matriz


class EstrategiaPivoteo(Protocol):
    """
    Protocolo de selección de pivote para columna 'col' a partir de 'desde_fila'.
    Debe devolver el índice de fila del pivote o None si no hay pivote válido.
    """
    def seleccionar_pivote(self, m: Matriz, col: int, desde_fila: int, eps: float = 1e-12) -> Optional[int]:
        ...


class SinPivoteo:
    """Selecciona la primera fila (desde_fila..fin) con |m[fila,col]|>eps, sin comparar magnitudes."""
    def seleccionar_pivote(self, m: Matriz, col: int, desde_fila: int, eps: float = 1e-12) -> Optional[int]:
        if col >= m.columnas:
            return None
        for i in range(desde_fila, m.filas):
            if m.obtener(i, col) != 0:
                return i
        return None


class PivoteoParcial:
    """Selecciona la fila con mayor |m[fila,col]| a partir de 'desde_fila' (recomendado)."""
    def seleccionar_pivote(self, m: Matriz, col: int, desde_fila: int, eps: float = 1e-12) -> Optional[int]:
        if col >= m.columnas:
            return None
        mejor_fila = None
        mejor_val = 0
        for i in range(desde_fila, m.filas):
            valor = m.obtener(i, col)
            v = abs(valor)
            if v > mejor_val:
                mejor_val = v
                mejor_fila = i
        if mejor_fila is None or mejor_val == 0:
            return None
        return mejor_fila
