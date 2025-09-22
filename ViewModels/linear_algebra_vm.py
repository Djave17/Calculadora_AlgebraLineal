from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Sequence

from Models.matriz import Matriz
from Operadores import vectores
from Operadores.solvers import classify_solution, null_space_from_rref, solve_Ax_b, solve_AX_B
from Operadores.matrices import construir_matriz_aumentada, to_fraction_matrix
from Operadores.SolucionGaussJordan.solucion import Solucion


@dataclass
class StepText:
    encabezado: str
    matriz: str


class LinearAlgebraViewModel:
    """Coordina operaciones siguiendo la teoría de Grossman (2019) y Lay (2012).

    - Combinación lineal: definición A·c = b con columnas de A iguales a los
      vectores generadores (Grossman §2.1, Lay §1.4).
    - Clasificación de soluciones de sistemas lineales acorde a rangos y RREF
      (Lay §2.3, Poole §1.5).
    - Uso de `Fraction` para aritmética exacta, recomendado por Chapra & Canale
      (2015) para evitar errores de redondeo.
    """

    # ---------------- Propiedades en R^n ----------------
    def propiedades_Rn(self, entrada: Dict[str, str]) -> Dict[str, object]:
        u = vectores.parse_vector(entrada.get("u", ""))
        v = vectores.parse_vector(entrada.get("v", ""))
        w_texto = entrada.get("w")
        w = vectores.parse_vector(w_texto) if w_texto else vectores.Vector.from_iter([1] * u.dim)

        alpha_texto = entrada.get("alpha")
        alpha = Fraction(alpha_texto) if alpha_texto not in (None, "") else None

        suma = u + v
        suma_pasos = [
            f"u = {list(u.componentes)}",
            f"v = {list(v.componentes)}",
            f"u + v = {list(suma.componentes)}",
        ]

        escalar_resultado = None
        if alpha is not None:
            producto = u.scale(alpha)
            escalar_resultado = {
                "alpha": str(alpha),
                "resultado": [str(c) for c in producto.componentes],
                "pasos": [
                    f"α = {alpha}",
                    f"α · u = {list(producto.componentes)}",
                ],
            }

        propiedades = []
        verificaciones = [
            ("Conmutativa", lambda: vectores.check_conmutativa(u, v)),
            ("Asociativa", lambda: vectores.check_asociativa(u, v, w)),
            ("Vector neutro", lambda: vectores.check_neutro(u)),
            ("Vector opuesto", lambda: vectores.check_inverso(u)),
        ]
        for nombre, funcion in verificaciones:
            cumple, pasos = funcion()
            propiedades.append({
                "propiedad": nombre,
                "cumple": cumple,
                "pasos": pasos,
            })

        return {
            "suma": {
                "resultado": [str(c) for c in suma.componentes],
                "pasos": suma_pasos,
            },
            "producto_escalar": escalar_resultado,
            "propiedades": propiedades,
        }

    # ---------------- Combinación lineal ----------------
    def combinacion_lineal(self, entrada: Dict[str, str]) -> Dict[str, object]:
        vectores_generadores = vectores.parse_vector_set(entrada.get("vectores", ""))
        objetivo = vectores.parse_vector(entrada.get("objetivo", ""))
        matriz_A = self._vectores_a_filas(vectores_generadores)
        matriz_aug = construir_matriz_aumentada(matriz_A, [[c] for c in objetivo.componentes])

        solucion = solve_Ax_b(matriz_A, objetivo.componentes)
        return self._formatear_respuesta_lineal(
            solucion,
            matriz_aug,
            matriz_A,
            list(objetivo.componentes),
        )

    # ---------------- Ecuación vectorial ----------------
    def ecuacion_vectorial(self, entrada: Dict[str, str]) -> Dict[str, object]:
        # Misma lógica que combinacion_lineal; se diferencia solo en la redacción.
        resultado = self.combinacion_lineal(entrada)
        resultado["tipo"] = "Ecuación vectorial"
        return resultado

    # ---------------- Ecuación matricial ----------------
    def ecuacion_matricial(self, entrada: Dict[str, object]) -> Dict[str, object]:
        A_rows = to_fraction_matrix(entrada.get("A", []))
        B_rows = to_fraction_matrix(entrada.get("B", []))
        soluciones = solve_AX_B(A_rows, B_rows)
        detalles: List[Dict[str, object]] = []
        for idx, solucion in soluciones:
            # reconstruir matriz aumentada para la columna correspondiente
            columna = [[fila[idx]] for fila in B_rows]
            matriz_aug = construir_matriz_aumentada(A_rows, columna)
            data = self._formatear_respuesta_lineal(
                solucion,
                matriz_aug,
                A_rows,
                [fila[idx] for fila in B_rows],
            )
            data["columna"] = idx
            detalles.append(data)

        estado_global = "UNICA"
        for detalle in detalles:
            if detalle["estado"] == "INCONSISTENTE":
                estado_global = "INCONSISTENTE"
                break
            if detalle["estado"] == "INFINITAS":
                estado_global = "INFINITAS"
        return {
            "estado": estado_global,
            "columnas": detalles,
        }

    # ---------------- Helpers ----------------
    def _vectores_a_filas(self, vectores_generadores: Sequence[vectores.Vector]) -> List[List[Fraction]]:
        dimension = vectores_generadores[0].dim
        columnas = len(vectores_generadores)
        filas: List[List[Fraction]] = []
        for i in range(dimension):
            filas.append([vectores_generadores[j].componentes[i] for j in range(columnas)])
        return filas

    def _formatear_respuesta_lineal(
        self,
        solucion: Solucion,
        matriz_aug: Matriz,
        A_rows: Sequence[Sequence[Fraction]] | None = None,
        b_vector: Sequence[Fraction] | None = None,
    ) -> Dict[str, object]:
        estado = classify_solution(solucion)
        pasos_historial = solucion.historial.pasos if solucion.historial else []
        respuesta: Dict[str, object] = {
            "estado": estado,
            "matriz_aumentada": self._formatear_matriz(matriz_aug.como_lista()),
            "pasos": self._renderizar_historial(pasos_historial),
        }

        if estado == "UNICA" and solucion.x is not None:
            respuesta["solucion"] = [str(Fraction(val)) for val in solucion.x]
        elif estado == "INFINITAS" and solucion.parametrica is not None:
            respuesta["solucion_particular"] = [str(Fraction(x)) for x in solucion.parametrica.particular]
            respuesta["direcciones"] = [
                [str(Fraction(comp)) for comp in direccion]
                for direccion in solucion.parametrica.direcciones
            ]
            respuesta["variables_libres"] = solucion.parametrica.libres
        else:
            respuesta["mensaje"] = "El sistema es inconsistente."

        if estado in {"UNICA", "INFINITAS"} and A_rows is not None and b_vector is not None:
            verificacion = self._verificar_producto(A_rows, solucion, b_vector)
            respuesta["verificacion"] = verificacion

        if pasos_historial:
            ultima = pasos_historial[-1].despues
            if ultima is not None:
                rref = Matriz(ultima)
                pivot_cols = solucion.columnas_pivote or []
                num_vars = rref.columnas - 1 if rref.columnas > 0 else 0
                if num_vars > 0:
                    nucleo = null_space_from_rref(rref, pivot_cols, num_vars)
                    respuesta["nucleo"] = [
                        [str(component) for component in vector]
                        for vector in nucleo
                    ]
        return respuesta

    def _formatear_matriz(self, datos: Sequence[Sequence[Fraction]]) -> List[str]:
        return [
            "[" + ", ".join(str(elem) for elem in fila) + "]"
            for fila in datos
        ]

    def _renderizar_historial(self, pasos) -> List[str]:
        lineas: List[str] = []
        for paso in pasos:
            descripcion = f"[{paso.numero:02d}] {paso.operacion} - {paso.descripcion}"
            lineas.append(descripcion)
            if paso.despues:
                lineas.extend("    " + fila for fila in self._formatear_matriz(paso.despues))
        return lineas

    def _verificar_producto(
        self,
        A_rows: Sequence[Sequence[Fraction]],
        solucion: Solucion,
        b_vector: Sequence[Fraction],
    ) -> Dict[str, object]:
        resultado: Dict[str, object] = {}
        if solucion.estado == "UNICA" and solucion.x is not None:
            calculado = self._multiplicar(A_rows, solucion.x)
            resultado["b_calculado"] = [str(Fraction(x)) for x in calculado]
            resultado["b_objetivo"] = [str(Fraction(x)) for x in b_vector]
            resultado["coincide"] = calculado == list(b_vector)
        elif solucion.estado == "INFINITAS" and solucion.parametrica is not None:
            particular = solucion.parametrica.particular
            calculado = self._multiplicar(A_rows, particular)
            resultado["b_calculado"] = [str(Fraction(x)) for x in calculado]
            resultado["b_objetivo"] = [str(Fraction(x)) for x in b_vector]
            resultado["coincide"] = calculado == list(b_vector)
        return resultado

    def _multiplicar(
        self,
        A_rows: Sequence[Sequence[Fraction]],
        coeficientes: Sequence[Fraction],
    ) -> List[Fraction]:
        return [
            sum(Fraction(fila[j]) * Fraction(coeficientes[j]) for j in range(len(coeficientes)))
            for fila in A_rows
        ]
