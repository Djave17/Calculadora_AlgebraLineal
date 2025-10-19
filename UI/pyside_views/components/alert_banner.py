"""Banners de alerta y confirmación para la GUI.

La implementación sigue la idea de paneles de retroalimentación que se
observa en Qt for Python, usando colores distintos para identificar el
significado del mensaje (Grossman, 2019; Lay, 2012, para reforzar el
vínculo entre teoría y comunicación clara al estudiante).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel


class AlertBanner(QFrame):
    """Panel compacto para mostrar mensajes de éxito, advertencia o error."""

    _PALETTES = {
        "success": "background-color: #234b2e; color: #d4f3dc; border: 1px solid #3c8c50;",
        "info": "background-color: #1d3a5f; color: #dbe9ff; border: 1px solid #4d7fb0;",
        "warning": "background-color: #5a4200; color: #ffe8b3; border: 1px solid #b07f2d;",
        "error": "background-color: #611727; color: #ffd6dd; border: 1px solid #b23c4d;",
    }

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("alertBanner")
        self.setVisible(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self._label = QLabel()
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._label, 1)

    def show_message(self, text: str, level: str = "info") -> None:
        """Muestra el banner con el nivel indicado."""

        palette = self._PALETTES.get(level, self._PALETTES["info"])
        self.setStyleSheet(palette)
        self._label.setText(text)
        self.setVisible(True)

    def clear(self) -> None:
        """Oculta el banner y limpia el mensaje."""

        self._label.clear()
        self.setVisible(False)
