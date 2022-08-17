import z3
from utils import StaticSolver
from math import sqrt, e, pi

class Z3Qubit:
    zero_amplitude: complex
    one_amplitude: complex
    zero_probability: z3.ArithRef
    one_probability: z3.ArithRef
    qubit: z3.Bool
    counter: int = 0
    name: str
    # imaginary_part : z3.Int

    def __init__(self, name):
        self.name = name
        self.zero_amplitude = complex(1, 0)
        self.one_amplitude = complex(0, 0)
        self.zero_probability = z3.RealVal(1)
        self.one_probability = z3.RealVal(0)
        self.qubit = z3.Bool(f"{name}_{self.counter}")
        self.counter += 1
        StaticSolver.solver.add(self.qubit == False)

    def get_vars(self) -> z3.Bool:
        qubit = z3.Bool(f"{self.name}_{self.counter}")
        self.counter += 1
        return qubit

    def get_probability(self, value: int) -> float:
        if value == 0:
            answer = self.zero_amplitude * self.zero_amplitude.conjugate()
        else:
            assert(value == 1)
            answer = self.one_amplitude * self.one_amplitude.conjugate()

        return answer.real

    def normalize(self):
        # Because of floating point precision error we should normalize the amplitudes of qubits
        # zero_p = self.zero_amplitude * self.zero_amplitude.conjugate()
        # one_p = self.one_amplitude * self.one_amplitude.conjugate()
        #
        # total_raw = zero_p + one_p
        #
        # zero_p = zero_p/total_raw
        # one_p = one_p/total_raw
        #
        # self.zero_amplitude = zero_p / self.zero_amplitude.conjugate()
        # self.one_amplitude = one_p / self.one_amplitude.conjugate()
        pass

    def swap_vars(self, temp_zero_amplitude, temp_one_amplitude, qubit) -> None:
        self.zero_amplitude = temp_zero_amplitude
        self.one_amplitude = temp_one_amplitude
        self.normalize()
        if qubit is not None:
            self.qubit = qubit

    def set_probabilties(self) -> None:
        zero_prob = z3.RealVal(self.get_probability(0))
        one_prob = z3.RealVal(self.get_probability(1))
        self.zero_probability = zero_prob
        self.one_probability = one_prob

    def quantum_not(self) -> None:
        qubit = self.get_vars()
        temp_one_amplitude = self.zero_amplitude
        temp_zero_amplitude = self.one_amplitude
        StaticSolver.solver.add(qubit == z3.Not(self.qubit))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)
        self.set_probabilties()

    def hadamard(self) -> None:
        # hadamard gate: 1/sqrt(2)[[1,1],[1,-1]]
        qubit = self.get_vars()
        temp_zero_amplitude = (self.zero_amplitude + self.one_amplitude) / sqrt(2)
        temp_one_amplitude = (self.zero_amplitude - self.one_amplitude) / sqrt(2)
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, qubit)
        self.set_probabilties()
        StaticSolver.solver.add(z3.Or(qubit, True))

    def y(self) -> None:
        # introduces a global phase i
        temp_zero_amplitude = self.one_amplitude * complex(0, -1)
        temp_one_amplitude = self.zero_amplitude * complex(0, 1)
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, None)
        self.set_probabilties()

    def z(self) -> None:
        # phase flip gate
        temp_zero_amplitude = self.zero_amplitude
        temp_one_amplitude = self.one_amplitude * complex(-1, 0)
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, None)
        self.set_probabilties()

    def t(self) -> None:
        temp_zero_amplitude = self.zero_amplitude
        temp_one_amplitude = self.one_amplitude * (complex(e, 0) ** complex(0, pi/4))
        self.swap_vars(temp_zero_amplitude, temp_one_amplitude, None)
        self.set_probabilties()

