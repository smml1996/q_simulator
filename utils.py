from typing import List, Optional

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
