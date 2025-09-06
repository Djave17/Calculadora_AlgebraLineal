from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Optional
from typing import List, Optional

class PasoGaussJordan:
    def __init__(
        self,
        numero: int,
        operacion: str,
        pivote_fila: Optional[int],
        pivote_col: Optional[int],
        filas_afectadas: List[int],
        descripcion: str,
        matriz: List[List[float]]
    ):
        self.numero = numero                # número del paso
        self.operacion = operacion          # tipo de operación (ej: "F2 <- F2 - 3F1")
        self.pivote_fila = pivote_fila      # fila del pivote usado en este paso
        self.pivote_col = pivote_col        # columna del pivote
        self.filas_afectadas = filas_afectadas  # filas modificadas en este paso
        self.descripcion = descripcion      # texto explicativo
        self.matriz = matriz                # copia de la matriz después de este paso



Operacion = Literal[
    "SELECCION_PIVOTE",
    "INTERCAMBIO_FILAS",
    "ESCALAR_FILA",
    "ELIMINAR_DEBAJO",
    "ELIMINAR_ENCIMA",
    "NORMALIZAR_PIVOTE"
]


@dataclass
class PasoReduccion:
    numero: int
    operacion: Operacion
    pivote_fila: Optional[int] = None
    pivote_col: Optional[int] = None
    filas_afectadas: List[int] = field(default_factory=list)
    factor: Optional[float] = None
    antes: Optional[List[List[float]]] = None   # matriz aumentada antes
    despues: Optional[List[List[float]]] = None # matriz aumentada después
    descripcion: str = ""


@dataclass
class HistorialReduccion:
    pasos: List[PasoReduccion] = field(default_factory=list)

    def agregar(self, paso: PasoReduccion) -> None:
        self.pasos.append(paso)


class RegistradorOperaciones:
    """
    Guarda los pasos aplicados durante la reducción (útil para la GUI).
    """
    def __init__(self) -> None:
        self._historial = HistorialReduccion()
        self._contador = 0

    def nuevo_paso(self,
                   operacion: Operacion,
                   pivote_fila: Optional[int] = None,
                   pivote_col: Optional[int] = None,
                   filas_afectadas: Optional[List[int]] = None,
                   factor: Optional[float] = None,
                   antes: Optional[List[List[float]]] = None,
                   despues: Optional[List[List[float]]] = None,
                   descripcion: str = "") -> None:
        self._contador += 1
        self._historial.agregar(PasoReduccion(
            numero=self._contador,
            operacion=operacion,
            pivote_fila=pivote_fila,
            pivote_col=pivote_col,
            filas_afectadas=filas_afectadas or [],
            factor=factor,
            antes=antes,
            despues=despues,
            descripcion=descripcion
        ))

    @property
    def historial(self) -> HistorialReduccion:
        return self._historial
