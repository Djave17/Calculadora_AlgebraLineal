UI (Flet)

Rol en la arquitectura (MVVM)
- Capa de presentación basada en Flet. Consume ViewModels y muestra datos y pasos de forma interactiva.

Archivos y vistas principales
- main.py: Punto de entrada. Configura tema y crea MainShell.
- styles.py: Paleta y estilos globales.
- methods.py: Catálogo de módulos; define categorías, IDs y tipos de vista.
- views/main_shell.py: Orquesta el layout (menú izquierdo, centro, panel derecho) y eventos (resolver, limpiar, pasos).
- views/components/matrix_editor.py: Editor de [A|b] con botón “Ver pasos Gauss–Jordan”.
- views/components/matrix_equation_view.py: AX=B por columnas, cada una con acceso a pasos.
- views/components/vector_properties_view.py: Propiedades en ℝⁿ.
- views/components/matrix_ops_view.py: Operaciones con matrices (A±B, αA, AB, traspuestas) con pasos.
- views/components/steps_dialog.py: Diálogo modal para mostrar la bitácora de pasos (Gauss–Jordan).

Nota sobre UI/pyside_views
- Se conserva una versión previa (PySide6) como referencia histórica. La UI activa es Flet.

