from typing import Optional, Dict

from z3 import Solver, Bool, sat, unsat, And


class StaticSolver:
    solver: Solver = Solver()

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
