from __future__ import annotations
from typing import List

class StepVM:
    number: int
    description: str
    after_matrix: List[List[float]]
    pivot_row: int | None = None
    pivot_col: int | None = None

class ResultadoRREF:
    def __init__(self, matriz_rref, columnas_pivote: List[int], rango: int):
        self.matriz_rref = matriz_rref
        self.columnas_pivote = columnas_pivote
        self.rango = rango
