import re
import LTL2Boolean as l2b
import os
import definitions
import syntax_utils as su
import subprocess
import time
import random
import specification as sp
from counterstrategy import Counterstrategy
from typing import Tuple, List, Dict, Any
import mathsat_utils as msu

class NonStateSeparableException(BaseException):
    pass

class NonIOSeparableException(BaseException):
    pass


def getStateFromLiteral(literal):
    # literal is an su.BoolOperand object
    return str(literal).split("__")[1]

def computeOtherNode(operand):
    # An OR, IMPLIES or DIMPLIES node can yield at most one state component
    # Actually this code works for single operands too
    state_component = str(operand)

    # Check all literals refer to the same state
    # Extract all unique states referenced in state_component
    states = set(re.findall(r"__\w+",state_component))
    if len(states)==1:
        state = states.pop().strip("__")
        return {state: state_component}
    else:
        raise NonStateSeparableException

def computeAndNode(and_node):
    """Extracts the state components from a subtree whose root is an AND node.
    The parameter is an su.BoolAnd object"""
    state_components = dict()

    # Optimization: Since the current node is an AND node, and since AND is idempotent
    # (a & a \equiv a), I loop over unique args of the AND to avoid a & a expressions
    for operand in set(and_node.args):
        if isinstance(operand,su.BoolAnd):
            state_components_op = computeAndNode(operand)
        else:
            state_components_op = computeOtherNode(operand)

        for state in state_components_op:
            if state in state_components:
                state_components[state] = state_components[state] + " & " + state_components_op[state]
            else:
                state_components[state] = state_components_op[state]

    return state_components

def removeStateReferences(formula):
    """Removes all state references from the literals in formula"""
    return re.sub(r"__\w+","",formula)

def extractStateComponents(interpolant):
    """Extracts the state components of an interpolant. Exception if the interpolant is not state-separable"""
    state_components = dict()
    parse_tree = su.getParseTreeFromBoolean(interpolant)

    if(isinstance(parse_tree,su.BoolAnd)):
        state_components = computeAndNode(parse_tree)
    elif(isinstance(parse_tree,su.BoolBinary)):
        state_components = computeOtherNode(parse_tree)
    else:
        state_components[getStateFromLiteral(parse_tree)] = str(parse_tree)
    # Remove state references from literals (they are useless by now)
    return {state: removeStateReferences(component) for state, component in state_components.items()}

def projectOtherNode(node,variables):
    projection = str(node)
    varnames = set(re.findall(r"\w+",projection))
    if all(varname in variables for varname in varnames):
        return projection
    else:
        return ""

def projectAndNode(and_node,variables):
    projection = ""
    for operand in and_node.args:
        if isinstance(operand,su.BoolAnd):
            # Initialize the projection with the expression of the child. If the projection already contains some parts,
            # put the current operand projection in conjunction with those parts
            operand_proj = projectAndNode(operand,variables)
            projection = projection + (" & " if projection != "" and operand_proj != "" else "") + operand_proj
        else:
            operand_proj = projectOtherNode(operand,variables)
            projection = projection + (" & " if projection != "" and operand_proj != "" else "") + operand_proj
    return projection

def projectOntoVars(state_component,variables):
    """Extracts the projection of a state component onto the given variables. Exception if a state component is not I/O-separable"""
    parse_tree = su.getParseTreeFromBoolean(state_component)
    if isinstance(parse_tree,su.BoolAnd):
        projection = projectAndNode(parse_tree,variables)
    else:
        projection = projectOtherNode(parse_tree,variables)
    if projection != "":
        return projection
    else:
        raise NonIOSeparableException

def contains_aux_vars(assumption):
    return "aux" in assumption or "CONSTRAINT" in assumption

