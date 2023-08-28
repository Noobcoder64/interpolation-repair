import subprocess
import re
import specification as sp
import experiment_properties as exp
from counterstrategy import CounterstrategyState, Counterstrategy

PATH_TO_CLI = "spectra/spectra-cli.jar"

def run_subprocess(cmd, newline):
    remaining_time = exp.timeout-exp.elapsed_time
    p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, timeout=remaining_time, text=True)
    output = p.stdout
    output = '\n'.join(str(output).split(newline))
    return output

def check_realizibility(spectra_file_path):
    cmd = "java -jar {} -i {}".format(PATH_TO_CLI, spectra_file_path)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("Result: Specification is unrealizable", output):
        return False
    elif re.search("Result: Specification is realizable", output):
        return True
    
    print("Spectra file in wrong format for CLI realizability check.")
    return None

def check_satisfiability(spectra_file_path):
    cmd = "java -jar {} -i {} -sat".format(PATH_TO_CLI, spectra_file_path)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("No. The specification is not satisfiable.", output):
        return False
    elif re.search("Yes. The specification is satisfiable.", output):
        return True
    
    print("Spectra file in wrong format for CLI satisfiability check.")
    return None

def check_well_separation(spectra_file_path):
    cmd = "java -jar {} -i {} --well-separation".format(PATH_TO_CLI, spectra_file_path)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("non-well-separated", output):
        return False
    elif re.search("well-separated", output):
        return True
    
    print("Error checking well-separation.")
    return None

def generate_counterstrategy(spectra_file_path):
    cmd = "java -jar {} -i {} --counter-strategy-jtlv-format".format(PATH_TO_CLI, spectra_file_path)
    output = run_subprocess(cmd, "\\n")
    if re.search("Result: Specification is unrealizable", output):
        return parse_counterstrategy(output.replace("\\t", ""))
    return None

def parse_counterstrategy(text):
    state_pattern = re.compile(r"(Initial )?(Dead )?State (\w+) <(.*?)>\s+With (?:no )?successors(?: : |.)(.*)(?:\n|$)")
    assignment_pattern = re.compile(r"(\w+):(\w+)")

    state_matches = re.finditer(state_pattern, text)
    states = dict()
    for match in state_matches:
        is_initial = match.group(1) != None
        is_dead = match.group(2) != None
        state_name = match.group(3)
        vars = dict(re.findall(assignment_pattern,  match.group(4)))
        inputs = {x:vars[x] for x in exp.inputVarsList}
        outputs = dict()
        for y in exp.outputVarsList:
            if y in vars:
                outputs[y] = vars[y]
        successors = []
        if not match.group(5) == '':
            successors = match.group(5).split(", ")
        state = CounterstrategyState(state_name, inputs, outputs, successors, is_initial, is_dead)
        states[state.name] = state

    return Counterstrategy(states, use_influential=True)

def compute_unrealizable_core(spectra_file_path):
    cmd = "java -jar {} -i {} -uc".format(PATH_TO_CLI, spectra_file_path)
    output = run_subprocess(cmd, "\\r\\n")
    core_found = re.compile("at lines <([^>]*)>").search(output)
    if not core_found:
        return None
    
    line_nums = [int(x) for x in core_found.group(1).split(" ") if x != ""]
    spec = sp.read_file(spectra_file_path)
    spec = [re.sub(r'\s', '', x) for x in spec]
    spec = sp.unspectra(spec)
    uc = []
    for line in line_nums:
        uc.append(spec[line])
    return uc
    

def main():
    specification = "Examples/Protocol.spectra"
    print(check_realizibility(specification))

if __name__ == "__main__":
    main()
