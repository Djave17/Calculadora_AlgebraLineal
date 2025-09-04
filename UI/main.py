"""
User interface for the matrix calculator using PySide6.

This module defines a main window that allows the user to input a linear
system in augmented matrix form, choose a resolution method, and view
the solution along with an optional step-by-step breakdown of the
Gauss–Jordan elimination process. The UI is built using Qt widgets
provided by PySide6 and follows a modern, dark-themed aesthetic.

The interface is divided into two primary panels:

1. **Configuración** – Located on the left, this panel lets the user
   specify the number of equations and variables (within predefined
   limits), choose the solution method (currently only Gauss–Jordan),
   reset or fill example data, and initiate the calculation.
2. **Resultados** – On the right, this panel displays the matrix
   augmented input table, the solution (unique, infinite or inconsistent),
   and optionally the list of steps taken during the Gauss–Jordan
   algorithm. Each step shows the operation performed and the matrix
   state after the operation.

The window communicates with the `MatrixCalculatorViewModel` defined
in `UI/ViewModels/viewmodels.py` to perform the actual computation.

Note: This module depends on PySide6. If PySide6 is not installed in
the environment, importing this module will raise an ImportError. The
repository containing this file may not include PySide6 by default; to
run the UI, please ensure that PySide6 is installed in your Python
environment.
"""

import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # carpeta raíz
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import sys
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, 
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QMessageBox,
    QStackedWidget,
    QTextEdit
)


from ViewModels.resolucion_matriz_vm import MatrixCalculatorViewModel, ResultVM, StepVM


