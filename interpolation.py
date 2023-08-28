import re
import copy
from counterstrategy import Counterstrategy
import LTL2Boolean as l2b
import os
import definitions
import syntax_utils as su
import specification as sp
import spectra_utils as spectra
import experiment_properties as exp

class NonStateSeparableException(BaseException):
    pass

class NonIOSeparableException(BaseException):
    pass


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
    return {state: removeStateReferences(component) for state,component in state_components.items()}

def projectOtherNode(node,variables):
    projection = str(node)
    # print("NODE: ", projection)
    varnames = set(re.findall(r"\w+",projection))
    # print("VARNAMES: ", varnames)
    # print("VARIABLES: ", variables)
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
    # print("PROJECTION: ", projection)
    if projection != "":
        return projection
    else:
        raise NonIOSeparableException

def getRefinementsFromStateComponents(state_components,path,input_vars):
    refinements = []
    non_io_separable_state_components = 0
    # First refinement: negation of initial condition
    if path.initial_state.id_state in state_components:
        try:
            refinements.append("!("+projectOntoVars(state_components[path.initial_state.id_state],input_vars)+")")
        except NonIOSeparableException:
            print("Initial state component not I/O-separable")
            non_io_separable_state_components = non_io_separable_state_components + 1
    # For each pair of consecutive states, extract an invariant
    for state in path.states:
        if path.states[state].successor is not None and state in state_components and path.states[state].successor in state_components:
            try:
                refinements.append("G(("+state_components[state]+") -> X(!("+projectOntoVars(state_components[path.states[state].successor],input_vars)+")))")
            except NonIOSeparableException:
                # If next state component is not IO-separable, the current state component may be anyway
                try:
                    refinements.append("G(!(" + projectOntoVars(state_components[state], input_vars) + "))")
                except NonIOSeparableException:
                    # Increase the number of non-IO-separable components here, since if I did before, when the non-separable
                    # component is the next one, this would be counted twice
                    non_io_separable_state_components = non_io_separable_state_components + 1
                    print("State "+path.states[state].successor+" component not I/O-separable 1")
        elif (path.states[state].successor is None or path.states[state].successor not in state_components) and state in state_components:
            try:
                refinements.append("G(!(" + projectOntoVars(state_components[state],input_vars) + "))")
            except NonIOSeparableException:
                non_io_separable_state_components = non_io_separable_state_components + 1
                print("State " + state + " component not I/O-separable 2")
    # Fairness condition: if each and every looping state has a state component, then extract a fairness condition from it
    # This applies only when path is looping
    if path.is_loop:
        if all(path.looping_states[i].id_state in state_components for i in range(len(path.looping_states))):
            looping_state_components = []
            for looping_state in path.looping_states:
                looping_state_components.append(state_components[looping_state.id_state])
            refinements.append("G(F(!("+ ") & !(".join(list(set(looping_state_components))) +")))")

    return list(set(refinements)),non_io_separable_state_components


def compute_interpolant(id, assum_val_boolean, guarantees_boolean):
    l2b.writeMathsatFormulaToFile("temp/counterstrategy_auto_" + id, assum_val_boolean)
    l2b.writeMathsatFormulaToFile("temp/guarantees_auto_" + id, guarantees_boolean)
    
    mathsat_path = os.path.join(definitions.ROOT_DIR, "MathSAT4/mathsat-4.2.17-linux-x86_64/bin/mathsat")
    os.system(f"{mathsat_path} -interpolate=temp/INTERP_{id} temp/counterstrategy_auto_{id} temp/guarantees_auto_{id}")
    
    interpolant_file = f"temp/INTERP_{id}.1.msat"
    
    if os.path.isfile(interpolant_file):
        interpolant = l2b.parseInterpolant(interpolant_file)
        if interpolant == "false":
            os.remove("temp/counterstrategy_auto_" + id)
            os.remove("temp/guarantees_auto_" + id)
            os.remove(interpolant_file)
            return "false"

        print("\n=== INTERPOLANT ===")
        print(interpolant)

        return interpolant
    
    return None

