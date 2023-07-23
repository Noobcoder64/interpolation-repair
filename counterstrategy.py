# import pydot
import random
import re
import spectra_utils as spectra
import copy
import specification as sp

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
    disjuncts = expression.split("|")
    for disjunct in disjuncts:
        conjuncts = disjunct.split("&")
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
    expressions = [re.sub(r"\(|\)", "", x) for x in expressions]
    expressions = [re.sub(r"\|", ";", x) for x in expressions]
    expressions = [re.sub(r"!", " not ", x) for x in expressions]
    expressions = [re.sub(r"&", ",", x) for x in expressions]
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
    expressions = aspify(expressions)
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

    unsat_next_exp_s = unsat_nexts(new_state, primed_expressions_cleaned_s)

    if unsat_next_exp + unsat_next_exp_s + unprimed_expressions + unprimed_expressions_s == []:
        # Pick random assignment
        vars = [var for var in variables if not re.search("prev_", var)]
        i = random.choice(range(2 ** len(vars)))
        # TODO: replace i with 0 for deadlock - in order to make deterministic
        i = 0
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

def complete_deadlock_alt(trace, file, deadlock_number):
    file = re.sub("_patterned", "", file)
    initial_expressions, prevs, primed_expressions, unprimed_expressions, variables = sp.extract_expressions(file,
                                                                                                          counter_strat=True)
    initial_expressions_s, prevs_s, primed_expressions_s, unprimed_expressions_s, variables_s = sp.extract_expressions(
        file,
        guarantee_only=True)

    print(unprimed_expressions_s)

    primed_expressions_cleaned = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions]
    primed_expressions_cleaned_s = [re.sub(r"PREV\((!*)([^\|^\(]*)\)", r"\1prev_\2", x) for x in primed_expressions_s]
    final_state = last_state(trace, prevs)
    assignments, is_violating = next_possible_assignments(final_state, primed_expressions_cleaned,
                                                          primed_expressions_cleaned_s, unprimed_expressions,
                                                          unprimed_expressions_s, variables)
    if assignments is None:
        return None
    return state_to_asp(random.choice(assignments), trace, deadlock_number)


def complete_deadlock(trace, file, deadlock_number):
    return complete_deadlock_alt(trace, file, deadlock_number)

def counter_strat_to_trace(lines=[], deadlock_required=[], cs_count=0, specification=""):
        # if lines == []:
        #     lines = read_file(cs)
        start = "INI"
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
        print(files)
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