def getRefinementsFromStateComponents(state_components, path, input_vars):
    refinements = []
    non_io_separable_state_components = 0
    # First refinement: negation of initial condition
    if path.initial_state.id_state in state_components:
        try:
            refinements.append("!(" + projectOntoVars(state_components[path.initial_state.id_state], input_vars) + ")")
        except NonIOSeparableException:
            print("Initial state component not I/O-separable")
            non_io_separable_state_components += 1
    # For each pair of consecutive states, extract an invariant
    for state in path.states:
        if path.states[state].successor is not None and state in state_components and path.states[state].successor in state_components:
            try:
                refinements.append("G((" + state_components[state] + ") -> X(!(" + projectOntoVars(state_components[path.states[state].successor], input_vars) + ")))")
            except NonIOSeparableException:
                # If next state component is not IO-separable, the current state component may be anyway
                try:
                    refinements.append("G(!(" + projectOntoVars(state_components[state], input_vars) + "))")
                except NonIOSeparableException:
                    # Increase the number of non-IO-separable components here, since if I did before, when the non-separable
                    # component is the next one, this would be counted twice
                    non_io_separable_state_components += 1
                    print("State " + path.states[state].successor + " component not I/O-separable")
        # elif path.states[state].successor is not None and state not in state_components and path.states[state].successor in state_components:
        #     try:
        #         refinements.append("G((" + " & ".join(path.states[state].valuation) + ") -> X(!(" + projectOntoVars(state_components[path.states[state].successor], input_vars) + ")))")
        #     except NonIOSeparableException:
        #         # If next state component is not IO-separable, the current state component may be anyway
        #         try:
        #             refinements.append("G(!(" + projectOntoVars(state_components[state], input_vars) + "))")
        #         except NonIOSeparableException:
        #             # Increase the number of non-IO-separable components here, since if I did before, when the non-separable
        #             # component is the next one, this would be counted twice
        #             non_io_separable_state_components += 1
        #             print("State " + path.states[state].successor + " component not I/O-separable")
        elif (path.states[state].successor is None or path.states[state].successor not in state_components) and state in state_components:
            try:
                # Need next?
                refinements.append("G(!(" + projectOntoVars(state_components[state], input_vars) + "))")
                # refinements.append("G(!X(" + projectOntoVars(state_components[state],input_vars) + "))")
            except NonIOSeparableException:
                non_io_separable_state_components += 1
                print("State " + state + " component not I/O-separable")
    # Fairness condition: if each and every looping state has a state component, then extract a fairness condition from it
    # This applies only when path is looping
    if path.is_loop:
        if all(path.looping_states[i].id_state in state_components for i in range(len(path.looping_states))):
            looping_state_components = []
            for looping_state in path.looping_states:
                looping_state_components.append(state_components[looping_state.id_state])
            refinements.append("G(F(!(" + ") & !(".join(list(set(looping_state_components))) +")))")
        if path.unrolled_states and all(path.unrolled_states[i].id_state in state_components for i in range(len(path.unrolled_states))):
            # If the path is unrolled, then the unrolled states are also looping states
            unrolled_state_components = []
            for unrolled_state in path.unrolled_states:
                unrolled_state_components.append(state_components[unrolled_state.id_state])
            refinements.append("G(F(!(" + ") & !(".join(list(set(unrolled_state_components))) +")))")

    # Filter out refinements with aux variables
    refinements = [asm for asm in refinements if not contains_aux_vars(asm)]

    return sorted(list(set(refinements))), non_io_separable_state_components
    # return sorted(list(set(refinements)), reverse=True), non_io_separable_state_components


