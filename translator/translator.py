import sys,traceback
from pyparsing import *
from pyparsing import pyparsing_common
ParserElement.enablePackrat()

import xml.etree.ElementTree as ET
import re
import os
import subprocess

sys.setrecursionlimit(1500)

####################################### XML Init ##############################################
# root = ET.Element("project")
# signals = ET.SubElement(root, "signals")
# requirements = ET.SubElement(root, "requirements")

####################################### Spec Init ##############################################

spec = []

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
                literals.append(("next(" if next else "") + self.name + "_" + str(i) + (")" if next else ""))
            else:
                literals.append(("next(" if next else "") + "!" + self.name + "_" + str(i) + (")" if next else ""))

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
    

env_variables = dict()
sys_variables = dict()
variables = dict()

integer_consts = dict()

assumptions = []
guarantees = []

####################################### Parse actions #########################################

def parseDefinition(t):
    if t[0] != "define":
        return parseVariable(t)
    spec.append("define\n\t" + " ".join(t[1:]) + ";")


def parseVariable(t):
    kind = t[0]
    boolean = t[1] == "boolean"
    name = t[-2]
    values = []
    if not boolean:
        for i in range(2,len(t)):
            if t[i] == '}':
                break
            values.append(t[i])

    var_obj = Variable(name, boolean, values)
    if kind == "env":
        env_variables[name] = var_obj
    elif kind == "sys" or kind == "aux":
        sys_variables[name] = var_obj

    ret = ""
    if boolean:
        ret += kind + " boolean " + var_obj.name + ";"
    else:
        for i in range(var_obj.num_bits):
            ret += kind + " boolean " + var_obj.name + "_" + str(i) + ";\n"

        for i in range(len(var_obj.values), 2**var_obj.num_bits):
            bin_value = format(i, "#0" + str(var_obj.num_bits+2) + "b")[2:]
            literals = []
            for j, x in enumerate(bin_value):
                if x == "1":
                    literals.append(name + "_" + str(j))
                else:
                    literals.append("!" + name + "_" + str(j))

            safety = ""
            if kind == "env":
                safety = "assumption\n\t"
            elif kind == "sys":
                safety = "guarantee\n\t"
            safety += "alw (!(" + " & ".join(literals) + "));\n"
            ret += safety

    variables[name] = var_obj
    return ret


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

def parseNegation(t):
    return [[t[0][0], t[0][1:]]]


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

    if len(t) == 3:
        # In this case the expression is ["var", "="/"!=", "constant"]
        # or ["var_1", "="/"!=", "var_2"]

        operand1 = t[0]
        operand2 = t[2]

        if operand1 in env_variables:
            var_1 = env_variables[operand1]
        else:
            var_1 = sys_variables[operand1]

        if operand2 in env_variables:
            var_2 = env_variables[operand2]
        elif operand2 in sys_variables:
            var_2 = sys_variables[operand2]
        elif operand2 in ["true", "TRUE"]:
            return var_1.name
        elif operand2 in ["false", "FALSE"]:
            return "!" + var_1.name
        else:
            # operand2 is an Enum value
            return var_1.convertFromEnumLabelToBooleanFormula(operand2, t[1] == "!=")

        # Here both terms are variable names
        # var_1 =/!= var_2
        if var_1.boolean:
            return var_1.name + " <-> " + ("!" if t[0][1] == "!=" else "") + var_2.name
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

    elif len(t) == 4:
        # There is some next operator involved
        # Previous ("Y") operators are dealt with in the relevant parser
        token_list = t._ParseResults__toklist
        index_X_operand = token_list.index("next") + 1
        X_operand = t[index_X_operand]
        if X_operand in env_variables:
            X_operand_obj = env_variables[X_operand]
        else:
            X_operand_obj = sys_variables[X_operand]

        if "=" in token_list:
            index_comparison_operator = token_list.index("=")
        else:
            index_comparison_operator = token_list.index("!=")

        if index_X_operand > index_comparison_operator:
            simple_term = t[index_comparison_operator - 1]
        else:
            simple_term = t[index_comparison_operator + 1]

        simple_term_obj = None
        if simple_term in env_variables:
            simple_term_obj = env_variables[simple_term]
        elif simple_term in sys_variables:
            simple_term_obj = sys_variables[simple_term]
        else:
            # The simple term is a constant and the formula is of the kind
            # X(var) =/!= CONSTANT
            # The constant may be a number or an enumerative value
            return X_operand_obj.convertFromEnumLabelToBooleanFormula(simple_term, t[index_comparison_operator] == "!=", True)

        if X_operand_obj.boolean:
            return simple_term + " <-> next(" \
                                + ("!" if t[index_comparison_operator] == "!=" else "") \
                                + X_operand + ")"

        formula_bits = []
        for i in range(simple_term_obj.num_bits):
            formula_bits.append("(" + simple_term + "_" + str(i)
                                + " <-> next("
                                + ("!" if t[index_comparison_operator] == "!=" else "")
                                + X_operand + "_" + str(i) + "))")
        if t[0][index_comparison_operator] == "!=":
            return "(" + " | ".join(formula_bits) + ")"
        else:
            return " & ".join(formula_bits)
    else:

        token_list = t._ParseResults__toklist
        operand1 = t[1][0]
        operand2 = t[4][0]

        if operand1 in env_variables:
            var1 = env_variables[operand1]
        else:
            var1 = sys_variables[operand1]

        # X(var) =/!= var
        if var1.boolean:
            return "next(" + ("!" if "!=" in token_list else "") + operand1 + ")" \
                    + " <-> " \
                    + "next(" + ("!" if "!=" in token_list else "") + operand2 + ")"

        formula_bits = []
        for i in range(var1.num_bits):
            formula_bits.append("(next(" + operand1 + "_" + str(i) + ")"
                                + " <-> " \
                                + "next(" + ("!" if "!=" in token_list else "") + operand2 + "_" + str(i) + "))")
        if  "!=" in token_list:
            return "(" + " | ".join(formula_bits) + ")"
        else:
            return " & ".join(formula_bits)


