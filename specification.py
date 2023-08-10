import re
import os
import sys

def read_file(spectra_file):
    file = open(spectra_file, 'r')
    spec = file.readlines()
    file.close()
    return spec

def make_directories_if_needed(output_filename):
    folder = re.sub(r"/[^/]*$", "", output_filename)
    if not os.path.isdir(folder):
        make_directories_if_needed(folder)
        os.mkdir(folder)


def write_file(spec, output_filename):
    '''
    NB: newline = '\\\\n' is necessary so that file is compatible with
    linux (ILASP is run from linux).\n
    :param spec: List of lines to save.
    :param output_filename: filename to save to
    '''
    output_filename = re.sub(r"\\", "/", output_filename)
    make_directories_if_needed(output_filename)
    output = ''.join(spec)
    file = open(output_filename, 'w', newline='\n')
    file.write(output)
    file.close()

def extract_string_within(pattern, line, strip_whitespace=False):
    line = re.compile(pattern).search(line).group(1)
    if strip_whitespace:
        return re.sub(r"\s", "", line)
    return line

def strip_vars(spec, sub=["env", "sys"]):
    return re.findall(r"[" + '|'.join(sub) + r"]\s*boolean\s*(.*)\s*;",''.join(spec))
    variables = []
    for line in spec:
        words = line.split(" ")
        if words[0] in sub and words[0] != "":
            search = re.compile("boolean\s*(.*)\s*;").search(line)
            if search:
                var = re.sub("\s", "", search.group(1))
                variables.append(var)
    return variables


def word_sub(spec, word, replacement):
    spec = [re.sub(r"\b" + word + r"\b", replacement, x) for x in spec]
    return spec

def enumerate_spec(new_vars, spec):
    for i, line in enumerate(spec):
        line = re.sub(r"\s", "", line)
        words = line.split(" ")
        reg = re.search(r"(env|sys){", line)
        if reg:
            # if words[0] in ['env', 'sys'] and line.find("{") >= 0:
            enum = extract_string_within("{(.*)}", line, True).split(",")
            name = extract_string_within("}(.*);", line, True)
            for value in enum:
                pattern = name + "\s*=\s*" + value
                replacement = name + "_" + value
                new_vars.append(replacement)
                spec = [re.sub(pattern, replacement, x) for x in spec]
                pattern = pattern.replace("=", "!=")
                replacement = "!" + replacement
                spec = [re.sub(pattern, replacement, x) for x in spec]
            replacement_line = ""
            for var in new_vars:
                replacement_line += reg.group(1) + " boolean " + var + ";\n\n"
            spec[i] = replacement_line
    return spec

def spread_temporal_operator(line, temporal):
    pattern = r"(!)?" + temporal + r"\(([^\)]*)(&|\|)\s*"
    replacement = temporal + r"(\1\2) \3 \1" + temporal + "("
    while re.search(pattern, line):
        line = re.sub(pattern, replacement, line)
    line = re.sub("!" + temporal + r"\(", temporal + "(!", line)
    return line

def assign_equalities(formula_n, variables):
    for var in variables:
        formula_n = re.sub("!" + var + "(?!=|[a-z])", var + "=false", formula_n)
        formula_n = re.sub(var + "(?!=|[a-z])", var + "=true", formula_n)
    return formula_n

def parenthetic_contents(string):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            stack.append(i)
        elif c == ')' and stack:
            start = stack.pop()
            yield (len(stack), string[start + 1: i])

def has_trivial_outer_brackets(output):
    contents = list(parenthetic_contents(output))
    if len(contents) == 1:
        if len(contents[0][1]) == len(output) - 2:
            return True
    return False

def remove_trivial_outer_brackets(output):
    if has_trivial_outer_brackets(output):
        return output[1:-1]
    return output

