import subprocess
import re
import specification as sp
import experiment_properties as exp
from counterstrategy import CounterstrategyState, Counterstrategy
import timeit

PATH_TO_CLI = "spectra/spectra-cli.jar"

def run_subprocess(cmd, newline):
    remaining_time = exp.timeout-exp.elapsed_time
    start_time = timeit.default_timer()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, timeout=remaining_time, text=True)
        output = p.stdout
        output = '\n'.join(str(output).split(newline))
    except:
        print("Timed out:", cmd)
    return output, timeit.default_timer() - start_time

def check_realizibility(spectra_file_path):
    cmd = "java -jar {} -i {}".format(PATH_TO_CLI, spectra_file_path)
    output, runtime = run_subprocess(cmd, "\\r\\n")

    match = re.search(r"TimeRealizabilityCheck: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    if re.search("Result: Specification is unrealizable", output):
        return False, actual_runtime
    elif re.search("Result: Specification is realizable", output):
        return True, actual_runtime
    return None, actual_runtime

def check_satisfiability(spectra_file_path):
    cmd = "java -jar {} -i {} -sat".format(PATH_TO_CLI, spectra_file_path)
    output, runtime = run_subprocess(cmd, "\\r\\n")

    match = re.search(r"Runtime: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    if re.search("No. The specification is not satisfiable.", output):
        return False, actual_runtime
    elif re.search("Yes. The specification is satisfiable.", output):
        return True, actual_runtime

    return None, actual_runtime

def check_well_separation(spectra_file_path):
    cmd = "java -jar {} -i {} --well-separation".format(PATH_TO_CLI, spectra_file_path)
    output, runtime = run_subprocess(cmd, "\\r\\n")

    match = re.search(r"Runtime: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    if re.search("non-well-separated", output):
        return False, actual_runtime
    elif re.search("well-separated", output):
        return True, actual_runtime
    
    print("Error checking well-separation.")
    return None, actual_runtime

def check_y_sat(spectra_file_path):
    cmd = "java -jar {} -i {} -y-sat".format(PATH_TO_CLI, spectra_file_path)
    output, runtime = run_subprocess(cmd, "\\r\\n")
    if re.search("y-sat", output):
        return True
    elif re.search("y-unsat", output):
        return False
    
    match = re.search(r"Runtime: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    print("Error checking y-sat.")
    return None

def generate_counterstrategy(spectra_file_path):
    cmd = "java -jar {} -i {} --counter-strategy-jtlv-format".format(PATH_TO_CLI, spectra_file_path)
    if exp.minimize_spec:
        cmd += " -min"
    output, runtime = run_subprocess(cmd, "\\n")

    match = re.search(r"TimeCounterstrategy: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    # print(output)
    if re.search("Result: Specification is unrealizable", output):
        return parse_counterstrategy(output.replace("\\t", "")), actual_runtime
    return None, actual_runtime

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
        inputs = dict()
        for x in exp.inputVarsList:
            inputs[x] = True if vars[x] == "true" else False
        outputs = dict()
        for y in exp.outputVarsList:
            if y in vars:
                outputs[y] = True if vars[y] == "true" else False
        successors = []
        if not match.group(5) == '':
            successors = match.group(5).split(", ")

        state = CounterstrategyState(state_name, inputs, outputs, successors, is_initial, is_dead)
        states[state.name] = state

    return Counterstrategy(states, use_influential=exp.use_influential)

def compute_unrealizable_core(spectra_file_path):
    cmd = "java -jar {} -i {} -uc".format(PATH_TO_CLI, spectra_file_path)
    output, runtime = run_subprocess(cmd, "\\r\\n")
    
    match = re.search(r"TimeUnrealizableCore: (\d+) millisecs.", output)
    actual_runtime = int(match.group(1)) / 1000.0
    exp.loading_time += runtime - actual_runtime

    core_found = re.compile("at lines <([^>]*)>").search(output)
    if not core_found:
        return None
    
    line_nums = [int(x) for x in core_found.group(1).split(" ") if x != ""]
    # print(line_nums)
    spec = sp.read_file(spectra_file_path)
    spec = [re.sub(r'\s', '', x) for x in spec]
    spec = sp.unspectra(spec)
    uc = []
    for line in line_nums:
        uc.append(spec[line])
    return uc
    
def main():
    specification = "SIMPLE/RG.spectra"
    print(check_realizibility(specification))

if __name__ == "__main__":
    main()
