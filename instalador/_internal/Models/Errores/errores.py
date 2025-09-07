# Models/Errores/errores.py

class ErrorAlgebraLineal(Exception):
    """Base de errores del dominio de Álgebra Lineal (capa Models)."""
    pass

# ---- Errores de estructura/dimensiones (Models) ----
class MatrizVaciaError(ErrorAlgebraLineal): pass
class MatrizNoRectangularError(ErrorAlgebraLineal): pass
class DimensionInvalidaError(ErrorAlgebraLineal): pass
class IndiceFueraDeRangoError(ErrorAlgebraLineal): pass
class LongitudFilaIncompatibleError(ErrorAlgebraLineal): pass

# ---- Errores operacionales (apoyo a Operadores) ----
class PivoteNumericamenteCeroError(ErrorAlgebraLineal): pass
class MatrizSingularError(ErrorAlgebraLineal): pass
class SistemaInconsistenteError(ErrorAlgebraLineal): pass
