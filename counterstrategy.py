import re
import random
from path import State, Path


class CounterstrategyState:

    def __init__(self, name: str, inputs: dict, outputs: dict, successors=None, is_initial=False, is_dead=False):
        self.name = name
        self.is_initial = is_initial
        self.is_dead = is_dead
        self.inputs = inputs
        self.outputs = outputs
        self.influential_outputs = dict()
        self.successors = successors or []
    
    def __str__(self):
        return  f"State: {self.name}\n" + \
                f"Initial: {self.is_initial}\n" + \
                f"Dead: {self.is_dead}\n" + \
                f"Inputs: {self.inputs}\n" + \
                f"Outputs: {self.outputs}\n" + \
                f"Influential outputs: {self.influential_outputs}\n" + \
                f"Successors: {self.successors}\n"


class Counterstrategy:

    def __init__(self, states=None, use_influential=True):
        self.states = states or {}
        self.num_states = len(self.states)
        self.use_influential = use_influential

        if self.use_influential:
            initial_states = [state for state in self.states.values() if state.is_initial]
            dummy_state = CounterstrategyState(
                name="dummy",
                inputs={},
                outputs=initial_states[0].outputs.copy(),
                successors=[state.name for state in initial_states],
                is_initial=False,
                is_dead=False
            )
            self._compute_influentials(dummy_state)
            for state in self.states.values():
                self._compute_influentials(state)

    def __str__(self):
        state_strs = [str(state) + "\n" for state in self.states.values()]
        return "\n".join(state_strs)

    def initial_states(self):
        """Returns the names of the initial states"""
        return [state.name for state in self.states.values() if state.is_initial]

    def successors(self, state_name: str):
        """Returns the names of successors of a state"""
        state = self.states.get(state_name)
        if not state:
            raise ValueError(f"State '{state_name}' not found")
        return state.successors

    def get_state(self, name) -> CounterstrategyState:
        return self.states.get(name)  

    def get_valuation(self, state_name: str):
        """Returns the valuation of a state as a list of literals"""
        state = self.states.get(state_name)
        if not state:
            raise ValueError(f"State '{state_name}' not found")
        literals = []
        for varname, val in state.inputs.items():
            literals.append(varname if val else "!" + varname)
        outputs = state.influential_outputs if self.use_influential else state.outputs
        for varname, val in outputs.items():
            literals.append(varname if val else "!" + varname)
        return literals

    def extract_random_path(self):
        """Extracts randomly a path from the counterstrategy"""

        # This is already random
        # successors = self.initial_states
        # successors = [state_name for state_name in self.states if self.states[state_name].is_initial and not self.states[state_name].is_dead]
        # successors = [state_name for state_name in self.states if self.states[state_name].is_initial]
        # successors = [state_name for state_name in self.states if self.states[state_name].is_initial and "Sf" in state_name]


        # Start from an initial state
        initial_state_name = self._pick_successor(self.initial_states())
        initial_state = State(f"{initial_state_name}_0", self.get_valuation(initial_state_name))

        # Perform a random walk from the initial state until hitting a failing state (no successors)
        # or completing a loop (which happens when visiting a state already visited in the walk
        visited_states = [initial_state_name]
        visited_edges = set()
        curr_state = initial_state_name
        path_states = [initial_state]
        looping = False
        loop_start_index = None

        i = 1
        # while successors != [] and not looping:
        while True:

            successors = [succ for succ in self.successors(curr_state) if (curr_state, succ) not in visited_edges]

            if not successors:
                # successors = [succ for succ in self.successors(curr_state) if not self.states[succ].is_dead]
                successors = self.successors(curr_state)
                if successors:
                    next_state = self._pick_successor(successors)
                    path_states[-1].set_successor(next_state)
                    if next_state in visited_states:
                        looping = True
                        # loop_start_index = visited_states.index(next_state)
                        loop_start_index = next(i for i in reversed(range(len(visited_states))) if visited_states[i] == next_state)
                break

            next_state = self._pick_successor(successors)
            
            state = State(f"{next_state}_{i}", self.get_valuation(next_state))
            path_states[-1].set_successor(state.id_state)
            path_states.append(state)

            visited_states.append(next_state)
            visited_edges.add((curr_state, next_state))
            curr_state = next_state
            i += 1

        transient_states = path_states[1:loop_start_index] if looping else path_states[1:]
        looping_states = path_states[loop_start_index:] if looping else None

        return Path(initial_state, transient_states, looping_states)

        # if not visited_states:
        #     visited_states.append(pick_successor([state for state in self.states if self.states[state].is_initial]))

        # transient_states = []
        # looping_states = None

        # if len(visited_states) > 1:
        #     initial_state.set_successor(visited_states[1])

        #     if not looping:

        #         # If the path is not looping, all the remaining states are transient
        #         for i, state_name in enumerate(visited_states[1:], 1):
        #             t_state = State(state_name, self.get_valuation(state_name))
        #             if i < len(visited_states) - 1:
        #                 t_state.set_successor(visited_states[i+1])
        #             transient_states.append(t_state)

        #         # If the path is not looping, it ends in a failing state
        #         successors = self.states[transient_states[-1].id_state].successors
        #         while successors != []:
                    
        #             failing_state_name = pick_successor(successors)
        #             failing_state = State(failing_state_name)
                
        #             for var in self.get_valuation(self.states[failing_state_name]):
        #                 failing_state.add_to_valuation(var)
        #             transient_states[-1].set_successor(failing_state_name)
        #             transient_states.append(failing_state)

        #             successors = self.states[transient_states[-1].id_state].successors

        #     else:
        #         # In case the path is looping, the transient states go from index 1 to index loop_startindex-1
        #         # and the remaining ones are the looping states
        #         for i, state in enumerate(visited_states[1:loop_start_index]):
        #             i = i + 1  # Indices start from 1, since we iterate from the second element
        #             new_state = State(state)
        #             if i < len(visited_states) - 1:
        #                 new_state.set_successor(visited_states[i + 1])

        #             for var in self.get_valuation(self.states[state]):
        #                 new_state.add_to_valuation(var)

        #             transient_states.append(new_state)

        #         visited_states.append(visited_states[loop_start_index])
        #         looping_states = []
        #         for i, state in enumerate(visited_states[loop_start_index:-1]):
        #             i = i + loop_start_index # Subarray starts at position loop_startindex
        #             new_state = State(state)
        #             new_state.set_successor(visited_states[i + 1])
        #             for var in self.get_valuation(self.states[state]):
        #                 new_state.add_to_valuation(var)
        #             looping_states.append(new_state)

        # else:

        #     if not looping:
                
        #         transient_states = []

        #         successors = self.states[initial_state.id_state].successors
        #         if successors != []:
        #             failing_state_name = pick_successor(successors)
        #             initial_state.set_successor(failing_state_name)
        #             failing_state = State(failing_state_name)

        #             for var in self.get_valuation(self.states[failing_state_name]):
        #                 failing_state.add_to_valuation(var)
        #             transient_states.append(failing_state)
                    
        #             successors = self.states[transient_states[-1].id_state].successors
        #             while successors != []:
                        
        #                 failing_state_name = pick_successor(successors)
        #                 failing_state = State(failing_state_name)
                    
        #                 for var in self.get_valuation(self.states[failing_state_name]):
        #                     failing_state.add_to_valuation(var)
        #                 transient_states[-1].set_successor(failing_state_name)
        #                 transient_states.append(failing_state)
                        
        #                 successors = self.states[transient_states[-1].id_state].successors
            
        #     else:
        #         # Make a copy of the initial state to create the looping state
        #         looping_state = State(initial_state.id_state.replace("S", "Sl"))
        #         for var in self.get_valuation(self.states[initial_state.id_state]):
        #             looping_state.add_to_valuation(var)
        #         looping_state.set_successor(looping_state.id_state)
        #         initial_state.set_successor(looping_state.id_state)
        #         path = Path(initial_state, [], [looping_state])
        #         return path

        # # print()
        # # print("=== INI ===")
        # # print(self.states[initial_state.id_state])
        # # print("\n=== TRANSIENT ===")
        # # for state in transient_states:
        # #     print(self.states[state.id_state])
        # # print("\n=== LOOPING ===")
        # # if looping_states is not None:
        # #     for state in looping_states:
        # #         print(self.states[state.id_state])

        # return Path(initial_state,transient_states,looping_states)

    def _compute_influentials(self, state: CounterstrategyState):
        successors = state.successors

        different_out_vars = []
        for out_var in state.outputs:
            can_be_1, can_be_0 = False, False
            for succ in successors:
                if self.states[succ].outputs.get(out_var) is True:
                    can_be_1 = True
                if self.states[succ].outputs.get(out_var) is False:
                    can_be_0 = True
                if can_be_1 and can_be_0:
                    different_out_vars.append(out_var)
                    break

        for succ in successors:
            for out_var in different_out_vars:
                self.states[succ].influential_outputs[out_var] = self.states[succ].outputs[out_var]

    def _pick_successor(self, successors, random_choice=False):
        if random_choice:
            return random.choice(successors)
    
        successors = sorted(successors, key=lambda s: int(''.join(filter(str.isdigit, s))))
        return successors[0]
