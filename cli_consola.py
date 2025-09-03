# cli_consola.py
# Consola interactiva para resolver A x = b con Gauss-Jordan (sobre [A|b])
# Enfoque: el usuario SIEMPRE ingresa el sistema. Útil para probar Models (Matriz/Fábrica/Errores).

from __future__ import annotations
from typing import List, Optional

# Imports del proyecto (ejecutar desde la raíz del repo)
from Models.matriz import Matriz
from Models.fabrica_matriz import FabricaMatriz  # por si quieres generar identidad/ceros en la sesión
from Models.Errores.errores import  ErrorAlgebraLineal
from Operadores.sistema_lineal import SistemaLineal
from Operadores.Solucion.solucion_gauss_jordan import SolucionadorGaussJordan
from Operadores.estrategia_pivoteo import PivoteoParcial


# ----------------------- Helpers de entrada -----------------------

def pedir_entero(msg: str, minimo: int = 1) -> int:
    while True:
        s = input(msg).strip()
        if s.lower() in {"q", "salir"}:
            raise KeyboardInterrupt
        try:
            v = int(s)
            if v < minimo:
                print(f"  • Debe ser un entero >= {minimo}.")
                continue
            return v
        except ValueError:
            print("  • Ingresa un número entero válido (o 'q' para salir).")

def parsear_fila(msg: str, n: int) -> List[float]:
    while True:
        s = input(msg).strip()
        if s.lower() in {"q", "salir"}:
            raise KeyboardInterrupt
        # admite espacios y/o comas
        s = s.replace(",", " ")
        partes = [p for p in s.split() if p]
        if len(partes) != n:
            print(f"  • Debes ingresar exactamente {n} números.")
            continue
        try:
            return [float(p) for p in partes]
        except ValueError:
            print("  • Hay valores no numéricos. Intenta de nuevo.")

def pedir_si_no(msg: str, por_defecto: bool = False) -> bool:
    suf = " [S/n]" if por_defecto else " [s/N]"
    while True:
        s = input(msg + suf + ": ").strip().lower()
        if s in {"", "s", "si", "sí"}:
            return True if s != "" else por_defecto
        if s in {"n", "no"}:
            return False
        print("  • Responde 's' o 'n' (o Enter para el valor por defecto).")

def pedir_nombres_variables(n: int) -> Optional[List[str]]:
    if not pedir_si_no("¿Quieres nombrar las variables (x1..xn por defecto)?", por_defecto=False):
        return [f"x{i+1}" for i in range(n)]
    nombres: List[str] = []
    print("Introduce los nombres (un solo token por nombre, p. ej. x, y, z):")
    for j in range(n):
        while True:
            nom = input(f"  Nombre de la variable {j+1}: ").strip()
            if not nom:
                print("    • El nombre no puede estar vacío.")
                continue
            if any(c.isspace() for c in nom):
                print("    • Evita espacios en el nombre.")
                continue
            nombres.append(nom)
            break
    return nombres


# ----------------------- I/O de solución -----------------------

def mostrar_solucion(nombres: List[str], solucion, mostrar_pasos: bool) -> None:
    print("\n=== Resultado ===")
    print(f"Estado: {solucion.estado}")

    if solucion.estado == "UNICA":
        xs = solucion.x or []
        for nom, val in zip(nombres, xs):
            print(f"  {nom} = {val:.6g}")

    elif solucion.estado == "INFINITAS":
        print(f"Columnas pivote: {solucion.columnas_pivote}")
        print(f"Variables libres: {solucion.variables_libres}")
        p = solucion.parametrica
        if p:
            print("Solución particular:")
            for nom, val in zip(nombres, p.particular):
                print(f"  {nom} = {val:.6g}")
            print("Direcciones (una por variable libre, con parámetros t1, t2, ...):")
            for k, dirv in enumerate(p.direcciones, start=1):
                term = " + ".join(
                    f"{coef:.6g}·{nom}"
                    for nom, coef in zip(nombres, dirv) if abs(coef) > 1e-12
                ) or "0"
                print(f"  t{k}: {term}")

    else:  # INCONSISTENTE
        print("No existe solución (aparece una fila [0 ... 0 | c] con c ≠ 0 en RREF).")

    if mostrar_pasos and solucion.historial:
        print("\n-- Pasos Gauss-Jordan --")
        for paso in solucion.historial.pasos:
            print(f"[{paso.numero:03d}] {paso.operacion:>18} | pivote=({paso.pivote_fila},{paso.pivote_col}) "
                  f"| factor={'' if paso.factor is None else f'{paso.factor:.6g}'} "
                  f"| filas={paso.filas_afectadas} | {paso.descripcion}")


# ----------------------- Bucle principal -----------------------

def main():
    print("=== Calculadora de Sistemas Lineales (Gauss-Jordan) ===")
    print("   Ingresa 'q' en cualquier momento para salir.\n")

    while True:
        try:
            m = pedir_entero("Número de ecuaciones (m): ", minimo=1)
            n = pedir_entero("Número de variables (n): ", minimo=1)
            nombres = pedir_nombres_variables(n)

            print("\nIntroduce la matriz A (m filas, cada una con n números):")
            A_datos: List[List[float]] = []
            for i in range(m):
                A_datos.append(parsear_fila(f"  Fila {i+1} ({n} números): ", n))

            print("\nIntroduce el vector b (m números):")
            b_datos = parsear_fila("  b: ", m)

            # --- Aquí probamos que funcionen los MODELS ---
            # Construcción/validación de Matriz
            A = Matriz(A_datos)

            # Construcción del sistema (A, b)
            sis = SistemaLineal(A, b_datos, nombres_variables=nombres)

            # Preferencias de ejecución
            mostrar_pasos = pedir_si_no("¿Deseas registrar y mostrar los pasos de Gauss-Jordan?", por_defecto=False)

            # Resolver (Gauss-Jordan sobre [A|b])
            solver = SolucionadorGaussJordan(pivoteo=PivoteoParcial())
            solucion = solver.resolver(sis, registrar_pasos=mostrar_pasos)

            # Mostrar resultado
            mostrar_solucion(nombres, solucion, mostrar_pasos)

            print("\n--------------------------------------------\n")
            if not pedir_si_no("¿Resolver otro sistema?", por_defecto=True):
                break

        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except ErrorAlgebraLineal as e:
            # Cualquier excepción del dominio Models cae aquí (validaciones, índices, etc.)
            print(f"\n[ERROR de dominio] {e}\n  Vuelve a intentarlo.\n")
        except Exception as e:
            print(f"\n[ERROR inesperado] {e}\n")
            break


if __name__ == "__main__":
    main()

