# import pydot
import random
import experiment_properties as exp
from path import State, Path

class CounterstrategyState:
    def __init__(self, name: str, inputs: dict, outputs: dict, successors=[], is_dead: bool = False):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.influential_outputs = dict()
        self.successors = successors
        self.is_dead = is_dead

    def add_successor(self, state_name):
        self.successors.append(state_name)
    
    def __str__(self):
        return f"State: {self.name}\nInputs: {self.inputs}\nOutputs: {self.outputs}\nSuccessors: {', '.join(self.successors)}\nInfluential outputs: {self.influential_outputs}\nDEAD: {self.is_dead}"


class Counterstrategy:

    def __init__(self, states = dict(), dead_states = dict(), use_influential=True):
        self.states = states
        self.dead_states = dead_states
        self.use_influential = use_influential

        if self.use_influential:
            for state in self.states.values():
                self.compute_influentials(state)
        self.num_states = len(self.states)

    def __str__(self):
        state_strs = [str(state) + "\n" for state in self.states.values()]
        dead_state_strs = [str(state) + "\n" for state in self.dead_states.values()]
        return "\n".join(state_strs) + "\n" + "\n".join(dead_state_strs)

    def add_state(self, state):
        self.states[state.name] = state

    def get_state(self, name):
        return self.states.get(name)

    def compute_influentials(self, state: CounterstrategyState):
        for i in range(len(state.successors)-1):
            for j in range(i+1, len(state.successors)):
                next_state1 = state.successors[i]
                next_state2 = state.successors[j]

                if next_state1 in self.dead_states or next_state2 in self.dead_states:
                    continue

                if next_state1 == next_state2:
                    continue

                if self.states[next_state1].inputs == self.states[next_state2].inputs:
                    continue

                outputs1 = self.states[next_state1].outputs
                outputs2 = self.states[next_state2].outputs

                for var in outputs1:
                    if outputs1[var] != outputs2[var]:
                        self.states[next_state1].influential_outputs[var] = outputs1[var]
                        self.states[next_state2].influential_outputs[var] = outputs2[var]

    def getValuation(self, state):
        literals = []
        for varname in state.inputs:
            if state.inputs[varname] == 'true':
                literals.append(varname)
            else:
                literals.append("!"+varname)
        if self.use_influential:
            outputs = state.influential_outputs
        else:
            outputs = state.outputs
        for varname in outputs:
            if state.outputs[varname] == 'true':
                literals.append(varname)
            else:
                literals.append("!"+varname)
        return literals    

    def extractRandomPath(self):
        """Extracts randomly a path from the counterstrategy"""

        # Build a State object for the initial state
        curr_state = "S0"
        # Perform a random walk from the initial state until hitting a failing state (no successors)
        # or completing a loop (which happens when visiting a state already visited in the walk)
        visited_states = ["S0"]
        looping = False
        loop_startindex = None

        while self.states[curr_state].successors != [] and not looping:

            successors = [state for state in self.states[curr_state].successors if state not in self.dead_states]
            curr_state = random.choice(successors)

            if curr_state in visited_states:
                looping = True
                loop_startindex  = visited_states.index(curr_state)
            else:
                visited_states.append(curr_state)

        initial_state = State("S0")
        for var in self.getValuation(self.states["S0"]):
            initial_state.add_to_valuation(var)

        if len(visited_states)>1:
            initial_state.set_successor(visited_states[1])
            transient_states = []

            if not looping:

                # If the path is not looping, all the remaining states are transient
                for i,state in enumerate(visited_states[1:]):
                    i = i + 1 # Indices start from 1, since we iterate from the second element
                    new_state = State(state)
                    if i < len(visited_states)-1:
                        new_state.set_successor(visited_states[i+1])

                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)

                    transient_states.append(new_state)

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
                for i,state in enumerate(visited_states[loop_startindex:-1]):
                    i = i + loop_startindex # Subarray starts at position loop_startindex
                    new_state = State(state)
                    new_state.set_successor(visited_states[i + 1])
                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)
                    looping_states.append(new_state)

        else:

            transient_states = []
            looping_states = None

            if looping:
                looping_states = [initial_state]

        return Path(initial_state,transient_states,looping_states)

    def extendFinitePath(self, path):
        """If path does not reach a guarantee violation, extends it with a new state where supposedly the violation
        occurs. Needed because RATSY sometimes stops finite counterruns some steps before the actual violation"""
        
        if path.transient_states[-1].id_state == "Sf":
            new_state_name = "Sf2"
        else:

            if (path.transient_states[-1].id_state)[2:] == '':
                last_id = int((path.transient_states[-1].id_state)[1:])
            else:
                last_id = int((path.transient_states[-1].id_state)[2:])
            new_state_name = "Sf" + str(last_id+1)

        # The new state will have the constant input variables set to the value defined in the counterstrategy.
        # Since this state does not come from the counterstrategy graph, at this point we are sure there are no
        # other pieces of input valuation in the previous state
        
        input_vars = set(exp.inputVarsList)

        failing_state = State(new_state_name)
        last_state = path.transient_states[-1].valuation
        for var in assignments:
            # if re.sub(r'!', '', var) in input_vars:
            failing_state.add_to_valuation(var)

        path.states[new_state_name] = failing_state
        path.transient_states[-1].set_successor(new_state_name)
        path.transient_states.append(failing_state)

        return path
