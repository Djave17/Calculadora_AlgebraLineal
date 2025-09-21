from __future__ import annotations
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QLineEdit, QMessageBox
)

from UI.ViewModels.vector_vm import VectorCalculatorViewModel, VectorResultVM


class VectorCalculatorPage(QWidget):
    MIN_DIMENSION = 1
    MAX_DIMENSION = 5

    def __init__(self) -> None:
        super().__init__()
        self.view_model = VectorCalculatorViewModel()
        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(16)

        # Panel de configuración y entrada de vectores
        config_panel = QGroupBox("Configuración y Entrada de Vectores")
        layout = QVBoxLayout()
        config_panel.setLayout(layout)

        # Dimensión
        dim_label = QLabel("Dimensión")
        self.dim_spin = QSpinBox()
        self.dim_spin.setMinimum(self.MIN_DIMENSION)
        self.dim_spin.setMaximum(self.MAX_DIMENSION)
        self.dim_spin.setValue(self.view_model.dimension)
        self.dim_spin.valueChanged.connect(self._on_dimension_changed)
        layout.addWidget(dim_label)
        layout.addWidget(self.dim_spin)

        # Vector 1
        layout.addWidget(QLabel("Vector 1:"))
        self.vector1_table = QTableWidget(1, self.view_model.dimension)
        self.vector1_table.setHorizontalHeaderLabels([f"v{i+1}" for i in range(self.view_model.dimension)])
        self.vector1_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vector1_table)

        # Vector 2
        layout.addWidget(QLabel("Vector 2 (para operaciones binarias):"))
        self.vector2_table = QTableWidget(1, self.view_model.dimension)
        self.vector2_table.setHorizontalHeaderLabels([f"v{i+1}" for i in range(self.view_model.dimension)])
        self.vector2_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vector2_table)

        # Escalar
        layout.addWidget(QLabel("Escalar (para multiplicación):"))
        self.scalar_input = QLineEdit("1.0")
        layout.addWidget(self.scalar_input)

        # Parámetro t para ecuación vectorial
        layout.addWidget(QLabel("Parámetro t (para ecuación vectorial):"))
        self.param_t_input = QLineEdit("0.0")
        layout.addWidget(self.param_t_input)

        # Matriz para multiplicación matriz-vector
        layout.addWidget(QLabel("Matriz para multiplicación matriz-vector:"))
        self.matriz_table = QTableWidget(self.view_model.dimension, self.view_model.dimension)
        self.matriz_table.setHorizontalHeaderLabels([f"c{i+1}" for i in range(self.view_model.dimension)])
        self.matriz_table.setVerticalHeaderLabels([f"f{i+1}" for i in range(self.view_model.dimension)])
        self.matriz_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matriz_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.matriz_table)

        # Botones de operación
        btn_layout = QGridLayout()
        self.btn_sumar = QPushButton("V1 + V2")
        self.btn_sumar.clicked.connect(lambda: self._on_operation_clicked("sumar"))
        btn_layout.addWidget(self.btn_sumar, 0, 0)

        self.btn_restar = QPushButton("V1 - V2")
        self.btn_restar.clicked.connect(lambda: self._on_operation_clicked("restar"))
        btn_layout.addWidget(self.btn_restar, 0, 1)

        self.btn_prod_escalar = QPushButton("V1 · V2")
        self.btn_prod_escalar.clicked.connect(lambda: self._on_operation_clicked("producto_escalar"))
        btn_layout.addWidget(self.btn_prod_escalar, 1, 0)

        self.btn_mult_escalar = QPushButton("V1 * Escalar")
        self.btn_mult_escalar.clicked.connect(lambda: self._on_operation_clicked("multiplicar_por_escalar"))
        btn_layout.addWidget(self.btn_mult_escalar, 1, 1)

        self.btn_prod_vectorial = QPushButton("V1 x V2 (3D)")
        self.btn_prod_vectorial.clicked.connect(lambda: self._on_operation_clicked("producto_vectorial"))
        btn_layout.addWidget(self.btn_prod_vectorial, 2, 0)

        self.btn_norma = QPushButton("||V1||")
        self.btn_norma.clicked.connect(lambda: self._on_operation_clicked("norma"))
        btn_layout.addWidget(self.btn_norma, 2, 1)

        self.btn_ecuacion_vectorial = QPushButton("Evaluar Ecuación Vectorial")
        self.btn_ecuacion_vectorial.clicked.connect(lambda: self._on_operation_clicked("ecuacion_vectorial"))
        btn_layout.addWidget(self.btn_ecuacion_vectorial, 3, 0)

        self.btn_matriz_vector = QPushButton("Multiplicar Matriz por Vector")
        self.btn_matriz_vector.clicked.connect(lambda: self._on_operation_clicked("multiplicar_matriz_vector"))
        btn_layout.addWidget(self.btn_matriz_vector, 3, 1)

        layout.addLayout(btn_layout)

        main_layout.addWidget(config_panel)

        # Panel de resultados
        result_panel = QGroupBox("Resultado de la Operación")
        result_layout = QVBoxLayout()
        result_panel.setLayout(result_layout)

        self.operation_label = QLabel("Operación: Ninguna")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.operation_label.setFont(font)
        result_layout.addWidget(self.operation_label)

        self.result_label = QLabel("Resultado:")
        self.result_label.setFont(QFont("", 11))
        result_layout.addWidget(self.result_label)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e06c75;")
        result_layout.addWidget(self.error_label)

        main_layout.addWidget(result_panel, stretch=1)

        self._on_dimension_changed()  # Inicializar tablas

    def _on_dimension_changed(self) -> None:
        dim = self.dim_spin.value()
        self.view_model.dimension = dim

        # Actualizar tablas de vectores
        for table in [self.vector1_table, self.vector2_table]:
            table.setColumnCount(dim)
            table.setHorizontalHeader
            table.setHorizontalHeaderLabels([f"v{i+1}" for i in range(dim)])