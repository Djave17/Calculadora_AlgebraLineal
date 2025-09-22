from dataclasses import dataclass
from typing import List, Tuple, Optional
import re
from Models.matriz import Matriz
from Operadores.sistema_lineal import SistemaLineal
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial

@dataclass
class CombinacionLinealResultVM:
    """Resultado de la verificación de combinación lineal"""
    es_combinacion_lineal: bool
    coeficientes: Optional[List[float]] = None
    pasos: List[str] = None
    sistema: Optional[List[List[float]]] = None
    solucion: Optional[str] = None

class CombinacionLinealViewModel:
    """ViewModel para verificar combinación lineal de vectores"""
    
    def __init__(self, tol: float = 1e-9):
        self.tol = tol
    
    def parse_vector(self, text: str) -> List[float]:
        """Convierte una cadena en lista de floats"""
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
    
    def verificar_combinacion_lineal(self, vectores: List[List[float]], objetivo: List[float]) -> CombinacionLinealResultVM:
        """Verifica si el vector objetivo es combinación lineal de los vectores dados"""
        # Verificar dimensiones
        self._check_same_dim(*vectores, objetivo)
        
        pasos = []
        sistema = []
        
        # Construir el sistema de ecuaciones
        pasos.append("Paso 1: Plantear el sistema de ecuaciones")
        sistema_str = f"k₁{vectores[0]}"
        for i in range(1, len(vectores)):
            sistema_str += f" + k_{i+1}{vectores[i]}"
        sistema_str += f" = {objetivo}"
        pasos.append(sistema_str)
        
        # Construir matriz del sistema
        n = len(objetivo)
        m = len(vectores)
        matriz_sistema = []
        
        for i in range(n):
            ecuacion = []
            for j in range(m):
                ecuacion.append(vectores[j][i])
            ecuacion.append(objetivo[i])
            matriz_sistema.append(ecuacion)
        
        sistema = matriz_sistema
        pasos.append("Paso 2: Matriz aumentada del sistema:")
        pasos.append(str(matriz_sistema))
        
        # Resolver el sistema
        try:
            # Extraer A и b
            A_data = [row[:-1] for row in matriz_sistema]
            b_data = [row[-1] for row in matriz_sistema]
            
            A = Matriz(A_data)
            sistema_lineal = SistemaLineal(A, b_data)
            solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
            solucion = solver.resolver(sistema_lineal, registrar_pasos=False)
            
            pasos.append("Paso 3: Resolver el sistema usando eliminación Gaussiana")
            
            if solucion.estado == "UNICA":
                coeficientes = solucion.x
                pasos.append(f"Solución única encontrada: {coeficientes}")
                return CombinacionLinealResultVM(
                    es_combinacion_lineal=True,
                    coeficientes=coeficientes,
                    pasos=pasos,
                    sistema=matriz_sistema,
                    solucion="Única"
                )
            elif solucion.estado == "INFINITAS":
                pasos.append("Infinitas soluciones - el vector es combinación lineal")
                return CombinacionLinealResultVM(
                    es_combinacion_lineal=True,
                    pasos=pasos,
                    sistema=matriz_sistema,
                    solucion="Infinitas"
                )
            else:
                pasos.append("Sistema inconsistente - el vector NO es combinación lineal")
                return CombinacionLinealResultVM(
                    es_combinacion_lineal=False,
                    pasos=pasos,
                    sistema=matriz_sistema,
                    solucion="Ninguna"
                )
                
        except Exception as e:
            pasos.append(f"Error al resolver el sistema: {str(e)}")
            return CombinacionLinealResultVM(
                es_combinacion_lineal=False,
                pasos=pasos,
                sistema=matriz_sistema,
                solucion="Error"
            )