# TODO: Separate file -> Specification class
def format_spec(spec):
    variables = strip_vars(spec)
    spec = word_sub(spec, "spec", "module")
    spec = word_sub(spec, "alwEv", "GF")
    spec = word_sub(spec, "alw", "G")
    # I is later removed as not real Spectra syntax:
    spec = word_sub(spec, "ini", "I")
    spec = word_sub(spec, "asm", "assumption --")
    spec = word_sub(spec, "gar", "guarantee --")
    new_vars = []
    # This bit deals with multi-valued 'enums'
    # spec = enumerate_spec(new_vars, spec)
    for i, line in enumerate(spec):
        words = line.strip("\t").split(" ")
        words = [x for x in words if x != ""]
        # This bit fixes boolean style
        if words[0] not in ['env', 'sys', 'spec', 'assumption', 'guarantee', 'module']:
            if len(re.findall(r"\(", line)) == len(re.findall(r"\)", line)) + 1:
                line = line.replace(";", " ) ;")
            # This replaces next(A & B) with next(A) & next(B):
            line = spread_temporal_operator(line, "next")
            line = spread_temporal_operator(line, "PREV")
            # line = assign_equalities(line, variables + new_vars)
            spec[i] = line
    # This simplifies multiple brackets to single brackets
    # spec = [re.sub(r"\(\s*\((.*)\)\s*\)", r"(\1)", x) for x in spec]
    spec = [remove_trivial_outer_brackets(x) for x in spec]
    # This changes names that start with capital letters to lowercase so that ilasp/clingo knows they are not variables.
    # spec = [re.sub('--[A-Z]', lambda m: m.group(0).lower(), x) for x in spec]
    return spec

def interpolation_spec(spec):
    spec = [re.sub(r"GF\s*\(([^\)]*)\)", r"G(F(\1))", line) for line in spec]
    spec = word_sub(spec, "next", "X")
    spec = [re.sub(r'(\w+)=true', '', x) for x in spec]
    spec = [re.sub(r'(\w+)=false', r'!\1', x) for x in spec]
    spec = [re.sub(";", "", line) for line in spec]
    return spec

def unformat_spec(spec):
    spec = [re.sub(r"G\(F\(([^\)]*)\)", r"alwEv (\1", line) for line in spec]
    spec = [re.sub(r"GF\s*\(([^\)]*)\)", r"alwEv (\1)", line) for line in spec]
    spec = [re.sub(r"G\s*\(([^\)]*)\)", r"alw (\1)", line) for line in spec]
    spec = [re.sub(r"X\(([^\)]*)\)", r"next(\1)", line) for line in spec]
    spec = [re.sub(r"\s*;", r";", line) for line in spec]
    return spec

def unspectra(spec):
    spec = [re.sub(r"alwEv\s*\(([^\)]*)\)", r"G(F(\1))", line) for line in spec]
    spec = [re.sub(r"alw\s*\(([^\)]*)\)", r"G(\1)", line) for line in spec]
    spec = [re.sub(r'(\w+)=true', '', x) for x in spec]
    spec = [re.sub(r'(\w+)=false', r'!\1', x) for x in spec]
    spec = [re.sub(r"next\(([^\)]*)\)", r"X(\1)", line) for line in spec]
    spec = [re.sub(r"\s*;", "", line) for line in spec]

    return spec

def assumptions(spec):
    spec = [x for x in spec if 'asm' in x]
    return format_spec(spec)

def guarantees(spec):
    spec = [x for x in spec if 'gar' in x]
    return format_spec(spec)

def simplify_assignments(spec, variables):
    vars = "|".join(variables)
    spec = [re.sub(r"(" + vars + ")=true", r"\1", line) for line in spec]
    spec = [re.sub(r"(" + vars + ")=false", r"!\1", line) for line in spec]
    return spec

def extract_all_expressions(exp_type, spec):
    search_type = exp_type
    if exp_type in ["asm", "assumption"]:
        search_type = "asm|assumption"
    if exp_type in ["gar", "guarantee"]:
        search_type = "gar|guarantee"
    output = [re.sub(r"\s", "", spec[i + 1]) for i, line in enumerate(spec) if re.search(search_type, line)]
    return output


def check_first_chars(list, type):
    if len(list) == 1:
        return list[0]
    if type == "conjuncts":
        dist_char = "F"
        join_char = "|"
    if type == "disjuncts":
        dist_char = "G"
        join_char = "&"

    first_chars = [chars[0:2] for chars in list]
    character = first_chars[0]
    if all(character == char for char in first_chars):
        if character in ["X(", dist_char + "("]:
            list = [chars[2:-1] for chars in list]
            output = character[0] + "(" + join_char.join(list) + ")"
            return output
    output = join_char.join(list)
    return output


