import xml.etree.ElementTree
import re
import specification as sp

# Returns a list with all assumptions and guarantees from a .rat file
def extractGR1UnitsList( SpecFile ):
    infile = open(SpecFile,"r")

    # Requirements are listed in the <requirements> element
    e = xml.etree.ElementTree.parse(infile).getroot().find("requirements")

    assumptionList = []

    # The LTL formula of an assumption unit is in the <requirement> element
    for req in e.findall("requirement"):
        # The <property> node contains the temporal expression
        assumptionList.append(normalizeFormulaSyntax(req.find("property").text))

    infile.close()
    return assumptionList

# Returns a dictionary with all assumptions in a .rat file indexed by their names
def extractAssumptionListWithNames( SpecFile ):
    infile = open(SpecFile,"r")

    # Requirements are listed in the <requirements> element
    e = xml.etree.ElementTree.parse(infile).getroot().find("requirements")

    assumptionDict = dict()

    # The LTL formula of an assumption unit is in the <requirement> element
    for req in e.findall("requirement"):
        # The <kind> node contains the requirement type (A or G)
        # The <property> node contains the temporal expression
        # The <name> node contains the name of the assumption
        if req.find("kind").text.lstrip().rstrip() == "A":
            assumptionDict[req.find("name").text] = normalizeFormulaSyntax(req.find("property").text)

    infile.close()
    return assumptionDict

# Returns a list with all assumptions in a .rat file
def extractAssumptionList( SpecFile ):
    infile = sp.read_file(SpecFile)
    infile = sp.assumptions(infile)
    print("ASSUMPTIONS:")
    for asm in infile:
        print(asm)
    print()
    return infile

# Returns a list with all guarantees in a .rat file
def extractGuaranteesList( SpecFile ):
    infile = sp.read_file(SpecFile)
    infile = sp.guarantees(infile)
    print("GUARANTEES:")
    for asm in infile:
        print(asm)
    print()
    return infile

# Extract variables from .rat file
def extractVariablesFromFile( SpecFile ):
    infile = open(SpecFile, "r")

    # Variables are listed in the <signals> element
    e = xml.etree.ElementTree.parse(infile).getroot().find("signals")

    variables = []

    for signal in e.findall("signal"):
        variables.append(signal.find("name").text.strip())

    infile.close()
    return variables

# Extract input variables from .rat file
def extractInputVariablesFromFile( SpecFile ):
    infile = sp.read_file(SpecFile)

    variables = []
    for line in infile:
        match = re.search(r'(?:env)\s+boolean\s+(\w+)\s*;', line)
        if match:
            variables.append(match.group(1))

    print("INPUT VARIABLES:", variables)
    print()
    return variables

    # # Variables are listed in the <signals> element
    # e = xml.etree.ElementTree.parse(infile).getroot().find("signals")

    # variables = []

    # for signal in e.findall("signal"):
    #     if signal.find("kind").text.strip() == "E":
    #         variables.append(signal.find("name").text.strip())

    # infile.close()
    # return variables

# Extract output variables from .rat file
def extractOutputVariablesFromFile( SpecFile ):
    infile = sp.read_file(SpecFile)
    
    variables = []
    for line in infile:
        match = re.search(r'(?:sys)\s+boolean\s+(\w+)\s*;', line)
        if match:
            variables.append(match.group(1))

    print("OUTPUT VARIABLES:", variables)
    print()
    return variables

# Extract variables as a list from a string formula
def extractVariablesFromFormula(phi):
    return [x for x in re.findall("\w+", phi) if x != "G" and x != "F" and x != "X" and x != "U"]

# Chains assumption units from a .rat file into a single assumption
def chainAssumptionUnits( SpecFile ):
    infile = open(SpecFile,"r")

    # Requirements are listed in the <requirements> element
    e = xml.etree.ElementTree.parse(infile).getroot().find("requirements")

    chainedAssumption = ""

    # The LTL formula of an assumption unit is in the <requirement> element
    for req in e.findall("requirement"):
        # The <kind> node contains the requirement type (A or G)
        # The <property> node contains the temporal expression
        if req.find("kind").text.lstrip().rstrip() == "A":
            chainedAssumption += normalizeFormulaSyntax(req.find("property").text) + " & "
    # Delete trailing " & "
    chainedAssumption = chainedAssumption[:-3]

    infile.close()
    return chainedAssumption


# Replaces '&&' with '&', '||' with '|'
def normalizeFormulaSyntax( formula ):
    formula = formula.replace('&&','&')
    formula = formula.replace('||','|')
    formula = re.sub(r"\b%s\b" % "next", "X", formula)
    formula = re.sub(r"\b%s\b" % "always", "G", formula)
    formula = re.sub(r"\b%s\b" % "eventually!", "F", formula)
    # Pattern replacement for boolean variables expressed as name=value
    patternBoolPosVar = re.compile("([A-Za-z0-9_]+)( ?= ?1)")
    patternBoolNegVar = re.compile("([A-Za-z0-9_]+)( ?= ?0)")

    formula = patternBoolPosVar.sub(r"\1",formula)
    formula = patternBoolNegVar.sub(r"!\1",formula)
    formula = formula.lstrip().rstrip()

    return formula

def normalizeSpinFormulaSyntax( formula ):
    formula = re.sub(r'\b&\b', '&&',formula)
    formula = re.sub(r'\b\|\b', '||',formula)
    # The last replacement is necessary when formula is output by a parser that recognizes FALSE as F(ALSE)
    formula = re.sub(r"\b%s\b" % "next", "X", formula)
    formula = re.sub(r"\b%s\b" % "always", "G", formula)
    formula = re.sub(r"\b%s\b" % "eventually!", "F", formula)
    formula = formula.replace("TRUE","true").replace("FALSE","false").replace("F(ALSE)","false")
    # Pattern replacement for boolean variables expressed as name=value
    patternBoolPosVar = re.compile("([A-Za-z0-9_]+)( ?= ?1)")
    patternBoolNegVar = re.compile("([A-Za-z0-9_]+)( ?= ?0)")

    formula = patternBoolPosVar.sub(r"\1", formula)
    formula = patternBoolNegVar.sub(r"!\1", formula)
    formula = formula.lstrip().rstrip()

    return formula

# varpattern matches variable names in LTL formulae
varpattern = re.compile(r"\b(?!TRUE|FALSE)\w+")

def getDistinctVariablesInFormula(formula):
    """Returns the set of all distinct variables appearing in formula"""
    varset = set(varpattern.findall(formula))
    varset.discard("X")
    varset.discard("G")
    varset.discard("F")
    return varset

def countBoolOpsInFormula(formula):
    formula = normalizeFormulaSyntax(formula)
    # We do not include the number of "<->" in the formula since they are already counted in "->"
    return formula.count("&") + formula.count("|") + formula.count("->")

def main():
    print(extractInputVariablesFromFile("/home/dgc14/WeakestAssumptions/Weakness/tests/amba08.rat"))
    print(extractOutputVariablesFromFile("/home/dgc14/WeakestAssumptions/Weakness/tests/amba08.rat"))

if __name__=="__main__":
    main()