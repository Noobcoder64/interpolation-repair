import re
import random
from path import State, Path


def pick_successor(successors):
    return random.choice(successors)
    # successors = sorted(successors, key=lambda s: int(''.join(filter(str.isdigit, s))))
    # return successors[0]

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

    def get_state(self, name) -> CounterstrategyState:
        return self.states.get(name)

    def getValuation(self, state: CounterstrategyState):
        literals = []
        for varname in state.inputs:
            if state.inputs[varname] is True:
                literals.append(varname)
            else:
                literals.append("!"+varname)
        if self.use_influential:
            outputs = state.influential_outputs
        else:
            outputs = state.outputs
        for varname in outputs:
            if state.outputs[varname] is True:
                literals.append(varname)
            else:
                literals.append("!"+varname)
        return literals    

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

        # Perform a random walk from the initial state until hitting a failing state (no successors)
        # or completing a loop (which happens when visiting a state already visited in the walk)
        visited_states = []
        looping = False
        loop_startindex = None

        # initial_states = [state.name for state in self.states.values() if state.is_initial]
        # print("Initial states:", sorted(initial_states))

        # This is already random
        successors = [state_name for state_name in self.states if self.states[state_name].is_initial and not "Sf" in state_name]
        # successors = [state_name for state_name in self.states if self.states[state_name].is_initial]
        # successors = [state_name for state_name in self.states if self.states[state_name].is_initial and "Sf" in state_name]

        while successors != [] and not looping:
            
            curr_state = pick_successor(successors)
            # curr_state = successors[0]

            if curr_state in visited_states:
                looping = True
                loop_startindex = visited_states.index(curr_state)
            else:
                successors = [state_name for state_name in self.states[curr_state].successors if not "Sf" in state_name]
                # successors = [state_name for state_name in self.states[curr_state].successors]
                visited_states.append(curr_state)

        if visited_states == []:
            visited_states.append(pick_successor([state for state in self.states if self.states[state].is_initial]))

        initial_state = State(visited_states[0])
        for var in self.getValuation(self.states[visited_states[0]]):
            initial_state.add_to_valuation(var)

        if len(visited_states) > 1:
            initial_state.set_successor(visited_states[1])
            transient_states = []

            if not looping:

                # If the path is not looping, all the remaining states are transient
                for i, state in enumerate(visited_states[1:]):
                    i = i + 1 # Indices start from 1, since we iterate from the second element
                    new_state = State(state)
                    if i < len(visited_states)-1:
                        new_state.set_successor(visited_states[i+1])

                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)

                    transient_states.append(new_state)

                # If the path is not looping, it ends in a failing state
                successors = self.states[transient_states[-1].id_state].successors
                while successors != []:
                    
                    failing_state_name = pick_successor(successors)
                    failing_state = State(failing_state_name)
                
                    for var in self.getValuation(self.states[failing_state_name]):
                        failing_state.add_to_valuation(var)
                    transient_states[-1].set_successor(failing_state_name)
                    transient_states.append(failing_state)

                    successors = self.states[transient_states[-1].id_state].successors

                looping_states = None

            else:
                # In case the path is looping, the transient states go from index 1 to index loop_startindex-1
                # and the remaining ones are the looping states
                for i, state in enumerate(visited_states[1:loop_startindex]):
                    i = i + 1  # Indices start from 1, since we iterate from the second element
                    new_state = State(state)
                    if i < len(visited_states) - 1:
                        new_state.set_successor(visited_states[i + 1])

                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)

                    transient_states.append(new_state)

                visited_states.append(visited_states[loop_startindex])
                looping_states = []
                for i, state in enumerate(visited_states[loop_startindex:-1]):
                    i = i + loop_startindex # Subarray starts at position loop_startindex
                    new_state = State(state)
                    new_state.set_successor(visited_states[i + 1])
                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)
                    looping_states.append(new_state)

        else:

            if not looping:
                
                transient_states = []

                successors = self.states[initial_state.id_state].successors
                if successors != []:
                    failing_state_name = pick_successor(successors)
                    initial_state.set_successor(failing_state_name)
                    failing_state = State(failing_state_name)

                    for var in self.getValuation(self.states[failing_state_name]):
                        failing_state.add_to_valuation(var)
                    transient_states.append(failing_state)
                    
                    successors = self.states[transient_states[-1].id_state].successors
                    while successors != []:
                        
                        failing_state_name = pick_successor(successors)
                        failing_state = State(failing_state_name)
                    
                        for var in self.getValuation(self.states[failing_state_name]):
                            failing_state.add_to_valuation(var)
                        transient_states[-1].set_successor(failing_state_name)
                        transient_states.append(failing_state)
                        
                        successors = self.states[transient_states[-1].id_state].successors

                looping_states = None
            
            else:
                # Make a copy of the initial state to create the looping state
                looping_state = State(initial_state.id_state.replace("S", "Sl"))
                for var in self.getValuation(self.states[initial_state.id_state]):
                    looping_state.add_to_valuation(var)
                looping_state.set_successor(looping_state.id_state)
                initial_state.set_successor(looping_state.id_state)
                path = Path(initial_state, [], [looping_state])
                return path

        # print()
        # print("=== INI ===")
        # print(self.states[initial_state.id_state])
        # print("\n=== TRANSIENT ===")
        # for state in transient_states:
        #     print(self.states[state.id_state])
        # print("\n=== LOOPING ===")
        # if looping_states is not None:
        #     for state in looping_states:
        #         print(self.states[state.id_state])

        return Path(initial_state,transient_states,looping_states)

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
