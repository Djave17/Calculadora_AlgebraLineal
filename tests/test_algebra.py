import unittest
from fractions import Fraction

from Operadores.solvers import classify_solution, solve_AX_B, solve_Ax_b
from Operadores.vectores import check_neutro, check_conmutativa, Vector
from ViewModels.linear_algebra_vm import LinearAlgebraViewModel


class TestSolvers(unittest.TestCase):
    def test_unique_solution(self):
        A = [[1, 2], [3, 4]]
        b = [5, 11]
        solucion = solve_Ax_b(A, b, registrar=False)
        self.assertEqual(classify_solution(solucion), "UNICA")
        self.assertEqual(solucion.x, [Fraction(1), Fraction(2)])

    def test_inconsistent_system(self):
        A = [[1, 1], [2, 2]]
        b = [3, 8]
        solucion = solve_Ax_b(A, b, registrar=False)
        self.assertEqual(classify_solution(solucion), "INCONSISTENTE")

    def test_infinite_solutions(self):
        A = [[1, 2, 0], [0, 0, 1]]
        b = [3, 1]
        solucion = solve_Ax_b(A, b, registrar=False)
        self.assertEqual(classify_solution(solucion), "INFINITAS")
        self.assertEqual(solucion.parametrica.particular, [Fraction(3), Fraction(0), Fraction(1)])
        self.assertEqual(solucion.parametrica.libres, [1])
        self.assertEqual(solucion.parametrica.direcciones[0], [Fraction(-2), Fraction(1), Fraction(0)])

    def test_solve_AX_B_multiple_columns(self):
        A = [[1, 0], [0, 1]]
        B = [[1, 2], [3, 4]]
        soluciones = solve_AX_B(A, B, registrar=False)
        estados = [classify_solution(sol) for _, sol in soluciones]
        self.assertEqual(estados, ["UNICA", "UNICA"])
        self.assertEqual(soluciones[0][1].x, [Fraction(1), Fraction(3)])
        self.assertEqual(soluciones[1][1].x, [Fraction(2), Fraction(4)])


class TestVectores(unittest.TestCase):
    def test_propiedades_vectoriales(self):
        u = Vector.from_iter([1, 2])
        v = Vector.from_iter([3, 4])
        neutro, _ = check_neutro(u)
        conmutativa, _ = check_conmutativa(u, v)
        self.assertTrue(neutro)
        self.assertTrue(conmutativa)

    def test_propiedades_con_vector_cero(self):
        u = Vector.from_iter([0, 0, 0])
        neutro, _ = check_neutro(u)
        self.assertTrue(neutro)


class TestViewModel(unittest.TestCase):
    def test_null_space_matches_parametric(self):
        vm = LinearAlgebraViewModel()
        entrada = {
            "vectores": "1, 0, 0; 1, 0, 0; 0, 1, 0",
            "objetivo": "1, 0, 0",
        }
        resultado = vm.combinacion_lineal(entrada)
        self.assertEqual(resultado["estado"], "INFINITAS")
        direcciones = resultado.get("direcciones")
        nucleo = resultado.get("nucleo")
        self.assertIsNotNone(direcciones)
        self.assertIsNotNone(nucleo)
        self.assertEqual(len(direcciones), len(nucleo))
        self.assertEqual(direcciones[0], nucleo[0])


if __name__ == "__main__":
    unittest.main()
