from __future__ import annotations
from typing import List, Sequence

class Vector:
    def __init__(self, datos: Sequence[float]):
        if not datos:
            raise ValueError("El vector no puede ser vacío.")
        self._datos: List[float] = list(float(x) for x in datos)
        self._dimension: int = len(self._datos)

    @property
    def dimension(self) -> int:
        return self._dimension

    def obtener(self, i: int) -> float:
        if not (0 <= i < self._dimension):
            raise IndexError(f"Índice fuera de rango: {i} (0..{self._dimension-1}).")
        return self._datos[i]

    def poner(self, i: int, valor: float) -> None:
        if not (0 <= i < self._dimension):
            raise IndexError(f"Índice fuera de rango: {i} (0..{self._dimension-1}).")
        self._datos[i] = valor

    def como_lista(self) -> List[float]:
        return list(self._datos)

    def __len__(self) -> int:
        return self._dimension

    def __getitem__(self, key: int) -> float:
        return self.obtener(key)

    def __setitem__(self, key: int, value: float) -> None:
        self.poner(key, value)

    def __repr__(self) -> str:
        return f"Vector({self._datos!r})"

    def __str__(self) -> str:
        return f"[{', '.join(f'{v:.6g}' for v in self._datos)}]"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self._datos == other._datos
