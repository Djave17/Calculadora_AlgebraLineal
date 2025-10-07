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
                id="matrix_equation",
                label="Ecuación AX = B",
                icon="TABLE_ROWS",
                available=False,
                description="Resuelve columnas de B como sistemas independientes. Disponible en la versión PySide por ahora.",
                category="Sistemas de ecuaciones",
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
            ),
            MethodInfo(
                id="vector_dependence",
                label="Dependencia lineal",
                icon="HUB",
                available=True,
                description="Determina si sólo existe la solución trivial del sistema homogéneo A·c = 0 para los vectores dados.",
                category="Dependencia lineal",
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
                available=False,
                description="Explora suma, multiplicación escalar y verificación de propiedades básicas. Pendiente de portar desde PySide.",
                category="Operaciones vectoriales",
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
                available=False,
                description="Resumen del Método de Eliminación por Renglones (MER) y pasos teóricos. Disponible en la versión previa.",
                category="Teoría",
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
