from dataclasses import dataclass
from typing import List, Optional, Union
import re  # AÑADIR ESTE IMPORT
from Models.matriz import Matriz
from Operadores.sistema_lineal import SistemaLineal
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial

@dataclass
class EcuacionMatricialResultVM:
    """Resultado de resolver una ecuación matricial"""
    estado: str  # "SOLUCION", "SIN_SOLUCION", "ERROR"
    solucion: Optional[Matriz] = None
    pasos: List[str] = None
    matriz_aumentada: Optional[List[List[float]]] = None

class EcuacionMatricialViewModel:
    """ViewModel para resolver ecuaciones matriciales AX = B"""
    
    def __init__(self):
        pass
    
    def parse_matriz(self, text: str) -> List[List[float]]:
        """Convierte texto en matriz (lista de listas de floats)"""
        lineas = text.strip().split('\n')
        matriz = []
        
        for linea in lineas:
            linea = linea.strip()
            if linea == "":
                continue
                
            # Separar por espacios o comas
            elementos = re.split(r'[,\s]+', linea)
            fila = []
            
            for elem in elementos:
                if elem == "":
                    continue
                try:
                    fila.append(float(elem))
                except ValueError:
                    raise ValueError(f"Valor no numérico en matriz: '{elem}'")
            
            if fila:
                matriz.append(fila)
        
        if not matriz:
            raise ValueError("Matriz vacía")
        
        # Verificar que todas las filas tengan la misma longitud
        n_cols = len(matriz[0])
        for i, fila in enumerate(matriz):
            if len(fila) != n_cols:
                raise ValueError(f"Fila {i+1} tiene longitud diferente a la primera fila")
        
        return matriz
    
    def resolver_ecuacion_matricial(self, A_data: List[List[float]], B_data: Union[List[float], List[List[float]]]) -> EcuacionMatricialResultVM:
        """Resuelve la ecuación matricial AX = B"""
        pasos = []
        
        # Convertir B a matriz si es un vector
        if isinstance(B_data[0], (int, float)):
            # B es un vector, convertirlo a matriz columna
            B_matriz = [[b] for b in B_data]
        else:
            # B ya es una matriz
            B_matriz = B_data
        
        pasos.append("Paso 1: Ecuación matricial AX = B")
        pasos.append(f"A = {A_data}")
        pasos.append(f"B = {B_matriz}")
        
        # Verificar dimensiones
        if len(A_data) != len(B_matriz):
            raise ValueError("El número de filas de A debe coincidir con el número de filas de B")
        
        # Para cada columna de B, resolver el sistema A X_col = B_col
        soluciones = []
        matriz_aumentada = None
        
        for col_idx in range(len(B_matriz[0])):
            pasos.append(f"Resolviendo para la columna {col_idx+1} de X:")
            
            # Extraer la columna actual de B
            b_col = [fila[col_idx] for fila in B_matriz]
            
            # Construir matriz aumentada [A | b_col]
            matriz_aumentada_col = []
            for i in range(len(A_data)):
                fila = A_data[i][:]  # Copiar fila de A
                fila.append(b_col[i])  # Añadir elemento de b
                matriz_aumentada_col.append(fila)
            
            if matriz_aumentada is None:
                matriz_aumentada = matriz_aumentada_col
            
            pasos.append(f"Matriz aumentada para columna {col_idx+1}: {matriz_aumentada_col}")
            
            # Resolver el sistema
            try:
                A_mat = Matriz(A_data)
                sistema = SistemaLineal(A_mat, b_col)
                solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
                solucion = solver.resolver(sistema, registrar_pasos=False)
                
                if solucion.estado == "UNICA":
                    soluciones.append(solucion.x)
                    pasos.append(f"Solución para columna {col_idx+1}: {solucion.x}")
                else:
                    pasos.append(f"No hay solución única para columna {col_idx+1}")
                    return EcuacionMatricialResultVM(
                        estado="SIN_SOLUCION",
                        pasos=pasos,
                        matriz_aumentada=matriz_aumentada
                    )
                    
            except Exception as e:
                pasos.append(f"Error al resolver para columna {col_idx+1}: {str(e)}")
                return EcuacionMatricialResultVM(
                    estado="ERROR",
                    pasos=pasos,
                    matriz_aumentada=matriz_aumentada
                )
        
        # Construir la matriz solución X
        # Transponer las soluciones (cada solución es una columna)
        if soluciones:
            X_data = []
            # CORREGIR ESTA PARTE: usar 'soluciones' en lugar de 'sol'
            for i in range(len(soluciones[0])):
                fila = [soluciones[j][i] for j in range(len(soluciones))]  # CORREGIDO: soluciones[j][i]
                X_data.append(fila)
            
            X = Matriz(X_data)
            pasos.append(f"Solución X = {X_data}")
            
            return EcuacionMatricialResultVM(
                estado="SOLUCION",
                solucion=X,
                pasos=pasos,
                matriz_aumentada=matriz_aumentada
            )
        else:
            return EcuacionMatricialResultVM(
                estado="SIN_SOLUCION",
                pasos=pasos,
                matriz_aumentada=matriz_aumentada
            )