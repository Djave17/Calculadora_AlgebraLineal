"""CLI interactiva para la calculadora de Álgebra Lineal."""

from __future__ import annotations

from fractions import Fraction
from typing import List

from Models.Errores.errores import ErrorAlgebraLineal
from ViewModels.linear_algebra_vm import LinearAlgebraViewModel

SALIR = {"q", "salir", "exit"}


def pedir_entero(mensaje: str, minimo: int = 1) -> int:
    while True:
        valor = input(mensaje).strip().lower()
        if valor in SALIR:
            raise KeyboardInterrupt
        try:
            numero = int(valor)
            if numero < minimo:
                print(f"  • Debe ser un entero mayor o igual que {minimo}.")
                continue
            return numero
        except ValueError:
            print("  • Entrada inválida. Introduce un entero.")


def pedir_vector_etiqueta(etiqueta: str) -> str:
    valor = input(f"  {etiqueta}: ").strip()
    if valor.lower() in SALIR:
        raise KeyboardInterrupt
    if not valor:
        raise ValueError("El vector no puede estar vacío.")
    return valor


def pedir_vectores(numero: int) -> str:
    vectores = []
    for idx in range(1, numero + 1):
        texto = pedir_vector_etiqueta(f"Vector v{idx}")
        vectores.append(texto)
    return ";".join(vectores)


def pedir_fila(n: int, etiqueta: str) -> List[Fraction]:
    while True:
        texto = input(f"  {etiqueta}: ").strip()
        if texto.lower() in SALIR:
            raise KeyboardInterrupt
        tokens = [tok for tok in texto.replace(",", " ").split() if tok]
        if len(tokens) != n:
            print(f"  • Debes proporcionar exactamente {n} números.")
            continue
        try:
            return [Fraction(tok) for tok in tokens]
        except ValueError:
            print("  • Se detectó un valor inválido. Intenta de nuevo.")


def mostrar_lista(lineas: List[str], sangria: str = "  ") -> None:
    for linea in lineas:
        print(f"{sangria}{linea}")


def opcion_propiedades(vm: LinearAlgebraViewModel) -> None:
    print("\n--- Propiedades en ℝⁿ ---")
    try:
        u = pedir_vector_etiqueta("Vector u")
        v = pedir_vector_etiqueta("Vector v")
        w = input("  Vector w (opcional, Enter para utilizar (1,...,1)): ").strip()
        alpha = input("  Escalar α (opcional): ").strip()
        resultado = vm.propiedades_Rn({"u": u, "v": v, "w": w, "alpha": alpha})
        print("\nResultado de u + v:")
        mostrar_lista(resultado["suma"]["pasos"])
        print(f"  Resultado final: {resultado['suma']['resultado']}")
        if resultado.get("producto_escalar"):
            print("\nMultiplicación por escalar:")
            mostrar_lista(resultado["producto_escalar"]["pasos"])
        print("\nVerificación de propiedades:")
        for prop in resultado["propiedades"]:
            estado = "Cumple" if prop["cumple"] else "No cumple"
            print(f"  - {prop['propiedad']}: {estado}")
            mostrar_lista(prop["pasos"], sangria="    ")
    except Exception as exc:
        print(f"  [Error] {exc}")


def opcion_combinacion(vm: LinearAlgebraViewModel) -> None:
    print("\n--- Combinación lineal ---")
    try:
        cantidad = pedir_entero("Número de vectores generadores: ", minimo=1)
        vectores_texto = pedir_vectores(cantidad)
        objetivo = pedir_vector_etiqueta("Vector objetivo b")
        resultado = vm.combinacion_lineal({"vectores": vectores_texto, "objetivo": objetivo})
        imprimir_solucion_lineal(resultado)
    except Exception as exc:
        print(f"  [Error] {exc}")


def opcion_vectorial(vm: LinearAlgebraViewModel) -> None:
    print("\n--- Ecuación vectorial ---")
    try:
        cantidad = pedir_entero("Número de vectores vᵢ: ", minimo=1)
        vectores_texto = pedir_vectores(cantidad)
        objetivo = pedir_vector_etiqueta("Vector b")
        resultado = vm.ecuacion_vectorial({"vectores": vectores_texto, "objetivo": objetivo})
        imprimir_solucion_lineal(resultado)
    except Exception as exc:
        print(f"  [Error] {exc}")


def opcion_matricial(vm: LinearAlgebraViewModel) -> None:
    print("\n--- Ecuación matricial AX = B ---")
    try:
        filas = pedir_entero("Número de filas de A: ", minimo=1)
        columnas = pedir_entero("Número de columnas de A: ", minimo=1)
        columnas_b = pedir_entero("Número de columnas de B: ", minimo=1)

        print("Ingresa la matriz A (componentes separados por espacio o coma):")
        A_rows = [pedir_fila(columnas, f"Fila {i+1}") for i in range(filas)]

        print("Ingresa la matriz B:")
        B_rows = [pedir_fila(columnas_b, f"Fila {i+1}") for i in range(filas)]

        resultado = vm.ecuacion_matricial({"A": A_rows, "B": B_rows})
        print(f"\nEstado global: {resultado['estado']}")
        for columna in resultado["columnas"]:
            print(f"\n>>> Columna b{columna['columna'] + 1}")
            imprimir_solucion_lineal(columna)
    except Exception as exc:
        print(f"  [Error] {exc}")


def imprimir_solucion_lineal(resultado: dict) -> None:
    print(f"  Estado: {resultado['estado']}")
    print("  Matriz aumentada [A|b]:")
    mostrar_lista(resultado["matriz_aumentada"], sangria="    ")
    if "solucion" in resultado:
        print(f"  Solución única: {resultado['solucion']}")
    if "solucion_particular" in resultado:
        print(f"  Solución particular: {resultado['solucion_particular']}")
    if "direcciones" in resultado:
        print("  Direcciones del núcleo:")
        for direccion in resultado["direcciones"]:
            print(f"    {direccion}")
    if "nucleo" in resultado and resultado["nucleo"]:
        print("  Núcleo calculado a partir de la RREF:")
        for vector in resultado["nucleo"]:
            print(f"    {vector}")
    if "mensaje" in resultado:
        print(f"  {resultado['mensaje']}")
    if resultado.get("pasos"):
        print("  Pasos Gauss-Jordan:")
        mostrar_lista(resultado["pasos"], sangria="    ")


def main() -> None:
    vm = LinearAlgebraViewModel()
    print("=== Calculadora de Álgebra Lineal ===")
    print("(Escribe 'q' para salir en cualquier momento)\n")

    menu = {
        "1": ("Propiedades en ℝⁿ", opcion_propiedades),
        "2": ("Combinación lineal", opcion_combinacion),
        "3": ("Ecuación vectorial", opcion_vectorial),
        "4": ("Ecuación matricial AX = B", opcion_matricial),
    }

    try:
        while True:
            print("Menú principal:")
            for clave, (descripcion, _) in menu.items():
                print(f"  {clave}. {descripcion}")
            print("  0. Salir")

            eleccion = input("Selecciona una opción: ").strip()
            if eleccion.lower() in SALIR or eleccion == "0":
                print("Hasta luego.")
                break
            if eleccion not in menu:
                print("Opción no válida. Intenta nuevamente.\n")
                continue
            _, funcion = menu[eleccion]
            funcion(vm)
            print("\n---------------------------------------------\n")
    except KeyboardInterrupt:
        print("\nSaliendo...")
    except ErrorAlgebraLineal as exc:
        print(f"Error de álgebra lineal: {exc}")


if __name__ == "__main__":
    main()
