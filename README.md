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

#### Guía paso a paso

1. **Propiedades en ℝⁿ**
   - Introduce los vectores `u`, `v` y opcionalmente `w` (Lay §1.2).
   - Presiona “u + v” o “α · u” para ver la operación elemental.
   - Usa “Verificar propiedades” para confirmar conmutativa, asociativa, neutro y opuesto.
   - La salida indica si cada propiedad se cumple y muestra los cálculos intermedios.

2. **Combinación lineal / Ecuación vectorial**
   - Captura los vectores generadores `v₁,…,vₖ` como columnas y el vector objetivo `b`.
   - Se construye la matriz `A = [v₁ … vₖ]` y se resuelve `A·c = b` (Grossman §2.1).
   - Resultado: clasificación (única, infinitas, inconsistente), solución particular y base del núcleo si aplica.
   - La sección “Bitácora” detalla cada operación elemental del método de Gauss–Jordan.

3. **Ecuación matricial AX = B**
   - Define filas y columnas de `A` y `B`; cada columna de `B` se resuelve como un sistema independiente (Lay §2.3).
   - Guarda la bitácora de pasos por columna y la clasificación de cada sistema.

#### Preguntas frecuentes

- **¿Qué representa la bitácora de pasos?**<br>
  Cada entrada responde a una operación elemental del método Gauss–Jordan (Lay §2.2). El formato `[nn] OPERACIÓN – descripción` indica el número de paso, el tipo (intercambio, normalización, eliminación) y la matriz resultante.

- **¿Por qué se usa `Fraction` en lugar de floats?**<br>
  Para evitar errores de redondeo y asegurar resultados exactos, siguiendo las recomendaciones numéricas de Chapra & Canale (2015).

- **¿Cómo detecta la calculadora infinitas soluciones?**<br>
  Se revisa el rango de `A` y la presencia de variables libres según el RREF (Lay §2.3, Poole §1.5). Se muestra una solución particular y un conjunto de direcciones del núcleo.

- **¿Qué ocurre si la matriz B no tiene la misma cantidad de filas que A?**<br>
  La GUI y el CLI muestran un mensaje claro y no intentan resolver el sistema; la condición `m_A = m_B` es necesaria para que `AX = B` tenga sentido (Grossman §2.1).

- **¿Dónde encuentro ejemplos de referencia?**<br>
  Revisa Lay §1.4–1.7 y Grossman §2.1 para ver problemas de combinación lineal; Poole §1.5 explica la interpretación geométrica de soluciones infinitas.

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
