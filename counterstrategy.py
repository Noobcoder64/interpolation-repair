# import pydot
import random
import re
import spectra_utils as spectra
import copy
import specification as sp
import experiment_properties as exp
import spot

def var_to_asp(sys, timepoint):
    vars = re.split(",\s*", sys)
    output = ""
    for var in vars:
        parts = var.split(":")
        suffix = ""
        if parts[1] == "false":
            suffix = "not_"
        params = [parts[0], str(timepoint), "trace_name"]
        output += suffix + "holds_at(" + ','.join(params) + ").\n"
    return output

def extract_trace(lines, output, start, timepoint, trace_name, traces):
    if len(re.findall(start, trace_name)) > 1 or start == "DEAD":
        output = re.sub("trace_name", trace_name, output)
        return output
    pattern = re.compile("^" + start)
    states = list(filter(pattern.search, lines))
    env = re.compile("{(.*)}\s*/", ).search(states[0]).group(1)
    output += var_to_asp(env, timepoint)
    for state in states:
        sys = re.compile("/\s*{(.*)}", ).search(state).group(1)
        out_copy = copy.deepcopy(output)
        out_copy += var_to_asp(sys, timepoint)
        next = extract_string_within("->\s*([^\s]*)\s", state)
        if next != "DEAD" or next == "DEAD":
            key = trace_name + "_" + next
            new_output = extract_trace(lines, out_copy, next, timepoint + 1, key, traces)
            if new_output is not None:
                traces[key] = new_output


def last_state(trace, prevs, offset=0):
    prevs = ["prev_" + x if not re.search("prev_", x) else x for x in prevs]
    last_timepoint = max(re.findall(r",(\d*),", trace))
    if last_timepoint == "0" and offset != 0:
        return ()
    last_timepoint = str(int(last_timepoint) - offset)
    absent = re.findall(r"not_holds_at\((.*)," + last_timepoint, trace)
    atoms = re.findall(r"holds_at\((.*)," + last_timepoint, trace)
    assignments = ["!" + x if x in absent else x for x in atoms]
    if last_timepoint == '0':
        prev_assign = ["!" + x for x in prevs]
    else:
        prev_timepoint = str(int(last_timepoint) - 1)
        absent = re.findall(r"not_holds_at\((.*)," + prev_timepoint, trace)
        prev_assign = ["!" + x if x in absent else x for x in prevs]
    assignments += prev_assign
    variables = [re.sub(r"!", "", x) for x in assignments]
    assignments = [i for _, i in sorted(zip(variables, assignments))]
    return tuple(assignments)

def no_next(dis):
    conjuncts = dis.split("&")
    for conjunct in conjuncts:
        if re.search("next", conjunct):
            return False
    return True

def sub_next_only(dis):
    conjuncts = dis.split("&")
    output = '&'.join([re.sub(r"next\(([^\)]*)\)", r"\1", x) for x in conjuncts if re.search("next", x)])
    return re.sub(r"\(|\)", "", output)

def next_only(x, new_state):
    disjuncts = x.split("|")
    # TODO: seems to be generating things that violate assumptions.
    # disjuncts = [dis for dis in disjuncts if not no_next(dis)]
    # currs = [re.sub(r"next\([^\)]*\)", "", dis) for dis in disjuncts]
    # currs = [re.sub(r"&(\))|(\()&", r"\1",c) for c in currs]
    # currs = [re.sub(r"&&","&",c) for c in currs]
    #
    # [satisfies(c,new_state) for c in currs]

    disjuncts = [sub_next_only(dis) for dis in disjuncts if not no_next(dis)]
    return '|'.join(disjuncts)

def satisfies(expression, state):
    expression = "(speedButton_0 & next(yBoolExpr_0)) | (!speedButton_0 & next(!yBoolExpr_0))"
    # print("====================================")
    # print("EXPRESSION: ", expression)
    # print("STATE: ", state)
    disjuncts = expression.split("|")
    # print("DIS: ", disjuncts)
    for disjunct in disjuncts:
        conjuncts = disjunct.split("&")
        # print("CON: ", conjuncts)
        if all([conjunct in state for conjunct in conjuncts]):
            return True
    return False

def unsat_nexts(new_state, primed_expressions_cleaned):
    if new_state == []:
        return []
    unsat_primed_exp = [expression for expression in primed_expressions_cleaned if not satisfies(expression, new_state)]
    output = [next_only(x, new_state) for x in unsat_primed_exp]
    output = [x for x in output if x != ""]
    return output

