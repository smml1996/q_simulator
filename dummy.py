from z3qubit import Z3Qubit as Qubit
from z3quantum_gate import Z3QuantumGate

q = Qubit("control")
q2 = Qubit("target")


Z3QuantumGate.mapping["control"] = q
Z3QuantumGate.mapping["target"] = q2

Z3QuantumGate("cx", ["control", "target"]).execute()

# q.normalization_constraint()

from utils import StaticSolver
print(StaticSolver.check())
StaticSolver.model()
