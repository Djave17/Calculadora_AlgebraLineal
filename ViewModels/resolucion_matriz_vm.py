"""
ViewModels de la calculadora de matrices.

El módulo reúne varias `dataclasses` que sirven como transporte de datos
entre la capa de dominio (operadores algebraicos) y la interfaz de
usuario. Aquí se describen los resultados de un sistema lineal, los pasos
del proceso de Gauss-Jordan y el `ViewModel` que actúa como fachada del
solucionador.

El diseño sigue el patrón MVVM (Model-View-ViewModel):

- **Modelo**: Las clases algebraicas (`Matriz`, `SistemaLineal`,
  `SolucionadorGaussJordan`, etc.) ubicadas en `Models` y `Operadores`,
  encargadas de la lógica matemática.
- **ViewModel**: Este módulo. Orquesta las llamadas al solucionador,
  conserva las dimensiones y expone los datos listos para la vista.
- **Vista**: Implementada en `UI/main.py` con Flet. Responde a la
  interacción del usuario (tabla, botones) consultando este ViewModel.

Todos los datos numéricos se representan con `Fraction` para preservar
exactitud; la conversión desde cadenas ocurre en la vista. El ViewModel evita realizar operaciones de
IU (mostrar diálogos, manipular widgets) para mantener la separación de
responsabilidades indicada por MVVM.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional

# Importamos clases del dominio. Estas importaciones se resuelven de forma
# diferida al invocar el solucionador; si faltan (por ejemplo en entornos
# donde solo está disponible la UI) se lanzará ImportError al llamar a solve().
from Models.matriz import Matriz
from Operadores.sistema_lineal import SistemaLineal, SistemaMatricial
from Operadores.SolucionGaussJordan.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial


@dataclass
class StepVM:
    """Representa una operación elemental aplicada durante Gauss-Jordan.

    Cada paso almacena el tipo de operación, el pivote utilizado, los
    renglones afectados, el factor empleado (si corresponde) y la matriz
    antes y después de ejecutar la operación. La matriz se guarda como una
    lista de listas de fracciones correspondiente a la matriz aumentada.

    Atributos
    ---------
    number: int
        Índice 1-based del paso dentro de la secuencia completa.
    operation: str
        Código corto de la operación (ej. "INTERCAMBIO_FILAS", "ESCALAR_FILA",
        "ELIMINAR_DEBAJO", "ELIMINAR_ENCIMA", "NORMALIZAR_PIVOTE").
    description: str
        Descripción en lenguaje natural (español) de la operación realizada.
    before_matrix: List[List[Fraction]]
        Copia de la matriz aumentada antes de aplicar la operación.
    after_matrix: List[List[Fraction]]
        Copia de la matriz aumentada después de aplicar la operación.
    pivot_row: Optional[int]
        Índice de renglón del pivote empleado, cuando corresponde.
    pivot_col: Optional[int]
        Índice de columna del pivote empleado, cuando corresponde.
    affected_rows: Optional[List[int]]
        Renglones impactados por la operación.
    factor: Optional[Fraction]
        Factor multiplicativo usado en combinaciones lineales (None si no aplica).
    """

    number: int
    operation: str
    description: str
    before_matrix: List[List[Fraction]]
    after_matrix: List[List[Fraction]]
    pivot_row: Optional[int] = None
    pivot_col: Optional[int] = None
    affected_rows: Optional[List[int]] = None
    factor: Optional[Fraction] = None


@dataclass
class ParametricVM:
    """Describe la forma paramétrica de un sistema con infinitas soluciones.

    Si el rango es r < n (n variables), existen n - r variables libres. La
    solución se expresa como una solución particular más una combinación
    lineal de vectores dirección. Esta clase reúne esa información para la
    vista.

    Atributos
    ---------
    particular: List[Fraction]
        Solución particular del sistema (longitud n).
    direcciones: List[List[Fraction]]
        Vectores dirección asociados a cada variable libre; indican cómo
        cambia la solución al incrementar su parámetro en una unidad.
    free_vars: List[int]
        Índices (0-based) de las variables libres.
    """

    particular: List[Fraction]
    direcciones: List[List[Fraction]]
    free_vars: List[int]

    @property
    def directions(self) -> List[List[Fraction]]:
        """Alias en inglés para compatibilidad retroactiva."""
        return self.direcciones

    @directions.setter
    def directions(self, value: List[List[Fraction]]) -> None:
        self.direcciones = value


@dataclass
class ResultVM:
    """ViewModel con el resultado de resolver un sistema lineal.

    Atributos
    ---------
    status: str
        "UNICA", "INFINITAS" o "INCONSISTENTE" según el diagnóstico.
    solution: Optional[List[Fraction]]
        Valores de las variables cuando la solución es única; en otro caso `None`.
    parametric: Optional[ParametricVM]
        Representación paramétrica cuando existen infinitas soluciones; `None` en otro caso.
    pivot_cols: Optional[List[int]]
        Índices (0-based) de las columnas pivote, útil para diagnóstico.
    free_vars: Optional[List[int]]
        Índices (0-based) de las variables libres.
    steps: Optional[List[StepVM]]
        Secuencia de pasos registrada durante Gauss-Jordan, incluido el estado inicial.
    """

    status: str
    solution: Optional[List[Fraction]] = None
    parametric: Optional[ParametricVM] = None
    pivot_cols: Optional[List[int]] = None
    free_vars: Optional[List[int]] = None
    steps: Optional[List[StepVM]] = None


@dataclass
class ColumnResultVM:
    """Resultado asociado a una columna específica de B en AX = B."""

    index: int
    label: str
    result: ResultVM


@dataclass
class MatrixEquationResultVM:
    """Encapsula la solución global de una ecuación matricial AX = B."""

    status: str
    columns: List[ColumnResultVM]


@dataclass
class InterpretationVM:
    """Resume el significado cualitativo del resultado del solver.

    Se usa en la interfaz para comunicar, con lenguaje propio de la
    teoría (Lay, 2012; Grossman, 2019), si el sistema es consistente,
    si los vectores son dependientes, etc.
    """

    summary: str
    details: List[str]
    level: str


class MatrixCalculatorViewModel:
    """Coordina la resolución de sistemas lineales con Gauss-Jordan.

    Conserva las dimensiones de la matriz, el método elegido (por ahora
    Gauss-Jordan) y expone `solve`, que recibe filas de la matriz
    aumentada [A|b] y devuelve un `ResultVM` con el diagnóstico. La vista
    es responsable de validar y convertir las entradas; este ViewModel
    asume que los datos ya tienen la forma esperada.
    """

    def __init__(self) -> None:
        # Dimensiones por defecto, modificables desde la interfaz de usuario.
        self._rows: int = 2
        self._cols: int = 3  # número de variables; la matriz aumentada usa cols+1 columnas
        self._method: str = "Gauss-Jordan"

    # Accesores y mutadores para la cantidad de ecuaciones (filas)
    @property
    def rows(self) -> int:
        return self._rows

    @rows.setter
    def rows(self, value: int) -> None:
        self._rows = max(1, min(8, value))

    # Accesores y mutadores para la cantidad de variables (columnas)
    @property
    def cols(self) -> int:
        return self._cols

    @cols.setter
    def cols(self, value: int) -> None:
        self._cols = max(1, min(12, value))

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        # Por ahora solo se implementa Gauss-Jordan; en el futuro se pueden añadir otros métodos.
        self._method = value

    def solve(self, augmented: List[List[Fraction]]) -> ResultVM:
        """Resuelve el sistema lineal descrito por una matriz aumentada.

        Parámetros
        -----------
        augmented: List[List[Fraction]]
            Lista de `rows` filas con `cols + 1` fracciones. Las primeras
            `cols` columnas corresponden a la matriz A y la última al vector b.

        Devuelve
        --------
        ResultVM
            ViewModel con el estado de la solución y, si se solicitó, la
            secuencia de pasos aplicados.

        Excepciones
        -----------
        ValueError
            Se lanza cuando la forma de la matriz aumentada no coincide con
            las dimensiones esperadas.
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

        # Construir la matriz de coeficientes A y el vector b para la capa de dominio
        A_data = [row[:-1] for row in augmented]
        b_data = [row[-1] for row in augmented]

        solver = self._build_solver()
        return self._solve_with_rows(A_data, b_data, solver)

    def solve_matrix_equation(
        self,
        A_rows: List[List[Fraction]],
        B_rows: List[List[Fraction]],
    ) -> MatrixEquationResultVM:
        """Resuelve AX = B tratando cada columna de B como un sistema independiente."""
        if not A_rows or not A_rows[0]:
            raise ValueError("La matriz A no puede ser vacía.")
        if len(A_rows) != len(B_rows):
            raise ValueError("A y B deben tener el mismo número de filas.")
        num_vars = len(A_rows[0])
        for fila in A_rows:
            if len(fila) != num_vars:
                raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if not B_rows or not B_rows[0]:
            raise ValueError("La matriz B debe tener al menos una columna.")

        self._rows = len(A_rows)
        self._cols = num_vars

        matriz_A = Matriz(A_rows)
        sistema_matricial = SistemaMatricial(matriz_A, B_rows)
        solver = self._build_solver()

        column_results: List[ColumnResultVM] = []
        for idx, sistema in enumerate(sistema_matricial.sistemas_individuales()):
            solucion = solver.resolver(sistema, registrar_pasos=True)
            column_results.append(
                ColumnResultVM(
                    index=idx,
                    label=f"b{idx + 1}",
                    result=self._build_result_vm(solucion),
                )
            )

        status = self._aggregate_status(column_results)
        return MatrixEquationResultVM(status=status, columns=column_results)

    def _build_solver(self) -> SolucionadorGaussJordan:
        if self._method.lower() in ["gauss-jordan", "gauss_jordan", "gauss jordan"]:
            return SolucionadorGaussJordan(pivoteo=PivoteoParcial())
        return SolucionadorGaussJordan(pivoteo=PivoteoParcial())

    def _solve_with_rows(
        self,
        A_rows: List[List[Fraction]],
        b_data: List[Fraction],
        solver: Optional[SolucionadorGaussJordan] = None,
    ) -> ResultVM:
        if len(A_rows) != len(b_data):
            raise ValueError("Dimensión inconsistente entre A y b.")
        if solver is None:
            solver = self._build_solver()
        A = Matriz(A_rows)
        sistema = SistemaLineal(A, b_data)
        solucion = solver.resolver(sistema, registrar_pasos=True)
        return self._build_result_vm(solucion)

    def _build_result_vm(self, solucion) -> ResultVM:
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
            return ResultVM(
                status=status,
                solution=solution,
                parametric=None,
                pivot_cols=pivot_cols,
                free_vars=free_vars,
                steps=steps_vm,
            )

        if status == "INFINITAS":
            param = solucion.parametrica
            if param is not None:
                param_vm = ParametricVM(
                    particular=param.particular,
                    direcciones=param.direcciones,
                    free_vars=param.libres,
                )
            else:
                param_vm = None
            return ResultVM(
                status=status,
                solution=None,
                parametric=param_vm,
                pivot_cols=pivot_cols,
                free_vars=free_vars,
                steps=steps_vm,
            )

        return ResultVM(
            status=status,
            solution=None,
            parametric=None,
            pivot_cols=pivot_cols,
            free_vars=free_vars,
            steps=steps_vm,
        )

    @staticmethod
    def _aggregate_status(columns: List[ColumnResultVM]) -> str:
        statuses = [col.result.status for col in columns]
        if any(status == "INCONSISTENTE" for status in statuses):
            return "INCONSISTENTE"
        if any(status == "INFINITAS" for status in statuses):
            return "INFINITAS"
        return "UNICA"

    @staticmethod
    def interpret_result(
        result: ResultVM,
        *,
        context: str,
        is_homogeneous: bool,
        variable_labels: List[str],
    ) -> "InterpretationVM":
        """Construye una interpretación textual del estado del sistema.

        El razonamiento sigue los criterios clásicos: si un sistema
        homogéneo solo tiene la solución trivial, los vectores columna
        son independientes (Lay, §1.7); si aparecen variables libres, el
        sistema posee soluciones no triviales y, por lo tanto, hay
        dependencia lineal (Grossman, cap. 2).
        """

        pivot_cols = result.pivot_cols or []
        free_vars = result.free_vars or []
        pivot_count = len(pivot_cols)
        free_count = len(free_vars)
        num_vars = len(variable_labels)

        # Detalles comunes mostrando la estructura de pivotes/libres.
        details = [
            f"Pivotes detectados: {pivot_count} de {num_vars} variables.",
            f"Variables libres: {free_count}",
        ]

        status = result.status

        if context == "combination":
            if is_homogeneous:
                if status == "UNICA":
                    return InterpretationVM(
                        summary=(
                            "Sistema homogéneo con única solución trivial; "
                            "las columnas son linealmente independientes (Lay, §1.7)."
                        ),
                        details=details,
                        level="success",
                    )
                if status == "INFINITAS":
                    details.append(
                        "Existen soluciones no triviales; hay vectores dirección en el núcleo."
                    )
                    return InterpretationVM(
                        summary=(
                            "Sistema homogéneo con soluciones no triviales; "
                            "los vectores generan dependencias lineales (Grossman, cap. 2)."
                        ),
                        details=details,
                        level="warning",
                    )
                return InterpretationVM(
                    summary=(
                        "Se detectó inconsistencia inesperada en un sistema homogéneo; "
                        "verifica los datos de entrada."
                    ),
                    details=details,
                    level="error",
                )

            # Caso no homogéneo: análisis de pertenencia de b al subespacio.
            if status == "UNICA":
                details.append("No hay variables libres; el rango coincide con el número de incógnitas.")
                return InterpretationVM(
                    summary=(
                        "El sistema es consistente con solución única; b pertenece al subespacio "
                        "generado por las columnas de A (Lay, §1.5)."
                    ),
                    details=details,
                    level="success",
                )
            if status == "INFINITAS":
                details.append(
                    "La presencia de variables libres indica una familia infinita de coeficientes."
                )
                return InterpretationVM(
                    summary=(
                        "El sistema es consistente con infinitas soluciones; existe dependencia "
                        "lineal entre los vectores generadores."
                    ),
                    details=details,
                    level="warning",
                )
            return InterpretationVM(
                summary=(
                    "Sistema inconsistente; b no pertenece al subespacio generado por las columnas "
                    "de A (Lay, §1.3)."
                ),
                details=details,
                level="error",
            )

        if context == "dependence":
            if status == "UNICA":
                details.append("El núcleo contiene solo la solución nula.")
                return InterpretationVM(
                    summary=(
                        "Los vectores introducidos son linealmente independientes; la única "
                        "solución a A·c = 0 es c = 0 (Lay, §1.7)."
                    ),
                    details=details,
                    level="success",
                )
            if status == "INFINITAS":
                details.append("El núcleo tiene dimensión positiva; hay relaciones lineales no triviales.")
                return InterpretationVM(
                    summary=(
                        "Los vectores son linealmente dependientes; existen soluciones no triviales "
                        "para A·c = 0 (Grossman, cap. 2)."
                    ),
                    details=details,
                    level="warning",
                )
            return InterpretationVM(
                summary=(
                    "El solucionador reportó inconsistencia; revisa la construcción del sistema."
                ),
                details=details,
                level="error",
            )

        # Contexto genérico: devolver una descripción básica.
        generic = {
            "UNICA": (
                "success",
                "Sistema consistente con solución única.",
            ),
            "INFINITAS": (
                "warning",
                "Sistema consistente con infinitas soluciones.",
            ),
            "INCONSISTENTE": (
                "error",
                "Sistema inconsistente; no existe solución.",
            ),
        }
        level, summary = generic.get(status, ("info", f"Estado: {status}"))
        return InterpretationVM(summary=summary, details=details, level=level)