def aspify(expressions):
    # is this first one ok?
    expressions = [spot.formula(x).simplify().to_str() for x in expressions]
    expressions = [re.sub(r"\(|\)", "", x) for x in expressions]
    expressions = [re.sub(r"\|", ";", x) for x in expressions]
    expressions = [re.sub(r"!", " not ", x) for x in expressions]
    expressions = [re.sub(r"&", ",", x) for x in expressions]
    expressions = [x for x in expressions if x != "1" and x != "0"]
    return expressions

import subprocess

# This determines the paths for running clingo and ILASP and whether to use Windows Subsystem for Linux (WSL):
SETUP_DICT = {'wsl': False,
              'clingo': 'clingo',
              'ILASP': '~/ILASP',
              'FastLAS': 'FastLAS',
              'ltlfilt': 'ltlfilt'
              }

def create_cmd(param):
    cmd = []
    if SETUP_DICT['wsl']:
        cmd.append('wsl')
    cmd.append(SETUP_DICT[param[0]])
    if len(param) == 1:
        return cmd
    cmd += param[1:]
    return cmd

def run_clingo_raw(filename):
    filepath = filename
    # cmd = ['wsl', 'clingo', filepath]
    cmd = create_cmd(['clingo', filepath])
    cmd = ' '.join(cmd)
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.DEVNULL).communicate()[0]
    return output

def generate_model(expressions, neg_expressions, variables, scratch=False, asp_restrictions="", force=False):
    if scratch:
        prevs = ["prev_" + var for var in variables]
        nexts = ["next_" + var for var in variables]
        if any([re.search("next", x) for x in expressions + neg_expressions]):
            variables = variables + prevs + nexts
        elif any([re.search(r"\b" + r"|\b".join(variables), x) for x in expressions + neg_expressions]):
            variables = variables + prevs
        else:
            variables = prevs
        output = asp_restrictions + "\n"
    else:
        output = ""
    # print("EXPRESSION BEFORE: ", expressions)
    expressions = aspify(expressions)
    # print("EXPRESSIONS: ", expressions)
    for i, rule in enumerate(expressions):
        name = "t" + str(i)
        disjuncts = rule.split(";")
        output += '\n'.join([name + " :- " + x + "." for x in disjuncts])
        output += "\ns" + name + " :- not " + name + ".\n:- s" + name + ".\n"

    # output = '\n'.join([x + "." for x in expressions])
    # output += '\n'
    output += '\n'.join(["{" + var + "}." for var in variables])
    output += '\n'

    neg_expressions = aspify(neg_expressions)
    rules = []
    for i, x in enumerate(neg_expressions):
        name = "rule" + str(i)
        disjuncts = x.split(";")
        output += '\n'.join([name + " :- " + dis + "." for dis in disjuncts]) + "\n"
        # output += name + " :- " + x + ".\n"
        rules.append(name)

    if len(rules) > 0:
        output += ":- " + ','.join(rules) + ".\n"
    output += '\n'.join(["#show " + var + "/0." for var in variables]) + "\n"

    file = "./Translators/output-files/temp_asp.lp"
    sp.write_file(output, file)
    clingo_out = run_clingo_raw(file)
    # print(clingo_out)
    violation = True

    reg = re.search(r"Answer: 1(.*)SATISFIABLE", str(clingo_out))
    if not reg:
        # print(clingo_out)
        # print("Something not right with model generation")
        return None, None
    model = reg.group(1)
    model = re.sub(r"\\n", "", model)
    state = model.split(" ")
    [state.append("!" + x) for x in variables if x not in state]
    state = [x for x in state if x != ""]
    return [state], violation


def next_possible_assignments(new_state, primed_expressions_cleaned, primed_expressions_cleaned_s, unprimed_expressions,
                              unprimed_expressions_s, variables):
    unsat_next_exp = unsat_nexts(new_state, primed_expressions_cleaned)
    # print("UNE: ", unsat_next_exp)
    unsat_next_exp_s = unsat_nexts(new_state, primed_expressions_cleaned_s)
    # print("UNES: ", unsat_next_exp_s)

    # if unsat_next_exp + unsat_next_exp_s + unprimed_expressions + unprimed_expressions_s == []:
    if False:
        # Pick random assignment
        vars = [var for var in variables if not re.search("prev_", var)]
        i = random.choice(range(2 ** len(vars)))
        # TODO: replace i with 0 for deadlock - in order to make deterministic
        # i = 0
        n = "{0:b}".format(i)
        assignments = '0' * (len(vars) - len(n)) + n
        assignments = [int(x) for x in assignments]
        state = ["!" + var if assignments[i] else var for i, var in enumerate(vars)]
        return [state], False
    return generate_model(unsat_next_exp + unprimed_expressions, unsat_next_exp_s + unprimed_expressions_s, variables,
                          force=True)