class MatrixCalculatorWindow(QMainWindow):
    """Main application window for the matrix calculator.
    Rediseñada con una estética moderna y atractiva.
    """

    # Limits for the size of the matrix.
    MIN_ROWS = 2
    MAX_ROWS = 10
    MIN_COLS = 3
    MAX_COLS = 12

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calculadora de Matrices")
        self.resize(1200, 750)

        # Instantiate the view model
        self.view_model = MatrixCalculatorViewModel()

        # ------------------------------------------------------------------
        # Build navigation and stacked pages
        # ------------------------------------------------------------------
        # Central widget with horizontal layout: navigation panel + content stack
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        central_widget.setLayout(root_layout)

        # Navigation panel on the left
        self.nav_panel = self._create_nav_panel()
        root_layout.addWidget(self.nav_panel)

        # Stacked widget to hold different pages (calculator, other screens)
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, stretch=1)

        # Create pages
        self.home_page = self._create_home_page()
        self.calculator_page = self._create_calculator_page()
        self.theory_page = self._create_theory_page()
        
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.calculator_page)
        self.stack.addWidget(self.theory_page)

        # Set the first navigation button as active by default
        self.btn_home_page.setChecked(True)
        self.stack.setCurrentIndex(0)

        # Apply the new style
        self._apply_modern_theme()

        # Initialize table dimensions on calculator page
        self._update_table_dimensions()

    # ------------------------------------------------------------------
    # UI Creation
    # ------------------------------------------------------------------
    def _create_config_panel(self) -> QWidget:
        panel = QGroupBox("Configuración")
        panel.setStyleSheet("""
            QGroupBox {
                background-color: #F8FAFF;
                border: 1px solid #A5C0E6;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 10px;
                font-weight: bold;
                color: #2A2A2A;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2A2A2A;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        panel.setLayout(layout)

        # Grid layout for inputs
        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        layout.addLayout(grid)

        # Rows spin box
        rows_label = QLabel("Filas")
        rows_label.setStyleSheet("color: #2A2A2A; font-weight: bold;")
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(self.MIN_ROWS)
        self.rows_spin.setMaximum(self.MAX_ROWS)
        self.rows_spin.setValue(self.view_model.rows)
        self.rows_spin.valueChanged.connect(self._on_dimensions_changed)
        self.rows_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #A5C0E6;
                border-radius: 4px;
                background-color: white;
                color: #2A2A2A;
            }
        """)
        rows_note = QLabel("2–10 filas")
        rows_note.setStyleSheet("font-size: 9pt; color: #6B7280;")

        grid.addWidget(rows_label, 0, 0)
        grid.addWidget(self.rows_spin, 0, 1)
        grid.addWidget(rows_note, 1, 0, 1, 2)

        # Columns spin box
        cols_label = QLabel("Columnas")
        cols_label.setStyleSheet("color: #2A2A2A; font-weight: bold;")
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(self.MIN_COLS)
        self.cols_spin.setMaximum(self.MAX_COLS)
        self.cols_spin.setValue(self.view_model.cols)
        self.cols_spin.valueChanged.connect(self._on_dimensions_changed)
        self.cols_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #A5C0E6;
                border-radius: 4px;
                background-color: white;
                color: #2A2A2A;
            }
        """)
        cols_note = QLabel("3–12 columnas")
        cols_note.setStyleSheet("font-size: 9pt; color: #6B7280;")
        grid.addWidget(cols_label, 2, 0)
        grid.addWidget(self.cols_spin, 2, 1)
        grid.addWidget(cols_note, 3, 0, 1, 2)

        # Method combobox
        method_label = QLabel("Método")
        method_label.setStyleSheet("color: #2A2A2A; font-weight: bold;")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Gauss-Jordan"])
        self.method_combo.setCurrentIndex(0)
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        self.method_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #A5C0E6;
                border-radius: 4px;
                background-color: white;
                color: #2A2A2A;
            }
        """)
        method_note = QLabel("Método de resolución")
        method_note.setStyleSheet("font-size: 9pt; color: #6B7280;")

        grid.addWidget(method_label, 4, 0)
        grid.addWidget(self.method_combo, 4, 1)
        grid.addWidget(method_note, 5, 0, 1, 2)

        # Matrix dimension label
        self.dimension_label = QLabel()
        font_dim = QFont()
        font_dim.setPointSize(9)
        font_dim.setItalic(True)
        self.dimension_label.setFont(font_dim)
        self.dimension_label.setStyleSheet("color: #4267B2;")
        grid.addWidget(self.dimension_label, 6, 0, 1, 2)

        # Buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.solve_button = QPushButton("Calcular Resultado")
        self.solve_button.clicked.connect(self._on_solve_clicked)
        
        self.steps_button = QPushButton("Mostrar Pasos")
        self.steps_button.clicked.connect(lambda: self.steps_scroll.setVisible(True))
        
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        
        self.example_button = QPushButton("Ejemplo")
        self.example_button.clicked.connect(self._on_example_clicked)
        
        # Style for buttons
        button_style = """
            QPushButton {
                background-color: #4267B2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #365A9C;
            }
            QPushButton:pressed {
                background-color: #2A4A85;
            }
        """
        
        self.solve_button.setStyleSheet(button_style)
        self.steps_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)
        self.example_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.solve_button)
        buttons_layout.addWidget(self.steps_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.example_button)

        layout.addSpacing(10)
        layout.addLayout(buttons_layout)
        layout.addStretch()

        return panel

    def _create_theory_page(self) -> QWidget:
        """Página con teoría básica de Álgebra Lineal."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 20, 40, 20)
        page.setLayout(layout)

        title = QLabel("Teoría de Matrices")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E2A4A; margin-bottom: 30px;")
        layout.addWidget(title)

        # Create a scroll area for the theory content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        # Theory content
        theory_content = QTextEdit()
        theory_content.setReadOnly(True)
        theory_content.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 20px;
                color: #2A2A2A;
                font-size: 11pt;
            }
        """)
        
        theory_content.setHtml("""
            <h2 style="color: #1E2A4A;">Conceptos Esenciales de Álgebra Lineal</h2>
            
            <h3 style="color: #4267B2;">Matrices</h3>
            <p>Una matriz es un arreglo rectangular de números reales, organizados en filas y columnas. 
            Se utiliza para representar sistemas de ecuaciones lineales, transformaciones lineales y 
            muchas otras relaciones matemáticas.</p>
            
            <h3 style="color: #4267B2;">Sistemas de Ecuaciones Lineales</h3>
            <p>Un sistema de ecuaciones lineales es un conjunto de ecuaciones lineales que comparten 
            las mismas variables. La solución del sistema es el conjunto de valores que satisfacen 
            todas las ecuaciones simultáneamente.</p>
            
            <h3 style="color: #4267B2;">Forma Escalonada Reducida</h3>
            <p>Una matriz está en forma escalonada reducida cuando:</p>
            <ul>
                <li>Todas las filas cero están en la parte inferior</li>
                <li>El primer elemento no nulo de cada fila (pivote) es 1</li>
                <li>El pivote de cada fila está a la derecha del pivote de la fila anterior</li>
                <li>Todos los elementos por encima y por debajo de un pivote son cero</li>
            </ul>
            
            <h3 style="color: #4267B2;">Eliminación de Gauss-Jordan</h3>
            <p>Es un algoritmo para resolver sistemas de ecuaciones lineales. El procedimiento consiste 
            en realizar operaciones elementales de fila para reducir la matriz aumentada a su forma 
            escalonada reducida. Las operaciones permitidas son:</p>
            <ul>
                <li>Intercambiar dos filas</li>
                <li>Multiplicar una fila por una constante no nula</li>
                <li>Sumar a una fila un múltiplo de otra</li>
            </ul>
            
            <h3 style="color: #4267B2;">Tipos de Solución</h3>
            <p>Un sistema de ecuaciones lineales puede tener:</p>
            <ul>
                <li><strong>Solución Única:</strong> El sistema tiene exactamente una solución</li>
                <li><strong>Infinitas Soluciones:</strong> El sistema tiene un número infinito de soluciones</li>
                <li><strong>Sistema Inconsistente:</strong> El sistema no tiene solución</li>
            </ul>
        """)
        
        content_layout.addWidget(theory_content)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        return page

    def _create_result_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        panel.setLayout(layout)

        # Augmented matrix table title
        title = QLabel("Matriz aumentada del sistema")
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        title.setFont(font_title)
        title.setStyleSheet("color: #1E2A4A;")
        layout.addWidget(title)

        # Table for augmented matrix [A|b]
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table.setFixedHeight(220)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #E5E7EB;
                color: #2A2A2A;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #2A2A2A;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table)

        # Solution output area
        solution_title = QLabel("Resultado")
        solution_title.setFont(font_title)
        solution_title.setStyleSheet("color: #1E2A4A;")
        layout.addWidget(solution_title)

        # Label for state (UNICA, INFINITAS, INCONSISTENTE)
        self.state_label = QLabel()
        font_state = QFont()
        font_state.setPointSize(12)
        font_state.setBold(True)
        self.state_label.setFont(font_state)
        self.state_label.setStyleSheet("color: #4267B2; margin-bottom: 10px;")
        layout.addWidget(self.state_label)

        # Container for variable values or parametric solution
        self.solution_container = QVBoxLayout()
        self.solution_container.setSpacing(5)
        layout.addLayout(self.solution_container)

        # Scroll area for steps
        steps_title = QLabel("Pasos Gauss-Jordan")
        steps_title.setFont(font_title)
        steps_title.setStyleSheet("color: #1E2A4A; margin-top: 20px;")
        layout.addWidget(steps_title)

        self.steps_scroll = QScrollArea()
        self.steps_scroll.setWidgetResizable(True)
        self.steps_scroll.setFrameShape(QFrame.NoFrame)
        self.steps_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setContentsMargins(15, 15, 15, 15)
        self.steps_layout.setSpacing(15)
        self.steps_container.setLayout(self.steps_layout)
        self.steps_scroll.setWidget(self.steps_container)
        self.steps_scroll.setVisible(False)  # Initially hidden
        layout.addWidget(self.steps_scroll)

        return panel

    # ------------------------------------------------------------------
    # Navigation and Pages
    # ------------------------------------------------------------------
    def _create_nav_panel(self) -> QWidget:
        """Create the lateral navigation panel with page selection buttons."""
        panel = QFrame()
        panel.setObjectName("navPanel")
        panel.setFixedWidth(250)
        panel.setStyleSheet("""
            #navPanel {
                background-color: #2A3858;
            }
        """)

        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        panel.setLayout(nav_layout)

        # Logo / Title
        logo_widget = QWidget()
        logo_widget.setFixedHeight(80)
        logo_layout = QVBoxLayout()
        logo_widget.setLayout(logo_layout)
        logo_widget.setStyleSheet("background-color: #1E2A4A;")
        
        title_label = QLabel("MatrixCalc")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; padding: 8px;")
        logo_layout.addWidget(title_label)
        
        nav_layout.addWidget(logo_widget)

        # Navigation buttons
        nav_buttons = [
            ("Menú principal", 0),
            ("Calculadora", 1),
            ("Teoría", 2)
        ]
        
        self.nav_buttons = []
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, idx=index: self.stack.setCurrentIndex(idx))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #FFFFFF;
                    padding: 15px 20px;
                    text-align: left;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #3A4868;
                }
                QPushButton:checked {
                    background-color: #4267B2;
                    font-weight: bold;
                }
            """)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            if index == 0:
                self.btn_home_page = btn
            elif index == 1:
                self.btn_calc_page = btn
            elif index == 2:
                self.btn_theory_page = btn

        # Logout button at the bottom
        nav_layout.addStretch()
        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
                padding: 15px 20px;
                text-align: left;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #3A4868;
            }
        """)
        nav_layout.addWidget(logout_btn)

        return panel

    def _create_calculator_page(self) -> QWidget:
        """Create the calculator page with configuration and result panels."""
        page = QWidget()
        page.setStyleSheet("background-color: #FFFFFF;")
        
        # Create top bar
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #1E2A4A;")
        top_layout = QHBoxLayout()
        top_bar.setLayout(top_layout)
        
        title = QLabel("Calculadora de Matrices")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        top_layout.addWidget(title)
        
        # Main content
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        content_widget.setLayout(content_layout)

        # Configuration panel on the left
        self.config_panel = self._create_config_panel()
        content_layout.addWidget(self.config_panel, 1)

        # Result panel on the right
        result_panel = self._create_result_panel()
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setWidget(result_panel)
        content_layout.addWidget(result_scroll, 2)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(top_bar)
        main_layout.addWidget(content_widget)
        page.setLayout(main_layout)

        return page

    def _create_home_page(self) -> QWidget:
        """Create the home page with matrix type selection."""
        page = QWidget()
        page.setStyleSheet("background-color: #FFFFFF;")
        
        # Create top bar
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #1E2A4A;")
        top_layout = QHBoxLayout()
        top_bar.setLayout(top_layout)
        
        title = QLabel("MatrixCalc - Menú Principal")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        top_layout.addWidget(title)
        
        # Main content
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_widget.setLayout(content_layout)

        title = QLabel("Elige tu matriz")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1E2A4A; margin-bottom: 10px;")
        content_layout.addWidget(title)

        subtitle = QLabel("Selecciona el tipo de matriz para comenzar")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6B7280; font-size: 14px; margin-bottom: 40px;")
        content_layout.addWidget(subtitle)

        # Opciones de selección
        options_layout = QHBoxLayout()
        options_layout.setSpacing(30)

        btn_nxn = QPushButton("Matriz nxn\n(Determinantes, inversa, sistemas)")
        btn_nxn.setFixedSize(200, 120)
        btn_nxn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_nxn.setStyleSheet("""
            QPushButton {
                background-color: #4267B2;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #365A9C;
            }
        """)
        
        btn_nxm = QPushButton("Matriz nxm\n(Reducción, forma escalonada)")
        btn_nxm.setFixedSize(200, 120)
        btn_nxm.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_nxm.setStyleSheet("""
            QPushButton {
                background-color: #4267B2;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #365A9C;
            }
        """)

        options_layout.addStretch()
        options_layout.addWidget(btn_nxn)
        options_layout.addWidget(btn_nxm)
        options_layout.addStretch()

        content_layout.addLayout(options_layout)
        content_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(top_bar)
        main_layout.addWidget(content_widget)
        page.setLayout(main_layout)

        return page

    def _apply_modern_theme(self) -> None:
        """Apply a modern light theme to the entire application."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(42, 42, 42))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(248, 250, 255))
        palette.setColor(QPalette.Text, QColor(42, 42, 42))
        palette.setColor(QPalette.Button, QColor(66, 103, 178))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(66, 103, 178))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

        # Global style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QWidget {
                font-size: 10.5pt;
            }
            QLabel {
                color: #2A2A2A;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    # ------------------------------------------------------------------
    # Event Handlers
    # ------------------------------------------------------------------
    def _on_dimensions_changed(self) -> None:
        """Handle changes to the number of rows or columns."""
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        self.view_model.rows = m
        self.view_model.cols = n
        self._update_table_dimensions()
        self.dimension_label.setText(f"Matriz {m}×{n} (A|b)")

    def _on_method_changed(self) -> None:
        method_text = self.method_combo.currentText()
        self.view_model.method = method_text

    def _on_solve_clicked(self) -> None:
        """Read the matrix values from the table, invoke the solver and
        display the results. Invalid inputs trigger a message box.
        """
        try:
            augmented = []
            for i in range(self.table.rowCount()):
                row_values: List[float] = []
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    value_str = item.text() if item else "0"
                    # Empty cells are treated as zero; otherwise parse float
                    try:
                        value = float(value_str.strip()) if value_str.strip() != "" else 0.0
                    except ValueError:
                        raise ValueError(
                            f"Valor no numérico en fila {i+1}, columna {j+1}: '{value_str}'"
                        )
                    row_values.append(value)
                augmented.append(row_values)
            result = self.view_model.solve(augmented)
            self._update_result_display(result)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_clear_clicked(self) -> None:
        """Clear all entries in the matrix table and reset the result panel."""
        self._reset_table_to_zero()
        self.state_label.clear()
        self._clear_solution_display()
        self._clear_steps_display()

    def _on_example_clicked(self) -> None:
        """Fill the table with a simple example matrix and vector."""
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        # Example: A is identity-like with sequential numbers; b is 1..m
        for i in range(m):
            for j in range(n):
                value = 1.0 if i == j else float((i + j) % 5 + 1)
                item = QTableWidgetItem(f"{value}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            # b vector: sequential integers starting from 1
            b_value = float(i + 1)
            b_item = QTableWidgetItem(f"{b_value}")
            b_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, n, b_item)

    # ------------------------------------------------------------------
    # UI Update Helpers
    # ------------------------------------------------------------------
    def _update_table_dimensions(self) -> None:
        """Resize the table to match the current rows and columns."""
        m = self.view_model.rows
        n = self.view_model.cols
        current_rows = self.table.rowCount()
        current_cols = self.table.columnCount()

        # Adjust row count
        if current_rows != m:
            self.table.setRowCount(m)
        # Adjust column count (n variables + 1 for b)
        if current_cols != n + 1:
            self.table.setColumnCount(n + 1)
            # Set column headers
            headers = [f"x{j + 1}" for j in range(n)] + ["b"]
            self.table.setHorizontalHeaderLabels(headers)
        
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Adjust table height based on number of rows
        row_height = 24
        header_height = 30
        desired = min(320, row_height * m + header_height)
        self.table.setFixedHeight(desired)

        # Initialize new cells with empty text
        for i in range(m):
            for j in range(n + 1):
                if not self.table.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

    def _reset_table_to_zero(self) -> None:
        """Set all entries in the matrix table to zero."""
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if not item:
                    item = QTableWidgetItem()
                    self.table.setItem(i, j, item)
                item.setText("0")
                item.setTextAlignment(Qt.AlignCenter)

    def _clear_solution_display(self) -> None:
        """Remove existing solution widgets from the solution container."""
        while self.solution_container.count():
            child = self.solution_container.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

    def _clear_steps_display(self) -> None:
        """Remove existing step widgets from the steps container."""
        while self.steps_layout.count():
            child = self.steps_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

    def _update_result_display(self, result: ResultVM) -> None:
        """Update the solution and steps areas based on the result."""
        # Clear previous output
        self._clear_solution_display()
        self._clear_steps_display()

        # State label
        if result.status == "UNICA":
            self.state_label.setText("Solución única")
        elif result.status == "INFINITAS":
            self.state_label.setText("Infinitas soluciones")
        else:
            self.state_label.setText("Sistema inconsistente")

        # Solution or parametric
        if result.status == "UNICA" and result.solution is not None:
            for idx, value in enumerate(result.solution, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
        elif result.status == "INFINITAS" and result.parametric is not None:
            p = result.parametric
            # Particular solution
            particular_title = QLabel("Solución particular:")
            particular_title.setStyleSheet("font-size: 10pt; font-weight: bold;")
            self.solution_container.addWidget(particular_title)
            for idx, value in enumerate(p.particular, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
            # Direction vectors
            directions_title = QLabel("Direcciones asociadas a cada variable libre:")
            directions_title.setStyleSheet("font-size: 10pt; font-weight: bold; margin-top: 8px;")
            self.solution_container.addWidget(directions_title)
            for k, dir_vec in enumerate(p.directions):
                items = []
                for j, coef in enumerate(dir_vec):
                    if abs(coef) > 1e-12:
                        items.append(f"{coef:.6g}·x{j+1}")
                term = " + ".join(items) if items else "0"
                dir_label = QLabel(f"t{k+1}: {term}")
                dir_label.setStyleSheet("font-size: 10pt; color: #a3c2e3;")
                self.solution_container.addWidget(dir_label)
        else:
            # Inconsistent: no solution values to display
            inc_label = QLabel("No existe solución.")
            inc_label.setStyleSheet("font-size: 10pt; color: #e06c75;")
            self.solution_container.addWidget(inc_label)

        # Steps
        if result.steps:
            for step in result.steps:
                step_widget = self._create_step_widget(step)
                self.steps_layout.addWidget(step_widget)
            self.steps_layout.addStretch()

    def _create_step_widget(self, step: StepVM) -> QWidget:
        """Create a widget representing a single Gauss–Jordan step."""
        widget = QGroupBox(f"Paso {step.number} – {step.description}")
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Table showing the matrix after the operation
        matrix = step.after_matrix
        if not matrix:
            # If no after matrix provided, skip matrix display
            return widget
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        table = QTableWidget(rows, cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table.setFixedHeight(20 * rows + 2)
        # Populate table
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(f"{matrix[i][j]:.6g}")
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        # Resize columns proportionally
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        return widget


def main() -> None:
    app = QApplication(sys.argv)
    window = MatrixCalculatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()