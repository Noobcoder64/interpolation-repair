import xml.etree.ElementTree
import re
import sys

def write_file(spec, output_filename):
    output_filename = re.sub(r"\\", "/", output_filename)
    output = ''.join(spec)
    file = open(output_filename, 'w', newline='\n')
    file.write(output)
    file.close()

# Replaces '&&' with '&', '||' with '|'
def normalizeFormulaSyntax( formula ):
    formula = formula.replace('&&','&')
    formula = formula.replace('||','|')
    # formula = re.sub(r"\b%s\b" % "next", "X", formula)
    formula = re.sub(r"\b%s\b" % "always", "G", formula)
    formula = re.sub(r"\b%s\b" % "eventually!", "F", formula)
    formula = re.sub(r"G\(F\(([^\)]*)\)", r"GF (\1", formula)
    # formula = re.sub(r"G\(([^\)]*)\)", r"alw (\1)", formula)
    formula = re.sub(r"X\(([^\)]*)\)", r"next(\1)", formula)
    # Pattern replacement for boolean variables expressed as name=value
    patternBoolPosVar = re.compile("([A-Za-z0-9_]+)( ?= ?1)")
    patternBoolNegVar = re.compile("([A-Za-z0-9_]+)( ?= ?0)")

    formula = patternBoolPosVar.sub(r"\1",formula)
    formula = patternBoolNegVar.sub(r"!\1",formula)
    formula = formula.lstrip().rstrip()

    return formula

input = sys.argv[1]
directory = input.split("/")[0] + "/"
specification = input.split("/")[1].replace(".rat", "")
lines = ["module " + specification + "\n"]

file = open(directory + specification + ".rat", "r")
e = xml.etree.ElementTree.parse(file).getroot().find("signals")
for signal in e.findall("signal"):
    if signal.find("kind").text.strip() == "E":
        lines.append("env boolean " + signal.find("name").text.strip() + ";\n")
    elif signal.find("kind").text.strip() == "S":
        lines.append("sys boolean " + signal.find("name").text.strip() + ";\n")
file.close()

lines.append("\n")

file = open(directory + specification + ".rat", "r")
 # Requirements are listed in the <requirements> element
e = xml.etree.ElementTree.parse(file).getroot().find("requirements")
# The LTL formula of an assumption unit is in the <requirement> element
for req in e.findall("requirement"):
    # The <kind> node contains the requirement type (A or G)
    # The <property> node contains the temporal expression
    if req.find("kind").text.lstrip().rstrip() == "A":
        lines.append("assumption\n\t" + normalizeFormulaSyntax(req.find("property").text) + ";\n")
    elif req.find("kind").text.lstrip().rstrip() == "G":
        lines.append("guarantee\n\t" + normalizeFormulaSyntax(req.find("property").text) + ";\n")
file.close()

write_file(lines, "AMBAs/" + specification + ".spectra")
