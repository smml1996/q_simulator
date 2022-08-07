from z3 import Solver
class StaticSolver:
    solver : Solver = Solver()

    @staticmethod
    def check():
        return StaticSolver.solver.check()

    @staticmethod
    def model():
        m = StaticSolver.solver.model()
        print(m)

