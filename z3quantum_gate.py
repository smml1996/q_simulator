from typing import Dict, List, Optional
from z3qubit import Z3Qubit
from settings import *
from utils import StaticSolver
import z3


class Z3QuantumGate:
    name: str
    mapping: Dict[str, Z3Qubit] = dict()

    def __init__(self, name, args):
        self.name = name
        self.base_class = None
        self.args = args

    def set_instruction(self):
        if self.name == X:
            self.base_class = XGate(self.name, self.args)
        elif self.name == H:
            self.base_class = HGate(self.name, self.args)
        elif self.name == CX:
            self.base_class = CXGate(self.name, self.args)

    @property
    def specific_subclass(self) -> object:
        if self.base_class is None:
            self.set_instruction()
        return self.base_class

    def execute(self) -> None:
        self.specific_subclass.execute()

    @staticmethod
    def measure(self) -> Dict[str, bool]:
        raise Exception("missing implementation")

    @staticmethod
    def does_state_exists(state: Dict[str, bool]) -> Optional[float]:
        '''

        :param state: a dictionary mapping variable names to boolean values
        :return: probability that the given state is observed upon measurement, or None
        '''
        answer = 1.0
        for (var, value) in state.items():
            StaticSolver.solver.push() # create new scope
            qubit = Z3QuantumGate.mapping[var]
            StaticSolver.solver.add(qubit.qubit == value)
            check_output = StaticSolver.check()
            if  check_output == "unsat":
                return 0.0
            elif check_output == "unknown":
                return None


        return answer



class XGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert(len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].quantum_not()


class HGate(Z3QuantumGate):

    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].hadamard()


class CXGate(Z3QuantumGate):

    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 2)
        control = Z3QuantumGate.mapping[self.args[0]]
        target = Z3QuantumGate.mapping[self.args[1]]

        alpha1 = target.zero_real
        beta1 = target.one_real

        alpha2 = control.zero_real
        beta2 = control.one_real

        temp_control_zero, temp_control_one, control_qubit = control.get_vars()
        temp_target_zero, temp_target_one, target_qubit = target.get_vars()

        StaticSolver.solver.add(temp_control_zero == alpha1*alpha2 + alpha2*beta1)
        StaticSolver.solver.add(temp_control_one == beta1*beta2 + beta2*alpha1)

        StaticSolver.solver.add(temp_target_zero == alpha1*alpha2 + beta1*beta2)
        StaticSolver.solver.add(temp_target_one == alpha1*beta2 + alpha2*beta1)

        StaticSolver.solver.add(target_qubit == z3.If(control.qubit, z3.Not(target.qubit), target.qubit))
        control.swap_vars(temp_control_zero, temp_control_one, None)
        target.swap_vars(temp_target_zero, temp_target_zero, target_qubit)