def push_negations(disjuncts):
    disjuncts = [re.sub(r"!\((.*)\)W\((.*)\)", r"(!\2)U((!\2)&(!\1))", x) for x in disjuncts]
    disjuncts = [re.sub(r"!\((.*)\)U\((.*)\)", r"(!\2)W((!\2)&(!\1))", x) for x in disjuncts]
    disjuncts = [re.sub(r"!!", r"", x) for x in disjuncts]
    disjuncts = [re.sub(r"!F\(", r"G(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!G\(", r"F(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!X\(", r"X(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!next\(", r"next(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!PREV\(", r"PREV(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!\(", r"(!", x) for x in disjuncts]
    disjuncts = [re.sub(r"!!", r"", x) for x in disjuncts]
    return disjuncts

def remove_double_outer_brackets(string):
    if string[0:2] == "((" and string[-3:-1] == "))":
        return string[1:-1]
    return string

def negate(string):
    '''
    Assumes precedence of AND (DNF)
    :param string:
    :return:
    '''
    # examples:
    # string1 = 'F(level_1_nest_0)|F(level_1_nest_1)|F(level_1_nest_2)'
    # string2 = "A|B&C"
    # string = "(level_1)W(level_2)"
    if string == "":
        return string
    disjuncts = re.sub(r"\s", "", string).split("|")
    for i, sub_string in enumerate(disjuncts):
        conjuncts = sub_string.split("&")
        conjuncts = ["!" + x for x in conjuncts]
        conjuncts = push_negations(conjuncts)
        # This way we push F's out if they are common
        conjunct = check_first_chars(conjuncts, "conjuncts")
        # conjunct = "|".join(conjuncts)
        if len(conjuncts) > 1 and len(disjuncts) > 1:
            conjunct = "(" + conjunct + ")"
        conjunct = remove_double_outer_brackets(conjunct)
        disjuncts[i] = conjunct
    disjuncts = push_negations(disjuncts)
    # This is if we want to push G's out, which i've decided we don't
    # disjuncts = check_first_chars(disjuncts, "disjuncts")
    # return disjuncts
    output = '&'.join(disjuncts)
    output = remove_trivial_outer_brackets(output)
    return output

def spectra_to_DNF(formula):
    prefix = ""
    suffix = ";"
    justice = re.search(r"G\s*\((.*)\)\s*;", formula)
    liveness = re.search(r"GF\s*\((.*)\)\s*;", formula)
    if justice:
        prefix = "G("
        suffix = ");"
        pattern = justice
    if liveness:
        prefix = "GF("
        suffix = ");"
        pattern = liveness
    if not justice and not liveness:
        non_temporal_formula = formula
    else:
        non_temporal_formula = pattern.group(1)
    parts = non_temporal_formula.split("->")
    if len(parts) == 1:
        return prefix + non_temporal_formula + suffix
    return prefix + '|'.join([negate(parts[0]), parts[1]]) + suffix


def extract_non_liveness(spec, exp_type):
    output = extract_all_expressions(exp_type, spec)
    return [spectra_to_DNF(x) for x in output if not re.search("F", x)]


def extract_expressions(spec, counter_strat=False, guarantee_only=False):
    variables = strip_vars(spec)
    spec = simplify_assignments(spec, variables)
    assumptions = extract_non_liveness(spec, "assumption")
    print("ASSUMPTIONS: ", assumptions)
    guarantees = extract_non_liveness(spec, "guarantee")
    print("GUARANTEES ===============")
    for gar in guarantees:
        print(gar)

    if counter_strat:
        guarantees = []
    if guarantee_only:
        assumptions = []
    prev_expressions = [re.search(r"G\((.*)\);", x).group(1) for x in assumptions + guarantees if
                        re.search(r"PREV", x) and re.search("G", x)]
    list_of_prevs = ["PREV\\(" + s + "\\)" for s in variables + ["!" + x for x in variables]]
    prev_occurances = [re.findall('|'.join(list_of_prevs), exp) for exp in prev_expressions]
    prevs = [item for sublist in prev_occurances for item in sublist]
    prevs = [re.sub(r"PREV\(!*(.*)\)", r"prev_\1", x) for x in prevs]
    prevs = list(dict.fromkeys(prevs))
    variables += prevs
    variables.sort()
    
    unprimed_expressions = [re.search(r"G\(([^F]*)\);", x).group(1) for x in assumptions + guarantees if
                            not re.search(r"PREV|next", x) and re.search(r"G\s*\(", x)]
    primed_expressions = [re.search(r"G\(([^F]*)\);", x).group(1) for x in assumptions + guarantees if
                          re.search(r"PREV|next", x) and re.search(r"G\s*\(", x)]
    initial_expressions = [x.strip(";") for x in assumptions + guarantees if not re.search(r"G\s*\(|GF\s*\(", x)]
    return initial_expressions, prevs, primed_expressions, unprimed_expressions, variables

