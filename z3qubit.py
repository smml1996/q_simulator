import z3
from utils import StaticSolver
from math import sqrt


class Z3Qubit:
    zero_amplitude: complex
    one_amplitude: complex
    qubit: z3.Bool
    counter: int = 0
    name: str
    # imaginary_part : z3.Int

    def __init__(self, name):
        self.name = name
        self.zero_amplitude = complex(1,0)
        self.one_amplitude = complex(0,0)
        self.qubit = z3.Bool(f"{name}_{self.counter}")
        self.counter += 1
        StaticSolver.solver.add(self.qubit == False)

    def get_vars(self) -> z3.Bool:
        qubit = z3.Bool(f"{self.name}_{self.counter}")
        self.counter += 1
        return qubit

    def swap_vars(self, temp_zero_amplitude, temp_one_amplitude, qubit) -> None:
        self.zero_amplitude = temp_zero_amplitude
        self.one_amplitude = temp_one_amplitude
        if qubit is not None:
            self.qubit = qubit

    def quantum_not(self) -> None:
        qubit = self.get_vars()
        temp_one_amplitude = self.zero_amplitude
        temp_zero_amplitude = self.one_amplitude
        StaticSolver.solver.add(qubit == z3.Not(self.qubit))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)

    def hadamard(self) -> None:
        # hadamard gate: 1/sqrt(2)[[1,1],[1,-1]]
        qubit = self.get_vars()
        temp_zero_amplitude = (self.zero_amplitude + self.one_amplitude) / sqrt(2)
        temp_one_amplitude = (self.zero_amplitude - self.one_amplitude) / sqrt(2)
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)
