import os
import re
import subprocess
import syntax_utils as su

# Static MathSAT binary path
MATHSAT_PATH = "MathSAT4/mathsat-4.2.17-linux-x86_64/bin/mathsat"


def writeMathsatFormulaToFile(filename, formula):
    outfile = open(filename, "w")
    # Get unique ids appearing in formula
    bool_vars_unique = set(re.findall(r"(\w+)", formula))
    bool_vars_unique.discard("TRUE")
    bool_vars_unique.discard("FALSE")

    mathsat_formula = "VAR\n" + ','.join(bool_vars_unique) + ": BOOLEAN\n" + "FORMULA\n" + formula

    outfile.write(mathsat_formula)
    outfile.close()


def is_satisfiable(formula, temp_dir="temp", cleanup=True):
    """
    Check the satisfiability of a formula using MathSAT.

    :param formula: The formula to check.
    :param temp_dir: Directory to store temporary files.
    :param cleanup: Whether to delete temporary files after execution.
    :return: True if satisfiable, False if unsatisfiable, None if error.
    """
    if not formula:
        raise ValueError("Formula must be provided.")

    # Ensure the temporary directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique file identifiers
    unique_id = os.getpid()  # Use process ID to ensure uniqueness
    formula_file = os.path.join(temp_dir, f"formula_{unique_id}")

    # Write the formula to a file
    writeMathsatFormulaToFile(formula_file, formula)

    cmd = [MATHSAT_PATH, "-solve", formula_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check for errors in MathSAT execution
    if result.returncode != 0:
        print(f"MathSAT error: {result.stderr}")
        if cleanup and os.path.isfile(formula_file):
            os.remove(formula_file)
        return None

    # Check the output for satisfiability
    output = result.stdout.strip()
    # print(output)

    # Cleanup temporary files
    if cleanup and os.path.isfile(formula_file):
        os.remove(formula_file)

    if "unsat" in output:
        return False

    return True


def parseInterpolant(filename):
    """Parses an interpolant as stored in a file produced by MathSAT"""

    infile = open(filename)
    # Find all auxiliary variables definitions and add them to a dictionary.
    # The key is the variable name and the value is its definition.
    define_pattern = re.compile(r"DEFINE (\w+) := (.*)")
    formula_pattern = re.compile(r"FORMULA (.*)")
    varname_pattern = re.compile(r"(def_\d+)")

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
        # formula = formula.replace(varname, definitions[varname])
        formula = re.sub(rf'\b{varname}\b', definitions[varname], formula)

    return su.removeUnnecessaryParentheses(formula)


def compute_craig_interpolant(formula1, formula2, temp_dir="temp", cleanup=True):
    """
    Compute a Craig interpolant for two formulas using MathSAT.

    :param formula1: The first formula (generic).
    :param formula2: The second formula (generic).
    :param mathsat_path: Path to the MathSAT binary.
    :param temp_dir: Directory to store temporary files.
    :param cleanup: Whether to delete temporary files after execution.
    :param parse_interpolant_func: Function to parse the interpolant file.
    :return: The computed interpolant or None if unsuccessful.
    """
    if not formula1 or not formula2:
        raise ValueError("Both formula1 and formula2 must be provided.")

    # Ensure the temporary directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique file identifiers
    unique_id = os.getpid()  # Use process ID to ensure uniqueness
    formula1_file = os.path.join(temp_dir, f"formula1_{unique_id}")
    formula2_file = os.path.join(temp_dir, f"formula2_{unique_id}")
    interpolant_file = os.path.join(temp_dir, f"interpolant_{unique_id}")

    # Write formulas to files
    writeMathsatFormulaToFile(formula1_file, formula1)
    writeMathsatFormulaToFile(formula2_file, formula2)
    
    cmd = [MATHSAT_PATH, f"-interpolate={interpolant_file}", formula1_file, formula2_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check for errors in MathSAT execution
    if result.returncode != 0:
        print(f"MathSAT error: {result.stderr}")
        if cleanup:
            for file in [formula1_file, formula2_file, interpolant_file]:
                if os.path.isfile(file):
                    os.remove(file)
        return None

    interpolant_file = interpolant_file + ".1.msat"

    # Parse the interpolant
    interpolant = None
    if os.path.isfile(interpolant_file):
        interpolant = parseInterpolant(interpolant_file)
        
    # Cleanup temporary files
    if cleanup:
        for file in [formula1_file, formula2_file, interpolant_file]:
            if os.path.isfile(file):
                os.remove(file)
    
    return interpolant