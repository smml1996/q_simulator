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
    def get_objective_function(mapping, state) -> Any:
        # because of entanglement we need a state beforehand
        objective_function = 1.0
        # for (var_name, z3qubit) in mapping.items():
        #     # objective_function *= (z3qubit.one_amplitude.squared_norm()*z3qubit.qubit
        #     #                       + z3qubit.zero_amplitude.squared_norm()*Not(z3qubit.qubit))
        #     objective_function *= If(z3qubit.qubit, z3qubit.one_amplitude.squared_norm(),
        #                              z3qubit.zero_amplitude.squared_norm())

        for (var_name, value) in state.items():

            z3qubit = mapping[var_name]

            sat_curr_value = StaticSolver.is_value_sat(z3qubit.qubit, value)
            sat_not_curr_value = StaticSolver.is_value_sat(z3qubit.qubit, not value)
            StaticSolver.solver.add(z3qubit.qubit == value)
            if sat_not_curr_value is None or sat_curr_value is None:
                raise Exception("SAT solver timeout")
            if sat_curr_value:
                if sat_not_curr_value:
                    if value:
                        objective_function *= z3qubit.one_amplitude.squared_norm()
                    else:
                        objective_function *= z3qubit.zero_amplitude.squared_norm()
                else:
                    # means that qubit is entangled its probability is 1.0 for current value
                    pass
            else:
                if not sat_not_curr_value:
                    raise Exception("this is weird, the qubit does not satisfies for any value")
                else:
                    objective_function *= RealVal(0.0)
                    return objective_function

        return objective_function


    @staticmethod
    def get_highest_prob(mapping: Dict[str, Any], is_binary_string = False):
        # TODO: this doesnt work, entanglement does not allows to do this
        # obj_f = StaticSolver.get_objective_function(mapping)
        # y = Real("y")
        # StaticSolver.solver.add(y == obj_f)
        # StaticSolver.solver.maximize(y)
        check_output = StaticSolver.solver.check()
        if check_output == sat:
            model = StaticSolver.solver.model()
            return model
            #return model[y].as_decimal(3), StaticSolver.get_last_state_from_model(model, mapping, is_binary_string)
        elif check_output == unknown:
            return "solver timeout"
        else:
            return "unsat"

    @staticmethod
    def print_amplitudes(model, mapping):
        for (key, z3qubit) in mapping.items():
            print(key, model[z3qubit.zero_amplitude.real].as_decimal(3), model[z3qubit.one_amplitude.real].as_decimal(3))

    @staticmethod
    def get_state_probability(state, mapping):

        StaticSolver.solver.push()
        y = Real("y")
        StaticSolver.solver.add(y == StaticSolver.get_objective_function(mapping, state))
        check_output = StaticSolver.solver.check()

        if check_output == sat:
            model = StaticSolver.solver.model()
            #print(model)
            StaticSolver.print_amplitudes(model, mapping)
            print(state, model[y].as_decimal(3))
        elif check_output == unknown:
            print("solver timeout")
        else:
            print(state, "unsat")

        StaticSolver.solver.pop()