def state_to_asp(state, trace, number):
    end = ",trace_" + str(number) + ")."
    last_timepoint = max(re.findall(r",(\d*),", trace))
    timepoint = str(int(last_timepoint) + 1)
    variables = [s for s in state if not re.search("prev_", s)]
    asp = ["not_holds_at(" + v[1:] if re.search("!", v) else "holds_at(" + v for v in variables]
    asp = [x + "," + timepoint + end for x in asp]
    return re.sub(r",[^,]*\)\.", end, trace) + '\n'.join(asp)

def complete_deadlock(trace, file, deadlock_number):
    file = re.sub("_patterned", "", file)
    initial_expressions, prevs, primed_expressions, unprimed_expressions, variables = sp.extract_expressions(file,
                                                                                                          counter_strat=True)
    initial_expressions_s, prevs_s, primed_expressions_s, unprimed_expressions_s, variables_s = sp.extract_expressions(
        file,
        guarantee_only=True)

    primed_expressions_cleaned = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions]
    primed_expressions_cleaned_s = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions_s]
    final_state = last_state(trace, prevs)
    assignments, is_violating = next_possible_assignments(final_state, primed_expressions_cleaned,
                                                          primed_expressions_cleaned_s, unprimed_expressions,
                                                          unprimed_expressions_s, variables)
    if assignments is None:
        return None
    return state_to_asp(random.choice(assignments), trace, deadlock_number)

def complete_deadlock_alt(last_state, file):
    # print("LAST STATE: ", last_state)
    spec = sp.read_file(file)
    spec = sp.format_spec(spec)
    # spec = sp.format_iff(spec)
    # search_type = "asm|assumption|gar|guarantee"
    # for i, line in enumerate(spec):
    #     if re.search(search_type, line):
    #         # spec[i+1] = spot.formula(spec[i+1])
    #         formula = spot.formula(re.sub(r";", "", spec[i+1])).simplify()
    #         print("FORMULA: ", formula)
    #         print("LINE: ", spec[i+1])
    #         spec[i+1] = "\t" + formula.to_str() + "\n"
    #         # spec[i+1] = "\t" + sp.spectra_to_DNF(spec[i + 1]) + "\n"
    sp.write_file(spec, "./deadlock.spectra")

    initial_expressions, prevs, primed_expressions, unprimed_expressions, variables = sp.extract_expressions(spec,
                                                                                                          counter_strat=True)
    initial_expressions_s, prevs_s, primed_expressions_s, unprimed_expressions_s, variables_s = sp.extract_expressions(
        spec,
        guarantee_only=True)

    # primed_expressions = [spot.formula(x).simplify().to_str(parenth=True) for x in primed_expressions]

    primed_expressions_cleaned = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions]
    primed_expressions_cleaned_s = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions_s]
    # print()
    # print("PEC: ", primed_expressions_cleaned)
    # print()
    # print("UE: ", unprimed_expressions)
    # print()
    # print("PECS: ", primed_expressions_cleaned_s)
    # print()
    # print("UES: ", unprimed_expressions_s)
    # print()
    assignments, is_violating = next_possible_assignments(last_state, primed_expressions_cleaned,
                                                          primed_expressions_cleaned_s, unprimed_expressions,
                                                          unprimed_expressions_s, variables)
    # print()
    # print("ASSIGNMENTS: ", assignments)
    # print()
    return assignments


def counter_strat_to_trace(lines=[], deadlock_required=[], cs_count=0, specification=""):
        # if lines == []:
        #     lines = read_file(cs)
        start = "S0"
        output = ""
        files = {}
        deadlock_number = 0
        extract_trace(lines, output, start, 0, "ini", files)

        for key in files.keys():
            if re.search("DEAD", key):
                deadlock = files[key]
                # if self.deadlock_needed(learning_type):
                # if "counter_strat_" + str(cs_count) in deadlock_required:
                deadlock = complete_deadlock(files[key], specification, deadlock_number)
                # This bit ensures max one deadlock is added
                if deadlock is None or deadlock_number > 0:
                    files[key] = "problem"
                else:
                    files[key] = deadlock
                    deadlock_number += 1
            cs_count += 1
        trace_list = [files[key] for key in files.keys() if files[key] != "problem"]
        return trace_list, cs_count

