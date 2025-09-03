from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Optional, Dict


EstadoSolucion = Literal["UNICA", "INFINITAS", "INCONSISTENTE"]


@dataclass
class Parametrica:
    """
    Representación paramétrica: x = particular + sum_k t_k * v_k
    - particular: List[float]
    - direcciones: List[List[float]]  (una por variable libre)
    - libres: índices de variables libres en el mismo orden que 'direcciones'
    """
    particular: List[float]
    direcciones: List[List[float]]
    libres: List[int]


@dataclass
class Solucion:
    estado: EstadoSolucion
    x: Optional[List[float]] = None              # si es única
    columnas_pivote: Optional[List[int]] = None  # para diagnóstico
    variables_libres: Optional[List[int]] = None
    parametrica: Optional[Parametrica] = None
    historial: Optional[object] = None           # HistorialReduccion (no tipamos duro para desacoplar)
