from __future__ import annotations
from typing import List
from Models.vector import Vector
from Models.matriz import Matriz

class OperadorVectores:
    @staticmethod
    def sumar(v1: Vector, v2: Vector) -> Vector:
        if v1.dimension != v2.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión para sumarse.")
        resultado = [v1[i] + v2[i] for i in range(v1.dimension)]
        return Vector(resultado)

    @staticmethod
    def restar(v1: Vector, v2: Vector) -> Vector:
        if v1.dimension != v2.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión para restarse.")
        resultado = [v1[i] - v2[i] for i in range(v1.dimension)]
        return Vector(resultado)

    @staticmethod
    def producto_escalar(v1: Vector, v2: Vector) -> float:
        if v1.dimension != v2.dimension:
            raise ValueError("Los vectores deben tener la misma dimensión para el producto escalar.")
        return sum(v1[i] * v2[i] for i in range(v1.dimension))

    @staticmethod
    def multiplicar_por_escalar(v: Vector, escalar: float) -> Vector:
        resultado = [v[i] * escalar for i in range(v.dimension)]
        return Vector(resultado)

    @staticmethod
    def producto_vectorial(v1: Vector, v2: Vector) -> Vector:
        if v1.dimension != 3 or v2.dimension != 3:
            raise ValueError("El producto vectorial solo está definido para vectores 3D.")
        x = v1[1] * v2[2] - v1[2] * v2[1]
        y = v1[2] * v2[0] - v1[0] * v2[2]
        z = v1[0] * v2[1] - v1[1] * v2[0]
        return Vector([x, y, z])

    @staticmethod
    def norma(v: Vector) -> float:
        return (sum(x**2 for x in v.como_lista()))**0.5

    @staticmethod
    def combinacion_lineal(vectores: List[Vector], escalares: List[float]) -> Vector:
        if len(vectores) != len(escalares):
            raise ValueError("La cantidad de vectores y escalares debe coincidir.")
        dimension = vectores[0].dimension
        for v in vectores:
            if v.dimension != dimension:
                raise ValueError("Todos los vectores deben tener la misma dimensión.")
        resultado = [0.0] * dimension
        for escalar, vector in zip(escalares, vectores):
            for i in range(dimension):
                resultado[i] += escalar * vector[i]
        return Vector(resultado)

    @staticmethod
    def multiplicar_matriz_vector(matriz: Matriz, vector: Vector) -> Vector:
        if matriz.columnas != vector.dimension:
            raise ValueError("La cantidad de columnas de la matriz debe coincidir con la dimensión del vector.")
        resultado = []
        for i in range(matriz.filas):
            suma = 0.0
            for j in range(matriz.columnas):
                suma += matriz.obtener(i, j) * vector[j]
            resultado.append(suma)
        return Vector(resultado)
