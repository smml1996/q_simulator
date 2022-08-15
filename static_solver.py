from typing import Optional, Dict, Any

from z3 import Bool, sat, unsat, Optimize, Not, Real


class StaticSolver:
    solver: Optimize = Optimize()

    @staticmethod
    def check():
        return StaticSolver.solver.check()

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
    def get_highest_prob(mapping: Dict[str, Any]):
        # this doesnt work, entanglement does not allows to do this
        objective_function = 1.0
        for (var_name, z3qubit) in mapping.items():
            prob_zero = z3qubit.get_probability(0)
            prob_one = z3qubit.get_probability(1)
            objective_function *= (prob_one*z3qubit.qubit + prob_zero*Not(z3qubit.qubit))

        y = Real("y")
        StaticSolver.solver.add(y == objective_function)
        StaticSolver.solver.maximize(y)
        if StaticSolver.solver.check() == sat:
            print(StaticSolver.solver.model())
        else:
            print("unsat")
