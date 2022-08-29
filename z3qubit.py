from typing import Optional

import z3
from utils import StaticSolver
from math import sqrt, e, pi
from symbolic_complex import SymbolicComplex


class Z3Qubit:
    zero_amplitude: SymbolicComplex
    one_amplitude: SymbolicComplex
    qubit: z3.Bool
    counter: int
    name: str
    had_count: int

    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.zero_amplitude = SymbolicComplex(f"z_{name}_{self.counter}", 1.0, 0.0)
        self.one_amplitude = SymbolicComplex(f"o_{name}_{self.counter}", 0.0, 0.0)
        self.qubit = z3.Bool(f"b_{name}_{self.counter}")
        self.counter += 1
        StaticSolver.solver.add(self.qubit == False)
        self.had_count = 0

    def get_vars(self) -> (SymbolicComplex, SymbolicComplex, z3.Bool):
        zero_amplitude = SymbolicComplex(f"z_{self.name}_{self.counter}")
        one_amplitude = SymbolicComplex(f"o_{self.name}_{self.counter}")
        qubit = z3.Bool(f"{self.name}_{self.counter}")
        self.counter += 1
        return zero_amplitude, one_amplitude, qubit

    def get_probability(self, value: int) -> float:
        if value == 0:
            return self.zero_amplitude.squared_norm()
        else:
            return self.one_amplitude.squared_norm()

    def swap_vars(self, temp_zero_amplitude: SymbolicComplex, temp_one_amplitude: SymbolicComplex,
                  qubit: z3.Bool = None) -> None:
        self.zero_amplitude = temp_zero_amplitude
        self.one_amplitude = temp_one_amplitude
        if qubit is not None:
            self.qubit = qubit

    def quantum_not(self) -> None:
        _, _, qubit = self.get_vars()
        temp_one_amplitude = self.zero_amplitude
        temp_zero_amplitude = self.one_amplitude
        StaticSolver.solver.add(qubit == z3.Not(self.qubit))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)

    def hadamard(self) -> None:
        # hadamard gate: 1/sqrt(2)[[1,1],[1,-1]]

        temp_zero_amplitude, temp_one_amplitude, qubit = self.get_vars()
        StaticSolver.solver.add(temp_zero_amplitude == ((self.zero_amplitude + self.one_amplitude) / sqrt(2)))
        StaticSolver.solver.add(temp_one_amplitude == ((self.zero_amplitude - self.one_amplitude) / sqrt(2)))
        if self.had_count == 0:
            self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)
        else:
            self.swap_vars(temp_zero_amplitude, temp_one_amplitude)
        self.had_count += 1
        # StaticSolver.solver.add(z3.Or(qubit, True))

    def y(self) -> None:
        # introduces a global phase i
        temp_zero_amplitude, temp_one_amplitude, qubit = self.get_vars()
        StaticSolver.solver.add(temp_zero_amplitude == self.one_amplitude * complex(0, -1))
        StaticSolver.solver.add(temp_one_amplitude == self.zero_amplitude * complex(0, 1))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)

    def z(self) -> None:
        # phase flip gate
        temp_zero_amplitude, temp_one_amplitude, qubit = self.get_vars()
        temp_zero_amplitude = self.zero_amplitude
        StaticSolver.solver.add(temp_one_amplitude == self.one_amplitude * complex(-1, 0))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)

    def t(self) -> None:
        temp_zero_amplitude, temp_one_amplitude, _ = self.get_vars()
        temp_zero_amplitude = self.zero_amplitude
        StaticSolver.solver.add(temp_one_amplitude == self.one_amplitude * (complex(e, 0) ** complex(0, pi/4)))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude)

    def t_transpose(self) -> None:
        temp_zero_amplitude, temp_one_amplitude, _ = self.get_vars()
        temp_zero_amplitude = self.zero_amplitude
        StaticSolver.solver.add(temp_one_amplitude == self.one_amplitude * (complex(e, 0) ** complex(0, - pi / 4)))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude)
