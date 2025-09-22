### Calculadora de Álgebra Lineal (GUI/CLI)

Herramienta desarrollada para los ejercicios de la UAM siguiendo:

- Grossman, S. & Flores Godoy, J. (2019). *Álgebra lineal* (8.ª ed.).
- Lay, D. C. (2012). *Álgebra lineal y sus aplicaciones* (4.ª ed.).
- Chapra, S. C. & Canale, R. P. (2015). *Métodos numéricos para ingenieros* (7.ª ed.).
- Poole, D. (2011). *Álgebra lineal: Introducción moderna* (3.ª ed.).

#### Funcionalidades

1. **Propiedades en ℝⁿ** (Lay §1.2).
2. **Combinación lineal / ecuación vectorial** (`A·c = b`, Grossman §2.1, Lay §1.4).
3. **Ecuaciones matriciales AX = B** (Lay §2.3, Poole §1.5).

El algoritmo Gauss–Jordan registra cada operación (intercambio, normalización, eliminación) y todas las operaciones usan `fractions.Fraction` (Chapra & Canale).

#### Ejecución GUI

```
python UI/main.py
```

- Selecciona la sección en el panel izquierdo.
- Introduce vectores/matrices; la bitácora aparece en la parte derecha.
- En AX=B puedes definir filas de `A` y `B`; si difieren se muestra un mensaje.

#### Ejecución CLI

```
python cli_consola.py
```

- Menú con cuatro opciones.
- Entradas separadas por comas o espacios.
- Se muestra clasificación, solución (única/paramétrica/inconsistente) y bitácora de pasos.

#### Pruebas

```
python -m unittest
```

Incluye casos inspirados en Lay §1.7 y Grossman §2.1.
