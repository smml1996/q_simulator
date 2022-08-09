from typing import Optional

from z3 import Solver, Bool, sat, unsat, And


class StaticSolver:
    solver: Solver = Solver()

    @staticmethod
    def check():
        return StaticSolver.solver.check()

    @staticmethod
    def is_value_sat(var: Bool, value: bool) -> Optional[bool]:
        StaticSolver.solver.push()  # create new scope
        StaticSolver.solver.add(var == value)
        check_value = StaticSolver.check()
        StaticSolver.solver.pop()  # restore state
        if check_value == sat:
            return True
        if check_value == unsat:
            return False
        return None

    @staticmethod
    def model():
        m = StaticSolver.solver.model()
        print(m)


def get_amplitudes(qubits, args, amplitudes, current_amplitude=1.0):
    zero_amplitude = qubits[args[0]].zero_amplitude
    one_amplitude = qubits[args[0]].one_amplitude
    for i in range(2):
        if i == 0:
            updated_amplitude = current_amplitude*zero_amplitude
            if len(args) > 1:
                get_amplitudes(args[1:], amplitudes, updated_amplitude)
            else:
                amplitudes.append(updated_amplitude)
        else:
            updated_amplitude = current_amplitude*one_amplitude
            if len(args) > 1:
                get_amplitudes(args[1:], amplitudes, updated_amplitude)
            else:
                amplitudes.append(updated_amplitude)


def get_and_expression(qubits):
    expression = qubits[0]

    if len(qubits) > 1:
        for qubit in qubits[1:]:
            expression = And(expression, qubit)
    else:
        print("WARNING: and expression called only with 1 qubit. Expected at least 2.")
    return expression