def parseInequality(t):

    # Transform the inequality (for instance v<5) into a set of disjoint equalities (v=0 | v=1 | ...)
    var_obj = variables[t[0][0]]



def parseNext(t):
    return ["X", [t[0][1]]]

def parsePrev(t):
    return ["PREV", t[0][1:]]

identifier_pattern = re.compile(r"\w+")
# count_prevs = 0
# def parsePrev(t):
#     global count_prevs

#     prev_bool_expr = str(t[0][1])

#     # Need to check whether this auxiliary variable is an env or sys variable
#     # Match the variable name in the expression
#     # var_name contains the name of the first variable used in the expression.
#     # We are assuming arguments of PREV use only one variable. They are expressions
#     # of the kind variable = CONSTANT.
#     # When parsePrev is called, those expressions have already been parsed by parseComparison,
#     # hence been transformed into Boolean expressions like variable_0 & !variable_1.
#     # In order to recover the variable name and search the lists of environment and controller
#     # variables, we perform this pattern matching and possible remove the final _i
#     var_name = identifier_pattern.findall(prev_bool_expr)[0]

#     is_environment_variable = False
#     if var_name in env_variables or var_name.rsplit('_', 1)[0] in env_variables:
#         is_environment_variable = True

#     # Introduce the auxiliary variable yboolexpr_i
#     fresh_variable_name = "yBoolExpr_" + str(count_prevs)
#     if is_environment_variable:
#         env_variables[fresh_variable_name] = Variable(fresh_variable_name, True)
#     else:
#         sys_variables[fresh_variable_name] = Variable(fresh_variable_name, True)
#     count_prevs += 1

#     # Add constraint binding this fresh variable to the Boolean expression
#     if is_environment_variable:
#         assumptions.append("G((" + prev_bool_expr + ") <-> X(" + fresh_variable_name + "))")
#     else:
#         guarantees.append("G((" + prev_bool_expr + ") <-> X(" + fresh_variable_name + "))")

#     # The parsed formula is transformed into the fresh variable literal
#     return [fresh_variable_name]


# count_responds_to = 0
def parseRespondsTo(t):
    trigger = t[1]
    response = t[2]
    return ["respondsTo(" + trigger + "," + response + ")"]

    # global count_responds_to

    # trigger = t[1]
    # response = t[2]

    # # Like in parsePrec, this needs to figure out whether this condition is an environment
    # # or a controller constraint
    # var_name = identifier_pattern.findall(response)[0]

    # is_environment_variable = False
    # if var_name in env_variables or var_name.rsplit('_', 1)[0] in env_variables:
    #     is_environment_variable = True

    # fresh_variable_name = "responded_" + str(count_responds_to)
    # responded = Variable(fresh_variable_name, True)
    # count_responds_to += 1

    # if is_environment_variable:
    #     env_variables[fresh_variable_name] = responded
    #     assumptions.append("G(F(" + fresh_variable_name + "))")
    # else:
    #     sys_variables[fresh_variable_name] = responded
    #     guarantees.append("G(F(" + fresh_variable_name + "))")

    # return ["G(X(" + fresh_variable_name + ") <-> ((" + response + ") | !(" + trigger + ")))"]


