from typing import Dict, List, Optional, Tuple
from z3qubit import Z3Qubit
from settings import *
from utils import StaticSolver
import z3
from random import random
import math


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
    def measure() -> Tuple[float, Dict[str, bool]]:
        """

        :return: the probability of measuring a state, and the state itself or it raises an Exception
        """
        prob: float = 1.0
        state: Dict[str, bool] = dict()
        for (var_name, obj_qubit) in Z3QuantumGate.mapping.items():
            random_num = random()
            assert(0 <= random_num <= 1.0)
            assert(math.isclose(obj_qubit.zero_real**2 + obj_qubit.one_real**2, 1.0, rel_tol=1e-5))
            if random_num <= obj_qubit.zero_real**2:
                assign_value = False
            else:
                assign_value = True

            if not StaticSolver.is_value_sat(obj_qubit.qubit, assign_value):
                if StaticSolver.is_value_sat(obj_qubit.qubit, not assign_value):
                    assign_value = not assign_value
                else:
                    raise Exception(f"No value satisfies for {var_name}")

            StaticSolver.solver.add(obj_qubit.qubit == assign_value)
            if assign_value:
                prob *= obj_qubit.one_real
            else:
                prob *= obj_qubit.zero_real
            assert(var_name not in state.keys())
            state[var_name] = assign_value
        return round(prob, 2), state

    @staticmethod
    def does_state_exists(state: Dict[str, bool]) -> Optional[float]:
        """
        Check whether a given state exists
        :param state: a dictionary mapping variable names to boolean values
        :return: probability that the given state is observed upon measurement, or None
        """
        answer = 1.0
        pop_count = 0
        for (var, value) in state.items():
            StaticSolver.solver.push()  # create new scope
            pop_count += 1
            qubit = Z3QuantumGate.mapping[var]
            StaticSolver.solver.add(qubit.qubit == value)
            check_output = StaticSolver.check()
            if check_output == z3.unsat:
                while pop_count > 0:
                    StaticSolver.solver.pop()
                    pop_count -= 1
                return 0.0
            elif check_output == z3.unknown:
                return None
            if value:
                answer *= qubit.one_real
            else:
                answer *= qubit.zero_real

        while pop_count > 0:
            StaticSolver.solver.pop()
            pop_count -= 1
        return round(answer, 2)


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

        target_qubit = target.get_vars()

        temp_control_zero = alpha1*alpha2 + alpha2*beta1
        temp_control_one = beta1*beta2 + beta2*alpha1

        temp_target_zero = alpha1*alpha2 + beta1*beta2
        temp_target_one = alpha1*beta2 + alpha2*beta1

        StaticSolver.solver.add(target_qubit == z3.If(control.qubit, z3.Not(target.qubit), target.qubit))
        control.swap_vars(temp_control_zero, temp_control_one, None)
        target.swap_vars(temp_target_zero, temp_target_one, target_qubit)
