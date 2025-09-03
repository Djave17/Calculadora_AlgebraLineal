from __future__ import annotations
from typing import Protocol
from .sistema_lineal import SistemaLineal
from .solucion import Solucion


class Solucionador(Protocol):
    def resolver(self, sistema: SistemaLineal, registrar_pasos: bool = False) -> Solucion:
        ...
