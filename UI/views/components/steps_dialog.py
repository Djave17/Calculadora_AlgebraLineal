from __future__ import annotations

from typing import Iterable, List

import flet as ft
from flet import Colors as colors

from ViewModels.resolucion_matriz_vm import StepVM

from ...styles import (
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SURFACE_COLOR,
    TEXT_DARK,
    TEXT_MUTED,
)


def show_steps_dialog(
    page: ft.Page,
    steps: Iterable[StepVM],
    pivot_cols: Iterable[int],
    title: str = "Pasos Gauss–Jordan",
) -> None:
    steps = list(steps)
    if not steps:
        return

    pivot_labels = ", ".join(f"x{idx + 1}" for idx in pivot_cols) or "—"
    header = ft.Text(
        f"Columnas pivote: {pivot_labels}",
        color=TEXT_MUTED,
        size=12,
    )

    items: List[ft.Control] = []
    for step in steps:
        items.append(_build_step_card(step))

    scrollable = ft.Container(
        height=420,
        content=ft.Column(
            spacing=14,
            controls=items,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    content = ft.Column(
        spacing=16,
        controls=[header, scrollable],
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
        content=ft.Container(
            width=720,
            padding=ft.Padding(12, 12, 12, 12),
            bgcolor=SURFACE_COLOR,
            content=content,
        ),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: _close_dialog(page),
                style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: PRIMARY_COLOR}),
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=18),
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


def _close_dialog(page: ft.Page) -> None:
    if page.dialog:
        page.dialog.open = False
        page.update()


def _build_step_card(step: StepVM) -> ft.Control:
    pivot_text = ""
    if step.pivot_row is not None and step.pivot_col is not None:
        pivot_text = f" | pivote en fila {step.pivot_row + 1}, columna {step.pivot_col + 1}"
    title = ft.Text(
        f"Paso {step.number}. {step.description}{pivot_text}",
        weight=ft.FontWeight.W_600,
        color=TEXT_DARK,
    )

    matrix = step.after_matrix or []
    matrix_view = ft.Column(spacing=4)
    for i, row in enumerate(matrix):
        cells: List[ft.Control] = []
        for j, value in enumerate(row):
            bgcolor = None
            if step.pivot_row == i and step.pivot_col == j:
                bgcolor = SECONDARY_COLOR
            cells.append(
                ft.Container(
                    width=56,
                    height=32,
                    alignment=ft.alignment.center,
                    bgcolor=bgcolor,
                    border=ft.border.all(1, color=PRIMARY_COLOR if bgcolor is None else SECONDARY_COLOR),
                    border_radius=8,
                    content=ft.Text(str(value), color=TEXT_DARK if bgcolor is None else colors.WHITE, size=12),
                )
            )
        matrix_view.controls.append(ft.Row(cells, spacing=6))

    card = ft.Container(
        bgcolor="#fff1f1",
        border_radius=16,
        padding=ft.Padding(16, 16, 16, 16),
        border=ft.border.all(1, color=PRIMARY_COLOR),
        content=ft.Column(
            spacing=12,
            controls=[
                title,
                matrix_view,
            ],
        ),
    )
    return card
