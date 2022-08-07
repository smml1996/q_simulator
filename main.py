import sys
from qiskit import QuantumCircuit
from z3qubit import Z3Qubit
from z3quantum_gate import *

input_file = sys.argv[1] # path to OpenQASM file

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


# put constraint to all qubits
for qubit in Z3QuantumGate.mapping.values():
    qubit.normalization_constraint()