class Counterstrategy:

    def __init__(self, specification=""):
        self.specification = specification
        self.counterstrategy = spectra.generate_counter_strat(specification)
        self.states = dict()

        # for n in self.graph[0].obj_dict['nodes']:
        #     if n[0] == 'S':
        #         # print(n)
        #         self.states[n] = dict()
        #         self.states[n]['successors'] = set()
        #         self.states[n]['input_valuation'] = dict()
        #         self.states[n]['next_input_valuation'] = dict()
        #         self.states[n]['output_valuation'] = dict()
        #         # Extract next input values
        #         # print(self.graph[0].obj_dict['nodes'][n][0]['attributes'])
        #         next_input_list = self.graph[0].obj_dict['nodes'][n][0]['attributes']['label'].rsplit('|',1)[1].strip('" ').rstrip("\\n ").split("\\n ")
        #         for var in next_input_list:
        #             if var != "":
        #                 varname = var.split("=")[0]
        #                 value = var.split("=")[1]
        #                 if value == "True":
        #                     self.states[n]['next_input_valuation'][varname] = 1
        #                 elif value == "False":
        #                     self.states[n]['next_input_valuation'][varname] = 0
        #                 else:
        #                     self.states[n]['next_input_valuation'][varname] = int(value)
        #         #print n + ": "+str(self.states[n]['next_input_valuation'])

        # # Read output valuations and successor relations from edges
        # for e in self.graph[0].obj_dict['edges']:
        #     if e[0] != 'A':
        #         self.states[e[0]]['successors'].add(e[1])
        #         # Edge labels contain valuations of output variables
        #         label = self.graph[0].obj_dict['edges'][e][0]['attributes']['label'].strip('" ').rstrip("\\n")
        #         if label != "":
        #             vars = label.split("\\n")
        #             for var in vars:
        #                 varname = var.split("=")[0]
        #                 value = int(var.split("=")[1])
        #                 # Add the variable to the valuation of the destination state
        #                 self.states[e[1]]['output_valuation'][varname] = value


        # # Extract constant next input values
        # const_next_input_list = self.graph[0].obj_dict['nodes']['ConstantNextInputs'][0]['attributes']['label'].strip('" ').replace("Constant next input values:\\n ", "").rstrip("\\n").split("\\n ")
        # # Remove empty string from the list of constant inputs
        # const_next_input_list = [x for x in const_next_input_list if x != ""]


        # for n in self.states:
        #     if n != "S0":
        #         for var in const_next_input_list:
        #             varname = var.split("=")[0]
        #             value = int(var.split("=")[1])
        #             self.states[n]['input_valuation'][varname] = value

        #     for var in self.states[n]['next_input_valuation']:
        #         for succ_n in self.states[n]['successors']:
        #             self.states[succ_n]['input_valuation'][var] = self.states[n]['next_input_valuation'][var]

        # # Workaround for keeping ConstantNextInput when a counterstrategy has initial state only
        # # (used in extractRandomPath)
        # self.states["S0"]['const_next_input'] = dict()
        # for var in const_next_input_list:
        #     varname = var.split("=")[0]
        #     value = var.split("=")[1]
        #     if value != 'X':
        #         value = int(value)
        #         self.states["S0"]['const_next_input'][varname] = value

        # RATSY does not return the initial state valuation in the counterstrategy graph. Must be read from the BDDs
        # marduk = counterstrategy_bdd[0]
        # for var_obj in marduk.input_vars:
        #     varname = var_obj.get_name()
        #     (can_be_1, can_be_0) = marduk.spec_debug_utils.get_val(counterstrategy_bdd[1], var_obj, False)
        #     if can_be_1 and not can_be_0:
        #         self.states["S0"]['input_valuation'][varname] = 1
        #     elif can_be_0 and not can_be_1:
        #         self.states["S0"]['input_valuation'][varname] = 0
        #     else:
        #         self.states["S0"]['input_valuation'][varname] = random.randint(0,1)


    def getValuation(self, state):
        literals = []
        for varname in state["input_valuation"]:
            if state["input_valuation"][varname]:
                literals.append(varname)
            else:
                literals.append("!"+varname)
        for varname in state["output_valuation"]:
            if state["output_valuation"][varname]:
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

    def influential_output_valuations(self, transitions):

        for i in range(len(transitions)-1):
            for j in range(i+1, len(transitions)):
                next_state1 = extract_string_within("->\s*([^\s]*)\s", transitions[i])
                next_state2 = extract_string_within("->\s*([^\s]*)\s", transitions[j])

                if next_state1 == next_state2:
                    continue

                vars1 = re.compile("/\s*{(.*)}", ).search(transitions[i]).group(1).split(', ')
                vars2 = re.compile("/\s*{(.*)}", ).search(transitions[j]).group(1).split(', ')

                for k in range(len(vars1)):

                    varname1 = vars1[k].split(":")[0]
                    varname2 = vars2[k].split(":")[0]
                    if varname1 != varname2:
                        raise Exception("Variables not equal")
                    value1 = int(vars1[k].split(":")[1] == 'true')
                    value2 = int(vars2[k].split(":")[1] == 'true')
                    if value1 != value2:
                        self.initialize_state(next_state1)
                        self.states[next_state1]['output_valuation'][varname1] = value1
                        self.initialize_state(next_state2)
                        self.states[next_state2]['output_valuation'][varname2] = value2

    def extractRandomPath(self):
        """Extracts randomly a path from the counterstrategy"""

        # Build a State object for the initial state
        curr_state = "INI"
        # Perform a random walk from the initial state until hitting a failing state (no successors)
        # or completing a loop (which happens when visiting a state already visited in the walk)
        visited_states = ["INI"]
        looping = False
        loop_startindex = None

        while curr_state and not looping:
            
            # pattern = re.compile("^" + curr_state + " -> " + r"(?!DEAD)")
            # pattern = re.compile("^" + curr_state + r" -> (" + "|".join(visited_states) + r")")
            pattern = re.compile("^" + curr_state)
            transitions = list(filter(pattern.search, self.counterstrategy))
            # print("TRANSITIONS from:", curr_state)
            # for t in transitions:
            #     print(t)
            # print()

            if transitions == []:
                pattern = re.compile("^" + curr_state)
                transitions = list(filter(pattern.search, self.counterstrategy))

            self.initialize_state(curr_state)
            # self.states[curr_state]['successors'] = self.get_successors(transitions)


            # print("STATES:", states)
            transition = random.choice(transitions)
            next_state = extract_string_within("->\s*([^\s]*)\s", transition)
            self.initialize_state(next_state)

            vars = re.compile("{(.*)}\s*/", ).search(transition).group(1).split(', ')
            for var in vars:
                varname = var.split(":")[0]
                value = int(var.split(":")[1] == 'true')
                self.states[curr_state]['input_valuation'][varname] = value
            
            # TODO: output valuation is of current state
            # vars = re.compile("/\s*{(.*)}", ).search(transition).group(1).split(', ')
            # for var in vars:
            #     varname = var.split(":")[0]
            #     value = int(var.split(":")[1] == 'true')
            #     self.states[next_state]['output_valuation'][varname] = value

            self.influential_output_valuations(transitions)

            # vars = re.compile("{(.*)}\s*/", ).search(transition).group(1).split(', ')
            # for var in vars:
            #     varname = var.split(":")[0]
            #     value = int(var.split(":")[1] == 'true')
            #     self.states[curr_state]['next_input_valuation'][varname] = value

            curr_state = next_state
            
            if curr_state in visited_states:
                looping = True
                loop_startindex  = visited_states.index(curr_state)
            elif curr_state == "DEAD":
                curr_state = None
            else:
                visited_states.append(curr_state)

        # print(self.states)
        # print("VISITED STATES: ", visited_states)
        # print("LOOPING: ", looping)

        initial_state = State("INI")
        for var in self.states["INI"]['input_valuation']:
            initial_state.add_to_valuation(var if self.states["INI"]['input_valuation'][var] == 1 else "!" + var)

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
                failing_state = State("Sf")
                # sf_input_valuation = self.states[transient_states[-1].id_state]['input_valuation']
                # for var in sf_input_valuation:
                #     failing_state.add_to_valuation(var if sf_input_valuation[var] == 1 else "!" + var)


                # Sf is failing for any output valuation. Pick one, for instance the same valuation as the previous state
                # sf_output_valuation = self.states["DEAD"]['output_valuation']
                # for var in sf_output_valuation:
                #    failing_state.add_to_valuation(var if sf_output_valuation[var] == 1 else "!" + var)

                transient_states[-1].set_successor("Sf")
                transient_states.append(failing_state)

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
            sf_input_valuation = self.states[initial_state.id_state]['input_valuation']
            transient_states = []
            if sf_input_valuation != dict():

                # Workaround field const_next_input to store the valuation of the failing state Sf
                initial_state.set_successor("Sf")
                failing_state = State("Sf")

                # for var in sf_input_valuation:
                #     failing_state.add_to_valuation(var if sf_input_valuation[var] == 1 else "!" + var)
                
                # sf_output_valuation = self.states["DEAD"]['output_valuation']
                # for var in sf_output_valuation:
                #    failing_state.add_to_valuation(var if sf_output_valuation[var] == 1 else "!" + var)

                transient_states.append(failing_state)


            looping_states = None
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
        sf_input_valuation = self.states['INI']['input_valuation']
        failing_state = State(new_state_name)
        path.states[new_state_name] = failing_state
        path.transient_states[-1].set_successor(new_state_name)
        path.transient_states.append(failing_state)
        for var in sf_input_valuation:
            failing_state.add_to_valuation(var if sf_input_valuation[var] == 1 else "!" + var)

        return path

