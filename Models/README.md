Modelos (Models)

Rol en la arquitectura (MVVM)
- Define estructuras de datos básicas como Matriz (representación con Fraction) y tipos de error.
- No contiene lógica de IU ni dependencias de Flet; sirve a Operadores (capa de dominio).

Archivos relevantes
- matriz.py: Implementa la matriz con métodos utilitarios (obtener, asignar, clonar, como_lista).
- fabrica_matriz.py: Construcción auxiliar de matrices.
- Errores/: Tipos y manejador de errores de la capa de dominio.

Algoritmos y decisiones
- Todas las entradas numéricas se guardan como fractions.Fraction para exactitud aritmética.

Puntos de entrada desde otras capas
- Usada por Operadores.reductor_escalonado y solucionadores para manipular las matrices durante Gauss–Jordan.

