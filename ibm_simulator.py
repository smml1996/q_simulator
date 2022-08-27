import numpy as np

# Import Qiskit
from qiskit import QuantumCircuit, execute
from qiskit.providers.aer import QasmSimulator

qc = QuantumCircuit.from_qasm_file("./benchmarks/small/adder_n4/adder_n4.qasm")
qc.save_statevector()
backend = QasmSimulator()
backend_options = {'method': 'statevector'}
job = execute(qc, backend, backend_options=backend_options)
job_result = job.result()
print(len(job_result.get_statevector(qc)))