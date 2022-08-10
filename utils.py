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

def get_amplitudes(qubits, args, amplitudes, current_state, current_amplitude=complex(1,0)):

    zero_amplitude = qubits[args[0]].zero_amplitude
    one_amplitude = qubits[args[0]].one_amplitude
    current_qubit = qubits[args[0]].qubit
    print("prev", args[0], zero_amplitude, one_amplitude)
    for i in range(2):
        assert(current_qubit not in current_state.keys())
        current_state[current_qubit] = True
        eval_true = StaticSolver.is_state_sat(current_state)
        current_state[current_qubit] = False
        eval_false = StaticSolver.is_state_sat(current_state)
        if eval_true is None or eval_false is None:
            raise Exception("SAT solver timeout")

        if i == 0:
            current_state[current_qubit] = False

            if eval_true and eval_false:
                updated_amplitude = current_amplitude * zero_amplitude
            else:
                print("keep current_amplitude")
                updated_amplitude = current_amplitude
        else:
            current_state[current_qubit] = True

            if eval_true and eval_false:
                updated_amplitude = current_amplitude * one_amplitude
            else:
                updated_amplitude = current_amplitude

        if len(args) > 1:
            get_amplitudes(qubits, args[1:], amplitudes, current_state, updated_amplitude)
        else:
            amplitudes.append(updated_amplitude)

        del current_state[current_qubit]


def get_and_expression(qubits):
    expression = qubits[0]

    if len(qubits) > 1:
        for qubit in qubits[1:]:
            expression = And(expression, qubit)
    else:
        print("WARNING: and expression called only with 1 qubit. Expected at least 2.")
    return expression