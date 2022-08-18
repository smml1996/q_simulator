from typing import Dict, List, Optional, Tuple
from z3qubit import Z3Qubit
from settings import *
from static_solver import StaticSolver
from utils import *
import z3
from random import random
import math
import numpy as np


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
        elif self.name == CZ:
            self.base_class = CZGate(self.name, self.args)
        elif self.name == SWAP:
            self.base_class = SwapGate(self.name, self.args)
        elif self.name == I:
            self.base_class = IGate(self.name, self.args)
        elif self.name == Z:
            self.base_class = ZGate(self.name, self.args)
        elif self.name == Y:
            self.base_class = YGate(self.name, self.args)
        elif self.name == T:
            self.base_class = TGate(self.name, self.args)
        elif self.name == S:
            self.base_class = SGate(self.name, self.args)
        elif self.name == CCX:
            self.base_class = CCXGate(self.name, self.args)
        else:
            raise Exception(f"Gate ({self.name}) not implemented")

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
        prob: complex = 1.0
        state: Dict[str, bool] = dict()
        StaticSolver.solver.push()
        for (var_name, obj_qubit) in Z3QuantumGate.mapping.items():
            random_num = random()
            assert(0 <= random_num <= 1.0)
            assert(is_unitary(Z3QuantumGate.mapping, var_name))
            if random_num <= (obj_qubit.zero_amplitude * obj_qubit.zero_amplitude.conjugate()).real:
                assign_value = False
            else:
                assign_value = True

            if not StaticSolver.is_value_sat(obj_qubit.qubit, assign_value):
                if StaticSolver.is_value_sat(obj_qubit.qubit, not assign_value):
                    assign_value = not assign_value
                else:
                    raise Exception(f"No value satisfies for {var_name}")
            elif StaticSolver.is_value_sat(obj_qubit.qubit, not assign_value):
                if assign_value:
                    prob *= obj_qubit.one_amplitude
                else:
                    prob *= obj_qubit.zero_amplitude

            StaticSolver.solver.add(obj_qubit.qubit == assign_value)

            assert(var_name not in state.keys())
            state[var_name] = assign_value
        prob = prob * prob.conjugate()
        StaticSolver.solver.pop()
        return round(prob.real, 2), state

    @staticmethod
    def does_state_exists(state: Dict[str, bool]) -> Optional[float]:
        """
        Check whether a given state exists
        :param state: a dictionary mapping variable names to boolean values
        :return: probability that the given state is observed upon measurement, or None
        """
        answer = get_state_amplitude(Z3QuantumGate.mapping, state)
        answer = answer * answer.conjugate()
        return round(answer.real, 2)


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
        # new qubit for target qubit
        temp_zero_probability, temp_one_probability, target_qubit = target.get_vars()

        # adding the new zero probability
        # StaticSolver.solver.add(temp_zero_probability == z3.If(control.qubit, target.one_amplitude, target.zero_amplitude))
        StaticSolver.solver.add(temp_zero_probability.real == z3.If(control.qubit, target.one_amplitude.real, target.zero_amplitude.real))
        StaticSolver.solver.add(temp_zero_probability.im == z3.If(control.qubit, target.one_amplitude.im, target.zero_amplitude.im))

        # adding the new one probability
        # StaticSolver.solver.add(temp_one_probability == z3.If(control.qubit, target.zero_amplitude, target.one_amplitude))
        StaticSolver.solver.add(temp_one_probability.real == z3.If(control.qubit, target.zero_amplitude.real, target.one_amplitude.real))
        StaticSolver.solver.add(temp_one_probability.im == z3.If(control.qubit, target.zero_amplitude.im, target.one_amplitude.im))

        # add condition to SAT formula
        StaticSolver.solver.add(target_qubit == z3.If(control.qubit, z3.Not(target.qubit), target.qubit))
        target.swap_vars(temp_zero_probability, temp_one_probability, target_qubit)


class CZGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 2)
        target = Z3QuantumGate.mapping[self.args[1]]
        target.hadamard()
        Z3QuantumGate(CX, self.args).execute()
        target.hadamard()


class SwapGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 2)
        Z3QuantumGate(CX, self.args).execute()
        Z3QuantumGate(CX, self.args[::-1]).execute()
        Z3QuantumGate(CX, self.args).execute()


class IGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        # identity gate
        assert (len(self.args) == 1)


class ZGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert(len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].z()


class YGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].y()


class TGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].t()


class SGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 1)
        Z3QuantumGate.mapping[self.args[0]].t()
        Z3QuantumGate.mapping[self.args[0]].t()

class CCXGate(Z3QuantumGate):
    def __init__(self, name: str, args: List[str]):
        super().__init__(name, args)

    def execute(self) -> None:
        assert (len(self.args) == 1)
