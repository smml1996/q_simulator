from typing import List, Optional, Dict

from z3 import And
from static_solver import StaticSolver
import math

def get_probability(zero_amplitude, one_amplitude):
    qubit_total_probability = zero_amplitude * zero_amplitude.conjugate() + one_amplitude * one_amplitude.conjugate()
    qubit_total_probability = qubit_total_probability.real
    return qubit_total_probability

def is_unitary(qubits, name):
    zero_amplitude = qubits[name].zero_amplitude
    one_amplitude = qubits[name].one_amplitude
    qubit_total_probability = get_probability(zero_amplitude, one_amplitude)
    return math.isclose(qubit_total_probability, 1.0, rel_tol=1e-5)

def get_and_expression(qubits):
    expression = qubits[0]

    if len(qubits) > 1:
        for qubit in qubits[1:]:
            expression = And(expression, qubit)
    else:
        print("WARNING: and expression called only with 1 qubit. Expected at least 2.")
    return expression


def get_qubit_probabilities(qubit) -> (complex, complex):
    is_true_sat = StaticSolver.is_value_sat(qubit.qubit, True)
    is_false_sat = StaticSolver.is_value_sat(qubit.qubit, False)

    if is_true_sat is None or is_false_sat is None:
        raise Exception("SAT solver timeout")

    if is_true_sat and is_false_sat:
        return qubit.zero_amplitude, qubit.one_amplitude

def build_state(vars, n) -> Dict[str, bool]:
    state = dict()
    for var in vars[::-1]:
        state[var] = int(n % 2) == 1
        n /= 2
    return state

def get_state_amplitude(mapping, state: Dict[str, bool]) -> Optional[complex]:
    """
    Check whether a given state exists
    :param state: a dictionary mapping variable names to boolean values
    :return: probability that the given state is observed upon measurement, or None
    """
    answer = 1.0
    StaticSolver.solver.push()
    for (var, value) in state.items():
        qubit = mapping[var]
        check_output = StaticSolver.is_value_sat(qubit.qubit, value)
        if check_output:
            check_output2 = StaticSolver.is_value_sat(qubit.qubit, not value)
            if check_output2:
                if value:
                    answer *= qubit.one_amplitude
                else:
                    answer *= qubit.zero_amplitude
            elif check_output2 is None:
                StaticSolver.solver.pop()
                return None
        elif not check_output:
            StaticSolver.solver.pop()
            return 0.0
        elif check_output is None:
            StaticSolver.solver.pop()
            return None

        StaticSolver.solver.add(qubit.qubit == value)
    StaticSolver.solver.pop()
    return round(answer.real, 2)


def get_amplitudes(mapping, args) -> List[complex]:
    amplitudes = []
    for n in range(2**len(args)):
        state = build_state(args, n)
        amplitude = get_state_amplitude(mapping, state)
        assert(amplitude is not None)
        amplitudes.append(amplitude)
    return amplitudes

def get_qubit_amplitude_from_amplitudes(new_state: List[complex], value, index):
    mask = 1 << index

    result = 0.0
    for i in range(len(new_state)):
        result_mask = i & mask
        if value == 0 and result_mask == 0:
            result += new_state[i]
        elif value == 1 and result_mask > 0:
            result += new_state[i]
    return result





