from pyparsing import *
from pyparsing import pyparsing_common
ParserElement.enablePackrat()

import xml.etree.ElementTree as ET

####################################### XML Init ##############################################
root = ET.Element("project")
signals = ET.SubElement(root, "signals")
requirements = ET.SubElement(root, "requirements")


####################################### Parse classes #########################################
class Variable:
    def __init__(self, name, boolean, values=None):
        self.name = name
        self.boolean = boolean # True: Boolean  False: enum
        self.values = values # Used in case the variable is enum
        if not boolean:
            self.num_bits = len(bin(len(values)-1))-2 # -2 because of the heading '#b' characters

    def __repr__(self):
        return str(self.name) + ": " + ("boolean" if self.boolean else str(self.values)) + " numbits: " + (str(self.num_bits) if not self.boolean else "1")

    def convertFromEnumLabelToBooleanFormula(self, value, negated=False, next=False):
        """Takes the enumeration value and returns a Boolean formula encoding its integer value's
        binary conversion"""
        if self.boolean:
            raise Exception("This is not an enum variable")

        bin_value = (format(self.values.index(value), "#0" + str(self.num_bits+2) + "b"))[2:] # To remove heading '0b'
        if negated:
            bin_value = ["1" if x == "0" else "0" for x in bin_value]
        literals = []
        for i,x in enumerate(bin_value):
            if x == "1":
                literals.append(("X(" if next else "") + self.name + "_" + str(i) + (")" if next else ""))
            else:
                literals.append(("X(" if next else "") + "!" + self.name + "_" + str(i) + (")" if next else ""))

        if not negated:
            return " & ".join(literals)
        else:
            return "(" + " | ".join(literals) + ")"

    def convertInequalityToBooleanFormula(self, operator, value, next=False):
        # First convert the constant name if value is not an integer
        if value in integer_consts:
            value = integer_consts[value]

        # Then check the bounds on the variable and convert the inequality operator into a disjunction of equalities
        # over the Boolean variables
        equalities = []
        if operator == "<=" or operator == "<":
            for i in range(0, min([len(self.values),value])):
                equalities.append(self.convertFromEnumLabelToBooleanFormula(i,False,next))
        elif operator == ">=" or operator == ">":
            for i in range(max([0,value]), len(self.values)):
                equalities.append(self.convertFromEnumLabelToBooleanFormula(i, False, next))
        if operator == "<=" or operator == ">=" and value>=0 and value < len(self.values):
            equalities.append(self.convertFromEnumLabelToBooleanFormula(i,False,next))

        return "(" + " | ".join(equalities) + ")"


    def getXMLDescription(self, env_signal):
        # env_signal: True: environment - False: controller
        signals = []
        if self.boolean:
            signal = ET.Element("signal")
            name = ET.SubElement(signal, "name")
            name.text = self.name
            kind = ET.SubElement(signal, "kind")
            kind.text = "E" if env_signal else "S"
            type = ET.SubElement(signal, "type")
            type.text = "boolean"
            notes = ET.SubElement(signal, "notes")
            signals.append(signal)
        else:
            for i in range(self.num_bits):
                signal = ET.Element("signal")
                name = ET.SubElement(signal, "name")
                name.text = self.name + "_" + str(i)
                kind = ET.SubElement(signal, "kind")
                kind.text = "E" if env_signal else "S"
                type = ET.SubElement(signal, "type")
                type.text = "boolean"
                notes = ET.SubElement(signal, "notes")
                signals.append(signal)
        return signals

env_variables = dict()
sys_variables = dict()
variables = dict()

integer_consts = dict()

assumptions = []
guarantees = []

####################################### Parse actions #########################################

def parseDefinition(t):
    if t[0] != "define":
        name = t[-1]
        boolean = t[1] == "boolean"
        values = []
        if not boolean:
            for i in range(2,len(t)):
                if t[i] == '}':
                    break
                values.append(t[i])

        var_obj = Variable(name, boolean, values)
        if t[0] == "env":
            env_variables[name] = var_obj
        elif t[0] == "sys":
            sys_variables[name] = var_obj
    else:
        # If the statement is a "define"
        name = t[1]
        var_obj = Variable(name, True)

        is_env_var = True
        for x in t[2:]:
            if x in sys_variables:
                is_env_var = False
                break
        if is_env_var:
            env_variables[name] = var_obj

        else:
            sys_variables[name] = var_obj

    variables[name] = var_obj

    return var_obj

def parseDefIntegerVariable(t):
    values = range(int(t[2]),int(t[4])+1)
    name = t[-1]
    var_obj = Variable(name, False, values)
    if t[0] == "env":
        env_variables[name] = var_obj
    elif t[0] == "sys":
        sys_variables[name] = var_obj
    variables[name] = var_obj

    return var_obj


