# Models/Errores/manejador_errores.py
from __future__ import annotations
from typing import Sequence, Optional
from .errores import (
    MatrizVaciaError,
    MatrizNoRectangularError,
    DimensionInvalidaError,
    IndiceFueraDeRangoError,
    LongitudFilaIncompatibleError,
    PivoteNumericamenteCeroError,
)

class ManejadorErrores:
    @staticmethod
    def validar_datos_matriz(datos: Sequence[Sequence[float]]) -> None:
        if not datos or not datos[0]:
            raise MatrizVaciaError("La matriz no puede ser vacía (m>0, n>0).")
        n_cols = len(datos[0])
        for fila in datos:
            if len(fila) != n_cols:
                raise MatrizNoRectangularError("Todas las filas deben tener la misma cantidad de columnas.")

    @staticmethod
    def validar_dimensiones_positivas(m: int, n: int) -> None:
        if m <= 0 or n <= 0:
            raise DimensionInvalidaError("Dimensiones deben ser positivas (m>0, n>0).")

    @staticmethod
    def validar_indice_fila(i: int, filas: int) -> None:
        if not (0 <= i < filas):
            raise IndiceFueraDeRangoError(f"Fila fuera de rango: {i} (0..{filas-1}).")

    @staticmethod
    def validar_indice_columna(j: int, columnas: int) -> None:
        if not (0 <= j < columnas):
            raise IndiceFueraDeRangoError(f"Columna fuera de rango: {j} (0..{columnas-1}).")

    @staticmethod
    def validar_indices(i: int, j: int, filas: int, columnas: int) -> None:
        ManejadorErrores.validar_indice_fila(i, filas)
        ManejadorErrores.validar_indice_columna(j, columnas)

    @staticmethod
    def validar_asignacion_fila(i: int, nueva_fila: Sequence[float], filas: int, columnas: int) -> None:
        ManejadorErrores.validar_indice_fila(i, filas)
        if len(nueva_fila) != columnas:
            raise LongitudFilaIncompatibleError(
                f"Esperado {columnas} columnas, recibido {len(nueva_fila)}."
            )

    @staticmethod
    def exigir_pivote_no_cero(pivote: float, eps: float = 1e-12, ubicacion: Optional[str] = None) -> None:
        if abs(pivote) <= eps:
            msg = "Pivote numéricamente cero."
            if ubicacion:
                msg += f" Ubicación: {ubicacion}."
            msg += " Sugerencia: aplicar pivoteo/intercambio de filas."
            raise PivoteNumericamenteCeroError(msg)
