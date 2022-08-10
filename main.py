import sys
from qiskit import QuantumCircuit
from z3quantum_gate import *
import warnings

# https://ericpony.github.io/z3py-tutorial/guide-examples.htm

warnings.filterwarnings('ignore', category=DeprecationWarning)  # DeprecationWarning: Back-references to from Bit
# instances to their containing Registers have been
# deprecated. Instead, inspect Registers to find
# their contained Bits.

input_file = sys.argv[1]  # path to OpenQASM file

# create quantum circuit from OpenQASM file
qc = QuantumCircuit.from_qasm_file(input_file)

# create necessary qubits
for instruction in qc.data:
    qubits = instruction.qubits
    for qubit in qubits:
        register_name = qubit.register.name
        qubit_index = qubit.index
        name = f"{register_name}_{qubit_index}"
        Z3QuantumGate.mapping[name] = Z3Qubit(name)

# apply gates
for instruction in qc.data:
    op = instruction.operation.name
    args = []
    qubits = instruction.qubits
    for qubit in qubits:
        register_name = qubit.register.name
        qubit_index = qubit.index
        name = f"{register_name}_{qubit_index}"
        args.append(name)

    Z3QuantumGate(op, args).execute()

print(Z3QuantumGate.measure())

# state = {'q_0': True, 'q_1': True, 'q_2': True, 'q_3': True}
# print("|00>: ", Z3QuantumGate.does_state_exists(state))
# state = {'q_0': True, 'q_1': False}
# print("|01>: ", Z3QuantumGate.does_state_exists(state))
# state = {'q_0': False, 'q_1': True}
# print("|10>: ", Z3QuantumGate.does_state_exists(state))
# state = {'q_0': True, 'q_1': True}
# print("|11>: ", Z3QuantumGate.does_state_exists(state))
