"""Ventana principal de la calculadora de álgebra lineal.

El módulo ahora compone las vistas modulares (`CalculatorPage`,
`VectorPropertiesPage`, etc.) y los ViewModels definidos en el paquete
`ViewModels`. De esta manera se respeta la separación del patrón MVVM
(Silverlight Toolkit, 2009) y se evitan las dependencias circulares que
se tenían al mezclar la lógica en un solo archivo.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Agregar raíz del proyecto al sys.path cuando se ejecuta como script.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ViewModels.combinacion_lineal_vm import CombinacionLinealViewModel
from ViewModels.matrix_equation_vm import MatrixEquationViewModel
from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel
from ViewModels.vector_propiedades_vm import VectorPropiedadesViewModel

from views.calculator_page import CalculatorPage
from views.combination_page import CombinationPage
from views.home_page import HomePage
from views.matrix_equation_page import MatrixEquationPage
from views.mer_page import MerPage
from views.vector_properties_page import VectorPropertiesPage


class MatrixCalculatorWindow(QMainWindow):
    """Ventana principal que coordina navegación y ViewModels."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calculadora de Matrices")
        self.resize(1200, 760)

        self._create_view_models()
        self._build_ui()
        self._nav_collapsed = False
        self._apply_dark_theme()

    # ---------------------- Composición de ViewModels ----------------------
    def _create_view_models(self) -> None:
        self.calculator_vm = MatrixCalculatorViewModel()
        self.vector_vm = VectorPropiedadesViewModel()
        self.combination_vm = CombinacionLinealViewModel()
        self.matrix_eq_vm = MatrixEquationViewModel()

    # ----------------------------- Configuración de UI -----------------------------
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        self.nav_panel = self._build_nav_panel()
        root_layout.addWidget(self.nav_panel)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, stretch=1)

        self.pages: Dict[str, Tuple[QWidget, QPushButton]] = {}
        self._register_pages()

        # Seleccionar la página de inicio por defecto
        self._set_current_page("home")

    def _build_nav_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("navPanel")
        panel.setProperty("collapsed", False)
        panel.setFixedWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)

        self.nav_toggle = QPushButton("≡")
        self.nav_toggle.setObjectName("navToggleButton")
        self.nav_toggle.setCursor(Qt.PointingHandCursor)
        self.nav_toggle.setFixedWidth(44)
        self.nav_toggle.clicked.connect(self._toggle_nav_panel)
        top_bar.addWidget(self.nav_toggle)

        title = QLabel("Calculadora")
        title.setObjectName("navTitle")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._nav_title_label = title
        top_bar.addWidget(title, 1)
        layout.addLayout(top_bar)

        self.nav_buttons: Dict[str, QPushButton] = {}
        self._nav_buttons_layout = QVBoxLayout()
        self._nav_buttons_layout.setContentsMargins(0, 8, 0, 0)
        self._nav_buttons_layout.setSpacing(6)
        layout.addLayout(self._nav_buttons_layout)
        layout.addStretch(1)
        return panel


    def _create_nav_button(self, key: str, text: str, index: int) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.clicked.connect(lambda: self._on_nav_clicked(key, index))
        self.nav_buttons[key] = button
        self._nav_buttons_layout.addWidget(button)
        return button

    def _register_pages(self) -> None:
        pages = [
            ("home", "Inicio", HomePage()),
            ("calculator", "Resolver", CalculatorPage(self.calculator_vm)),
            ("mer", "MER", MerPage()),
            ("vectors", "Propiedades ℝ^n", VectorPropertiesPage(self.vector_vm)),
            ("combination", "Combinación", CombinationPage(self.combination_vm)),
            ("matrix_eq", "AX = B", MatrixEquationPage(self.matrix_eq_vm)),
        ]

        for index, (key, label, widget) in enumerate(pages):
            button = self._create_nav_button(key, label, index)
            self.stack.addWidget(widget)
            self.pages[key] = (widget, button)

        self._nav_buttons_layout.addStretch(1)

    # ----------------------------- Navegación ---------------------------
    def _on_nav_clicked(self, key: str, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for name, (_, button) in self.pages.items():
            button.setChecked(name == key)

    def _set_current_page(self, key: str) -> None:
        widget, button = self.pages[key]
        index = self.stack.indexOf(widget)
        self.stack.setCurrentIndex(index)
        button.setChecked(True)

    def _toggle_nav_panel(self) -> None:
        self._nav_collapsed = not self._nav_collapsed
        if self._nav_collapsed:
            self.nav_panel.setFixedWidth(64)
            self._nav_title_label.setVisible(False)
            for button in self.nav_buttons.values():
                button.setVisible(False)
        else:
            self.nav_panel.setFixedWidth(200)
            self._nav_title_label.setVisible(True)
            for button in self.nav_buttons.values():
                button.setVisible(True)

        self.nav_panel.setProperty("collapsed", self._nav_collapsed)
        self.nav_panel.style().unpolish(self.nav_panel)
        self.nav_panel.style().polish(self.nav_panel)

    # ------------------------------ Estilos ------------------------------
    def _apply_dark_theme(self) -> None:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(10, 19, 43))
        palette.setColor(QPalette.WindowText, QColor(230, 239, 251))
        palette.setColor(QPalette.Base, QColor(18, 29, 61))
        palette.setColor(QPalette.AlternateBase, QColor(14, 24, 50))
        palette.setColor(QPalette.Text, QColor(230, 239, 251))
        palette.setColor(QPalette.Button, QColor(27, 44, 76))
        palette.setColor(QPalette.ButtonText, QColor(230, 239, 251))
        palette.setColor(QPalette.Highlight, QColor(64, 125, 188))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

        self.setStyleSheet(
            """
            QWidget { font-size: 14px; }
            QLabel { color: #e6effb; }
            QGroupBox {
                border: 1px solid #2b4168;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
                background-color: #11284a;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QSpinBox, QComboBox, QLineEdit {
                background-color: #1c3156;
                border: 1px solid #365a8e;
                border-radius: 4px;
                padding: 2px 4px;
                color: #e6effb;
                selection-background-color: #407dbc;
                selection-color: #ffffff;
            }
            QPushButton {
                background-color: #365a8e;
                border: 1px solid #407dbc;
                border-radius: 4px;
                padding: 6px 14px;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #407dbc; }
            QPushButton:pressed { background-color: #2a4475; }
            QTableWidget {
                background-color: #1c3156;
                gridline-color: #2f4c77;
                color: #e6effb;
            }
            QHeaderView::section {
                background-color: #152b51;
                color: #e6effb;
                padding: 4px;
                border: 1px solid #2b4168;
                font-weight: bold;
            }
            QMessageBox {
                background-color: #11284a;
                color: #e6effb;
                border: 1px solid #365a8e;
            }
            QMessageBox QLabel { color: #e6effb; }
            QMessageBox QPushButton {
                background-color: #365a8e;
                border: 1px solid #407dbc;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QMessageBox QPushButton:hover { background-color: #407dbc; }
            QMessageBox QPushButton:pressed { background-color: #2a4475; }
            #navPanel {
                background-color: #11284a;
                border-right: 1px solid #2b4168;
            }
            #navPanel[collapsed="true"] {
                border-right: none;
                background-color: #0d1c36;
            }
            #navToggleButton {
                background-color: #243f6b;
                border: 1px solid #365a8e;
                border-radius: 6px;
                padding: 6px 8px;
                color: #e6effb;
            }
            #navToggleButton:hover { background-color: #2f5288; }
            #navToggleButton:pressed { background-color: #1b2f55; }
            #navTitle {
                color: #ffffff;
                padding-left: 6px;
            }
            #navButton {
                background-color: transparent;
                border: none;
                color: #e6effb;
                padding: 12px 16px;
                text-align: left;
                font-size: 13px;
                border-radius: 6px;
            }
            #navButton:hover { background-color: #1c3156; }
            #navButton:checked {
                background-color: #365a8e;
                font-weight: bold;
            }
            QScrollArea { border: none; }
            QScrollArea > QWidget > QWidget { background-color: #1c3156; }
            """
        )


def run() -> None:
    app = QApplication(sys.argv)
    window = MatrixCalculatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover - ruta de ejecución manual
    run()
