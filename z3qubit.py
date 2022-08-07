import z3
from utils import StaticSolver
from math import sqrt


class Z3Qubit:
    zero_real: float
    one_real: float
    qubit: z3.Bool
    counter: int = 0
    name: str
    # imaginary_part : z3.Int

    def __init__(self, name):
        self.name = name
        self.zero_real = 1.0
        self.one_real = 0.0
        self.qubit = z3.Bool(f"bv_{name}_{self.counter}")
        self.counter += 1
        StaticSolver.solver.add(self.qubit == False)


    def get_vars(self) -> z3.Bool:
        qubit = z3.Bool(f"bv_{self.name}_{self.counter}")
        self.counter += 1
        return qubit

    def swap_vars(self, temp_zero_real, temp_one_real, qubit) -> None:
        self.zero_real = temp_zero_real
        self.one_real = temp_one_real
        if qubit is not None:
            self.qubit = qubit

    def quantum_not(self) -> None:
        qubit = self.get_vars()
        temp_one_real = self.zero_real
        temp_zero_real = self.one_real
        StaticSolver.solver.add(qubit == z3.Not(self.qubit))
        self.swap_vars(temp_zero_real, temp_one_real, qubit)

    def hadamard(self) -> None:
        # hadamard gate: 1/sqrt(2)[[1,1],[1,-1]]
        qubit = self.get_vars()
        temp_zero_real = (self.zero_real+self.one_real)/sqrt(2)
        temp_one_real = (self.zero_real-self.one_real)/sqrt(2)
        self.swap_vars(temp_zero_real, temp_one_real, qubit)
