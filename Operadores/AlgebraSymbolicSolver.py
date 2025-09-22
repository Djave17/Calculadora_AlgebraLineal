from __future__ import annotations
from typing import List, Dict, Optional, Tuple, Any, Union
import sympy as sp
from sympy import symbols, Eq, solve, simplify, Matrix
from Models.matriz import Matriz
from Operadores.sistema_lineal import Sistemalineal

class AlgebraSymbolicSolver:
    """Resuelve sistemas lineales con incógnitas simbólicas."""
    
    def __init__(self, tol: float = 1e-9):
        self.tol = tol
        self.symbols_cache = {}
    
    def parse_expression(self, text: str, allowed_vars: List[str] = None) -> Any:
        """Convierte texto en expresión simbólica."""
        if text is None or text.strip() == "":
            raise ValueError("Entrada vacía")
        
        s = text.strip()
        
        # Si es un número, convertirlo a float
        try:
            return float(s)
        except ValueError:
            pass
        
        # Si es una variable permitida, crear símbolo
        if allowed_vars and s in allowed_vars:
            if s not in self.symbols_cache:
                self.symbols_cache[s] = sp.symbols(s)
            return self.symbols_cache[s]
        
        # Intentar analizar como expresión
        try:
            # Reemplazar variables conocidas
            if allowed_vars:
                for var in allowed_vars:
                    if var in s:
                        # Crear expresión simbólica
                        return sp.sympify(s)
            raise ValueError(f"Expresión no reconocida: '{s}'")
        except:
            raise ValueError(f"Expresión no reconocida: '{s}'")
    
    def gaussian_elimination_symbolic(self, augmented_matrix: List[List[Any]]) -> Tuple[List[List[Any]], List[str]]:
        """Aplica eliminación gaussiana a una matriz con símbolos."""
        steps = []
        m = len(augmented_matrix)
        n = len(augmented_matrix[0]) - 1
        
        # Convertir a matriz sympy
        sympy_matrix = Matrix(augmented_matrix)
        steps.append("Matriz aumentada inicial:")
        steps.append(str(sympy_matrix))
        
        # Aplicar eliminación gaussiana
        for col in range(min(m, n)):
            # Encontrar pivote
            pivot_row = None
            for row in range(col, m):
                if sympy_matrix[row, col] != 0:
                    pivot_row = row
                    break
            
            if pivot_row is None:
                continue
            
            # Intercambiar filas si es necesario
            if pivot_row != col:
                sympy_matrix.row_swap(col, pivot_row)
                steps.append(f"Intercambio fila {col+1} con fila {pivot_row+1}")
                steps.append(str(sympy_matrix))
            
            # Normalizar fila pivote
            pivot_val = sympy_matrix[col, col]
            if pivot_val != 1:
                sympy_matrix[col, :] = sympy_matrix[col, :] / pivot_val
                steps.append(f"Normalizar fila {col+1} dividiendo por {pivot_val}")
                steps.append(str(sympy_matrix))
            
            # Eliminar debajo del pivote
            for row in range(col + 1, m):
                factor = sympy_matrix[row, col]
                if factor != 0:
                    sympy_matrix[row, :] = sympy_matrix[row, :] - factor * sympy_matrix[col, :]
                    steps.append(f"Eliminar elemento en ({row+1},{col+1}) usando fila {col+1}")
                    steps.append(str(sympy_matrix))
        
        return sympy_matrix.tolist(), steps
    
    def analyze_symbolic_solution(self, echelon_matrix: List[List[Any]]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """Analiza la solución de un sistema simbólico."""
        m = len(echelon_matrix)
        n = len(echelon_matrix[0]) - 1
        
        conditions = {}
        solution = {}
        
        # Analizar cada fila
        for i in range(m):
            # Verificar si es una fila de ceros en la parte izquierda
            left_zeros = all(echelon_matrix[i][j] == 0 for j in range(n))
            
            if left_zeros:
                # Ecuación: 0 = b
                b_val = echelon_matrix[i][n]
                if b_val != 0:
                    # Sistema inconsistente a menos que b_val = 0
                    return "INCONSISTENTE", {str(b_val): 0}, {}
            else:
                # Encontrar el primer elemento no cero (pivote)
                pivot_col = None
                for j in range(n):
                    if echelon_matrix[i][j] != 0:
                        pivot_col = j
                        break
                
                if pivot_col is not None:
                    # Resolver para esta variable
                    equation = sp.Eq(
                        echelon_matrix[i][pivot_col] * sp.symbols(f'x{pivot_col+1}'),
                        echelon_matrix[i][n] - sum(
                            echelon_matrix[i][j] * sp.symbols(f'x{j+1}') 
                            for j in range(pivot_col + 1, n)
                        )
                    )
                    solution[f'x{pivot_col+1}'] = equation
        
        # Determinar el tipo de solución
        if any('INCONSISTENTE' in str(val) for val in conditions.values()):
            return "INCONSISTENTE", conditions, {}
        elif len(solution) == n:
            return "UNICA", conditions, solution
        else:
            return "INFINITAS", conditions, solution
    
    def solve_symbolic_system(self, A_data: List[List[Any]], b_data: List[Any], 
                             symbolic_vars: List[str] = None) -> Tuple[str, Dict, Dict, List[str]]:
        """Resuelve un sistema con incógnitas simbólicas."""
        if symbolic_vars is None:
            symbolic_vars = []
        
        steps = []
        
        # Construir matriz aumentada
        augmented_matrix = []
        for i in range(len(A_data)):
            row = A_data[i][:]  # Copiar fila de A
            row.append(b_data[i])  # Añadir elemento de b
            augmented_matrix.append(row)
        
        steps.append("Matriz aumentada del sistema:")
        steps.append(str(Matrix(augmented_matrix)))
        
        # Aplicar eliminación gaussiana simbólica
        echelon_matrix, elim_steps = self.gaussian_elimination_symbolic(augmented_matrix)
        steps.extend(elim_steps)
        
        # Analizar solución
        status, conditions, solution = self.analyze_symbolic_solution(echelon_matrix)
        steps.append(f"Tipo de solución: {status}")
        
        if conditions:
            steps.append(f"Condiciones: {conditions}")
        if solution:
            steps.append(f"Solución: {solution}")
        
        return status, conditions, solution, steps