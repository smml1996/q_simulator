from z3qubit import Z3Qubit as Qubit
from z3quantum_gate import Z3QuantumGate

q = Qubit("control")
q2 = Qubit("target")


Z3QuantumGate.mapping["dy"] = q
Z3QuantumGate.mapping["pony"] = q2
q.t()
# Z3QuantumGate("cx", ["dummy", "pony"]).execute()

# q.normalization_constraint()

from utils import StaticSolver
print(StaticSolver.check())
StaticSolver.model()