class State(object):
    def __init__(self, id_state):
        """
        Constructor.
        """

        self.id_state = id_state
        self.valuation = set()

        #: The successor's id
        #: @type string
        self.successor = None

    def set_successor(self, id_state):
        self.successor = id_state
        return

    def get_valuation(self):
        # print str(self.valuation)
        valuation_with_ids = []
        for bool_literal in self.valuation:
            valuation_with_ids.append(bool_literal + "__" + self.id_state)
        return ' & '.join(valuation_with_ids)

    def add_to_valuation(self, bool_literal):
        # print "Valuation update (before) "+self.id_state+": "+str(self.valuation)
        self.valuation.add(bool_literal)
        # print "Valuation update (after) "+self.id_state+": "+str(self.valuation)
        return


"""This is a rewriting of the Path class, much simpler than previous version since it does not read the path from a file"""
class Path:
    def __init__(self, initial_state, transient_states, looping_states=None):
        #: List of all the states
        #: @type: L{State dict}
        self.states = dict()

        #: Initial state of the graph
        #: @type: L{State}
        self.initial_state = initial_state

        #: Transient states
        #: @type: L{State[]}
        self.transient_states = transient_states

        #: Looping states
        #: @type: L{State[]}
        if looping_states is not None:
            self.looping_states = looping_states
            self.is_loop = True
        else:
            self.is_loop = False
        self.unrolled_states = []
        self.unrolling_degree = 0

        self.states[self.initial_state.id_state] = self.initial_state
        for state in self.transient_states:
            self.states[state.id_state] = state

        if self.is_loop:
            for state in self.looping_states:
                self.states[state.id_state] = state

    def get_valuation(self):
        valuation = ""
        for s in self.states.values():
            if valuation != "" and s.get_valuation() != "":
                valuation = valuation + " & "
            valuation = valuation + s.get_valuation()
        return valuation

    def save(self,file):
        file.write(str(self))

    # Unrolls the path by one more degree
    def unroll(self):
        if self.is_loop:
            # Increase the unrolling degree
            self.unrolling_degree = self.unrolling_degree+1
            # Fit the first unrolled state in the path by changing the previous state's
            # successor
            unrolled_state = State(self.looping_states[0].id_state+"_"+str(self.unrolling_degree))
            if self.unrolling_degree == 1:
                if len(self.transient_states) >= 1:
                    self.transient_states[-1].set_successor(unrolled_state.id_state)
                else:
                    self.initial_state.set_successor(unrolled_state.id_state)
            else:
                self.unrolled_states[-1].set_successor(unrolled_state.id_state)
            self.unrolled_states.append(unrolled_state)
            self.states[unrolled_state.id_state] = unrolled_state
            unrolled_state.valuation = self.looping_states[0].valuation

            # Add the other unrolled states
            for i in range(1,len(self.looping_states)):
                unrolled_state = State(self.looping_states[i].id_state+"_"+str(self.unrolling_degree))
                self.unrolled_states[-1].set_successor(unrolled_state.id_state)
                self.unrolled_states.append(unrolled_state)
                self.states[unrolled_state.id_state] = unrolled_state
                unrolled_state.valuation = self.looping_states[i].valuation

            # Set the successor of the last unrolled state
            self.unrolled_states[-1].set_successor(self.looping_states[0].id_state)

    def __str__(self):
        ret_string = self.initial_state.id_state
        if self.transient_states is not None:
            for s in self.transient_states:
                ret_string = ret_string + " -> " + s.id_state
        if self.is_loop:
            if self.unrolling_degree >= 1:
                for s in self.unrolled_states:
                    ret_string = ret_string + " -> " + s.id_state
            ret_string = ret_string + " -> loop("
            for s in self.looping_states:
                ret_string = ret_string + " -> " + s.id_state
            ret_string = ret_string + ")"
        return ret_string


def extract_string_within(pattern, line, strip_whitespace=False):
    line = re.compile(pattern).search(line).group(1)
    if strip_whitespace:
        return re.sub(r"\s", "", line)
    return line

