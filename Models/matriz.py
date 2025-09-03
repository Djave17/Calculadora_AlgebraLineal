""" 
Clase operaciones básicas (obtener/establecer elementos, intercambiar filas, multiplicar filas, etc.)
@Rol: Contenedor de datos y operaciones elementales de fila.
Representa una matriz densa de tamaño (filas x columnas) y provee
operaciones elementales de fila (intercambio, escalar, suma de filas) necesarias para métodos de forma escalonada / escalonada reducida.

""" 

# algebra_lineal/Models/matriz.py
from __future__ import annotations
from typing import List, Sequence, Tuple
from Models.Errores.errores import ManejadorErrores as ME


class Matriz:

    def __init__(self, datos: Sequence[Sequence[float]]):
        if not datos or not datos[0]:
            raise ValueError("La matriz no puede ser vacía.")
        n_cols = len(datos[0])
        for fila in datos:
            if len(fila) != n_cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas.")
        # Copia profunda para evitar aliasing externo
        self._datos: List[List[float]] = [list(f) for f in datos]
        self._filas: int = len(self._datos)
        self._cols: int = n_cols

    # -------------------- Propiedades --------------------
    
    @property
    def filas(self) -> int:
        return self._filas

    @property
    def columnas(self) -> int:
        return self._cols

    def forma(self) -> Tuple[int, int]:
        return self._filas, self._cols

    # -------------------- Acceso seguro --------------------
    def _validar_indices(self, i: int, j: int) -> None:
        ME.validar_datos_matriz(self._datos)
        if not (0 <= i < self._filas):
            raise IndexError(f"Índice de fila fuera de rango: {i}")
        if not (0 <= j < self._cols):
            raise IndexError(f"Índice de columna fuera de rango: {j}")

    def obtener(self, i: int, j: int) -> float:
        ME.validar_indices(i, j, self._filas, self._cols)
        return self._datos[i][j]

    def poner(self, i: int, j: int, valor: float) -> None:
        ME.validar_indices(i, j, self._filas, self._cols)
        self._datos[i][j] = valor

    # Acceso por fila completa (copia para preservar encapsulamiento)
    def obtener_fila(self, i: int) -> List[float]:
        ME.validar_indice_fila(i, self._filas)
        return list(self._datos[i])

    def asignar_fila(self, i: int, nueva_fila: Sequence[float]) -> None:
        ME.validar_indice_fila(i, self._filas)
        if len(nueva_fila) != self._cols:
            raise ValueError("Longitud de fila incompatible con la matriz.")
        self._datos[i] = list(nueva_fila)

    # -------------------- Copias / Representación --------------------
    def clonar(self) -> "Matriz":
        # Retorna una copia de la matriz mediante la creación de una nueva instancia de Matriz
        return Matriz([fila[:] for fila in self._datos])

    def como_lista(self) -> List[List[float]]:
        # Retorna una representación de la matriz como una lista de listas.
        return [fila[:] for fila in self._datos]

    # Metodo para representación en cadena
    def __repr__(self) -> str:
        # Representación de la matriz
        return f"Matriz({self._datos!r})"

    # Representación en cadena
    def __str__(self) -> str:
        # Filas de la matriz
        filas_str = ["[" + ", ".join(f"{v:.6g}" for v in fila) + "]" for fila in self._datos]
        return "[" + ",\n ".join(filas_str) + "]"
