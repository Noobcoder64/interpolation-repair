from counterstrategy import Path as p
import re
import pyparsing as pp
import syntax_utils as su

fairness_pattern = re.compile(r"G\(F(\(.*\))\)")
invariant_pattern = re.compile(r"G(\(.*\))")

def gr1LTL2Boolean(ltlFormula, path):
    fairness_match = fairness_pattern.match(ltlFormula)
    invariant_match = invariant_pattern.match(ltlFormula)
    if fairness_match:
        return fairnessLTL2Boolean(fairness_match.group(1), path)
    elif invariant_match:
        return invariantLTL2Boolean(invariant_match.group(1), path)
    else:
        return initialLTL2Boolean(ltlFormula, path)

def initialLTL2Boolean(ltlFormula, path):
    """
    Translates an LTL initial condition formula (given as a string) into its boolean counterpart
    on the given model (given as a Path)
    @param ltlFormula: A string in normalized syntax, such as a & (b | !c)
    @type ltlFormula: str
    @param path: The path on which the formula is translated
    @type path: L{p.Path}
    @return: A string containing the translated initial condition
    """
    return "(" + re.sub(r"(\w+)", r"\1__" + path.initial_state.id_state, ltlFormula) + ")"

## Grammar definition for invariants
next_op = pp.Literal("X")
variable = pp.Word(pp.alphas+"_", pp.alphanums+"_")
lparen = pp.Literal("(")
rparen = pp.Literal(")")
symbol = next_op | variable | lparen | rparen | "&" | "|" | "->" | "<->" | "!"
ltlInvariant = pp.OneOrMore(symbol)

# variable = pp.Word(pp.alphas+"_", pp.alphanums+"_")
# literal = variable | "!" + variable
# # The Forward command is used to define ParserElements whose production rules are defined later than they are used
# bool_expr = pp.Forward()
# next_expr = "X" + literal | "X" + "(" + bool_expr + ")"
# next_expr.setResultsName('Next_expr')
# unary_expr = next_expr | literal | "!" + "(" + bool_expr +")" |  "(" + bool_expr + ")"
# and_expr = "&" + bool_expr
# or_expr = "|" + bool_expr
# impl_expr = "->" + bool_expr
# impl2_expr = "<->" + bool_expr
# bool_expr <<  (unary_expr + and_expr | unary_expr + or_expr | unary_expr + impl_expr | unary_expr + impl2_expr | unary_expr )

def invariantLTL2Boolean(ltlFormula, path):
    """
    Translates an LTL invariant condition formula (given as a string) into its boolean counterpart
    on the given model (given as a Path)
    @param ltlFormula: A string in normalized syntax, such as a & (b | !c)
    @type ltlFormula: str
    @param path: The path on which the formula is translated
    @type path: L{p.Path}
    @return: A string containing the translated invariant
    """

    translatedInv = ""

    # Returns all the tokens in ltlFormula
    ltlTokens = ltlInvariant.parseString(ltlFormula)
    translatedInv = translatedInv + "(" + _translateInvOnStatePair(ltlTokens, path.initial_state) + ") & "

    for state in path.transient_states:
        translatedInv = translatedInv + "("+ _translateInvOnStatePair(ltlTokens, state) + ") & "

    for state in path.unrolled_states:
        translatedInv = translatedInv + "(" + _translateInvOnStatePair(ltlTokens, state) + ") & "

    if path.is_loop:
        for state in path.looping_states:
            translatedInv = translatedInv + "("+ _translateInvOnStatePair(ltlTokens, state) + ") & "

    translatedInv = translatedInv[:-3]
    return translatedInv

def _translateInvOnStatePair(ltlTokens, state):
    ret_string = ""
    var_pattern = re.compile(r"\w+")
    cur_state_id = state.id_state
    next_paren_depth = 0
    for token in ltlTokens:
        if token == "X" and state.successor is not None:
            cur_state_id = state.successor
        elif token == "X" and state.successor is None:
            # In this case the path is finite, and the next state is actually the failing state
            return "TRUE"
        else:
            ret_string = ret_string + token
            if token == "(" and cur_state_id == state.successor:
                next_paren_depth = next_paren_depth + 1
            elif token == ")" and cur_state_id == state.successor:
                next_paren_depth = next_paren_depth - 1
                if next_paren_depth == 0:
                    cur_state_id = state.id_state
            elif var_pattern.match(token) is not None:
                ret_string = ret_string + "__" + cur_state_id

    # TRUE and FALSE are not variables. They are constant and the state id must not be postponed
    ret_string = re.sub(r"(TRUE|FALSE)__\w+", r"\1", ret_string)
    return ret_string

def fairnessLTL2Boolean(ltlFormula, path):
    """
    Translates an LTL fairness formula into boolean
    """
    if hasattr(path, "looping_states"):
        ret_string = "("
        for s in path.looping_states:
            ret_string = ret_string + "(" + re.sub(r"(\w+)", r"\1__" + s.id_state, ltlFormula) + ") | "
        ret_string = ret_string[:-3] + ")"

        # TRUE and FALSE are not variables. They are constant and the state id must not be postponed
        ret_string = re.sub(r"(TRUE|FALSE)__\w+", r"\1", ret_string)
        return ret_string
    else:
        return ""


def writeMathsatFormulaToFile(filename, formula):
    outfile = open(filename, "w")
    # Get unique ids appearing in formula
    bool_vars_unique = set(re.findall(r"(\w+)", formula))
    bool_vars_unique.discard("TRUE")
    bool_vars_unique.discard("FALSE")
#    bool_vars = list(bool_vars_unique)

    mathsat_formula = "VAR\n" + ','.join(bool_vars_unique) + ": BOOLEAN\n" + "FORMULA\n" + formula

    outfile.write(mathsat_formula)
    outfile.close()


def parseInterpolant(filename):
    """Parses an interpolant as stored in a file produced by MathSAT"""

    infile = open(filename)
    # Find all auxiliary variables definitions and add them to a dictionary.
    # The key is the variable name and the value is its definition.
    define_pattern = re.compile(r"DEFINE (\w+) := (.*)")
    formula_pattern = re.compile(r"FORMULA (.*)")
    varname_pattern = re.compile(r"(def_\d+)")
    negvarname_pattern = re.compile(r"!def_\d+")

    definitions = dict()
    formula = ""
    for line in [x[0:-1] for x in infile.readlines()]:
        if "DEFINE" in line:
            define_match = define_pattern.match(line)
            definitions[define_match.group(1)] = define_match.group(2)
        elif "FORMULA" in line:
            formula_match = formula_pattern.match(line)
            formula = formula_match.group(1)

    infile.close()

    # Now remove parentheses from & definitions
    for varname in definitions:
        if "|" not in definitions[varname] and "->" not in definitions[varname] and "!" not in definitions[varname]:
            definitions[varname] = definitions[varname].strip("()")

    # Replace any occurrence of a variable with the corresponding formula.
    # Now all useless parentheses have been stripped from the definitions.
    while "def_" in formula:
        # This gets the varname found in formula
        varname = varname_pattern.findall(formula)[0]
        formula = re.sub(r"\b%s\b" % varname, definitions[varname], formula)

    return su.removeUnnecessaryParentheses(formula)

