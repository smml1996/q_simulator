from typing import Optional, Dict, Any

from z3 import Bool, sat, unsat, unknown, Optimize, RealVal, Real, If


class StaticSolver:
    solver: Optimize = Optimize()
    # constants
    N1: Real = Real("sc_n1")
    Z3ZERO: Real = Real("z3_zero")

    @staticmethod
    def check():
        return StaticSolver.solver.check()

    @staticmethod
    def add_constants():
        StaticSolver.solver.add(StaticSolver.N1 == RealVal(-1))
        StaticSolver.solver.add(StaticSolver.Z3ZERO == RealVal(0))

    @staticmethod
    def is_value_sat(var: Bool, value: bool) -> Optional[bool]:
        StaticSolver.solver.push()  # create new scope
        StaticSolver.solver.add(var == value)
        check_value = StaticSolver.check()
        StaticSolver.solver.pop()  # restore state
        if check_value == sat:
            return True
        if check_value == unsat:
            return False
        return None

    @staticmethod
    def is_state_sat(state: Dict[Bool, bool]) -> Optional[bool]:
        StaticSolver.solver.push()
        for (var, value) in state.items():
            StaticSolver.solver.add(var == value)
        check_value = StaticSolver.check()
        StaticSolver.solver.pop()
        if check_value == sat:
            return True
        if check_value == unsat:
            return False
        return None

    @staticmethod
    def model():
        m = StaticSolver.solver.model()
        print(m)

    @staticmethod
    def get_last_state_from_model(model, mapping, is_binary_string) -> Dict[str, int]:
        vars_values = dict()
        for (var_name, z3qubit) in mapping.items():
            vars_values[var_name] = model[z3qubit.qubit]

        if is_binary_string:
            var_names = list(mapping.keys())
            var_names.sort()
            print(",".join(var_names))
            answer = ""
            for var_name in var_names:
                if model[mapping[var_name].qubit] == True:
                    answer += "1"
                else:
                    answer += "0"
            print(answer, "\n*****")
        return vars_values

    @staticmethod
    def get_highest_prob(mapping: Dict[str, Any], is_binary_string = False):
        # this doesnt work, entanglement does not allows to do this
        objective_function = 1.0
        for (var_name, z3qubit) in mapping.items():
            # objective_function *= (z3qubit.one_amplitude.squared_norm()*z3qubit.qubit
            #                       + z3qubit.zero_amplitude.squared_norm()*Not(z3qubit.qubit))
            objective_function *= If(z3qubit.qubit, z3qubit.one_amplitude.squared_norm(), z3qubit.zero_amplitude.squared_norm())

        y = Real("y")
        StaticSolver.solver.add(y == objective_function)
        StaticSolver.solver.maximize(y)
        check_output = StaticSolver.solver.check()
        if check_output == sat:
            model = StaticSolver.solver.model()
            return model[y].as_decimal(3), StaticSolver.get_last_state_from_model(model, mapping, is_binary_string)
        elif check_output == unknown:
            return "solver timeout"
        else:
            return "unsat"
