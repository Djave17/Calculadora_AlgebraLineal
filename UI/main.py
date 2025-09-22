"""
IU de la Calculadora de Matrices (PySide6) – Método de Gauss‑Jordan

Permite introducir una matriz aumentada A|b y resuelve el sistema lineal
aplicando eliminación de Gauss‑Jordan hasta alcanzar la forma escalonada
reducida por filas (RREF). Determina si el sistema es consistente, si tiene
solución única o infinitas soluciones y muestra la solución particular y las
direcciones asociadas a variables libres. Los pasos del algoritmo pueden
verse en una ventana separada.
"""

from __future__ import annotations

# Añadir la carpeta raíz al sys.path cuando se ejecuta este script directamente.
import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # directorio raíz del proyecto
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtWidgets import (
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
    QAbstractItemView,
    QAbstractScrollArea,
    QDialog,
    QLineEdit, 
    QTextEdit,
)

# Importa los view models utilizados en las distintas páginas.
from UI.ViewModels.resolucion_matriz_vm import (
    MatrixCalculatorViewModel,
    ResultVM,
    StepVM,
    MatrixEquationResultVM,
)
from UI.ViewModels.vector_propiedades_vm import VectorPropiedadesViewModel
from UI.ViewModels.combinacion_lineal_vm import (
    CombinacionLinealViewModel,
    CombinationResultVM,
)
from UI.ViewModels.matrix_equation_vm import MatrixEquationViewModel


