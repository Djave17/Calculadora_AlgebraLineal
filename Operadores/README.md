Operadores (Dominio algebraico)

Rol en la arquitectura (MVVM)
- Implementa los algoritmos de álgebra lineal y utilidades numéricas. Es la “lógica de negocio”.
- No conoce nada de la interfaz (Flet); expone funciones y clases puras.

Algoritmos clave
- Gauss–Jordan con pivoteo parcial: Solucionador principal que lleva [A|b] a RREF.
  - reductor_escalonado.py: Reducción a RREF, registra INTERCAMBIO, NORMALIZAR_PIVOTE y ELIMINAR arriba/abajo.
  - estrategia_pivoteo.py: Selección de pivote (PivoteoParcial).
  - registrador.py: Bitácora de pasos (PasoReduccion, HistorialReduccion).
  - SolucionGaussJordan/: Construcción de la solución (única/paramétrica/inconsistente).
- solvers.py: Facades solve_Ax_b y solve_AX_B para uso desde ViewModels y CLI; extracción de núcleo desde RREF.
- matrices.py: Conversión a Fraction, construcción de [A|B] y utilidades de rango.
- vectores.py: Tipo Vector y verificaciones/operaciones básicas en ℝⁿ (con parseo robusto).

Cómo se encadena
1) La UI recolecta valores y los convierte a Fraction (UI/helpers.parse_matrix).
2) ViewModels llaman a Operadores (p. ej., solve_Ax_b) para resolver/analizar.
3) El historial de pasos se devuelve y la UI lo presenta (dialog de pasos).

Ubicaciones
- a_forma_escalonada_reducida: Operadores/reductor_escalonado.py
- Solucionador principal: Operadores/SolucionGaussJordan/solucion_gauss_jordan.py
- Bitácora: Operadores/registrador.py
- Vectores de ℝⁿ: Operadores/vectores.py

