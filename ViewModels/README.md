ViewModels (Fachada de dominio para la UI)

Rol en la arquitectura (MVVM)
- Orquesta llamadas a Operadores, conserva dimensiones/estado y empaqueta resultados para la UI Flet.
- No renderiza controles; sólo prepara datos (texto, pasos, interpretaciones) para las vistas.

Componentes
- resolucion_matriz_vm.py: Facade para resolver [A|b] y AX=B con Gauss–Jordan. Expone ResultVM, StepVM, etc.
  - interpret_result(): Resume resultados en lenguaje natural (combinación, dependencia, caso general).
- combinacion_lineal_vm.py: Plantea A·c=b a partir de vectores generadores y objetivo, retorna interpretación.
- linear_algebra_vm.py: Propiedades en ℝⁿ (suma, producto escalar, axiomas) apoyándose en Operadores.vectores.
- vector_propiedades_vm.py: Pequeño VM para vistas de propiedades; su parseo delega a Operadores.vectores.
- matrix_ops_vm.py: Operaciones elementales con matrices (A±B, αA, AB, A^T) con pasos detallados.

Flujo de pasos (Gauss–Jordan)
1) Operadores registran cada operación elemental.
2) resolucion_matriz_vm convierte a StepVM (with before/after, pivote, etc.).
3) La vista invoca show_steps_dialog para mostrarlos.