class MatrixCalculatorWindow(QMainWindow):
    """Ventana principal de la calculadora de matrices.

    Esta clase construye la interfaz de usuario y enlaza los eventos
    generados por la vista con las acciones del ViewModel. Responde a
    cambios del usuario (como modificar dimensiones, introducir datos
    en la matriz, pulsar el botón de resolver) actualizando la tabla
    y mostrando los resultados correspondientes.
    """

    # Límites para el tamaño de la matriz (m ecuaciones, n variables)
    MIN_ROWS = 2
    MAX_ROWS = 10
    MIN_COLS = 3
    MAX_COLS = 12

    # Umbral máximo de pasos que se mostrarán directamente en la página
    # principal antes de recurrir a la ventana emergente de pasos.
    MAX_DISPLAY_STEPS = 10

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calculadora de Matrices")
        self.resize(1100, 700)

        # Instanciar los view models principales por página
        self.view_model = MatrixCalculatorViewModel()

        self.vector_vm = VectorPropiedadesViewModel()
        self.combination_vm = CombinacionLinealViewModel()
        self.matrix_eq_vm = MatrixEquationViewModel()

        # Almacenes para reutilizar resultados en diálogos
        self._combo_last_result: CombinationResultVM | None = None
        self._matrix_eq_last_result: MatrixEquationResultVM | None = None


        # ------------------------------------------------------------------
        # Construcción del layout principal
        # ------------------------------------------------------------------
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)
        central_widget.setLayout(root_layout)

        # Panel de navegación en el lado izquierdo
        self.nav_panel = self._create_nav_panel()
        root_layout.addWidget(self.nav_panel)

        # QStackedWidget para albergar distintas páginas
        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, stretch=1)


        # Crear páginas de la aplicación
        self.calculator_page = self._create_calculator_page()
        self.home_page = self._create_home_page()
        self.stack.addWidget(self.calculator_page)
        self.stack.addWidget(self.home_page)

        # Crear la nueva página (vectores) 
        self.vector_props_page = self._create_vector_prop_page()
        self.stack.addWidget(self.vector_props_page)

        # Página para combinación lineal de vectores
        self.combination_page = self._create_combination_page()
        self.stack.addWidget(self.combination_page)

        # Página para resolver ecuaciones matriciales AX = B
        self.matrix_eq_page = self._create_matrix_equation_page()
        self.stack.addWidget(self.matrix_eq_page)

        # Seleccionar la página del cálculo por defecto
        self.btn_calc_page.setChecked(True)

        # Aplicar tema oscuro
        self._apply_dark_theme()

        # Inicializar dimensiones de la tabla de la página de cálculo
        self._update_table_dimensions()

        # Almacén para los pasos completos de Gauss–Jordan. Cuando hay
        # demasiados pasos para mostrarse directamente en la página
        # principal, se guardan aquí y se muestran en una ventana
        # emergente al pulsar el botón "Ver pasos Gauss–Jordan".
        self._last_steps: List[StepVM] | None = None

        # Información de diagnóstico del último resultado
        # Columnas pivote (0‑based sobre A) y variables libres.
        # Se usa para resaltar en la vista de pasos.
        self._last_pivot_cols: List[int] | None = None
        self._last_free_vars: List[int] | None = None

        # Controla si el panel de navegación está expandido o colapsado. Por
        # defecto comienza expandido. Este flag se alterna mediante
        # `_toggle_nav_panel` cuando el usuario pulsa el botón de menú.
        self._nav_expanded: bool = True

    # ------------------------------------------------------------------
    # Creación de la UI
    # ------------------------------------------------------------------
    def _create_config_panel(self) -> QWidget:
        """Crea el panel de configuración para especificar dimensiones y método.

        Este panel se coloca en la columna izquierda de la página de
        cálculo. Incluye controles para seleccionar el número de filas
        (m), el número de columnas (n) y el método de solución.
        
        Devuelve
        -------
        QWidget
            El panel de configuración listo para insertar en un layout.
        """
        panel = QGroupBox("Configuración")
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Descripción breve del uso
        subtitle = QLabel(
            "Resuelve sistemas de ecuaciones lineales mediante el método de eliminación de Gauss-Jordan. El algoritmo transforma la matriz aumentada a su forma escalonada reducida para encontrar la solución."
        )
        subtitle.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        subtitle.setFont(font)
        layout.addWidget(subtitle)

        # Disposición en cuadrícula para los controles
        grid = QGridLayout()
        layout.addLayout(grid)

        # SpinBox de filas
        rows_label = QLabel("Filas")
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(self.MIN_ROWS)
        self.rows_spin.setMaximum(self.MAX_ROWS)
        self.rows_spin.setValue(self.view_model.rows)
        self.rows_spin.valueChanged.connect(self._on_dimensions_changed)
        rows_note = QLabel("2–10 filas")
        rows_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(rows_label, 0, 0)
        grid.addWidget(self.rows_spin, 0, 1)
        grid.addWidget(rows_note, 1, 0, 1, 2)

        # SpinBox de columnas
        cols_label = QLabel("Columnas")
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(self.MIN_COLS)
        self.cols_spin.setMaximum(self.MAX_COLS)
        self.cols_spin.setValue(self.view_model.cols)
        self.cols_spin.valueChanged.connect(self._on_dimensions_changed)
        cols_note = QLabel("3–12 columnas")
        cols_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(cols_label, 2, 0)
        grid.addWidget(self.cols_spin, 2, 1)
        grid.addWidget(cols_note, 3, 0, 1, 2)

        # Combobox para el método de resolución
        method_label = QLabel("Método")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Gauss-Jordan"])
        self.method_combo.setCurrentIndex(0)
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        method_note = QLabel("Método de resolución")
        method_note.setStyleSheet("font-size: 9pt; color: #9da5b4;")
        grid.addWidget(method_label, 4, 0)
        grid.addWidget(self.method_combo, 4, 1)
        grid.addWidget(method_note, 5, 0, 1, 2)

        # Etiqueta para mostrar la dimensión de la matriz (m × n)
        self.dimension_label = QLabel()
        font_dim = QFont()
        font_dim.setPointSize(9)
        font_dim.setItalic(True)
        self.dimension_label.setFont(font_dim)
        grid.addWidget(self.dimension_label, 6, 0, 1, 2)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        self.solve_button = QPushButton("Resolver")
        self.solve_button.clicked.connect(self._on_solve_clicked)
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.example_button = QPushButton("Ejemplo")
        self.example_button.clicked.connect(self._on_example_clicked)
        buttons_layout.addWidget(self.solve_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.example_button)

        layout.addSpacing(2)
        layout.addLayout(buttons_layout)

        return panel

    def _create_result_panel(self) -> QWidget:
        """Construye el panel de resultados y pasos.

        Incluye: título, tabla A|b, separador, estado y un área de
        soluciones dentro de un QScrollArea para evitar crecimiento
        infinito. Los pasos no se renderizan inline; se muestran en
        un diálogo mediante un botón.
        """
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(2)
        panel.setLayout(layout)

        # Título de la tabla
        title = QLabel("Matriz aumentada del sistema")
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        title.setFont(font_title)
        layout.addWidget(title)

        # Tabla de la matriz aumentada [A|b]
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Altura inicial; se recalcula en _update_table_dimensions
        self.table.setFixedHeight(300)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Sección de resultados
        solution_title = QLabel("Resultado")
        font_solution = QFont()
        # Reducir ligeramente el tamaño para ahorrar espacio vertical
        font_solution.setPointSize(13)
        font_solution.setBold(True)
        solution_title.setFont(font_solution)
        layout.addWidget(solution_title)

        self.state_label = QLabel()
        font_state = QFont()
        # Texto más compacto
        font_state.setPointSize(11)
        font_state.setBold(True)
        self.state_label.setFont(font_state)
        layout.addWidget(self.state_label)

        # Etiqueta de consistencia (consistente / inconsistente)
        self.consistency_label = QLabel()
        consistency_font = QFont()
        consistency_font.setPointSize(10)
        self.consistency_label.setFont(consistency_font)
        self.consistency_label.setStyleSheet("color: #cbd7ea;")
        layout.addWidget(self.consistency_label)

        # Etiqueta de columnas pivote (siempre visible tras resolver)
        self.pivots_label = QLabel()
        piv_font = QFont()
        piv_font.setPointSize(10)
        self.pivots_label.setFont(piv_font)
        self.pivots_label.setStyleSheet("color: #cbd7ea; margin-bottom: 2px;")
        layout.addWidget(self.pivots_label)

        # Contenedor vertical para la solución dentro de un área de scroll
        self.solution_widget = QWidget()
        self.solution_container = QVBoxLayout()
        self.solution_container.setContentsMargins(0, 0, 0, 0)
        self.solution_container.setSpacing(2)
        self.solution_widget.setLayout(self.solution_container)

        self.solution_scroll = QScrollArea()
        self.solution_scroll.setWidgetResizable(True)
        self.solution_scroll.setWidget(self.solution_widget)
        # Tamaño cómodo por defecto (más grande)
        self.solution_scroll.setMinimumHeight(400)
        self.solution_scroll.setMaximumHeight(1000)
        self.solution_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.solution_scroll)

        # Botón para ver los pasos en un diálogo
        self.btn_show_steps = QPushButton("Ver pasos Gauss–Jordan")
        self.btn_show_steps.setVisible(False)
        self.btn_show_steps.setCursor(Qt.PointingHandCursor)
        self.btn_show_steps.clicked.connect(self._show_steps_dialog)
        layout.addWidget(self.btn_show_steps)

        # Widgets de pasos (se mantienen ocultos; no se usan inline)
        self.steps_title = QLabel("Pasos Gauss-Jordan")
        self.steps_title.setFont(font_solution)
        layout.addWidget(self.steps_title)

        self.steps_scroll = QScrollArea()
        self.steps_scroll.setWidgetResizable(False)
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_container.setLayout(self.steps_layout)
        self.steps_scroll.setWidget(self.steps_container)
        layout.addWidget(self.steps_scroll)

        self.steps_title.setVisible(False)
        self.steps_scroll.setVisible(False)

        layout.addStretch()
        return panel

    # ------------------------------------------------------------------
    # Navegación y creación de páginas
    # ------------------------------------------------------------------
    def _create_nav_panel(self) -> QWidget:
        """Crea el panel lateral para la navegación entre páginas.

        El panel contiene un título y botones para navegar entre la
        página de cálculo y otras páginas adicionales. Los botones son
        checkables y exclusivos, de forma que resaltan cuál vista está
        activa.
        """
        panel = QFrame()
        panel.setObjectName("navPanel")
        # Anchura por defecto del panel de navegación (estado expandido)
        panel.setFixedWidth(180)
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        panel.setLayout(nav_layout)

        # ------------------------------------------------------------------
        # Barra superior con botón de menú (≡) y título de la aplicación
        # ------------------------------------------------------------------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(0)
        # Botón para contraer/expandir el panel lateral
        self.nav_toggle = QPushButton("≡")
        self.nav_toggle.setObjectName("navToggleButton")
        self.nav_toggle.setCursor(Qt.PointingHandCursor)
        # Ancho fijo para alinear correctamente el título cuando se colapsa
        self.nav_toggle.setFixedWidth(40)
        self.nav_toggle.clicked.connect(self._toggle_nav_panel)
        top_bar.addWidget(self.nav_toggle)
        # Título de la aplicación
        self.nav_title_label = QLabel("Calculadora")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.nav_title_label.setFont(title_font)
        self.nav_title_label.setAlignment(Qt.AlignCenter)
        self.nav_title_label.setStyleSheet("color: #ffffff;")
        top_bar.addWidget(self.nav_title_label)
        # Separador flexible para empujar el título a la izquierda cuando colapsado
        top_bar.addStretch()
        nav_layout.addLayout(top_bar)

        # ------------------------------------------------------------------
        # Botones de navegación (páginas). Son checkables y exclusivos.
        # ------------------------------------------------------------------
        self.btn_calc_page = QPushButton("Resolver")
        self.btn_calc_page.setObjectName("navButton")
        self.btn_calc_page.setCursor(Qt.PointingHandCursor)
        self.btn_calc_page.setCheckable(True)
        self.btn_calc_page.setAutoExclusive(True)
        self.btn_calc_page.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        nav_layout.addWidget(self.btn_calc_page)

        self.btn_home_page = QPushButton("MER")
        self.btn_home_page.setObjectName("navButton")
        self.btn_home_page.setCursor(Qt.PointingHandCursor)
        self.btn_home_page.setCheckable(True)
        self.btn_home_page.setAutoExclusive(True)
        self.btn_home_page.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        nav_layout.addWidget(self.btn_home_page)

        self.btn_vector_props = QPushButton("Propiedades ℝⁿ")
        self.btn_vector_props.setObjectName("navButton")
        self.btn_vector_props.setCursor(Qt.PointingHandCursor)
        self.btn_vector_props.setCheckable(True)
        self.btn_vector_props.setAutoExclusive(True)
        # Mover a la página 2 del stack
        self.btn_vector_props.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        nav_layout.addWidget(self.btn_vector_props)

        self.btn_combination = QPushButton("Combinación")
        self.btn_combination.setObjectName("navButton")
        self.btn_combination.setCursor(Qt.PointingHandCursor)
        self.btn_combination.setCheckable(True)
        self.btn_combination.setAutoExclusive(True)
        self.btn_combination.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        nav_layout.addWidget(self.btn_combination)

        self.btn_matrix_eq = QPushButton("AX = B")
        self.btn_matrix_eq.setObjectName("navButton")
        self.btn_matrix_eq.setCursor(Qt.PointingHandCursor)
        self.btn_matrix_eq.setCheckable(True)
        self.btn_matrix_eq.setAutoExclusive(True)
        self.btn_matrix_eq.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        nav_layout.addWidget(self.btn_matrix_eq)


        # Espaciador final para empujar los botones hacia arriba
        nav_layout.addStretch()
        return panel

    def _create_calculator_page(self) -> QWidget:
        """Compone la página de cálculo con configuración y resultados.

        La página consiste en el panel de configuración a la izquierda y
        un QScrollArea conteniendo el panel de resultados a la derecha.
        Se usan márgenes y espaciados para obtener una distribución
        armoniosa.
        """
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        page.setLayout(layout)

        # Panel de configuración
        self.config_panel = self._create_config_panel()
        layout.addWidget(self.config_panel)

        # Panel de resultados dentro de un área scroll
        result_panel = self._create_result_panel()
        result_scroll = QScrollArea()
        result_scroll.setWidgetResizable(True)
        result_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        result_scroll.setFrameShape(QFrame.NoFrame)
        result_scroll.setWidget(result_panel)
        layout.addWidget(result_scroll, stretch= 3)

        return page

    def _create_home_page(self) -> QWidget:
        """Crea una página vacía con un saludo.

        Esta página sirve de ejemplo para futuras secciones de la
        aplicación. Muestra un mensaje en el centro del panel.
        """
        page = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(40, 40, 40, 40)
        vbox.setSpacing(20)
        page.setLayout(vbox)

        greeting = QLabel("Método Escalonado Reducido (MER)")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        greeting.setFont(font)
        greeting.setAlignment(Qt.AlignCenter)
        greeting.setStyleSheet("color: #ffffff;")
        vbox.addStretch()
        vbox.addWidget(greeting)
        vbox.addStretch()

        return page
    
    def _create_vector_prop_page(self) -> QWidget:
        """Página para operaciones y verificación de propiedades en R^n."""
        page = QWidget()
        layout = QVBoxLayout()
        page.setLayout(layout)

        # Título
        title = QLabel("Propiedades algebraicas de ℝⁿ")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Pequeña explicación del método
        explicacion_label = QLabel(
            "En este apartado puedes explorar las propiedades básicas de los vectores en ℝⁿ:\n"
            " • La suma de vectores (u + v) y la multiplicación por un escalar (α·u).\n"
            " • Se verifican propiedades como la conmutatividad, asociatividad, existencia del cero y del opuesto.\n\n"
            "Nota: El vector w es opcional y se usa en la verificación de la propiedad asociativa:\n"
            "     (u + v) + w = u + (v + w)\n"
        )
        explicacion_label.setWordWrap(True)  # Para que el texto se ajuste a varias líneas
        layout.addWidget(explicacion_label)


        # Instrucciones
        instr = QLabel("Introduce vectores separados por comas o espacios. Ej: (1, 2, 3) o 1 2 3")
        instr.setWordWrap(True)
        layout.addWidget(instr)

        # Inputs: u, v, w (w opcional para asociatividad)
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("u ="))
        self.vector_u_input = QLineEdit()
        self.vector_u_input.setPlaceholderText("Ej: 1, 2, 3")
        input_row.addWidget(self.vector_u_input)

        input_row.addWidget(QLabel("v ="))
        self.vector_v_input = QLineEdit()
        self.vector_v_input.setPlaceholderText("Ej: 4, 5, 6")
        input_row.addWidget(self.vector_v_input)

        input_row.addWidget(QLabel("w (opcional) ="))
        self.vector_w_input = QLineEdit()
        self.vector_w_input.setPlaceholderText("Dejar vacío para usar w=(1,...,1)")
        input_row.addWidget(self.vector_w_input)

        layout.addLayout(input_row)


        # Escalar
        scalar_row = QHBoxLayout()
        scalar_row.addWidget(QLabel("Escalar α:"))
        self.scalar_input = QLineEdit()
        self.scalar_input.setMaximumWidth(120)
        self.scalar_input.setPlaceholderText("Ej: 2")
        scalar_row.addWidget(self.scalar_input)
        scalar_row.addStretch()
        layout.addLayout(scalar_row)

        # Botones de acción
        btn_row = QHBoxLayout()
        btn_sum = QPushButton("u + v")
        btn_scalar = QPushButton("α · u")
        btn_props = QPushButton("Verificar propiedades")
        clear_button = QPushButton("Limpiar")
        btn_row.addWidget(btn_sum)
        btn_row.addWidget(btn_scalar)
        btn_row.addWidget(btn_props)
        btn_row.addWidget(clear_button)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Área de resultados (texto, readonly)
        self.vector_result_output = QTextEdit()
        self.vector_result_output.setReadOnly(True)
        self.vector_result_output.setMinimumHeight(260)
        layout.addWidget(self.vector_result_output)

        # Función para limpiar campos
        def limpiar_campos():
            self.vector_u_input.clear()
            self.vector_v_input.clear()
            self.vector_w_input.clear()
            self.scalar_input.clear()
            self.vector_result_output.clear()

        # Conectar señales
        btn_sum.clicked.connect(self._on_sum_vectors)
        btn_scalar.clicked.connect(self._on_scalar_mult)
        btn_props.clicked.connect(self._on_verify_properties)
        clear_button.clicked.connect(limpiar_campos)


        return page


    # ------------------------------------------------------------------
    # Página: Combinación lineal de vectores
    # ------------------------------------------------------------------
    def _create_combination_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        page.setLayout(layout)

        title = QLabel("Combinación lineal de vectores")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        info = QLabel(
            "Determina si el vector objetivo puede escribirse como una combinación "
            "lineal de los vectores generadores. Se muestra el planteamiento del "
            "sistema y los pasos de Gauss–Jordan utilizados."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Dimensión:"))
        self.combo_dim_spin = QSpinBox()
        self.combo_dim_spin.setRange(1, self.MAX_ROWS)
        self.combo_dim_spin.setValue(3)
        self.combo_dim_spin.valueChanged.connect(self._update_combination_tables)
        config_row.addWidget(self.combo_dim_spin)

        config_row.addSpacing(12)
        config_row.addWidget(QLabel("Número de vectores:"))
        self.combo_vectors_spin = QSpinBox()
        self.combo_vectors_spin.setRange(1, self.MAX_COLS)
        self.combo_vectors_spin.setValue(2)
        self.combo_vectors_spin.valueChanged.connect(self._update_combination_tables)
        config_row.addWidget(self.combo_vectors_spin)

        config_row.addStretch()
        layout.addLayout(config_row)

        tables_row = QHBoxLayout()

        basis_group = QGroupBox("Vectores generadores (columnas)")
        basis_layout = QVBoxLayout()
        self.combo_basis_table = QTableWidget()
        self.combo_basis_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.combo_basis_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.combo_basis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.combo_basis_table.verticalHeader().setVisible(False)
        basis_layout.addWidget(self.combo_basis_table)
        basis_group.setLayout(basis_layout)
        tables_row.addWidget(basis_group, stretch=2)

        target_group = QGroupBox("Vector objetivo b")
        target_layout = QVBoxLayout()
        self.combo_target_table = QTableWidget()
        self.combo_target_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.combo_target_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.combo_target_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.combo_target_table.verticalHeader().setVisible(False)
        target_layout.addWidget(self.combo_target_table)
        target_group.setLayout(target_layout)
        tables_row.addWidget(target_group, stretch=1)

        layout.addLayout(tables_row)

        button_row = QHBoxLayout()
        self.combo_resolve_button = QPushButton("Analizar combinación")
        self.combo_resolve_button.clicked.connect(self._on_combo_resolve)
        button_row.addWidget(self.combo_resolve_button)

        self.combo_steps_button = QPushButton("Ver pasos detallados")
        self.combo_steps_button.setEnabled(False)
        self.combo_steps_button.clicked.connect(self._on_combo_show_steps)
        button_row.addWidget(self.combo_steps_button)

        self.combo_clear_button = QPushButton("Limpiar")
        self.combo_clear_button.clicked.connect(self._on_combo_clear)
        button_row.addWidget(self.combo_clear_button)

        button_row.addStretch()
        layout.addLayout(button_row)

        self.combo_result_output = QTextEdit()
        self.combo_result_output.setReadOnly(True)
        self.combo_result_output.setMinimumHeight(260)
        layout.addWidget(self.combo_result_output)

        self._update_combination_tables()
        return page

    def _update_combination_tables(self) -> None:
        rows = self.combo_dim_spin.value()
        cols = self.combo_vectors_spin.value()

        self.combo_basis_table.blockSignals(True)
        self.combo_basis_table.setRowCount(rows)
        self.combo_basis_table.setColumnCount(cols)
        self.combo_basis_table.setHorizontalHeaderLabels([f"v{j + 1}" for j in range(cols)])
        self.combo_basis_table.blockSignals(False)
        self._ensure_table_defaults(self.combo_basis_table)

        self.combo_target_table.blockSignals(True)
        self.combo_target_table.setRowCount(rows)
        self.combo_target_table.setColumnCount(1)
        self.combo_target_table.setHorizontalHeaderLabels(["b"])
        self.combo_target_table.blockSignals(False)
        self._ensure_table_defaults(self.combo_target_table)

    def _on_combo_resolve(self) -> None:
        self._combo_last_result = None
        try:
            basis_rows = self._table_to_matrix(self.combo_basis_table)
            generadores = self._columns_from_rows(basis_rows)
            target_rows = self._table_to_matrix(self.combo_target_table)
            objetivo = [row[0] for row in target_rows]

            resultado = self.combination_vm.analizar(generadores, objetivo)
            self._combo_last_result = resultado

            lines: List[str] = []
            lines.append("Matriz aumentada [A|b]:")
            lines.extend(self._matrix_lines(resultado.augmented_matrix, indent="  "))
            lines.append("")

            lines.extend(self._format_result_lines(resultado.solver_result, resultado.coefficient_labels))
            lines.append("")
            lines.extend(self._format_steps_lines(resultado.solver_result))

            self.combo_result_output.setPlainText("\n".join(lines))
            self.combo_steps_button.setEnabled(bool(resultado.solver_result.steps))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_combo_clear(self) -> None:
        self._fill_table_with_zero(self.combo_basis_table)
        self._fill_table_with_zero(self.combo_target_table)
        self.combo_result_output.clear()
        self.combo_steps_button.setEnabled(False)
        self._combo_last_result = None

    def _on_combo_show_steps(self) -> None:
        if not self._combo_last_result:
            return
        resultado = self._combo_last_result.solver_result
        if not resultado.steps:
            return
        self._show_steps_dialog(
            steps=resultado.steps,
            pivot_cols=resultado.pivot_cols or [],
            title="Pasos Gauss–Jordan (combinación lineal)",
        )


    # ------------------------------------------------------------------
    # Página: Resolución de AX = B con múltiples columnas
    # ------------------------------------------------------------------
    def _create_matrix_equation_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        page.setLayout(layout)

        title = QLabel("Ecuación matricial AX = B")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        info = QLabel(
            "Introduce la matriz de coeficientes A y la matriz B. El programa "
            "resuelve AX = B columna a columna, indicando si existe solución "
            "única, infinitas o si el sistema es inconsistente."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Filas (m):"))
        self.matrix_eq_rows_spin = QSpinBox()
        self.matrix_eq_rows_spin.setRange(1, self.MAX_ROWS)
        self.matrix_eq_rows_spin.setValue(3)
        self.matrix_eq_rows_spin.valueChanged.connect(self._update_matrix_eq_tables)
        config_row.addWidget(self.matrix_eq_rows_spin)

        config_row.addSpacing(10)
        config_row.addWidget(QLabel("Columnas (n):"))
        self.matrix_eq_cols_spin = QSpinBox()
        self.matrix_eq_cols_spin.setRange(1, self.MAX_COLS)
        self.matrix_eq_cols_spin.setValue(3)
        self.matrix_eq_cols_spin.valueChanged.connect(self._update_matrix_eq_tables)
        config_row.addWidget(self.matrix_eq_cols_spin)

        config_row.addSpacing(10)
        config_row.addWidget(QLabel("Columnas de B:"))
        self.matrix_eq_rhs_spin = QSpinBox()
        self.matrix_eq_rhs_spin.setRange(1, self.MAX_COLS)
        self.matrix_eq_rhs_spin.setValue(1)
        self.matrix_eq_rhs_spin.valueChanged.connect(self._update_matrix_eq_tables)
        config_row.addWidget(self.matrix_eq_rhs_spin)

        config_row.addStretch()
        layout.addLayout(config_row)

        matrices_row = QHBoxLayout()

        A_group = QGroupBox("Matriz A")
        A_layout = QVBoxLayout()
        self.matrix_eq_A_table = QTableWidget()
        self.matrix_eq_A_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.matrix_eq_A_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.matrix_eq_A_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_eq_A_table.verticalHeader().setVisible(False)
        A_layout.addWidget(self.matrix_eq_A_table)
        A_group.setLayout(A_layout)
        matrices_row.addWidget(A_group, stretch=3)

        B_group = QGroupBox("Matriz B")
        B_layout = QVBoxLayout()
        self.matrix_eq_B_table = QTableWidget()
        self.matrix_eq_B_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.matrix_eq_B_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.matrix_eq_B_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matrix_eq_B_table.verticalHeader().setVisible(False)
        B_layout.addWidget(self.matrix_eq_B_table)
        B_group.setLayout(B_layout)
        matrices_row.addWidget(B_group, stretch=2)

        layout.addLayout(matrices_row)

        button_row = QHBoxLayout()
        self.matrix_eq_resolve_button = QPushButton("Resolver AX = B")
        self.matrix_eq_resolve_button.clicked.connect(self._on_matrix_eq_solve)
        button_row.addWidget(self.matrix_eq_resolve_button)

        self.matrix_eq_steps_selector = QComboBox()
        self.matrix_eq_steps_selector.setEnabled(False)
        button_row.addWidget(self.matrix_eq_steps_selector)

        self.matrix_eq_steps_button = QPushButton("Ver pasos columna")
        self.matrix_eq_steps_button.setEnabled(False)
        self.matrix_eq_steps_button.clicked.connect(self._on_matrix_eq_show_steps)
        button_row.addWidget(self.matrix_eq_steps_button)

        self.matrix_eq_clear_button = QPushButton("Limpiar")
        self.matrix_eq_clear_button.clicked.connect(self._on_matrix_eq_clear)
        button_row.addWidget(self.matrix_eq_clear_button)

        button_row.addStretch()
        layout.addLayout(button_row)

        self.matrix_eq_result_output = QTextEdit()
        self.matrix_eq_result_output.setReadOnly(True)
        self.matrix_eq_result_output.setMinimumHeight(260)
        layout.addWidget(self.matrix_eq_result_output)

        self._update_matrix_eq_tables()
        return page

    def _update_matrix_eq_tables(self) -> None:
        rows = self.matrix_eq_rows_spin.value()
        cols = self.matrix_eq_cols_spin.value()
        rhs = self.matrix_eq_rhs_spin.value()

        self.matrix_eq_A_table.blockSignals(True)
        self.matrix_eq_A_table.setRowCount(rows)
        self.matrix_eq_A_table.setColumnCount(cols)
        self.matrix_eq_A_table.setHorizontalHeaderLabels([f"x{j + 1}" for j in range(cols)])
        self.matrix_eq_A_table.blockSignals(False)
        self._ensure_table_defaults(self.matrix_eq_A_table)

        self.matrix_eq_B_table.blockSignals(True)
        self.matrix_eq_B_table.setRowCount(rows)
        self.matrix_eq_B_table.setColumnCount(rhs)
        self.matrix_eq_B_table.setHorizontalHeaderLabels([f"b{j + 1}" for j in range(rhs)])
        self.matrix_eq_B_table.blockSignals(False)
        self._ensure_table_defaults(self.matrix_eq_B_table)

    def _on_matrix_eq_solve(self) -> None:
        self._matrix_eq_last_result = None
        try:
            A_rows = self._table_to_matrix(self.matrix_eq_A_table)
            B_rows = self._table_to_matrix(self.matrix_eq_B_table)
            resultado = self.matrix_eq_vm.resolver(A_rows, B_rows)
            self._matrix_eq_last_result = resultado

            var_labels = [f"x{j + 1}" for j in range(self.matrix_eq_cols_spin.value())]
            lines: List[str] = []
            lines.append("Matriz A ingresada:")
            lines.extend(self._matrix_lines(A_rows, indent="  "))
            lines.append("")
            lines.append("Matriz B ingresada:")
            lines.extend(self._matrix_lines(B_rows, indent="  "))
            lines.append("")
            lines.append(f"Estado global: {self._status_to_text(resultado.status)}")
            lines.append("")

            for column in resultado.columns:
                lines.append(f"Columna {column.label}: {self._status_to_text(column.result.status)}")
                lines.extend(self._format_result_lines(column.result, var_labels, indent="  "))
                lines.extend(self._format_steps_lines(column.result, indent="  "))
                lines.append("")

            self.matrix_eq_result_output.setPlainText("\n".join(lines).strip())
            self._populate_matrix_eq_steps_selector(resultado)
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _on_matrix_eq_clear(self) -> None:
        self._fill_table_with_zero(self.matrix_eq_A_table)
        self._fill_table_with_zero(self.matrix_eq_B_table)
        self.matrix_eq_result_output.clear()
        self.matrix_eq_steps_selector.clear()
        self.matrix_eq_steps_selector.setEnabled(False)
        self.matrix_eq_steps_button.setEnabled(False)
        self._matrix_eq_last_result = None

    def _populate_matrix_eq_steps_selector(self, result: MatrixEquationResultVM) -> None:
        self.matrix_eq_steps_selector.blockSignals(True)
        self.matrix_eq_steps_selector.clear()
        for column in result.columns:
            if column.result.steps:
                self.matrix_eq_steps_selector.addItem(column.label, column.index)
        self.matrix_eq_steps_selector.blockSignals(False)

        has_steps = self.matrix_eq_steps_selector.count() > 0
        self.matrix_eq_steps_selector.setEnabled(has_steps)
        self.matrix_eq_steps_button.setEnabled(has_steps)
        if has_steps:
            self.matrix_eq_steps_selector.setCurrentIndex(0)

    def _on_matrix_eq_show_steps(self) -> None:
        if not self._matrix_eq_last_result:
            return
        current_index = self.matrix_eq_steps_selector.currentIndex()
        if current_index < 0:
            return
        column_index = self.matrix_eq_steps_selector.currentData()
        column = next(
            (col for col in self._matrix_eq_last_result.columns if col.index == column_index),
            None,
        )
        if not column or not column.result.steps:
            return
        title = f"Pasos Gauss–Jordan ({column.label})"
        self._show_steps_dialog(
            steps=column.result.steps,
            pivot_cols=column.result.pivot_cols or [],
            title=title,
        )
    # Aplicación de tema oscuro y estilo
    # ------------------------------------------------------------------
    def _apply_dark_theme(self) -> None:
        """Define la paleta de colores y estilos de la aplicación.

        Se configuran colores oscuros y tonos de acento inspirados en la
        identidad visual de la UAM. Además se incrementa ligeramente el
        tamaño de la fuente por defecto para mejorar la legibilidad.
        """
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

        # Hoja de estilos global
        self.setStyleSheet(
            """
            QWidget {
                font-size: 15pt;
            }
            QLabel {
                color: #e6effb;
            }
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
            QSpinBox, QComboBox {
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
            QPushButton:hover {
                background-color: #407dbc;
            }
            QPushButton:pressed {
                background-color: #2a4475;
            }
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
            /* Estilo del panel de navegación */
            #navPanel {
                background-color: #11284a;
                border-right: 1px solid #2b4168;
            }
            #navButton {
                background-color: transparent;
                border: none;
                color: #e6effb;
                padding: 12px 16px;
                text-align: left;
                font-size: 11pt;
            }
            #navButton:hover {
                background-color: #1c3156;
            }
            #navButton:checked {
                background-color: #365a8e;
            }
            QScrollArea {
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #1c3156;
            }
            """
        )

    # ------------------------------------------------------------------
    # Manejadores de eventos
    # ------------------------------------------------------------------
    def _on_dimensions_changed(self) -> None:
        """Actualiza las dimensiones cuando el usuario cambia filas/columnas.

        Modifica las variables internas del view model, actualiza la
        tabla para reflejar la nueva dimensión y actualiza la etiqueta
        que indica la forma de la matriz.
        """
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        self.view_model.rows = m
        self.view_model.cols = n
        self._update_table_dimensions()
        self.dimension_label.setText(f"Matriz {m}×{n} (A|b)")

    def _on_method_changed(self) -> None:
        """Actualiza el método seleccionado en el view model."""
        method_text = self.method_combo.currentText()
        self.view_model.method = method_text

    def _on_solve_clicked(self) -> None:
        """Convierte la tabla en una matriz y calcula la solución.

        Lee los valores de la tabla, construye la matriz aumentada y
        utiliza el view model para resolver el sistema. Si se produce un
        error (por ejemplo, valor no numérico), se muestra un mensaje
        al usuario.
        """
        try:
            augmented = []
            for i in range(self.table.rowCount()):
                row_values: List[float] = []
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    value_str = item.text() if item else "0"
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
        """Limpia la tabla y la zona de resultados."""
        self._reset_table_to_zero()
        self.state_label.clear()
        self._clear_solution_display()
        self._clear_steps_display()

    def _on_example_clicked(self) -> None:
        """Rellena la matriz con un ejemplo de valores pequeños.

        Genera una matriz sencilla que permite verificar manualmente la
        salida del sistema. Utiliza patrones como una identidad y un
        vector de 1..m como término independiente.
        """
        m = self.rows_spin.value()
        n = self.cols_spin.value()
        for i in range(m):
            for j in range(n):
                value = 1.0 if i == j else float((i + j) % 5 + 1)
                item = QTableWidgetItem(f"{value}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            b_value = float(i + 1)
            b_item = QTableWidgetItem(f"{b_value}")
            b_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, n, b_item)
    
    def _format_vector(self, v: List[float]) -> str:
        # formatea bonito: (1, 2, 3)
        return "(" + ", ".join([f"{x:.6g}" for x in v]) + ")"

    def _status_to_text(self, status: str) -> str:
        mapping = {
            "UNICA": "Solución única",
            "INFINITAS": "Infinitas soluciones",
            "INCONSISTENTE": "Sistema inconsistente",
        }
        return mapping.get(status, status)

    def _matrix_lines(self, matrix: List[List[float]], indent: str = "") -> List[str]:
        if not matrix:
            return [f"{indent}—"]
        return [
            f"{indent}[{', '.join(f'{value:.6g}' for value in row)}]"
            for row in matrix
        ]

    def _table_to_matrix(self, table: QTableWidget) -> List[List[float]]:
        data: List[List[float]] = []
        for i in range(table.rowCount()):
            row_vals: List[float] = []
            for j in range(table.columnCount()):
                item = table.item(i, j)
                text = item.text().strip() if item and item.text() else "0"
                try:
                    row_vals.append(float(text))
                except ValueError as exc:
                    raise ValueError(
                        f"Valor no numérico en fila {i + 1}, columna {j + 1}: '{text}'"
                    ) from exc
            data.append(row_vals)
        return data

    def _columns_from_rows(self, rows: List[List[float]]) -> List[List[float]]:
        if not rows:
            return []
        num_cols = len(rows[0])
        for fila in rows:
            if len(fila) != num_cols:
                raise ValueError("Todas las filas deben tener la misma longitud.")
        return [[rows[i][j] for i in range(len(rows))] for j in range(num_cols)]

    def _format_result_lines(
        self,
        result: ResultVM,
        variable_labels: List[str],
        indent: str = "",
    ) -> List[str]:
        lines = [f"{indent}Estado: {self._status_to_text(result.status)}"]

        if result.status == "UNICA" and result.solution is not None:
            lines.append(f"{indent}Solución:")
            for label, value in zip(variable_labels, result.solution):
                lines.append(f"{indent}  {label} = {value:.6g}")
        elif result.status == "INFINITAS" and result.parametric is not None:
            lines.append(f"{indent}Solución particular:")
            for label, value in zip(variable_labels, result.parametric.particular):
                lines.append(f"{indent}  {label} = {value:.6g}")
            if result.parametric.direcciones:
                lines.append(f"{indent}Direcciones asociadas:")
                for idx, direction in enumerate(result.parametric.direcciones, start=1):
                    direction_str = ", ".join(f"{value:.6g}" for value in direction)
                    lines.append(f"{indent}  t{idx}: ({direction_str})")
        elif result.status == "INCONSISTENTE":
            lines.append(f"{indent}No existe solución compatible con B.")

        pivote_labels = ", ".join(
            variable_labels[idx] for idx in (result.pivot_cols or [])
        ) or "—"
        libre_labels = ", ".join(
            variable_labels[idx] for idx in (result.free_vars or [])
        ) or "—"
        lines.append(f"{indent}Columnas pivote: {pivote_labels}")
        lines.append(f"{indent}Variables libres: {libre_labels}")
        return lines

    def _format_steps_lines(self, result: ResultVM, indent: str = "") -> List[str]:
        if not result.steps:
            return [f"{indent}No se registraron pasos."]
        lines = [f"{indent}Pasos Gauss–Jordan:"]
        for step in result.steps:
            lines.append(f"{indent}  [{step.number}] {step.description}")
            if step.after_matrix:
                lines.extend(self._matrix_lines(step.after_matrix, indent + "    "))
        return lines

    def _ensure_table_defaults(self, table: QTableWidget) -> None:
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    table.setItem(i, j, item)
                if item.text().strip() == "":
                    item.setText("0")
                item.setTextAlignment(Qt.AlignCenter)

    def _fill_table_with_zero(self, table: QTableWidget) -> None:
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if item is None:
                    item = QTableWidgetItem("0")
                    table.setItem(i, j, item)
                else:
                    item.setText("0")
                item.setTextAlignment(Qt.AlignCenter)
    
    def _on_sum_vectors(self) -> None:
        try:
            u = self.vector_vm.parse_vector(self.vector_u_input.text())
            v = self.vector_vm.parse_vector(self.vector_v_input.text())
            res_vm = self.vector_vm.sum_vectors(u, v)
            out = []
            out.append(f"Resultado: u + v = {self._format_vector(res_vm.result)}")
            out.append("")
            out.append("Pasos:")
            out.extend(res_vm.steps)
            self.vector_result_output.setPlainText("\n".join(out))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
    
    def _on_scalar_mult(self) -> None:
        try:
            u = self.vector_vm.parse_vector(self.vector_u_input.text())
            alpha_str = self.scalar_input.text().strip()
            if alpha_str == "":
                raise ValueError("Introduce un valor para el escalar α.")
            alpha = float(alpha_str)
            res_vm = self.vector_vm.scalar_mult(alpha, u)
            out = [f"Resultado: {alpha} · u = {self._format_vector(res_vm.result)}", "", "Pasos:"]
            out.extend(res_vm.steps)
            self.vector_result_output.setPlainText("\n".join(out))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
    
    def _on_verify_properties(self) -> None:
        try:
            u = self.vector_vm.parse_vector(self.vector_u_input.text())
            v = self.vector_vm.parse_vector(self.vector_v_input.text())
            w_text = self.vector_w_input.text().strip()
            w = None
            if w_text != "":
                w = self.vector_vm.parse_vector(w_text)
            results = self.vector_vm.verify_properties(u, v, w)
            out = []
            for name, ok, steps in results:
                out.append(f"{name}: {'Cumple' if ok else 'No cumple'}")
                for s in steps:
                    out.append("  " + s)
                out.append("")  # línea en blanco entre propiedades
            self.vector_result_output.setPlainText("\n".join(out))
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    # ------------------------------------------------------------------
    # Métodos auxiliares para actualizar la interfaz
    # ------------------------------------------------------------------
    def _update_table_dimensions(self) -> None:
        """Ajusta filas y columnas de la tabla según `rows` y `cols`.

        La tabla tendrá `m` filas y `n + 1` columnas; las cabeceras se
        etiquetan como x1..xn y b. Las celdas nuevas se rellenan con
        "0" por defecto y se ajusta la altura total para acomodar más
        ecuaciones.
        """
        m = self.view_model.rows
        n = self.view_model.cols
        current_rows = self.table.rowCount()
        current_cols = self.table.columnCount()
        if current_rows != m:
            self.table.setRowCount(m)
        if current_cols != n + 1:
            self.table.setColumnCount(n + 1)
            headers = [f"x{j + 1}" for j in range(n)] + ["b"]
            self.table.setHorizontalHeaderLabels(headers)

        # Ajuste de la altura de la tabla (más alta)
        row_height = 34
        header_height = 34
        desired = min(600, row_height * m + header_height)
        self.table.setFixedHeight(desired)
        # Altura de filas por defecto para mejor legibilidad
        self.table.verticalHeader().setDefaultSectionSize(row_height)

        # Redimensión de columnas según número de variables
        h_header = self.table.horizontalHeader()
        if n <= 6:
            h_header.setSectionResizeMode(QHeaderView.Stretch)
        else:
            h_header.setSectionResizeMode(QHeaderView.Interactive)

        # Encabezados verticales
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Rellenar celdas vacías con 0
        for i in range(m):
            for j in range(n + 1):
                if not self.table.item(i, j):
                    item = QTableWidgetItem("0")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

    def _reset_table_to_zero(self) -> None:
        """Establece todas las celdas de la matriz a 0."""
        self._fill_table_with_zero(self.table)

    def _clear_solution_display(self) -> None:
        """Elimina los widgets de la zona de soluciones."""
        while self.solution_container.count():
            child = self.solution_container.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

    def _clear_steps_display(self) -> None:
        """
        Elimina los widgets de la zona de pasos y oculta tanto
        el contenedor de pasos como el botón para ver los pasos.

        Esta rutina se invoca siempre que se va a mostrar un nuevo
        resultado. Además de limpiar el layout se restablece la
        visibilidad de los elementos a su estado por defecto: se
        ocultan el título y el área de scroll de pasos, y el botón
        para ver pasos se desactiva.
        """
        # Vaciar cualquier widget existente en el layout
        while self.steps_layout.count():
            child = self.steps_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        # Ocultar el título y el área de scroll de pasos
        self.steps_title.setVisible(False)
        self.steps_scroll.setVisible(False)
        # Ocultar el botón de ver pasos, se mostrará según convenga
        self.btn_show_steps.setVisible(False)
        # Reiniciar el almacén de pasos
        self._last_steps = None

    def _update_result_display(self, result: ResultVM) -> None:
        """Actualiza las áreas de solución y pasos según el resultado.

        Dependiendo del estado del resultado, se muestran los valores
        calculados (en caso de solución única), la forma particular y
        direcciones (en caso de infinitas soluciones) o un mensaje de
        inconsistencia. Luego se renderizan los pasos en un layout
        vertical.
        """
        # Limpiar zonas previas
        self._clear_solution_display()
        self._clear_steps_display()

        # Mostrar el estado del sistema
        if result.status == "UNICA":
            self.state_label.setText("Solución única")
        elif result.status == "INFINITAS":
            self.state_label.setText("Infinitas soluciones")
        else:
            self.state_label.setText("Sistema inconsistente")

        # Mostrar la solución según el tipo de sistema
        if result.status == "UNICA" and result.solution is not None:
            # Listar los valores de cada variable
            for idx, value in enumerate(result.solution, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 12pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
        elif result.status == "INFINITAS" and result.parametric is not None:
            # Mostrar solución particular y direcciones asociadas a variables libres
            p = result.parametric
            particular_title = QLabel("Solución particular:")
            particular_title.setStyleSheet("font-size: 12pt; font-weight: bold;")
            self.solution_container.addWidget(particular_title)
            for idx, value in enumerate(p.particular, start=1):
                var_label = QLabel(f"x{idx} = {value:.6g}")
                var_label.setStyleSheet("font-size: 11pt; color: #a3c2e3;")
                self.solution_container.addWidget(var_label)
        else:
            # Sistema inconsistente o sin solución particular conocida
            inc_label = QLabel("No existe solución.")
            inc_label.setStyleSheet("font-size: 11pt; color: #e06c75;")
            self.solution_container.addWidget(inc_label)

        # Ajustar dinámicamente la altura de la zona de soluciones según
        # el número de elementos añadidos. Esto previene grandes espacios
        # en blanco cuando la solución es corta y evita un tamaño infinito
        # cuando hay muchas direcciones o variables. Cada elemento ocupa
        # aproximadamente 22 píxeles de alto; se suma un margen extra.
        item_count = self.solution_container.count()
        if item_count:
            estimated = 22 * item_count + 60
            target = max(320, min(900, estimated))
            self.solution_scroll.setMaximumHeight(target)
        else:
            self.solution_scroll.setMaximumHeight(320)

        # Guardar pivotes y variables libres del resultado
        self._last_pivot_cols = (result.pivot_cols or []) if hasattr(result, "pivot_cols") else []
        self._last_free_vars = (result.free_vars or []) if hasattr(result, "free_vars") else []

        # Mostrar consistencia independientemente del número de soluciones
        is_consistent = result.status in ("UNICA", "INFINITAS")
        self.consistency_label.setText("Sistema: Consistente" if is_consistent else "Sistema: Inconsistente")

        # Mostrar lista de columnas pivote
        piv_text = ", ".join([f"x{j+1}" for j in (self._last_pivot_cols or [])]) or "—"
        self.pivots_label.setText(f"Columnas pivote: {piv_text}")

        # Mostrar los pasos de Gauss–Jordan. En esta versión nunca se
        # renderizan los pasos directamente en la página principal; se
        # almacenan y se habilita un botón para verlos en una ventana
        # independiente. Así se evita que el panel de resultados crezca
        # indefinidamente y se mantiene una interfaz limpia.
        if result.steps:
            # Almacenar los pasos para poder visualizarlos en el diálogo
            self._last_steps = result.steps
            # Mostrar el botón de ver pasos
            self.btn_show_steps.setVisible(True)
            # Ocultar cualquier lista de pasos en la página (no se usa)
            self.steps_title.setVisible(False)
            self.steps_scroll.setVisible(False)
        else:
            # No hay pasos: se oculta el botón y se limpian referencias
            self._last_steps = None
            self.btn_show_steps.setVisible(False)
            self.steps_title.setVisible(False)
            self.steps_scroll.setVisible(False)

    def _create_step_widget(self, step: StepVM) -> QWidget:
        """Crea un widget que representa un paso de Gauss–Jordan."""
        # Construir título con columna/posición de pivote cuando esté disponible
        pr = getattr(step, "pivot_row", None)
        pc = getattr(step, "pivot_col", None)
        pivot_txt = ""
        if pr is not None and pc is not None:
            pivot_txt = f"  |  pivote x{pc+1} en ({pr+1},{pc+1})"
        widget = QGroupBox(f"Paso {step.number} – {step.description}{pivot_txt}")
        # Texto del título en blanco para mejorar contraste
        widget.setStyleSheet("QGroupBox { color: #ffffff; }")
        layout = QVBoxLayout()
        widget.setLayout(layout)
        matrix = step.after_matrix
        if not matrix:
            return widget
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        table = QTableWidget(rows, cols)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table.setFixedHeight(20 * rows + 2)
        # Colores para resaltar
        pivot_bg = QColor(64, 125, 188)   # azul acento
        free_bg = QColor(58, 47, 107)     # violeta tenue
        white_fg = QColor(255, 255, 255)

        # Ya definidos arriba: pr, pc
        # No resaltar variables libres en la tabla de pasos
        free_cols: List[int] = []
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(f"{matrix[i][j]:.6g}")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(white_fg)
                # Resaltar celda pivote si aplica
                if pr is not None and pc is not None and i == pr and j == pc:
                    item.setBackground(pivot_bg)
                    item.setForeground(white_fg)
                table.setItem(i, j, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        return widget

    # ------------------------------------------------------------------
    # Visualización de pasos en ventana emergente
    # ------------------------------------------------------------------
    def _show_steps_dialog(
        self,
        steps: List[StepVM] | None = None,
        pivot_cols: List[int] | None = None,
        title: str = "Pasos Gauss–Jordan",
    ) -> None:
        """
        Muestra una ventana modal con todos los pasos del algoritmo.

        Este método se invoca cuando el número de pasos supera
        `MAX_DISPLAY_STEPS`. Utiliza `_last_steps` para recuperar la
        lista completa de pasos y crea un `QDialog` con su propio
        `QScrollArea` para que el usuario pueda revisar cada paso.
        """
        steps_to_show = steps if steps is not None else self._last_steps
        if not steps_to_show:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(700, 500)
        vbox = QVBoxLayout(dialog)
        # Encabezado mostrando solo las columnas pivote
        piv = pivot_cols if pivot_cols is not None else (self._last_pivot_cols or [])
        def _fmt_vars(indices: List[int]) -> str:
            return ", ".join([f"x{idx+1}" for idx in indices]) if indices else "—"
        header = QLabel(f"Columnas pivote: {_fmt_vars(piv)}")
        header.setStyleSheet("color: #ffffff; font-weight: bold; margin-bottom: 6px;")
        vbox.addWidget(header)
        # Contenedor de pasos dentro de un área de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        # Crear widgets de paso
        for step in steps_to_show:
            w = self._create_step_widget(step)
            container_layout.addWidget(w)
        container_layout.addStretch()
        scroll.setWidget(container)
        vbox.addWidget(scroll)
        dialog.setLayout(vbox)
        # Ejecutar el diálogo de manera modal
        dialog.exec()

    # ------------------------------------------------------------------
    # Controlador para contraer/expandir el panel de navegación
    # ------------------------------------------------------------------
    def _toggle_nav_panel(self) -> None:
        """Alterna el estado del panel lateral entre expandido y colapsado.

        Este método modifica la anchura del panel de navegación y muestra u
        oculta las etiquetas asociadas. Cuando está colapsado, los
        botones de navegación muestran solo un espacio en blanco (o se
        podrían reemplazar por iconos en el futuro). Cuando está
        expandido, se restablecen los textos completos.
        """
        if self._nav_expanded:
            # Colapsar: reducir anchura y ocultar textos
            self.nav_panel.setFixedWidth(60)
            self.nav_title_label.setVisible(False)
            # Guardar los textos originales por si se necesitan más adelante
            self.btn_calc_page.setText("")
            self.btn_home_page.setText("")
            self.btn_vector_props.setText("")
            self.btn_combination.setText("")
            self.btn_matrix_eq.setText("")
            self._nav_expanded = False
        else:
            # Expandir: restaurar anchura y mostrar textos
            self.nav_panel.setFixedWidth(180)
            self.nav_title_label.setVisible(True)
            self.btn_calc_page.setText("Resolver")
            self.btn_home_page.setText("MER")
            self.btn_vector_props.setText("Propiedades ℝⁿ")
            self.btn_combination.setText("Combinación")
            self.btn_matrix_eq.setText("AX = B")
            self._nav_expanded = True


def main() -> None:
    """Punto de entrada para ejecutar la aplicación de resolución de matrices."""
    app = QApplication(sys.argv)
    window = MatrixCalculatorWindow()
    window.vector_vm = VectorPropiedadesViewModel()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
