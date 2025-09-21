"""
View models for the matrix calculator application.

This module defines a set of plain data classes used to transport data
between the domain layer (the algebraic solver) and the user interface.
The classes here encapsulate the results of solving a linear system as
well as the individual steps of the Gauss–Jordan elimination process.
In addition, it provides a view model class that acts as a façade for
the solver, hiding the complexity of constructing the system and
translating the solver's output into a form suitable for presentation.

The view model design follows the MVVM (Model–View–ViewModel) pattern:

- **Model**: The underlying algebraic classes (`Matriz`, `SistemaLineal`,
  `SolucionadorGaussJordan`, etc.) reside in the `Models` and
  `Operadores` packages. They contain the core logic for manipulating
  matrices and resolving linear systems.
- **ViewModel**: This module. It orchestrates calls to the solver,
  stores the current problem definition (dimensions, method) and
  exposes the solution in a structured way that the view can bind to.
- **View**: Implemented in `UI/main.py` using PySide. The view reacts
  to user input (changes in the matrix table, button clicks) by
  updating the view model and queries the view model for results.

All numerical data is stored as Python floats; conversion from string
inputs occurs in the view layer. The view model does not perform any
UI operations (such as showing dialogs or manipulating widgets) in
accordance with the separation of concerns required by the MVVM
pattern.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

# Import domain classes. These imports are lazily resolved at runtime when
# the solver is invoked. If these modules are missing (for example in
# environments where only the UI is available), an ImportError will be
# raised when solve() is called.
from Models.matriz import Matriz
from Operadores.sistema_lineal import SistemaLineal
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial
from Operadores.registrador import PasoReduccion

@dataclass
class StepVM:
    """Represents a single row operation performed during Gauss–Jordan.

    Each step includes the type of operation, the pivot position, the
    affected rows, the factor used (if any), the matrix before the
    operation and the matrix after the operation. The matrix is
    represented as a list of lists of floats (the augmented matrix).

    Attributes
    ----------
    number: int
        1-based index of the step in the overall sequence.
    operation: str
        A short code identifying the type of operation (e.g. "INTERCAMBIO_FILAS",
        "ESCALAR_FILA", "ELIMINAR_DEBAJO", "ELIMINAR_ENCIMA", "NORMALIZAR_PIVOTE").
    description: str
        Human-readable description of the operation in Spanish.
    before_matrix: List[List[float]]
        Snapshot of the augmented matrix before performing the operation.
    after_matrix: List[List[float]]
        Snapshot of the augmented matrix after performing the operation.
    pivot_row: Optional[int]
        The row index of the pivot used for the operation, if applicable.
    pivot_col: Optional[int]
        The column index of the pivot used for the operation, if applicable.
    affected_rows: List[int]
        List of row indices affected by this operation.
    factor: Optional[float]
        The scaling factor used when combining rows (None when not applicable).
    """

    number: int
    operation: str
    description: str
    before_matrix: List[List[float]]
    after_matrix: List[List[float]]
    pivot_row: Optional[int] = None
    pivot_col: Optional[int] = None
    affected_rows: Optional[List[int]] = None
    factor: Optional[float] = None


@dataclass
class ParametricVM:
    """Represents the parametric form of a solution for systems with infinitely
    many solutions.

    A system with rank r < n (n variables) has n - r free variables. The
    solution can be expressed as a particular solution plus a linear
    combination of direction vectors. This class encapsulates that data
    for presentation.

    Attributes
    ----------
    particular: List[float]
        A particular solution vector (size n).
    directions: List[List[float]]
        One direction vector for each free variable. Each direction
        vector has size n and represents the change in solution when
        increasing its associated parameter by one.
    free_vars: List[int]
        Indices of the variables that are free (0-based).
    """

    particular: List[float]
    directions: List[List[float]]
    free_vars: List[int]


@dataclass
class ResultVM:
    """View model for the result of solving a linear system.

    Attributes
    ----------
    status: str
        One of "UNICA", "INFINITAS" or "INCONSISTENTE".
    solution: Optional[List[float]]
        If the system has a unique solution, this contains the values of
        the variables in order. Otherwise, None.
    parametric: Optional[ParametricVM]
        If the system has infinite solutions, this holds the parametric
        representation. Otherwise, None.
    pivot_cols: List[int]
        Indices of the pivot columns (0-based). Useful for diagnostics.
    free_vars: List[int]
        Indices of the free variables (0-based).
    steps: List[StepVM]
        Sequence of steps taken during the Gauss–Jordan elimination,
        including the initial state. The view can iterate over this to
        present a step-by-step explanation.
    """

    status: str
    solution: Optional[List[float]] = None
    parametric: Optional[ParametricVM] = None
    pivot_cols: Optional[List[int]] = None
    free_vars: Optional[List[int]] = None
    steps: Optional[List[StepVM]] = None

@dataclass
class LinearCombinationResultVM:
    """View model for the result of a linear combination check.
    Attributes
    ----------
    status: str
        One of "Combinación Lineal Única", "Infinitas Combinaciones Lineales",
        or "No es Combinación Lineal".
    coefficients: Optional[List[float]]
        If a unique combination exists, these are the coefficients. Otherwise, None.
    augmented_matrix_before_rref: Optional[List[List[float]]]
        The initial augmented matrix [V|b] before RREF.
    steps: Optional[List[StepVM]]
        Sequence of steps taken during the Gauss–Jordan elimination.
    """
    status: str
    coefficients: Optional[List[float]] = None
    augmented_matrix_before_rref: Optional[List[List[float]]] = None
    steps: Optional[List[StepVM]] = None


class MatrixCalculatorViewModel:
    """View model orchestrating the process of solving linear systems.

    The view model stores the dimensions of the matrix and the chosen
    method (currently only Gauss–Jordan is implemented). It exposes a
    `solve` method that accepts a list of rows (each row is a list of
    floats representing a row of the augmented matrix [A|b]) and
    returns a `ResultVM` with the outcome. Input validation and error
    handling for user input should be done at the view layer; this
    class assumes the data passed in conforms to the expected shapes.
    """

    def __init__(self) -> None:
        # Default dimensions. The view can change these through its UI.
        self._rows: int = 2
        self._cols: int = 3  # number of variables; augmented matrix has cols+1 columns
        self._method: str = "Gauss-Jordan"

    # Accessor and mutator for number of equations (rows)
    @property
    def rows(self) -> int:
        return self._rows

    @rows.setter
    def rows(self, value: int) -> None:
        self._rows = max(1, value)

    # Accessor and mutator for number of variables (columns)
    @property
    def cols(self) -> int:
        return self._cols

    @cols.setter
    def cols(self, value: int) -> None:
        self._cols = max(1, value)

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        # At present only Gauss–Jordan is implemented. In the future,
        # additional methods could be supported.
        self._method = value

    def solve(self, augmented: List[List[float]]) -> ResultVM:
        """Solve the linear system defined by an augmented matrix.

        Parameters
        ----------
        augmented: List[List[float]]
            A list of `rows` lists, each containing `cols + 1` floats. The
            first `cols` columns constitute the coefficient matrix A and
            the last column constitutes the vector b.

        Returns
        -------
        ResultVM
            A view model containing the solution state and, if requested,
            the sequence of steps taken.

        Raises
        ------
        ValueError
            If the shape of the augmented matrix does not match the
            expected dimensions.
        """
        if len(augmented) != self._rows:
            raise ValueError(
                f"Se esperaban {self._rows} filas, pero se recibieron {len(augmented)}"
            )
        for i, fila in enumerate(augmented):
            if len(fila) != self._cols + 1:
                raise ValueError(
                    f"La fila {i+1} debe tener exactamente {self._cols + 1} números (incluyendo b)"
                )

        # Build the coefficient matrix A and vector b for the domain layer
        A_data = [row[:-1] for row in augmented]
        b_data = [row[-1] for row in augmented]

        # Use the domain model to construct the system
        A = Matriz(A_data)
        sistema = SistemaLineal(A, b_data)

        # Choose method; for now only Gauss–Jordan is supported
        if self._method.lower() in ["gauss-jordan", "gauss_jordan", "gauss jordan"]:
            solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
        else:
            # Fallback: Gauss–Jordan
            solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())

        solucion = solver.resolver(sistema, registrar_pasos=True)

        # Transform the domain result into a view model
        status = solucion.estado
        pivot_cols = solucion.columnas_pivote or []
        free_vars = solucion.variables_libres or []
        steps_vm: List[StepVM] = []
        if solucion.historial is not None:
            for paso in solucion.historial.pasos:
                steps_vm.append(
                    StepVM(
                        number=paso.numero,
                        operation=paso.operacion,
                        description=paso.descripcion,
                        before_matrix=paso.antes if paso.antes is not None else [],
                        after_matrix=paso.despues if paso.despues is not None else [],
                        pivot_row=paso.pivote_fila,
                        pivot_col=paso.pivote_col,
                        affected_rows=paso.filas_afectadas,
                        factor=paso.factor,
                    )
                )

        if status == "UNICA":
            solution = solucion.x or []
            result = ResultVM(
                status=status,
                solution=solution,
                parametric=None,
                pivot_cols=pivot_cols,
                free_vars=free_vars,
                steps=steps_vm,
            )
        elif status == "INFINITAS":
            param = solucion.parametrica
            if param is not None:
                param_vm = ParametricVM(
                    particular=param.particular,
                    directions=param.direcciones,
                    free_vars=param.libres,
                )
            else:
                param_vm = None
            result = ResultVM(
                status=status,
                solution=None,
                parametric=param_vm,
                pivot_cols=pivot_cols,
                free_vars=free_vars,
                steps=steps_vm,
            )
        else:  # INCONSISTENTE
            result = ResultVM(
                status=status,
                solution=None,
                parametric=None,
                pivot_cols=pivot_cols,
                free_vars=free_vars,
                steps=steps_vm,
            )

        return result
    
    def solve_linear_combination(self, vectors: List[List[float]], target_vector: List[float]) -> LinearCombinationResultVM:
        """
        Determina si el vector objetivo puede expresarse como combinación lineal
        de los vectores dados y devuelve el procedimiento.

        Parameters
        ----------
        vectors: List[List[float]]
            Una lista de vectores, donde cada vector es una lista de floats.
            Estos son los vectores v1, v2, ..., vk.
        target_vector: List[float]
            El vector objetivo b.
        
        Returns
        -------
        LinearCombinationResultVM
            Un view model que contiene el estado de la combinación lineal,
            los coeficientes (si existen) y los pasos de Gauss-Jordan.
        
        Raises
        ------
        ValueError
            Si las dimensiones de los vectores no son consistentes.
        """

        if not vectors:
            raise ValueError("Debe proporcionar al menos un vector.")
        if not target_vector:
            raise ValueError("Debe proporcionar un vector objetivo.")
        

        n_dim = len(vectors[0]) # Dimensión de los vectores
        if any(len(v) != n_dim for v in vectors):
            raise ValueError("Todos los vectores deben tener la misma dimensión.")
        if len(target_vector) != n_dim:
            raise ValueError("El vector objetivo debe tener la misma dimensión que los vectores dados.")
        

        # Construir la matriz A donde las columnas son los vectores dados
        # y el vector b es el vector objetivo.
        # El sistema a resolver es A * c = b, donde c son los coeficientes.
        A_data: List[List[float]] = []
        for i in range(n_dim): # Filas de A (dimensión de los vectores)
            row = []
            for j in range(len(vectors)): # Columnas de A (número de vectores)
                row.append(vectors[j][i])
            A_data.append(row)
        
        A = Matriz(A_data)
        sistema = SistemaLineal(A, target_vector)

       # Guardar la matriz aumentada inicial para el procedimiento
        augmented_matrix_before_rref = sistema.como_matriz_aumentada().como_lista()

        solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
        solucion = solver.resolver(sistema, registrar_pasos=True)

        
        steps_vm: List[StepVM] = []
        if solucion.historial is not None:
            for paso in solucion.historial.pasos:
                steps_vm.append(
                    StepVM(
                        number=paso.numero,
                        operation=paso.operacion,
                        description=paso.descripcion,
                        before_matrix=paso.antes if paso.antes is not None else [],
                        after_matrix=paso.despues if paso.despues is not None else [],
                        pivot_row=paso.pivote_fila,
                        pivot_col=paso.pivote_col,
                        affected_rows=paso.filas_afectadas,
                        factor=paso.factor,
                    )
                )
        
        
        if solucion.estado == "UNICA":
            return LinearCombinationResultVM(
                status="Combinación Lineal Única",
                coefficients=solucion.x,
                augmented_matrix_before_rref=augmented_matrix_before_rref,
                steps=steps_vm
            )
        elif solucion.estado == "INFINITAS":
            return LinearCombinationResultVM(
                status="Infinitas Combinaciones Lineales",
                coefficients=None, # Podrías añadir la forma paramétrica aquí si es necesario
                augmented_matrix_before_rref=augmented_matrix_before_rref,
                steps=steps_vm
            )
        else: # INCONSISTENTE
            return LinearCombinationResultVM(
                status="No es Combinación Lineal",
                coefficients=None,
                augmented_matrix_before_rref=augmented_matrix_before_rref,
                steps=steps_vm
            )