def generate_filename(spectra_file, replacement, output=False):
    if output:
        spectra_file = spectra_file.replace("input-files", "output-files")
    return spectra_file.replace(".spectra", replacement)

def lower_variables(spec, variables):
    mapping = {var: var.lower() for var in variables}
    for key in mapping.keys():
        spec = [re.sub(r"\b" + re.escape(key) + r"\b", mapping[key], line) for line in spec]
    return spec, list(mapping.values())

def name_expressions(spec):
    count = 0
    for i, line in enumerate(spec):
        exp_type = re.search(r"(assumption|guarantee)", line)
        if exp_type:
            if not re.search(r"(assumption|guarantee)\s*--\s*[a-zA-z]+", line):
                exp = exp_type.group(1)
                spec[i] = (exp + " -- " + exp + str(count) + '\n')
                count += 1
    return spec

def parenthetic_contents_with_function(string, include_after=False):
    """Generate parenthesized contents in string as pairs (level, contents)."""
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            stack.append(i)
        elif c == ')' and stack:
            start = stack.pop()
            pre = string[start - 1:start]
            # if start == 0:
            #     pre = string[0]
            if include_after:
                if i + 2 > len(string):
                    post = ""
                else:
                    post = string[i + 1:i + 2]
                yield (len(stack), pre, string[start + 1: i], post)
            else:
                yield (len(stack), pre, string[start + 1: i])


def iff_to_dnf_sub(formula):
    exp = re.search(r"(.*)<->(.*)", formula)
    if (exp):
        a = exp.group(1)
        b = exp.group(2)
        return "(" + a + "&" + b + "|" + negate(a) + "&" + negate(b) + ")"

    # formula = "((FULL & next(FULL)|!FULL&!next(FULL)) &(EMPTY & next(EMPTY)|!EMPTY&!next(EMPTY)))"

    return formula


def iff_to_dnf(line):
    # line = '\tG((ENQ <-> DEQ) -> ((FULL <-> next(FULL)) &(EMPTY <-> next(EMPTY))));\n'
    if not re.search("<->", line):
        return line
    contents = list(parenthetic_contents_with_function(line))
    levels = max([tup[0] for tup in contents]) + 1
    for i in reversed(range(levels)):
        for j, par in enumerate(contents):
            if par[0] == i:
                # replacement bit
                one_up = [x for x in contents if x[0] == i + 1]
                string = par[2]
                for x in one_up:
                    string = re.sub(re.escape(x[2]), x[3], string)
                contents[j] = tuple(list(contents[j]) + [iff_to_dnf_sub(string)])
    for tup in contents:
        if tup[0] == 0:
            line = re.sub(re.escape(tup[2]), tup[3], line)
    return line
    # exp = re.search(r"(G|GF)\s*\((.*)<->(.*)\s*\)\s*;", line)
    # if (exp):
    #     a = exp.group(2)
    #     b = exp.group(3)
    #     return "\t" + exp.group(1) + "(" + a + "&" + b + "|" + negate(a) + "&" + negate(b) + ");\n\n"
    # return line


def format_iff(spec):
    # variables = strip_vars(spec)
    # spec, variables = lower_variables(spec, variables)
    spec = [re.sub(r"next\(([^\)]*)\)", r"(next(\1))", line) for line in spec]
    # spec = format_spec(spec)
    # spec = simplify_assignments(spec, variables)
    # spec = name_expressions(spec)
    spec = [iff_to_dnf(line) for line in spec]
    # spec = [symplify(line, variables) for line in spec]
    return spec

# def main():
#     spectra_file = "Examples/cimattiAnalyzing/amba_ahb_w_guar_trans_amba_ahb_1.spectra"
#     format_iff(spectra_file)
#     spec = read_file(spectra_file)
#     # spec = format_spec(spec)
#     spec = unformat_spec(spec)
#     out_file = generate_filename(spectra_file, "_formatted.spectra")
#     # spec = [line + "\n" for line in spec]
#     write_file(spec, out_file)

def main():
    spectra_file = sys.argv[1]
    spec = read_file(spectra_file)
    spec = [re.sub('--[A-Z]', lambda m: m.group(0).lower(), x) for x in spec]
    out_file = generate_filename(spectra_file, "_formatted.spectra")
    # spec = [line + "\n" for line in spec]
    write_file(spec, out_file)

if __name__ == '__main__':
    main()