def GenerateAlternativeRefinements(id, c,assumptions_uc,guarantees_uc,input_vars,output_vars):
    # assumptions_uc = []
    # PROBLEM
    guarantees_uc = exp.guaranteesList

    print()
    print("=== COUNTERSTRATEGY ===")
    print(c)
    print()

    path = c.extractRandomPath()
    # path.unroll()

    print("=== COUNTERRUN ===")
    print(path)
    print(path.initial_state)
    print(path.transient_states)
    print(path.looping_states)
    print()



    assumptions_boolean = list(filter(None,[l2b.gr1LTL2Boolean(x,path) for x in assumptions_uc]))

    valuations_boolean = path.get_valuation()

    if assumptions_boolean != []:
        assum_val_boolean = " & ".join(assumptions_boolean) + ((" & " + valuations_boolean) if valuations_boolean != "" else "")
    else:
        assum_val_boolean = valuations_boolean

    guarantees_boolean = " & ".join(filter(None,[l2b.gr1LTL2Boolean(x, path) for x in guarantees_uc]))

    print("=== UNREALIZABLE CORE ===")
    for uc in guarantees_uc:
        print(uc)
    print()
    
    print("=== ASSUMPTIONS BOOLEAN ===")
    print(" & ".join(assumptions_boolean))
    print()
    print("=== VALUATIONS BOOLEAN ===")
    print(valuations_boolean)
    print()
    # print("=== ASM VAL BOOLEAN ===")
    # print(assum_val_boolean)
    print("=== GUARANTEES BOOLEAN ===")
    print(guarantees_boolean)
    print()

    interpolant  = compute_interpolant(id, assum_val_boolean, guarantees_boolean)

    state_components = dict()
    # Parse the interpolant file
    if interpolant is not None:
        if interpolant == "false":
            return ["FALSE"]
        
        try:
            state_components = extractStateComponents(interpolant)
            print()
            print("=== STATE COMPONENTS ===")
            print(state_components)
        except NonStateSeparableException:
            # If the interpolant is not state separable, just skip this particular counterstrategy.
            # To think about: is it possible to come up with refinements even in case of a non-state-separable interpolant?
            state_components = dict()
            print("Non-state-separable interpolant for " + assum_val_boolean + "\n and guarantees " + guarantees_boolean)
    else:
        raise Exception("Counterstrategy does not violate unrealizable core")
        if path.is_loop:
            path.unroll()
        else:
            # If no interpolant was produced, the solver returned SAT
            # Try extending the finite path by one failing state and repeat interpolation on the new path
            path = c.extendFinitePath(path)

        assumptions_boolean = list(filter(None, [l2b.gr1LTL2Boolean(x, path) for x in assumptions_uc]))

        # Avoid repeating the initial state's valuation twice in the counterrun expression
        literals_valuation = []
        for literal in path.initial_state.valuation:
            if literal not in assumptions_boolean:
                literals_valuation.append(literal+"__"+path.initial_state.id_state)
        valuation_components = [" & ".join(literals_valuation)]
        for state in path.states.values():
            valuation_components.append(state.get_valuation())
        valuations_boolean = " & ".join(valuation_components)

        # First term of interpolation
        if assumptions_boolean != []:
            assum_val_boolean = " & ".join(assumptions_boolean) + (
                (" & " + valuations_boolean) if valuations_boolean != "" else "")
        else:
            assum_val_boolean = valuations_boolean
        
        # Second term of interpolation
        # filter(None,l) removes empty strings from l
        guarantees_boolean = " & ".join(filter(None, [l2b.gr1LTL2Boolean(x, path) for x in guarantees_uc]))

        print("=== UNREALIZABLE CORE ===")
        for uc in guarantees_uc:
            print(uc)
        print()

        print("=== ASSUMPTIONS BOOLEAN ===")
        print(" & ".join(assumptions_boolean))
        print()
        print("=== VALUATIONS BOOLEAN ===")
        print(valuations_boolean)
        print()
        # print("=== ASM VAL BOOLEAN ===")
        # print(assum_val_boolean)
        print("=== GUARANTEES BOOLEAN ===")
        print(guarantees_boolean)
        print()

        l2b.writeMathsatFormulaToFile("temp/counterstrategy_auto_"+id, assum_val_boolean)
        l2b.writeMathsatFormulaToFile("temp/guarantees_auto_"+id, guarantees_boolean)

        # Use MathSAT 4 to generate the interpolant
        os.system(f"{definitions.ROOT_DIR}MathSAT4/mathsat-4.2.17-linux-x86_64/bin/mathsat -interpolate=temp/INTERP_{id} temp/counterstrategy_auto_{id} temp/guarantees_auto_{id}")

        interpolant = compute_interpolant(id, assum_val_boolean, guarantees_boolean)

        if interpolant is not None:
            if interpolant == "false":
                return ["FALSE"]
            try:
                state_components = extractStateComponents(interpolant)
            except NonStateSeparableException:
                # If the interpolant is not state separable, just skip this particular counterstrategy.
                # To think about: is it possible to come up with refinements even in case of a non-state-separable interpolant?
                state_components = dict()
                print("Non-state-separable interpolant for " + assum_val_boolean + "\n and guarantees " + guarantees_boolean)
                print("Interpolant: " + interpolant)
            print()
            print("=== INTERPOLANT ===")
            print(interpolant)
            state_components = extractStateComponents(interpolant)
            print()
            print("=== STATE COMPONENTS ===")
            print(state_components)

    # else:
    #     interpolant = ""
    #     state_components = dict()
    #     print("No interpolant for " + assum_val_boolean +"\n and guarantees " + guarantees_boolean + "\n on path " + str(path))

    os.remove("temp/counterstrategy_auto_"+id)
    os.remove("temp/guarantees_auto_"+id)
    if os.path.isfile(f"temp/INTERP_{id}.1.msat"):
        os.remove(f"temp/INTERP_{id}.1.msat")

    if state_components != dict():
        refinements,non_io_separable = getRefinementsFromStateComponents(state_components,path, input_vars)
        print()
        print("=== Refinements === ")
        print(refinements)
        return refinements
    else:
        return []

    # for i in range(5):
    #     print ("===== Randomly extracted path")
    #     p = c.extractRandomPath(counterstrategy)
    #     for s in p.states:
    #         print("State: "+p.states[s].id_state+" Valuation: "+p.states[s].get_valuation()+" Successor: "+str(p.states[s].successor))
    #     print("Looping states:")
    #     for s in p.looping_states:
    #         print(s.id_state)

if __name__ == "__main__":
    main()
