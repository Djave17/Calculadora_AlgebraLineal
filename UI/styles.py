from __future__ import annotations

import flet as ft

PRIMARY_COLOR = "#a6080f"
SECONDARY_COLOR = "#d44242"
ACCENT_COLOR = "#f0b5b5"
BACKGROUND_COLOR = "#fff8f7"
SURFACE_COLOR = "#ffffff"
TEXT_DARK = "#2c1a1a"
TEXT_MUTED = "#735555"
BORDER_COLOR = "#f3cdcd"
CARD_RADIUS = 16
PANEL_WIDTH = 320
LEFT_MENU_WIDTH = 288
TOP_BAR_HEIGHT = 64


def apply_theme(page: ft.Page) -> None:
    """Configura los valores globales del `Page` para respetar la guía visual."""

    page.title = "MatrixCalc"
    page.bgcolor = BACKGROUND_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.fonts = {
        "Inter": "https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTGJX7r1Q.woff2",
    }
    page.theme = ft.Theme(font_family="Inter")
