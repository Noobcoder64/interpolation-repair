import os
import sys
import re
import specification as sp

class Variable:

    def __init__(self, name, boolean, values=None):
        self.name = name
        self.values = values # Used in case the variable is enum
        self.num_bits = len(bin(len(values)-1))-2 # -2 because of the heading '#b' characters

    def getBoolean(self, value, next=False):
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



def main():
    spectra_file = sys.argv[1]
    spec = sp.read_file(spectra_file)

    translated_spec = []
    for line_index in range(len(spec)):
        line = spec[line_index]
        match = re.search(r'{(.*)}', line)
        if not match:
            translated_spec.append(line)
            continue
        values = match.group(1).split(', ')
        values = [re.sub(r'\s*', '', v) for v in values]
        name = re.search(r'}\s*(.*?)\s*;', line).group(1)
        kind = re.search(r'\s*(.*?)\s*{', line).group(1)
        num_bits = len(bin(len(values)-1))-2
        print(name)
        print(values)
        for bit in range(num_bits):
            translated_spec.append(f"{kind} boolean {name}_{bit};\n")

        for i in range(2**num_bits):
            bin_value = format(i, "#0" + str(num_bits+2) + "b")[2:]
            print(bin_value)
            literals = []
            for j, x in enumerate(bin_value):
                if x == "1":
                    literals.append(name + "_" + str(j))
                else:
                    literals.append("!" + name + "_" + str(j))
            if i < len(values):
                print(str(literals) + " - VALID")
                pattern = name + "\s*=\s*" + values[i]
                replacement = "(" + " & ".join(literals) + ")"
                spec = [re.sub(pattern, replacement, x) for x in spec]
                pattern = pattern.replace("=", "!=")
                replacement = "!" + replacement
                spec = [re.sub(pattern, replacement, x) for x in spec]
            else:
                print(str(literals) + " - INVALID")
                safety = ""
                if kind == "env":
                    safety = "assumption\n\t"
                elif kind == "sys":
                    safety = "guarantee\n\t"
                safety += "alw (!(" + " & ".join(literals) + "));"
                translated_spec.append("\n" + safety + "\n")

    translated_spec = [re.sub(r"G\s*\(", r"alw (", line) for line in translated_spec]
    translated_spec = [re.sub(r"GF\s*\(", r"alwEv (", line) for line in translated_spec]
    translated_spec = [re.sub(r"Y\s*\(", r"PREV(", line) for line in translated_spec]

    directory, filename = os.path.split(spectra_file)
    new_directory = os.path.join(directory, "translations")
    new_path = os.path.join(new_directory, filename)
    sp.write_file(translated_spec, new_path)

if __name__ == '__main__':
    main()