import z3

class SymbolicComplex(object):
    real: z3.Real
    im: z3.Real
    N1: z3.Real = z3.Real("sc_n1")
    local_counter: int = 0

    def __init__(self, real: float, im: float):
        self.real = z3.Real(real)
        self.im = z3.Real(im)

    def conjugate(self):
        return SymbolicComplex(self.real, SymbolicComplex.N1*self.im)

    def __add__(self, other):
        assert(type(other) == SymbolicComplex)
        return SymbolicComplex(self.real + other.real, self.im + other.im)

    def __eq__(self, other):
        assert(type(other) == SymbolicComplex)
        return z3.And(self.real == other.real, self.im == other.im)

    def __mul__(self, other):
        assert(type(other) == SymbolicComplex)
        return SymbolicComplex(other.real * self.real - other.im * self.im, other.im * self.real + other.real * self.im)

    def squared_norm(self) -> z3.Real:
        conj = self.conjugate()
        return self.__mul__(conj).real