def parseDefIntegerConst(t):
    integer_consts[t[1]] = int(t[3])


def parseComparison(t):
    # This is very complex. Comparisons can be:
    # - bool_variable = constant_value
    # - bool_variable_1 = bool_variable_2
    # - bool_variable_1 = X(bool_variable_2)
    # - X(bool_variable_1) = bool_variable_2
    # - X(bool_variable) = constant_value
    # - bool_variable_1 = Y(bool_variable_2)
    # - Y(bool_variable_1) = bool_variable_2
    # - same as before with integer values
    # - integer_variable = integer_value

    if len(t[0]) == 3:
        # In this case the expression is ["var", "="/"!=", "constant"]
        # or ["var_1", "="/"!=", "var_2"]
        if t[0][0] in env_variables:
            var_1 = env_variables[t[0][0]]
        else:
            var_1 = sys_variables[t[0][0]]

        if t[0][2] in env_variables:
            var_2 = env_variables[t[0][2]]
        elif t[0][2] in sys_variables:
            var_2 = sys_variables[t[0][2]]
        else:
            # If it is a constant, just return the Boolean expression
            # The constant may be a number or an enumerative value
            try:
                return var_1.convertFromEnumLabelToBooleanFormula(int(t[0][2]), t[0][1]=="!=")
            except ValueError:
                return var_1.convertFromEnumLabelToBooleanFormula(t[0][2], t[0][1] == "!=")

        # Here both terms are variable names
        # var_1 =/!= var_2
        if var_1.boolean:
            return var_1.name \
                        + " <-> "\
                        + ("!" if t[0][1] == "!=" else "") \
                        + var_2.name
        else:
            formula_bits = []
            for i in range(var_1.num_bits):
                formula_bits.append("("
                    + var_1.name + "_" + str(i)
                    + " <-> "
                    + ("!" if t[0][1] == "!=" else "")
                    + var_2.name + "_" + str(i)
                    + ")"
                )
            if t[0][1] == "=":
                return " & ".join(formula_bits)
            else:
                return "(" + " | ".join(formula_bits) + ")"

    else:
        # There is some next operator involved
        # Previous ("Y") operators are dealt with in the relevant parser
        token_list = t[0]._ParseResults__toklist
        index_X_operand = token_list.index("X") + 1
        X_operand = t[0][index_X_operand][0]
        if X_operand in env_variables:
            X_operand_obj = env_variables[X_operand]
        else:
            X_operand_obj = sys_variables[X_operand]

        if "=" in token_list:
            index_comparison_operator = token_list.index("=")
        else:
            index_comparison_operator = token_list.index("!=")

        if index_X_operand > index_comparison_operator:
            simple_term = t[0][index_comparison_operator - 1]
        else:
            simple_term = t[0][index_comparison_operator + 1]

        simple_term_obj = None
        if simple_term in env_variables:
            simple_term_obj = env_variables[simple_term]
        elif simple_term in sys_variables:
            simple_term_obj = sys_variables[simple_term]
        else:
            # The simple term is a constant and the formula is of the kind
            # X(var) =/!= CONSTANT
            # The constant may be a number or an enumerative value
            try:
                return X_operand_obj.convertFromEnumLabelToBooleanFormula(int(simple_term), t[0][index_comparison_operator]=="!=", True)
            except ValueError:
                return X_operand_obj.convertFromEnumLabelToBooleanFormula(simple_term, t[0][index_comparison_operator] == "!=", True)

        if X_operand_obj.boolean:
            return simple_term + " <-> X(" \
                                + ("!" if t[0][index_comparison_operator] == "!=" else "") \
                                + X_operand + ")"

        formula_bits = []
        for i in range(simple_term_obj.num_bits):
            formula_bits.append("(" + simple_term + "_" + str(i)
                                + " <-> X("
                                + ("!" if t[0][index_comparison_operator] == "!=" else "")
                                + X_operand + "_" + str(i) + "))")
        if t[0][index_comparison_operator] == "!=":
            return "(" + " | ".join(formula_bits) + ")"
        else:
            return " & ".join(formula_bits)

def parseInequality(t):

    # Transform the inequality (for instance v<5) into a set of disjoint equalities (v=0 | v=1 | ...)
    var_obj = variables[t[0][0]]



def parseNext(t):
    return ["X", [t[0][1]]]

