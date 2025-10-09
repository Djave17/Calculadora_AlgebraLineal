"""Aplicación MatrixCalc en Flet.

Reemplaza la interfaz basada en PySide6 por una experiencia moderna en
Flet con diseño de tres columnas, panel de configuración animado y una
pantalla de bienvenida. La lógica de cálculo permanece delegada en los
ViewModels existentes para mantener el patrón MVVM.
"""

from __future__ import annotations

import os
import sys

import flet as ft

# Ajustar rutas para importaciones relativas desde la raíz del proyecto.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel

from .methods import METHOD_CATEGORIES
from .styles import apply_theme
from .views.main_shell import MainShell
from .views.components.walkthrough import WalkthroughView


def main(page: ft.Page) -> None:
    apply_theme(page)

    view_model = MatrixCalculatorViewModel()
    root_container = ft.Container(expand=True)
    main_shell = MainShell(page, view_model, METHOD_CATEGORIES)

    def show_main_shell() -> None:
        root_container.content = main_shell.view
        root_container.update()
        page.update()

    walkthrough = WalkthroughView(on_start=show_main_shell)
    root_container.content = walkthrough.view
    page.add(root_container)


def run() -> None:  # pragma: no cover - punto de entrada manual
    ft.app(target=main, assets_dir=os.path.join(PROJECT_ROOT, "public"))


if __name__ == "__main__":  # pragma: no cover
    run()
