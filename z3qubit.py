import z3
from utils import StaticSolver
from math import sqrt


class Z3Qubit:
    zero_real: z3.Real
    one_real: z3.Real
    qubit: z3.Bool
    counter: int = 0
    name: str
    # imaginary_part : z3.Int

    def __init__(self, name):
        self.name = name
        self.zero_real = z3.Real(f"zero_real_{name}_{self.counter}")
        self.one_real = z3.Real(f"one_real_{name}_{self.counter}")
        self.qubit = z3.Bool(f"bv_{name}_{self.counter}")
        self.counter += 1
        StaticSolver.solver.add(self.zero_real == 1, self.one_real == 0)
        StaticSolver.solver.add(self.qubit == False)

    def normalization_constraint(self):
        StaticSolver.solver.add(self.zero_real**2 + self.one_real**2 == 1.0)

    def get_vars(self):
        temp_zero_real = z3.Real(f"zero_real_{self.name}_{self.counter}")
        temp_one_real = z3.Real(f"one_real_{self.name}_{self.counter}")
        qubit = z3.Bool(f"bv_{self.name}_{self.counter}")
        self.counter += 1
        return temp_zero_real, temp_one_real, qubit

    def swap_vars(self, temp_zero_real, temp_one_real, qubit) -> None:
        self.zero_real = temp_zero_real
        self.one_real = temp_one_real
        if qubit is not None:
            self.qubit = qubit

    def quantum_not(self):
        temp_zero_real, temp_one_real, qubit = self.get_vars()
        StaticSolver.solver.add(temp_one_real == self.zero_real)
        StaticSolver.solver.add(temp_zero_real == self.one_real)
        StaticSolver.solver.add(qubit == z3.Not(self.qubit))
        self.swap_vars(temp_zero_real, temp_one_real, qubit)

    def hadamard(self):
        # hadamard gate: 1/sqrt(2)[[1,1],[1,-1]]
        temp_zero_real, temp_one_real, qubit = self.get_vars()
        StaticSolver.solver.add(temp_zero_real == (self.zero_real+self.one_real)/sqrt(2))
        StaticSolver.solver.add(temp_one_real == (self.zero_real-self.one_real)/sqrt(2))
        self.swap_vars(temp_zero_real, temp_one_real, qubit)
