## Calculadora de Álgebra Lineal

Aplicación GUI/CLI diseñada para cursos de álgebra lineal (UAM). Toda la aritmética se realiza con `fractions.Fraction` para mantener exactitud; el solucionador de Gauss–Jordan registra cada paso elemental (intercambio, normalización y eliminación).

### Referencias principales
- Grossman & Flores Godoy, *Álgebra lineal* (8.ª ed.).
- Lay, *Álgebra lineal y sus aplicaciones* (4.ª ed.).
- Chapra & Canale, *Métodos numéricos para ingenieros* (7.ª ed.).
- Poole, *Álgebra lineal: Introducción moderna* (3.ª ed.).

---

### Módulos disponibles en la GUI

| Módulo | Qué permite |
| --- | --- |
| **Gauss–Jordan** | Resolver sistemas lineales y ver cada paso Gauss–Jordan con pivoteo parcial. |
| **Identidades de matrices** | Vista unificada para AX = B, combinación lineal y sistema homogéneo A·c = 0 (seleccionable dentro de la misma pantalla). |
| **Propiedades en ℝⁿ** | Suma, producto por escalar y verificación de axiomas básicos (conmutativa, asociativa, neutro, opuesto). |
| **Operaciones de matrices** | Suma, resta, α·A, producto A·B y traspuestas (A^T, B^T) con pasos detallados. |
| **Matriz traspuesta** | Cálculo de A^T mostrando el intercambio de filas por columnas y verificación de propiedades. |
| **MER – notas** | Material de apoyo y recordatorios teóricos. |
| **Notación (Prog 8)** | Tarjetas para descomponer números en base 10 y base 2, mostrando cada potencia y suma final. |
| **Errores (Prog 8)** | Conceptos ilustrados, ejemplos de punto flotante y laboratorio para error absoluto/relativo y propagación. |

### Métodos numéricos

- Ingresa f(x) con `^` para potencias; se aceptan constantes `pi`, `e` y `euler` (ej.: `pi^2`, `euler^(x)`).
- Funciones trigonométricas disponibles: `sen/sin`, `cos`, `tan`, `cotan` y variantes (`cot`, `cotg`, `ctg`), además de `log`, `sqrt`, `exp`, etc.
- Válido tanto para métodos abiertos (Newton-Raphson, Secante) como cerrados (Bisección, Regla Falsa).

---

### Documentación por carpetas

- [Models](Models/README.md) – Entidades base (`Matriz`, manejadores de errores).
- [Operadores](Operadores/README.md) – Algoritmos de dominio (Gauss–Jordan, vectores, utilidades matriciales).
- [ViewModels](ViewModels/README.md) – Adaptadores entre dominio y UI (ResultVM, interpretaciones, combinación, ops de matrices).
- [UI](UI/README.md) – Estructura general de la interfaz en Flet.
  - [UI/views/components](UI/views/components/README.md) – Componentes visuales reutilizables (editor, diálogo de pasos, paneles).
  - [UI/pyside_views](UI/pyside_views/README.md) – Implementación histórica en PySide6.
- [tests](tests/README.md) – Suite de pruebas unitarias.

---

### Cómo ejecutar la interfaz gráfica

```bash
python UI/main.py
```
```Venv
python3 -m UI.main.py
```

1. Selecciona el módulo en el panel izquierdo.
2. Ajusta dimensiones y parámetros desde el panel derecho.
3. Introduce datos (vectores o matrices); usa **Resolver** para ver resultados y **Ver pasos** cuando estén disponibles.

### Modo CLI

```bash
python cli_consola.py
```

El CLI guía por menús para resolver sistemas, combinación lineal y propiedades vectoriales. Los resultados incluyen clasificación (única, infinitas, inconsistente) y la bitácora Gauss–Jordan donde aplica.

---

### Preguntas frecuentes

- **Bitácora de pasos**: Cada entrada corresponde a una operación elemental Gauss–Jordan, siguiendo la notación `[nn] OPERACIÓN – descripción`.  
- **¿Por qué usar `Fraction`?** Evita errores de redondeo y mantiene exactitud simbólica (recomendación de Chapra & Canale).  
- **Detección de infinitas soluciones**: Se revisa el rango de la matriz y las variables libres en la RREF (Lay §2.3, Poole §1.5).  
- **Matriz no conforme**: Si A y B no son compatibles, la UI/CLI muestra un mensaje y no intenta resolver.

---

### Ejecutar pruebas

```bash
python -m unittest
```

Incluye casos inspirados en Lay §1.7 y Grossman §2.1 (solución única, infinitas, inconsistente, combinación lineal, etc.).
