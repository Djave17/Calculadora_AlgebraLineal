from __future__ import annotations

"""
Compatibilidad temporal: alias a los métodos cerrados de raíces.
Permite que vistas antiguas que importan `root_finding_vm` sigan funcionando.
"""

from ViewModels.root_methods_closed_vm import (
    ClosedMethodIterationVM as RootFindingIterationVM,
    ClosedMethodResultVM as RootFindingResultVM,
    ClosedMethodName as MethodName,
    solve_closed_root as solve_root,
)

__all__ = ["RootFindingIterationVM", "RootFindingResultVM", "MethodName", "solve_root"]
