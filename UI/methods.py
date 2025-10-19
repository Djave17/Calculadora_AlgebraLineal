from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class MethodInfo:
    id: str
    label: str
    icon: str
    available: bool
    description: str
    category: str
    view_type: str = "matrix_solver"
    analysis_context: Optional[str] = None
    force_homogeneous: bool = False
    variable_prefix: str = "x"
    shows_config_panel: bool = True
    default_rows: int = 3
    default_cols: int = 3


@dataclass(frozen=True)
class MethodCategory:
    id: str
    label: str
    methods: Tuple[MethodInfo, ...]


METHOD_CATEGORIES: Tuple[MethodCategory, ...] = (
    MethodCategory(
        id="systems",
        label="Sistemas de ecuaciones",
        methods=(
            MethodInfo(
                id="gauss_jordan",
                label="Gauss-Jordan",
                icon="SHOW_CHART",
                available=True,
                description="Resolución completa con pivoteo parcial y registro de pasos (Lay §2.2).",
                category="Sistemas de ecuaciones",
            ),
            MethodInfo(
                id="homogeneous",
                label="(Legacy) Sistema homogéneo",
                icon="LINEAR_SCALE",
                available=False,
                description="Usa 'Identidades de matrices' para analizar A·c = 0.",
                category="Sistemas de ecuaciones",
                analysis_context="dependence",
                force_homogeneous=True,
                variable_prefix="c",
            ),
        ),
    ),
    MethodCategory(
        id="identities",
        label="Combinaciones y dependencia",
        methods=(
            MethodInfo(
                id="matrix_identities",
                label="Identidades de matrices",
                icon="HUB",
                available=True,
                description="Unifica AX=B, combinación lineal y sistema homogéneo con pasos Gauss–Jordan.",
                category="Combinaciones y dependencia",
                view_type="matrix_identities",
                shows_config_panel=False,
            ),
        ),
    ),
    MethodCategory(
        id="vectors",
        label="Operaciones vectoriales",
        methods=(
            MethodInfo(
                id="vector_properties",
                label="Propiedades en ℝⁿ",
                icon="SCIENCE",
                available=True,
                description="Explora suma, multiplicación escalar y verificación de axiomas básicos del espacio vectorial.",
                category="Operaciones vectoriales",
                view_type="vector_properties",
                shows_config_panel=False,
            ),
        ),
    ),
    MethodCategory(
        id="matrices",
        label="Álgebra matricial",
        methods=(
            MethodInfo(
                id="matrix_ops",
                label="Operaciones de matrices",
                icon="TABLE_VIEW",
                available=True,
                description=(
                    "Suma, resta, α·A, producto A·B y traspuestas, con validación de dimensiones y pasos."
                ),
                category="Álgebra matricial",
                view_type="matrix_ops",
                shows_config_panel=False,
            ),
            MethodInfo(
                id="matrix_transpose",
                label="Matriz traspuesta",
                icon="SWAP_HORIZ",
                available=True,
                description=(
                    "Calcula A^T mostrando el intercambio de filas por columnas y verifica propiedades básicas."
                ),
                category="Álgebra matricial",
                view_type="matrix_transpose",
                shows_config_panel=False,
            ),
        ),
    ),
    MethodCategory(
        id="references",
        label="Material de apoyo",
        methods=(
            MethodInfo(
                id="mer_notes",
                label="MER – notas",
                icon="MENU_BOOK",
                available=True,
                description="Resumen del Método de Eliminación por Renglones y recomendaciones de aplicación práctica.",
                category="Teoría",
                view_type="mer_notes",
                shows_config_panel=False,
            ),
        ),
    ),
)

DEFAULT_METHOD_ID = "gauss_jordan"


def iter_methods() -> Iterable[MethodInfo]:
    for category in METHOD_CATEGORIES:
        for method in category.methods:
            yield method


def find_method(method_id: str) -> Optional[Tuple[MethodCategory, MethodInfo]]:
    for category in METHOD_CATEGORIES:
        for method in category.methods:
            if method.id == method_id:
                return category, method
    return None


def first_available_method() -> Tuple[MethodCategory, MethodInfo]:
    for category in METHOD_CATEGORIES:
        for method in category.methods:
            if method.available:
                return category, method
    raise ValueError("No hay métodos disponibles configurados.")
