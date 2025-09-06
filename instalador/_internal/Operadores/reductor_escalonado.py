from __future__ import annotations
from typing import List, Optional, Tuple
from Models.matriz import Matriz
from .operador_filas import OperadorFilas
from .estrategia_pivoteo import EstrategiaPivoteo
from .registrador import RegistradorOperaciones


class ResultadoRREF:
    def __init__(self, matriz_rref: Matriz, columnas_pivote: List[int], rango: int):
        self.matriz_rref = matriz_rref
        self.columnas_pivote = columnas_pivote
        self.rango = rango


class ReductorEscalonado:
    """
    Lleva la matriz aumentada [A|b] a Forma Escalonada Reducida (RREF) con Gauss-Jordan.
    - Usa EstrategiaPivoteo para elegir pivote en cada columna de variables.
    - Registra pasos si se provee un RegistradorOperaciones.
    """

    def __init__(self, eps: float = 1e-12):
        self._eps = eps

    def a_forma_escalonada_reducida(
        self,
        matriz_aumentada: Matriz,
        num_variables: int,
        pivoteo: EstrategiaPivoteo,
        registrador: Optional[RegistradorOperaciones] = None
    ) -> ResultadoRREF:
        m = matriz_aumentada.clonar()
        op = OperadorFilas(m)
        r = 0  # fila actual de pivote
        columnas_pivote: List[int] = []

        for c in range(num_variables):  # solo columnas de variables (excluye término independiente)
            if r >= m.filas:
                break

            # Seleccionar pivote
            fila_piv = pivoteo.seleccionar_pivote(m, c, r, eps=self._eps)
            if fila_piv is None:
                continue

            # Intercambiar si es necesario
            if fila_piv != r:
                antes = m.como_lista() if registrador else None
                op.intercambiar(fila_piv, r)
                if registrador:
                    registrador.nuevo_paso(
                        operacion="INTERCAMBIO_FILAS",
                        pivote_fila=r, pivote_col=c,
                        filas_afectadas=[fila_piv, r],
                        antes=antes, despues=m.como_lista(),
                        descripcion=f"Intercambio R{fila_piv} <-> R{r}"
                    )

            # Normalizar pivote a 1
            antes = m.como_lista() if registrador else None
            op.normalizar_pivote(r, c, eps=self._eps)
            if registrador:
                registrador.nuevo_paso(
                    operacion="NORMALIZAR_PIVOTE",
                    pivote_fila=r, pivote_col=c,
                    antes=antes, despues=m.como_lista(),
                    descripcion=f"Normalizar pivote en ({r},{c}) a 1"
                )

            # Anular por debajo y por encima
            # Debajo
            for i in range(r + 1, m.filas):
                val = m.obtener(i, c)
                if abs(val) > self._eps:
                    antes = m.como_lista() if registrador else None
                    op.combinar(i, r, -val)  # Ri <- Ri - val * Rr
                    if registrador:
                        registrador.nuevo_paso(
                            operacion="ELIMINAR_DEBAJO",
                            pivote_fila=r, pivote_col=c,
                            filas_afectadas=[i],
                            factor=-val,
                            antes=antes, despues=m.como_lista(),
                            descripcion=f"R{i} <- R{i} - ({val:.6g}) * R{r}"
                        )
            # Encima
            for i in range(0, r):
                val = m.obtener(i, c)
                if abs(val) > self._eps:
                    antes = m.como_lista() if registrador else None
                    op.combinar(i, r, -val)  # Ri <- Ri - val * Rr
                    if registrador:
                        registrador.nuevo_paso(
                            operacion="ELIMINAR_ENCIMA",
                            pivote_fila=r, pivote_col=c,
                            filas_afectadas=[i],
                            factor=-val,
                            antes=antes, despues=m.como_lista(),
                            descripcion=f"R{i} <- R{i} - ({val:.6g}) * R{r}"
                        )

            columnas_pivote.append(c)
            r += 1

        return ResultadoRREF(matriz_rref=m, columnas_pivote=columnas_pivote, rango=len(columnas_pivote))
