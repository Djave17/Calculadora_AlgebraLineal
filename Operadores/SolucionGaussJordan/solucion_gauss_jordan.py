from __future__ import annotations
from typing import List, Optional
from Operadores.sistema_lineal import SistemaLineal
from .solucion import Solucion, Parametrica
from .solucionador import Solucionador
from Operadores.estrategia_pivoteo import PivoteoParcial, EstrategiaPivoteo
from Operadores.reductor_escalonado import ReductorEscalonado
from Operadores.registrador import RegistradorOperaciones
from Models.matriz import Matriz

class SolucionadorGaussJordan(Solucionador):
    """
    Resuelve A x = b sobre la matriz aumentada [A|b] llevando a RREF (Gauss-Jordan).
    - Detecta inconsistencia / solución única / infinitas soluciones.
    - Si 'registrar_pasos' es True, adjunta el historial de operaciones.
    """

    def __init__(self, eps: float = 1e-12, pivoteo: Optional[EstrategiaPivoteo] = None):
        self._eps = eps
        self._pivoteo = pivoteo or PivoteoParcial()
        self._reductor = ReductorEscalonado(eps=eps)

    def resolver(self, sistema: SistemaLineal, registrar_pasos: bool = False) -> Solucion:
        A = sistema.A
        b = sistema.b
        aug = sistema.como_matriz_aumentada()
        n_vars = sistema.num_variables()

        registrador = RegistradorOperaciones() if registrar_pasos else None
        res = self._reductor.a_forma_escalonada_reducida(
            matriz_aumentada=aug,
            num_variables=n_vars,
            pivoteo=self._pivoteo,
            registrador=registrador
        )
        R = res.matriz_rref
        pivots = res.columnas_pivote

        # Diagnóstico de inconsistencia: fila [0 ... 0 | c] con c != 0
        col_last = R.columnas - 1
        inconsistent = False
        for i in range(R.filas):
            # chequea si todas las columnas de variables son ~0
            all_zero = True
            for j in range(n_vars):
                if abs(R.obtener(i, j)) > self._eps:
                    all_zero = False
                    break
            if all_zero and abs(R.obtener(i, col_last)) > self._eps:
                inconsistent = True
                break

        if inconsistent:
            return Solucion(
                estado="INCONSISTENTE",
                columnas_pivote=pivots,
                variables_libres=[j for j in range(n_vars) if j not in pivots],
                parametrica=None,
                historial=registrador.historial if registrador else None
            )

        rank = len(pivots)
        free_vars = [j for j in range(n_vars) if j not in pivots]

        # Única solución si rank == n_vars
        if rank == n_vars:
            x = [0.0] * n_vars
            # En RREF cada pivote está en una fila única; leer b
            for i, pcol in enumerate(pivots):
                # Ojo: no garantizamos que pivots estén ordenados por fila; reconstruimos por filas
                # Buscamos fila donde columna pcol tenga 1
                fila = self._fila_pivote(R, pcol)
                x[pcol] = R.obtener(fila, col_last)
            return Solucion(
                estado="UNICA",
                x=x,
                columnas_pivote=pivots,
                variables_libres=free_vars,
                parametrica=None,
                historial=registrador.historial if registrador else None
            )

        # Infinitas soluciones: construir forma paramétrica
        particular = [0.0] * n_vars
        # Fijamos todas libres = 0 para la particular
        for pcol in pivots:
            fila = self._fila_pivote(R, pcol)
            particular[pcol] = R.obtener(fila, col_last)

        direcciones: List[List[float]] = []
        for f in free_vars:
            v = [0.0] * n_vars
            v[f] = 1.0  # parámetro tf
            # Para cada pivote p: x_p = b - sum a_pf * x_f => contribución en dirección = -a_pf
            for pcol in pivots:
                fila = self._fila_pivote(R, pcol)
                coef = R.obtener(fila, f)  # a_{p,f} en la ecuación de la fila del pivote p
                if abs(coef) > self._eps:
                    v[pcol] = -coef
            direcciones.append(v)

        return Solucion(
            estado="INFINITAS",
            x=None,
            columnas_pivote=pivots,
            variables_libres=free_vars,
            parametrica=Parametrica(
                particular=particular,
                direcciones=direcciones,
                libres=free_vars
            ),
            historial=registrador.historial if registrador else None
        )

    def _fila_pivote(self, R: 'Matriz', col_pivote: int) -> int:
        for i in range(R.filas):
            val = R.obtener(i, col_pivote)
            if abs(val - 1.0) <= self._eps:
                return i
        # fallback (no debería ocurrir en RREF)
        for i in range(R.filas):
            if abs(R.obtener(i, col_pivote)) > self._eps:
                return i
        raise RuntimeError("No se encontró fila de pivote para la columna especificada.")

