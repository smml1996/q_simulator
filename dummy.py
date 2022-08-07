from z3qubit import Z3Qubit as Qubit
from z3quantum_gate import Z3QuantumGate
from utils import StaticSolver

q = Qubit("control")
q2 = Qubit("target")


Z3QuantumGate.mapping["control"] = q
Z3QuantumGate.mapping["target"] = q2

Z3QuantumGate("cx", ["control", "target"]).execute()

# q.normalization_constraint()


print(StaticSolver.check())
StaticSolver.model()
