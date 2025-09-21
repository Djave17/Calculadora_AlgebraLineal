from Models.vector import Vector
from Operadores.operador_vectores import OperadorVectores

class EcuacionVectorial:
    def __init__(self, punto: Vector, direccion: Vector):
        if punto.dimension != direccion.dimension:
            raise ValueError("El punto y el vector dirección deben tener la misma dimensión.")
        self.punto = punto
        self.direccion = direccion

    def evaluar(self, t: float) -> Vector:
        return OperadorVectores.sumar(
            self.punto,
            OperadorVectores.multiplicar_por_escalar(self.direccion, t)
        )
