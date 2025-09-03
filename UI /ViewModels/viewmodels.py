# Esqueleto; sin lógica de presentación aún.
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MatrizEntradaVM:
    filas: int
    columnas: int
    A: List[List[float]]
    b: List[float]
    nombres: Optional[List[str]] = None

@dataclass
class PasoVM:
    numero: int
    operacion: str
    descripcion: str
    antes: List[List[float]]
    despues: List[List[float]]

@dataclass
class ResultadoVM:
    estado: str
    solucion: Optional[List[float]]
    columnas_pivote: List[int]
    variables_libres: List[int]
    particular: Optional[List[float]]
    direcciones: Optional[List[List[float]]]
    pasos: Optional[List[PasoVM]]  # para “modo paso a paso”