def compute_interpolant(id, assum_val_boolean, guarantees_boolean):
    if assum_val_boolean ==[] or guarantees_boolean == []:
        return None
    
    counterstrategy_file = f"temp/counterstrategy_auto_{id}"
    guarantees_file = f"temp/guarantees_auto_{id}"

    l2b.writeMathsatFormulaToFile(counterstrategy_file, assum_val_boolean)
    l2b.writeMathsatFormulaToFile(guarantees_file, " & ".join(guarantees_boolean))
    
    interpolant_file = f"temp/INTERP_{id}"

    MATHSAT_PATH = os.path.join(definitions.ROOT_DIR, "MathSAT4/mathsat-4.2.17-linux-x86_64/bin/mathsat")
    cmd = [MATHSAT_PATH, f"-interpolate={interpolant_file}", counterstrategy_file, guarantees_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(result.stdout)
    interpolant_file = interpolant_file + ".1.msat"

    interpolant = None
    if os.path.isfile(interpolant_file):
        interpolant = l2b.parseInterpolant(interpolant_file)
        os.remove(interpolant_file)

    # os.remove(counterstrategy_file)
    # os.remove(guarantees_file)
    return interpolant


def generateRefinements(
        counterstrategy: Counterstrategy,
        assumptions: List[str],
        guarantees: List[str],
        input_vars: List[str]
    ) -> Tuple[List[str], Dict[str, Any]]:

    metrics = {
        "path_length": 0,
        "path_is_looping": False,
        "interpolant": None,
        "time_interpolation": None,
        "is_interpolant_state_separable": False,
        "num_state_components": 0,
        "num_non_io_separable_state_components": 0,
        "is_interpolant_fully_separable": False,
    }

    print("Extracting random path from counterstrategy...")
    path = counterstrategy.extract_random_path()
    print("Path extracted:", path)
    print("Unrolling path...")
    path.unroll()
    print("Path unrolled:", path)

    metrics["path_length"] = len(path.states)
    metrics["path_is_looping"] = path.is_loop

    # Convert assumptions and guarantees to format suitable for LTL2Boolean
    assumptions = [re.sub(r"\s", "", line) for line in sp.unspectra(assumptions)]
    guarantees = [re.sub(r"\s", "", line) for line in sp.unspectra(guarantees)]
    # print("Guarantees:", "\n".join(guarantees))

    print("Translating assumptions to boolean...")
    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(asm, path) for asm in assumptions]))
    # print("Assumptions translated:", "\n".join(assumptions_boolean))

    print("Extracting valuations from path...")
    valuations_boolean = path.get_valuation()
    # print("Valuations:", valuations_boolean)

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean

    print("Translating guarantees to boolean...")
    guarantees_boolean = list(filter(None,[l2b.gr1LTL2Boolean(gar, path) for gar in guarantees]))
    # print("Guarantees translated:", "\n".join(guarantees_boolean))

    # valuations_env = " & ".join([v for v in valuations_boolean.split(" & ") if v.lstrip("!").split("__")[0] in input_vars])
    # print("Valuations environment:", valuations_env)

    # valuations_sys = " & ".join([v for v in valuations_boolean.split(" & ") if v.lstrip("!").split("__")[0] not in input_vars])
    # print("Valuations system:", valuations_sys)

    # valuations_boolean = valuations_env

    # if valuations_sys != "":
        # guarantees_boolean += ["((" + valuations_env + ") -> (" + valuations_sys + "))"]
    # print("Updated guarantees with valuations:", "\n".join(guarantees_boolean))    

    # print("Valuations are satisfiable:", msu.is_satisfiable(valuations_boolean))
    # print("Guarantees are satisfiable:", msu.is_satisfiable(" & ".join(guarantees_boolean)))
    # print("Valuations and guarantees are satisfiable:", msu.is_satisfiable(valuations_boolean + " & " + " & ".join(guarantees_boolean)))
    # print("Valuations environment are satisfiable:", msu.is_satisfiable(valuations_env))
    # print("Valuations environment and guarantees are satisfiable:", msu.is_satisfiable(valuations_env + " & " + " & ".join(guarantees_boolean)))
    # print("Valuations system and guarantees are satisfiable:", msu.is_satisfiable(valuations_sys + " & " + " & ".join(guarantees_boolean)))

    if not msu.is_satisfiable(" & ".join(guarantees_boolean)):
        raise AssertionError("The conjunction of guarantees is not satisfiable.")

    print("Computing interpolant...")
    time_interpolation_start = time.perf_counter()
    # TODO: use new msu module
    # interpolant = compute_interpolant(id, assum_val_boolean, guarantees_boolean)
    interpolant = compute_interpolant(id, valuations_boolean, guarantees_boolean)
    metrics["time_interpolation"] = time.perf_counter() - time_interpolation_start
    # interpolant = compute_interpolant(id, valuations_env, guarantees_boolean)
    # interpolant = compute_interpolant(id, " & ".join(assumptions_boolean) + " & " + valuations_env, guarantees_boolean)
    metrics["interpolant"] = interpolant
    print("Interpolant computed:", interpolant)

    if interpolant is None:
        print("[x] No interpolant for " + assum_val_boolean +"\n and guarantees " + " & ".join(guarantees_boolean) + "\n on path " + str(path))
        return [], metrics

    if interpolant == "false" or interpolant == "true":
        return ["FALSE"], metrics

    state_components = dict()
    
    try:
        print("Extracting state components from interpolant...")
        state_components = extractStateComponents(interpolant)
        print("State components extracted:", state_components)

        metrics["is_interpolant_state_separable"] = len(state_components) > 0
        metrics["num_state_components"] = len(state_components)

    except NonStateSeparableException:
        # If the interpolant is not state separable, just skip this particular counterstrategy.
        # To think about: is it possible to come up with refinements even in case of a non-state-separable interpolant?
        print("[x] Non-state-separable interpolant for " + assum_val_boolean + "\n and guarantees " + " & ".join(guarantees_boolean))
    
    if state_components == dict():
        return [], metrics

    print("Generating refinements from state components...")
    refinements, num_non_io_separable_state_components = getRefinementsFromStateComponents(state_components, path, input_vars)
    print("Refinements generated:", refinements)

    metrics["num_non_io_separable_state_components"] = num_non_io_separable_state_components
    if num_non_io_separable_state_components == 0:
        metrics["is_interpolant_fully_separable"] = True

    return refinements, metrics
