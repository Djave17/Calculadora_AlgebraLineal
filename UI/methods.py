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
                label="Sistema homogéneo",
                icon="LINEAR_SCALE",
                available=True,
                description="Evalúa A·c = 0 para detectar dependencia lineal y soluciones no triviales (Lay §1.7).",
                category="Sistemas de ecuaciones",
                analysis_context="dependence",
                force_homogeneous=True,
                variable_prefix="c",
            ),
            MethodInfo(
                id="matrix_equation",
                label="Ecuación AX = B",
                icon="TABLE_ROWS",
                available=True,
                description="Resuelve columnas de B como sistemas independientes aplicando Gauss-Jordan a cada bᵢ.",
                category="Sistemas de ecuaciones",
                view_type="matrix_equation",
                shows_config_panel=False,
            ),
        ),
    ),
    MethodCategory(
        id="combinations",
        label="Combinaciones y dependencia",
        methods=(
            MethodInfo(
                id="linear_combination",
                label="Combinación lineal",
                icon="FUNCTIONS",
                available=True,
                description="Analiza si un vector objetivo b pertenece al span de {v₁,…,vₖ} resolviendo A·c = b (Grossman §2.1).",
                category="Combinación lineal",
                analysis_context="combination",
                variable_prefix="c",
            ),
            MethodInfo(
                id="vector_dependence",
                label="Dependencia lineal",
                icon="HUB",
                available=True,
                description="Determina si sólo existe la solución trivial del sistema homogéneo A·c = 0 para los vectores dados.",
                category="Dependencia lineal",
                analysis_context="dependence",
                force_homogeneous=True,
                variable_prefix="c",
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