import re
identifier_pattern = re.compile(r"\w+")
count_prevs = 0
def parsePrev(t):
    global count_prevs

    prev_bool_expr = str(t[0][1])

    # Need to check whether this auxiliary variable is an env or sys variable
    # Match the variable name in the expression
    # var_name contains the name of the first variable used in the expression.
    # We are assuming arguments of PREV use only one variable. They are expressions
    # of the kind variable = CONSTANT.
    # When parsePrev is called, those expressions have already been parsed by parseComparison,
    # hence been transformed into Boolean expressions like variable_0 & !variable_1.
    # In order to recover the variable name and search the lists of environment and controller
    # variables, we perform this pattern matching and possible remove the final _i
    var_name = identifier_pattern.findall(prev_bool_expr)[0]

    is_environment_variable = False
    if var_name in env_variables or var_name.rsplit('_', 1)[0] in env_variables:
        is_environment_variable = True

    # Introduce the auxiliary variable yboolexpr_i
    fresh_variable_name = "yBoolExpr_" + str(count_prevs)
    if is_environment_variable:
        env_variables[fresh_variable_name] = Variable(fresh_variable_name, True)
    else:
        sys_variables[fresh_variable_name] = Variable(fresh_variable_name, True)
    count_prevs += 1

    # Add constraint binding this fresh variable to the Boolean expression
    if is_environment_variable:
        assumptions.append("G((" + prev_bool_expr + ") <-> X(" + fresh_variable_name + "))")
    else:
        guarantees.append("G((" + prev_bool_expr + ") <-> X(" + fresh_variable_name + "))")

    # The parsed formula is transformed into the fresh variable literal
    return [fresh_variable_name]


count_responds_to = 0
def parseRespondsTo(t):
    global count_responds_to

    trigger = t[1]
    response = t[2]

    # Like in parsePrec, this needs to figure out whether this condition is an environment
    # or a controller constraint
    var_name = identifier_pattern.findall(response)[0]

    is_environment_variable = False
    if var_name in env_variables or var_name.rsplit('_', 1)[0] in env_variables:
        is_environment_variable = True

    fresh_variable_name = "responded_" + str(count_responds_to)
    responded = Variable(fresh_variable_name, True)
    count_responds_to += 1

    if is_environment_variable:
        env_variables[fresh_variable_name] = responded
        assumptions.append("G(F(" + fresh_variable_name + "))")
    else:
        sys_variables[fresh_variable_name] = responded
        guarantees.append("G(F(" + fresh_variable_name + "))")

    return ["G(X(" + fresh_variable_name + ") <-> ((" + response + ") | !(" + trigger + ")))"]


def parseAlwaysEventually(t):
    return ["G", ["F", [t[0][1]]]]

def parseTemporalLogicProperty(t):
    formula = ""
    if len(t)==1:
        if type(t[0]) == str:
            return t[0]
        else:
            return parseTemporalLogicProperty(t[0])
    for x in t:
        if type(x) == str:
            formula = formula + (x if len(formula) == 0 or formula[-1] == "!" else (" " + x))
        else:
            formula = formula + "(" + parseTemporalLogicProperty(x) + ")"
    return formula

def parseConstraint(t):
    if t[0] == "assumption":
        assumptions.append(t[1])
    else:
        guarantees.append(t[1])


############################### Grammar ##################################################

comment = ("--" + restOfLine) | nestedExpr('/*', '*/') | ("//" + restOfLine)

seq = Literal(";")
always_op = Keyword("G")
eventually_op = Keyword("F")
alwayseventually_op = Keyword("GF")
next_op = Keyword("X") | Keyword("next")
prev_op = Keyword("PREV") | Keyword("Y")

neg_op = Literal("!")
and_op = Literal("&") | Keyword("and")
or_op = Literal("|") | Keyword("or")
implies_op = Literal("->")
iff_op = Literal("<->") | Keyword("iff")


neq_op = Literal("!=")
eq_op = Literal("=")
comparison_op = neq_op | eq_op
leq_op = Literal("<=")
lt_op = Literal("<")
geq_op = Literal(">=")
gt_op = Literal(">")
inequality_op = leq_op | lt_op | geq_op | gt_op

identifier = pyparsing_common.identifier
enum_literal = Word(alphas.upper(), alphas.upper() + nums + "_")

bool_atom = identifier | enum_literal

atom = bool_atom | Word(nums)

bool_expr = infixNotation(bool_atom,
                             [(neg_op, 1, opAssoc.RIGHT),
                              (comparison_op, 2, opAssoc.LEFT, parseComparison),
                              (inequality_op, 2, opAssoc.LEFT, parseInequality),
                              (and_op, 2, opAssoc.LEFT),
                              (or_op, 2, opAssoc.LEFT),
                              (implies_op, 2, opAssoc.LEFT),
                              (iff_op, 2, opAssoc.LEFT)])

