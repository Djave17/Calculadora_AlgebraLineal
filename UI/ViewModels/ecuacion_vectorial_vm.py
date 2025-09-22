from dataclasses import dataclass
from typing import List, Optional
from Models.matriz import Matriz
from Operadores.sistema_lineal import SistemaLineal
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial
import re

@dataclass
class EcuacionVectorialResultVM:
    """Resultado de resolver una ecuación vectorial"""
    estado: str  # "UNICA", "INFINITAS", "INCONSISTENTE"
    coeficientes: Optional[List[float]] = None
    pasos: List[str] = None
    matriz_aumentada: Optional[List[List[float]]] = None

class EcuacionVectorialViewModel:
    """ViewModel para resolver ecuaciones vectoriales"""
    
    def __init__(self):
        pass
    
    def parse_vector(self, text: str) -> List[float]:
        """Convierte una cadena en lista de floats"""
        # Reutilizar el mismo método de parseo que en CombinacionLinealViewModel
        if text is None:
            raise ValueError("Entrada vacía para vector.")
        s = text.strip()
        if s == "":
            raise ValueError("Entrada vacía para vector.")
        
        s = s.replace("(", " ").replace(")", " ").replace("[", " ").replace("]", " ")
        tokens = re.split(r'[,\s]+', s.strip())
        vals = []
        
        for t in tokens:
            if t == "":
                continue
            try:
                vals.append(float(t))
            except ValueError:
                raise ValueError(f"Valor no numérico en vector: '{t}'")
        
        if len(vals) == 0:
            raise ValueError("No se detectaron números en el vector.")
        return vals
    
    def _check_same_dim(self, *vecs: List[float]) -> None:
        """Verifica que todos los vectores tengan la misma dimensión"""
        dims = [len(v) for v in vecs]
        if len(set(dims)) != 1:
            raise ValueError(f"Los vectores deben tener la misma dimensión. Dimensiones detectadas: {dims}")
    
    def resolver_ecuacion_vectorial(self, vectores: List[List[float]], vector_b: List[float]) -> EcuacionVectorialResultVM:
        """Resuelve la ecuación vectorial c1v1 + c2v2 + ... + cnvn = b"""
        # Verificar dimensiones
        self._check_same_dim(*vectores, vector_b)
        
        pasos = []
        
        # Construir la ecuación vectorial
        pasos.append("Paso 1: Ecuación vectorial")
        ecuacion_str = "c₁" + str(vectores[0])
        for i in range(1, len(vectores)):
            ecuacion_str += f" + c_{i+1}" + str(vectores[i])
        ecuacion_str += " = " + str(vector_b)
        pasos.append(ecuacion_str)
        
        # Construir matriz aumentada
        n = len(vector_b)
        m = len(vectores)
        matriz_aumentada = []
        
        for i in range(n):
            ecuacion = []
            for j in range(m):
                ecuacion.append(vectores[j][i])
            ecuacion.append(vector_b[i])
            matriz_aumentada.append(ecuacion)
        
        pasos.append("Paso 2: Matriz aumentada del sistema:")
        pasos.append(str(matriz_aumentada))
        
        # Resolver el sistema
        try:
            # Extraer A y b
            A_data = [row[:-1] for row in matriz_aumentada]
            b_data = [row[-1] for row in matriz_aumentada]
            
            A = Matriz(A_data)
            sistema_lineal = SistemaLineal(A, b_data)
            solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
            solucion = solver.resolver(sistema_lineal, registrar_pasos=False)
            
            pasos.append("Paso 3: Resolver el sistema usando eliminación Gaussiana")
            
            if solucion.estado == "UNICA":
                coeficientes = solucion.x
                pasos.append(f"Solución única encontrada: {coeficientes}")
                return EcuacionVectorialResultVM(
                    estado="UNICA",
                    coeficientes=coeficientes,
                    pasos=pasos,
                    matriz_aumentada=matriz_aumentada
                )
            elif solucion.estado == "INFINITAS":
                pasos.append("Infinitas soluciones")
                return EcuacionVectorialResultVM(
                    estado="INFINITAS",
                    pasos=pasos,
                    matriz_aumentada=matriz_aumentada
                )
            else:
                pasos.append("Sistema inconsistente - no hay solución")
                return EcuacionVectorialResultVM(
                    estado="INCONSISTENTE",
                    pasos=pasos,
                    matriz_aumentada=matriz_aumentada
                )
                
        except Exception as e:
            pasos.append(f"Error al resolver el sistema: {str(e)}")
            return EcuacionVectorialResultVM(
                estado="ERROR",
                pasos=pasos,
                matriz_aumentada=matriz_aumentada
            )