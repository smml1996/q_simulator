import z3
from static_solver import StaticSolver


class SymbolicComplex(object):
    real: z3.Real
    im: z3.Real
    local_counter: int = 0

    @staticmethod
    def to_complex(a):
        if isinstance(a, SymbolicComplex):
            return a
        elif isinstance(a, complex):
            SymbolicComplex.local_counter += 1
            return SymbolicComplex(f"const_{SymbolicComplex.local_counter}", a.real, a.imag)
        else:
            SymbolicComplex.local_counter += 1
            return SymbolicComplex(f"const_{SymbolicComplex.local_counter}", a, 0)

    def __init__(self, name: str, real: float = None, im: float = None):
        self.real = z3.Real("r_" + name)
        self.im = z3.Real("im_" + name)
        if real is not None:
            StaticSolver.solver.add(self.real == real)
            assert(im is not None)
            StaticSolver.solver.add(self.im == im)
        else:
            assert(im is None)


    def conjugate(self):
        name = f"conj_{SymbolicComplex.local_counter}"
        SymbolicComplex.local_counter += 1
        return SymbolicComplex(name, self.real, -1*self.im)

    def __add__(self, other):
        other = SymbolicComplex.to_complex(other)
        name = f"add_{SymbolicComplex.local_counter}"
        SymbolicComplex.local_counter += 1
        return SymbolicComplex(name,self.real + other.real, self.im + other.im)

    def __eq__(self, other):
        other =  SymbolicComplex.to_complex(other)
        return z3.And(self.real == other.real, self.im == other.im)

    def __mul__(self, other):
        other = SymbolicComplex.to_complex(other)
        name = f"mul_{SymbolicComplex.local_counter}"
        SymbolicComplex.local_counter +=1
        answer = SymbolicComplex(name, other.real * self.real - other.im * self.im, other.im * self.real + other.real * self.im)
        return answer

    def __sub__(self, other):
        other = SymbolicComplex.to_complex(other)
        name = f"sub_{SymbolicComplex.local_counter}"
        SymbolicComplex.local_counter += 1
        return SymbolicComplex(name, self.real - other.real, self.im - other.im)

    def inv(self):
        den = self.real * self.real + self.im * self.im
        name = f"inv_{SymbolicComplex.local_counter}"
        SymbolicComplex.local_counter += 1
        return SymbolicComplex(name, self.real / den, -self.im / den)

    def __truediv__(self, other):
        other = SymbolicComplex.to_complex(other)
        inv_other = other.inv()
        return self.__mul__(inv_other)

    def __rdiv__(self, other):
        other = SymbolicComplex.to_complex(other)
        return self.inv().__mul__(other)

    def squared_norm(self) -> z3.Real:
        conj = self.conjugate()
        return self.__mul__(conj).real