class CounterstrategyState:
    def __init__(self, name: str, inputs: dict, outputs: dict):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.influential_outputs = dict()
        self.successors = []
    
    def add_successor(self, state_name):
        self.successors.append(state_name)
    
    def __str__(self):
        return f"State: {self.name}\nInputs: {self.inputs}\nOutputs: {self.outputs}\nSuccessors: {', '.join(self.successors)}"

class Counterstrategy:

    def __init__(self, specification=""):
        self.specification = specification
        self.counterstrategy = spectra.generate_counter_strat(specification)
        self.states = dict()
        self.parse_counterstrategy(self.counterstrategy)
        for state in self.states.values():
            self.compute_influentials(state)
        self.num_states = len(self.states)
        # for state in self.states.values():
        #     print(state.name, state.influential_outputs)

    def __str__(self):
        state_strs = [str(state) for state in self.states.values()]
        return "\n".join(state_strs)

    def add_state(self, state):
        self.states[state.name] = state

    def get_state(self, name):
        return self.states.get(name)

    def parse_counterstrategy(self, cs: str):
        state_pattern = re.compile(r"State (\d+) <(.*?)>\s+With (?:no )?successors(?: : |.)(.*)(?:\n|$)")
        assignment_pattern = re.compile(r"(\w+):(\w+)")

        state_matches = re.finditer(state_pattern, cs)
        
        for match in state_matches:
            state_name = "S" + match.group(1)
            vars = dict(re.findall(assignment_pattern,  match.group(2)))
            inputs = {x:vars[x] for x in exp.inputVarsList}
            outputs = dict()
            for y in exp.outputVarsList:
                if y in vars:
                    outputs[y] = vars[y]
            state = CounterstrategyState(state_name, inputs, outputs)
            if not match.group(3) == '':
                state.successors = ["S"+i for i in match.group(3).split(", ")]
            # print(state)
            self.add_state(state)

    def compute_influentials(self, state: CounterstrategyState):
        for i in range(len(state.successors)-1):
            for j in range(i+1, len(state.successors)):
                next_state1 = state.successors[i]
                next_state2 = state.successors[j]

                if next_state1 == next_state2:
                    continue

                outputs1 = self.states[next_state1].outputs
                outputs2 = self.states[next_state2].outputs

                for var in outputs1:
                    if outputs1[var] != outputs2[var]:
                        self.states[next_state1].influential_outputs[var] = outputs1[var]
                        self.states[next_state2].influential_outputs[var] = outputs2[var]


    """
    Returns list of string literals
    @param name: description
    @type name: type
    @return: A list of string literals
    """
    def getValuation(self, state):
        literals = []
        for varname in state.inputs:
            if state.inputs[varname] == 'true':
                literals.append(varname)
            else:
                literals.append("!"+varname)
        for varname in state.influential_outputs:
        # for varname in state.outputs:
            if state.outputs[varname] == 'true':
                literals.append(varname)
            else:
                literals.append("!"+varname)
        return literals

    def getAdjacencyList(self):
        adjList = dict()
        for n in self.states:
            # Create a node for state Sx indexed by the integer x
            adjList[n] = []
            for successor in self.states[n]['successors']:
                adjList[n].append(successor)
        return adjList


    def initialize_state(self, state):
        if state in self.states: return
        self.states[state] = dict()
        # self.states[state]['successors'] = set()
        self.states[state]['input_valuation'] = dict()
        self.states[state]['output_valuation'] = dict()
        # self.states[state]['next_input_valuation'] = dict()

    def get_successors(self, states):
        successors = set()
        for s in states:
            successor = extract_string_within("->\s*([^\s]*)\s", s)
            successors.add(successor)
        return successors
    

    def extractRandomPath(self):
        """Extracts randomly a path from the counterstrategy"""

        # Build a State object for the initial state
        curr_state = "S0"
        # Perform a random walk from the initial state until hitting a failing state (no successors)
        # or completing a loop (which happens when visiting a state already visited in the walk)
        visited_states = ["S0"]
        looping = False
        loop_startindex = None

        if not self.counterstrategy:
            last_state = set()
            assignments = complete_deadlock_alt(last_state, self.specification)[0]

            input_vars = set(exp.inputVarsList)

            initial_state = State("S0")
            for var in assignments:
                # if re.sub(r'!', '', var) in input_vars:
                initial_state.add_to_valuation(var)

            last_state = assignments
            assignments = complete_deadlock_alt(last_state, self.specification)[0]
            # print("ASSIGNMENTS: ", assignments)

            transient_states = []
            initial_state.set_successor("Sf")
            failing_state = State("Sf")
            for var in assignments:
                # if re.sub(r'!', '', var) in input_vars:
                failing_state.add_to_valuation(var)
            transient_states.append(failing_state)

            looping_states = None
            return Path(initial_state,transient_states, None)

        while self.states[curr_state].successors != [] and not looping:

            curr_state = random.choice(self.states[curr_state].successors)

            if curr_state in visited_states:
                looping = True
                loop_startindex  = visited_states.index(curr_state)
            else:
                visited_states.append(curr_state)

        # print(self.states)
        # print("VISITED STATES: ", visited_states)
        # print("LOOPING: ", looping)

        initial_state = State("S0")
        for var in self.getValuation(self.states["S0"]):
            initial_state.add_to_valuation(var)
        # for var in self.states["S0"].inputs:
        #     initial_state.add_to_valuation(var if self.states["S0"].inputs[var] == 'true' else "!" + var)
        # # Does not make difference for AMBA
        # for var in self.states["S0"].influential_outputs:
        #     initial_state.add_to_valuation(var if self.states["S0"].influential_outputs[var] == 'true' else "!" + var)


        if len(visited_states)>1:
            initial_state.set_successor(visited_states[1])
            transient_states = []

            if not looping:
                # TODO: Treat DEAD as failing state?
                # If the path is not looping, all the remaining states are transient
                for i,state in enumerate(visited_states[1:]):
                    i = i + 1 # Indices start from 1, since we iterate from the second element
                    new_state = State(state)
                    if i < len(visited_states)-1:
                        new_state.set_successor(visited_states[i+1])

                    for var in self.getValuation(self.states[state]):
                        new_state.add_to_valuation(var)

                    transient_states.append(new_state)
                    # print("TRANSIENT STATES: ", transient_states)

                # If the path is not looping, it ends in a failing state
                # failing_state = State("Sf")
                # sf_input_valuation = self.states[transient_states[-1].id_state]['input_valuation']
                # for var in sf_input_valuation:
                #     failing_state.add_to_valuation(var if sf_input_valuation[var] == 1 else "!" + var)


                # Sf is failing for any output valuation. Pick one, for instance the same valuation as the previous state
                # sf_output_valuation = self.states["DEAD"]['output_valuation']
                # for var in sf_output_valuation:
                #    failing_state.add_to_valuation(var if sf_output_valuation[var] == 1 else "!" + var)

                # last_state = set()
                # for var in self.states[transient_states[-1].id_state].inputs:
                #     last_state.add(var if self.states[transient_states[-1].id_state].inputs[var] == 'true' else "!" + var)
                # for var in self.states[transient_states[-1].id_state].outputs:
                #     last_state.add(var if self.states[transient_states[-1].id_state].outputs[var] == 'true' else "!" + var)
                # assignments = complete_deadlock_alt(last_state, self.specification)

                # # input_vars = set(exp.inputVarsList)

                # failing_state = State("Sf")
                # for var in assignments[0]:
                #     # if re.sub(r'!', '', var) in input_vars:
                #     failing_state.add_to_valuation(var)

                # transient_states[-1].set_successor("Sf")
                # transient_states.append(failing_state)

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
            # The path contains the initial state only.
            # Two possible cases: the failure occurs in the initial state or it occurs in the next state.
            # If there is a next state, then there is a const_next_input field in the counterstrategy graph

            # last_state = set()
            # for var in self.states["S0"]['input_valuation']:
            #     last_state.add(var if self.states["S0"]['input_valuation'][var] == 1 else "!" + var)
            # for var in self.states["S0"]['output_valuation']:
            #     last_state.add(var if self.states["S0"]['output_valuation'][var] == 1 else "!" + var)
            # assignments = complete_deadlock_alt(last_state, self.specification)
            # print("ASSIGNMENTS: ", assignments)

            transient_states = []
            
            # initial_state.set_successor("Sf")
            # failing_state = State("Sf")
            # for var in self.getValuation(self.states["S0"]):
            #     failing_state.add_to_valuation(var)
            # transient_states.append(failing_state)

            # for var in assignments[0]:
            #         failing_state.add_to_valuation(var)
            # transient_states.append(failing_state)

            # sf_input_valuation = self.states[initial_state.id_state]['input_valuation']

            # if sf_input_valuation != dict():

            #     # Workaround field const_next_input to store the valuation of the failing state Sf
            #     initial_state.set_successor("Sf")
            #     failing_state = State("Sf")

            #     for var in sf_input_valuation:
            #         failing_state.add_to_valuation(var if sf_input_valuation[var] == 1 else "!" + var)
                
            #     # sf_output_valuation = self.states["DEAD"]['output_valuation']
            #     # for var in sf_output_valuation:
            #     #    failing_state.add_to_valuation(var if sf_output_valuation[var] == 1 else "!" + var)

            looping_states = None
        # print("INI: ", initial_state)
        # print("TRANSIENT: ", transient_states)
        return Path(initial_state,transient_states,looping_states)

    def extendFinitePath(self, path):
        """If path does not reach a guarantee violation, extends it with a new state where supposedly the violation
        occurs. Needed because RATSY sometimes stops finite counterruns some steps before the actual violation"""

        if path.transient_states[-1].id_state == "Sf":
            new_state_name = "Sf2"
        else:
            last_id = int((path.transient_states[-1].id_state)[2:])
            new_state_name = "Sf" + str(last_id+1)

        # The new state will have the constant input variables set to the value defined in the counterstrategy.
        # Since this state does not come from the counterstrategy graph, at this point we are sure there are no
        # other pieces of input valuation in the previous state
        
        input_vars = set(exp.inputVarsList)

        failing_state = State(new_state_name)
        last_state = path.transient_states[-1].valuation
        assignments = complete_deadlock_alt(last_state, self.specification)[0]
        for var in assignments:
            # if re.sub(r'!', '', var) in input_vars:
            failing_state.add_to_valuation(var)

        path.states[new_state_name] = failing_state
        path.transient_states[-1].set_successor(new_state_name)
        path.transient_states.append(failing_state)

        return path

