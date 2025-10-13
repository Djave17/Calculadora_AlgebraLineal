Componentes UI (Flet)

Descripción breve
- LeftMethodsMenu: Menú de selección de módulos (métodos) con estado activo.
- MatrixEditor: Tabla de la matriz aumentada [A|b], muestra diagnóstico y botón “Ver pasos”.
- MatrixEquationView: Editor y resultado para AX=B (por columnas); integra visor de pasos por columna.
- MatrixOpsView: Vista para operaciones de matrices con pasos y validaciones.
- VectorPropertiesView: Entrada de u, v, w y α; muestra operaciones y verificación de axiomas.
- RightConfigPanel: Parámetros del solucionador (filas/columnas) y acciones Resolver/Limpiar.
- steps_dialog.py: Construye el dialog de pasos (lista de StepVM con matrices resaltando pivote).

Algoritmos mostrados
- Gauss–Jordan: pasos provienen de ViewModels.resolucion_matriz_vm (convertidos desde la capa Operadores).
- Operaciones matriciales: pasos se calculan en ViewModels/matrix_ops_vm.py (suma/resta/escala/producto/traspuesta).