def main():

    specification = "Examples/cimattiAnalyzing/amba_ahb_w_guar_trans_amba_ahb_1.spectra"
    # specification = "Examples/Protocol.spectra"

    # c = Counterstrategy(specification)
    # This shows how to access nodes and edges of the graph in the DOT file
    # print "Nodes: "
    # print str(c.graph[0].obj_dict['nodes']).replace(', ','\n')
    # print "\n\nEdges: "
    # print str(c.graph[0].obj_dict['edges']).replace(', ', '\n')

    # c.counterstrategy = [
    #     'INI -> S0 {req:false, cl:true} / {gr:false, val:false};',
    #     'INI -> DEAD {req:false, cl:true} / {gr:false, val:true};',
    #     'INI -> S0 {req:false, cl:true} / {gr:true, val:false};',
    #     'INI -> DEAD {req:false, cl:true} / {gr:true, val:true};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:false, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:false, val:true};',
    #     'S0 -> S0 {req:false, cl:true} / {gr:true, val:false};',
    #     'S0 -> DEAD {req:false, cl:true} / {gr:true, val:true};',
    #     'INI -> S1 {req:false, cl:true} / {gr:false, val:false};',
    # ]

    # c.counterstrategy = [
    #     'INI -> S0 {req:false, cl:true} / {gr:false, val:false};',
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
    print(trace_list)

if __name__ == '__main__':
    main()