bool_expr.setParseAction(parseTemporalLogicProperty)

responds_to = Keyword("respondsTo") + Suppress("(") + bool_expr + Suppress(",") + bool_expr + Suppress(")")
responds_to.setParseAction(parseRespondsTo)

temporal_logic_expr = responds_to | infixNotation(atom,
                                    [(neg_op, 1, opAssoc.RIGHT),
                                     (next_op, 1, opAssoc.RIGHT, parseNext),
                                     (prev_op, 1, opAssoc.RIGHT, parsePrev),
                                     (comparison_op, 2, opAssoc.LEFT, parseComparison),
                                     (inequality_op, 2, opAssoc.LEFT, parseInequality),
                                     (and_op, 2, opAssoc.LEFT),
                                     (or_op, 2, opAssoc.LEFT),
                                     (implies_op, 2, opAssoc.LEFT),
                                     (iff_op, 2, opAssoc.LEFT),
                                     (always_op, 1, opAssoc.RIGHT),
                                     (eventually_op, 1, opAssoc.RIGHT),
                                     (alwayseventually_op, 1, opAssoc.RIGHT, parseAlwaysEventually)])

temporal_logic_expr.setParseAction(parseTemporalLogicProperty)

def_integer_const = Keyword("define") + identifier + Literal(":=") + Word(nums)
def_integer_const.setParseAction(parseDefIntegerConst)

def_boolean = (Keyword("env") | Keyword("sys")) + Keyword("boolean") + identifier
def_enum = (Keyword("env") | Keyword("sys")) \
           + Literal("{") + delimitedList(enum_literal) + Literal("}") \
           + identifier
def_internal_variable = (Keyword("define") + identifier + Literal(":=") + temporal_logic_expr)

definition = def_boolean | def_enum | def_internal_variable
definition.ignore(comment)
definition.setParseAction(parseDefinition)

def_integer_variable = (Keyword("env") | Keyword("sys")) \
           + Literal("Int(") + Word(nums) + Literal("..") + Word(nums) + Literal(")") \
           + identifier
def_integer_variable.ignore(comment)
def_integer_variable.setParseAction(parseDefIntegerVariable)

constraint = (Keyword("assumption") | Keyword("guarantee")) + (temporal_logic_expr | bool_expr)
constraint.ignore(comment)
constraint.setParseAction(parseConstraint)

statement = (def_integer_const | def_integer_variable | definition | constraint) + seq
statement.ignore(comment)

pattern = nestedExpr("pattern", "}")

program = Keyword("module") + identifier \
          + OneOrMore(statement) \
          + ZeroOrMore(pattern)

program.ignore(comment)

###################################### Tests ##################################################
import sys,traceback
try:
    filename = sys.argv[1]
    output_folder = sys.argv[2]
    input_file = open(filename,"r")
    print(program.parseString(input_file.read(),parseAll=True))
    print("assumptions: " + str(assumptions))
    print("guarantees: " + str(guarantees))

    print("## Producing XML signals")
    for variable in env_variables:
        signals.extend(env_variables[variable].getXMLDescription(True))
    for variable in sys_variables:
        signals.extend(sys_variables[variable].getXMLDescription(False))

    print("## Producing XML assumptions and guarantees")
    for i,assumption in enumerate(assumptions):
        requirement = ET.SubElement(requirements, "requirement")
        name = ET.SubElement(requirement, "name")
        name.text = "assum_" + str(i)
        property = ET.SubElement(requirement, "property")
        property.text = assumption
        kind = ET.SubElement(requirement, "kind")
        kind.text = "A"
        notes = ET.SubElement(requirement, "notes")
        toggled = ET.SubElement(requirement, "toggled")
        toggled.text = "1"

    for i,guarantee in enumerate(guarantees):
        requirement = ET.SubElement(requirements, "requirement")
        name = ET.SubElement(requirement, "name")
        name.text = "guar_" + str(i)
        property = ET.SubElement(requirement, "property")
        property.text = guarantee
        kind = ET.SubElement(requirement, "kind")
        kind.text = "G"
        notes = ET.SubElement(requirement, "notes")
        toggled = ET.SubElement(requirement, "toggled")
        toggled.text = "1"

    import xml.dom.minidom as md
    dom = md.parseString(ET.tostring(root))
    xmlfile = open(filename+".rat", "w")
    xmlfile.write((dom.toprettyxml()).replace("!!",""))
    print(dom.toprettyxml())
    xmlfile.close()
    input_file.close()
except Exception as e:
    print(str(filename) + " " + str(traceback.print_exc(e)))
