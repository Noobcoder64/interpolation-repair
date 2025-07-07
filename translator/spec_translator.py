import sys
import os
import re
import subprocess
from pyparsing import *
from pyparsing import pyparsing_common
ParserElement.enablePackrat()

env_variables = dict()
sys_variables = dict()

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


####################################### Parse actions #########################################

def parseDefinition(t):
    kind = t[0]
    boolean = t[1] == "boolean"
    name = t[-2]
    values = []
    if not boolean:
        for i in range(2, len(t)):
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

    return ret

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
            return var_1.name + " <-> " + ("!" if t[1] == "!=" else "") + var_2.name
        else:
            formula_bits = []
            for i in range(var_1.num_bits):
                formula_bits.append("("
                    + var_1.name + "_" + str(i)
                    + " <-> "
                    + ("!" if t[1] == "!=" else "")
                    + var_2.name + "_" + str(i)
                    + ")"
                )
            if t[1] == "!=":
                return "(" + " | ".join(formula_bits) + ")"
            else:
                return " & ".join(formula_bits)

    else:
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
        elif simple_term in ["true", "TRUE"]:
            return "next(" + X_operand + ")"
        elif simple_term in ["false", "FALSE"]:
            return "next(!" + X_operand + ")"
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
        if t[index_comparison_operator] == "!=":
            return "(" + " | ".join(formula_bits) + ")"
        else:
            return " & ".join(formula_bits)


############################### Grammar ##################################################

comment = ("--" + restOfLine) | nestedExpr('/*', '*/') | ("//" + restOfLine)
seq = Literal(";")

neq_op = Literal("!=")
eq_op = Literal("=")
comparison_op = neq_op | eq_op

identifier = pyparsing_common.identifier
enum_literal = Word(alphas.upper(), alphas.upper() + nums + "_")

next_op = Literal("next") + Suppress("(") + identifier + Suppress(")")
bool_atom = next_op | identifier | enum_literal

def_boolean = (Keyword("env") | Keyword("sys") | Keyword("aux")) + Keyword("boolean") + identifier
def_enum = (Keyword("env") | Keyword("sys") | Keyword("aux")) \
           + Literal("{") + delimitedList(enum_literal) + Literal("}") \
           + identifier

definition = (def_boolean | def_enum) + seq
definition.ignore(comment)
definition.setParseAction(parseDefinition)

comparison_exp = bool_atom + comparison_op + bool_atom
comparison_exp.setParseAction(parseComparison)


###################################### Main ##################################################

"""
Usage:
    python spec_translator.py <input_file> [output_directory]

Arguments:
    <input_file>         Input specification file to translate.
    [output_directory]   (Optional) Directory for the output file (default: "outputs").

Description:
    Translates a specification file using `spec-translator.jar` and applies transformations
    for enumerative variables and temporal operators.

Dependencies:
    - Python modules: `sys`, `os`, `re`, `subprocess`, `pyparsing`
    - Java Runtime Environment (JRE) for `spec-translator.jar`

Example:
    python spec_translator.py input.spec translated_outputs
"""

# Problem 1: Need to be in the same directory as the jar file
# Problem 2: Cannot specify the output file name
# Problem 3: pREV looks ugly

TRANSLATE_ENUM = True

input_path = sys.argv[1]

if len(sys.argv) >= 3:
    output_directory = sys.argv[2]
else:
    output_directory = "outputs"

if not os.path.isdir(output_directory):
    os.makedirs(output_directory)

directory, filename = os.path.split(input_path)
print "TRANSLATING: " + filename

PATH_TO_JAR = "spec-translator.jar"
cmd = "java -jar {} -i {} -o {}".format(PATH_TO_JAR, input_path, output_directory)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
p.wait()

if TRANSLATE_ENUM:
    new_path = os.path.join(output_directory, filename)

    with open(new_path, "r") as input_file:
        old_spec = input_file.read()

    new_spec = definition.transformString(old_spec)

    with open(new_path, "w") as output_file:
        output_file.write(new_spec)

    with open(new_path, "r") as input_file:
        old_spec = input_file.read()

    new_spec = comparison_exp.transformString(old_spec)

    new_spec = re.sub(r"alwEv\s*\(", r"GF (", new_spec)
    new_spec = re.sub(r"alw\s*\(", r"G (", new_spec)

    with open(new_path, "w") as output_file:
        output_file.write(new_spec)