def main():

    specification = "Examples/cimattiAnalyzing/amba_ahb_w_guar_trans_amba_ahb_1_normalised.spectra"
    # specification = "Examples/Protocol.spectra"

    # c = Counterstrategy(specification)
    # This shows how to access nodes and edges of the graph in the DOT file
    # print "Nodes: "
    # print str(c.graph[0].obj_dict['nodes']).replace(', ','\n')
    # print "\n\nEdges: "
    # print str(c.graph[0].obj_dict['edges']).replace(', ', '\n')

    # c.counterstrategy = [
    #     'S0 -> S0 {req:false, cl:true} / {gr:false, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:false, val:true};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:true, val:true};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:false, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:false, val:true};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:true, val:true};',
    #     'S0 -> S1 {req:false, cl:true} / {gr:false, val:false};',
    # ]

    # c.counterstrategy = [
    #     'S0 -> S0 {req:false, cl:true} / {gr:false, val:false};',
    #     'S0 -> S1 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S2 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S3 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S4 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S5 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S6 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:true, val:false};',
    # ]

    # print ("===== Randomly extracted path")
    # p = c.extractRandomPath()
    # for s in p.states:
    #     print("State: "+p.states[s].id_state+" Valuation: "+p.states[s].get_valuation()+" Successor: "+str(p.states[s].successor))
    # print("Looping states:")
    # for s in p.looping_states:
    #     print(s.id_state)

    # This tests counterstrategy fields
    # print("===== Counterstrategy structure")
    # print(str(c.states))

    # for i in range(5):
    #     print ("===== Randomly extracted path")
    #     p = c.extractRandomPath()
    #     for s in p.states:
    #         print("State: "+p.states[s].id_state+" Valuation: "+p.states[s].get_valuation()+" Successor: "+str(p.states[s].successor))
    #     print("Looping states:")
    #     for s in p.looping_states:
    #         print(s.id_state)

    lines = spectra.generate_counter_strat(specification)
    trace_list, cs_count = counter_strat_to_trace(lines, specification=specification)
    trace_list = trace_list[0].split("\n")
    valuations = []
    for assignment in trace_list:
        print(assignment)
        matches = re.search(r'holds_at\(([^,]+),\s*(\d+)', assignment)
        if matches:
            var = matches.group(1)
            state = int(matches.group(2))
            if state == 0:
                state = "S0"
            else:
                state = "S" + str(state - 1)
            valuation = var + "__" + state
            if re.search("not", assignment):
                valuation = "!" + valuation
            valuations.append(valuation)

    print(" & ".join(valuations))

if __name__ == '__main__':
    main()