def parseAlwaysEventually(t):
    return ["GF", [t[0][1]]]

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
    spec.append(t[0] + "\n\t" + t[1] + ";")

def parsePattern(t):
    for items in t:
        line = "pattern "
        for item in items:
            if item.endswith('{') or item.endswith(';'):
                line += item
                spec.append(line)
                line = ""
            else:
                line += item + " "
        spec.append("}")

def printStatement(t):
    print(t)

############################### Grammar ##################################################

comment = ("--" + restOfLine) | nestedExpr('/*', '*/') | ("//" + restOfLine)

seq = Literal(";")
always_op = Keyword("G") | Keyword("alw")
eventually_op = Keyword("F")
alwayseventually_op = Keyword("GF") | Keyword("alwEv")
# next_op = Keyword("X") | Keyword("next")
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

next_op = Literal("next") + Suppress("(") + identifier + Suppress(")")
bool_atom = next_op | identifier | enum_literal

atom = bool_atom | Word(nums)

bool_expr = infixNotation(bool_atom,
                             [(next_op, 1, opAssoc.RIGHT, parseNext),
                              (neg_op, 1, opAssoc.RIGHT, parseNegation),
                              (prev_op, 1, opAssoc.RIGHT, parsePrev),
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
                                    [(neg_op, 1, opAssoc.RIGHT, parseNegation),
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

def_boolean = (Keyword("env") | Keyword("sys") | Keyword("aux")) + Keyword("boolean") + identifier
def_enum = (Keyword("env") | Keyword("sys")) \
           + Literal("{") + delimitedList(enum_literal) + Literal("}") \
           + identifier
def_internal_variable = (Keyword("define") + identifier + Literal(":=") + temporal_logic_expr)

definition = (def_boolean | def_enum | def_internal_variable) + seq
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
# statement.setParseAction(printStatement)

pattern = nestedExpr("pattern", "}")
pattern.setParseAction(parsePattern)

program = Keyword("module") + identifier \
          + OneOrMore(statement) \
          + ZeroOrMore(pattern)

program.ignore(comment)

comparison_exp = bool_atom + comparison_op + bool_atom
comparison_exp.setParseAction(parseComparison)

###################################### IO ####################################################

def write_file(spec, output_filename):
    output = '\n'.join(spec)
    file = open(output_filename, 'w')
    file.write(output)
    file.close()

###################################### Tests ##################################################


input_path = sys.argv[1]

if len(sys.argv) >= 3:
    output_directory = sys.argv[2]
else:
    # Default output directory if not provided
    output_directory = "outputs"

if not os.path.isdir(output_directory):
    os.makedirs(output_directory)

directory, filename = os.path.split(input_path)
print "TRANSLATING: " + filename

# === Run SpecTranslator.java ===

PATH_TO_JAR = "SpecTranslator.jar"
cmd = "java -jar {} -i {} -o {}".format(PATH_TO_JAR, input_path, output_directory)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
p.wait()

new_path = os.path.join(output_directory, filename)

with open(new_path, "r") as input_file:
    old_spec = input_file.read()

new_spec = definition.transformString(old_spec)

with open(new_path, "w") as output_file:
    output_file.write(new_spec)

with open(new_path, "r") as input_file:
    old_spec = input_file.read()

new_spec = comparison_exp.transformString(old_spec)

with open(new_path, "w") as output_file:
    output_file.write(new_spec)

# Normalize syntax
# spec = [re.sub(r"G\s*\(", r"alw (", line) for line in spec]
# spec = [re.sub(r"GF\s*\(", r"alwEv (", line) for line in spec]
# spec = [re.sub(r"alwEv\s*\(", r"GF (", line) for line in spec]
# spec = [re.sub(r"alw\s*\(", r"G (", line) for line in spec]
# spec = [re.sub(r"X\s*\(", r"next(", line) for line in spec]
# spec = [re.sub(r"Y\s*\(", r"PREV(", line) for line in spec]
# spec = [re.sub(r'(\w+)=true', r'\1', x) for x in spec]
# spec = [re.sub(r'(\w+)=false', r'!\1', x) for x in spec]




