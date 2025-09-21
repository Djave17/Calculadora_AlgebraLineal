from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from Models.vector import Vector
from Models.ecuacion_vectorial import EcuacionVectorial
from Models.matriz import Matriz
from Operadores.operador_vectores import OperadorVectores

@dataclass
class VectorResultVM:
    operation_name: str
    result_vector: Optional[List[float]] = None
    result_scalar: Optional[float] = None
    error_message: Optional[str] = None

class VectorCalculatorViewModel:
    def __init__(self):
        self._dimension: int = 3

    @property
    def dimension(self) -> int:
        return self._dimension

    @dimension.setter
    def dimension(self, value: int) -> None:
        self._dimension = max(1, value)

    def perform_operation(self,
                          operation_type: str,
                          vector1_data: List[float],
                          vector2_data: Optional[List[float]] = None,
                          escalares: Optional[List[float]] = None,
                          matriz_data: Optional[List[List[float]]] = None,
                          parametro_t: Optional[float] = None,
                          scalar_value: Optional[float] = None) -> VectorResultVM:
        try:
            if len(vector1_data) != self._dimension:
                raise ValueError(f"El vector 1 debe tener dimensión {self._dimension}.")
            if vector2_data is not None and len(vector2_data) != self._dimension:
                raise ValueError(f"El vector 2 debe tener dimensión {self._dimension}.")

            v1 = Vector(vector1_data)
            v2 = Vector(vector2_data) if vector2_data is not None else None

            if v1.dimension != self._dimension and operation_type != "norma":
                raise ValueError(f"El vector 1 debe tener dimensión {self._dimension}.")
            if v2 and v2.dimension != self._dimension:
                raise ValueError(f"El vector 2 debe tener dimensión {self._dimension}.")

            if operation_type == "sumar":
                result = OperadorVectores.sumar(v1, v2)
                return VectorResultVM("Suma", result_vector=result.como_lista())

            elif operation_type == "restar":
                result = OperadorVectores.restar(v1, v2)
                return VectorResultVM("Resta", result_vector=result.como_lista())

            elif operation_type == "producto_escalar":
                result = OperadorVectores.producto_escalar(v1, v2)
                return VectorResultVM("Producto Escalar", result_scalar=result)

            elif operation_type == "multiplicar_por_escalar":
                if scalar_value is None:
                    raise ValueError("Se requiere un valor escalar para esta operación.")
                result = OperadorVectores.multiplicar_por_escalar(v1, scalar_value)
                return VectorResultVM("Multiplicación por Escalar", result_vector=result.como_lista())

            elif operation_type == "producto_vectorial":
                result = OperadorVectores.producto_vectorial(v1, v2)
                return VectorResultVM("Producto Vectorial", result_vector=result.como_lista())

            elif operation_type == "norma":
                result = OperadorVectores.norma(v1)
                return VectorResultVM("Norma", result_scalar=result)

            elif operation_type == "combinacion_lineal":
                if escalares is None or len(escalares) == 0:
                    raise ValueError("Se requieren escalares para la combinación lineal.")
                vectores = [Vector(v) for v in vector2_data] if vector2_data else []
                vectores.insert(0, v1)  # incluir v1 como primer vector
                if len(vectores) != len(escalares):
                    raise ValueError("Número de vectores y escalares debe coincidir.")
                result = OperadorVectores.combinacion_lineal(vectores, escalares)
                return VectorResultVM("Combinación Lineal", result_vector=result.como_lista())

            elif operation_type == "ecuacion_vectorial":
                if vector2_data is None or parametro_t is None:
                    raise ValueError("Se requiere vector dirección y parámetro t para ecuación vectorial.")
                direccion = Vector(vector2_data)
                ecuacion = EcuacionVectorial(v1, direccion)
                result = ecuacion.evaluar(parametro_t)
                return VectorResultVM("Ecuación Vectorial", result_vector=result.como_lista())

            elif operation_type == "multiplicar_matriz_vector":
                if matriz_data is None:
                    raise ValueError("Se requiere matriz para esta operación.")
                matriz = Matriz(matriz_data)
                result = OperadorVectores.multiplicar_matriz_vector(matriz, v1)
                return VectorResultVM("Multiplicación Matriz-Vector", result_vector=result.como_lista())

            else:
                return VectorResultVM("Error", error_message="Operación no soportada.")

        except ValueError as e:
            return VectorResultVM("Error", error_message=str(e))
        except Exception as e:
            return VectorResultVM("Error", error_message=f"Error inesperado: {e}")
