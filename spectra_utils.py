import subprocess
import re
import specification as sp
import experiment_properties as exp

PATH_TO_CLI = "spectra/spectra-cli.jar"

def run_subprocess(cmd, newline):
    remaining_time = exp.timeout-exp.elapsed_time
    p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, timeout=remaining_time, text=True)
    output = p.stdout
    output = '\n'.join(str(output).split(newline))
    return output

def extract_unrealizable_cores(specification):
    '''
    Extracted runnable jar from cores.ExploreCores from
    https://github.com/jringert/spectra-tutorial/blob/main/D2_counter-strategy/src/cores/ExploreCores.java
    \nHad to edit file, so it takes input from args.\n
    :return: True if cores found, False otherwise.
    '''
    path_to_jar = "spectra/spectra_unrealizable_cores.jar"
    cmd = "java -jar {} {}".format(path_to_jar, specification)
    output = run_subprocess(cmd, "\\r\\n")
    core_found = re.compile("at lines <([^>]*)>").search(output)
    if core_found:
        line_nums = [int(x) for x in core_found.group(1).split(" ") if x != ""]
        # line_nums = [59, 71, 75]
        spec = sp.read_file(specification)
        # spec = sp.format_spec(spec)
        spec = [re.sub(r'\s*;\n$', '', re.sub(r'\s', '', x)) for x in spec]
        spec = sp.unspectra(spec)
        uc = []
        for line in line_nums:
            uc.append(spec[line])
        # self.guarantee_violation_list = names
        # self.calculate_violated_expressions(exp_type="guarantee")
        return uc
    # else:
    #     line_nums = ['']
    # if line_nums != ['']:
    #     print("\nUnrealizable core:")
    # else:
    #     print("\nNo Unrealizable Core Found.")
    #     return False

def generate_counter_strat(specification):
    cmd = "java -jar {} -i {} --counter-strategy-jtlv-format".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\n")
    if re.search("Result: Specification is unrealizable", output):
        return output.replace("\\t", "")
    return None

def check_realizibility(specification):
    cmd = "java -jar {} -i {}".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("Result: Specification is unrealizable", output):
        return False
    elif re.search("Result: Specification is realizable", output):
        return True
    
    print("Spectra file in wrong format for CLI realizability check.")
    return None

def check_satisfiability(specification):
    cmd = "java -jar {} -i {} -sat".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("No. The specification is not satisfiable.", output):
        return False
    elif re.search("Yes. The specification is satisfiable.", output):
        return True
    
    print("Spectra file in wrong format for CLI satisfiability check.")
    return None

def check_well_separation(specification):
    cmd = "java -jar {} -i {} --well-separation".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\r\\n")
    if re.search("non-well-separated", output):
        return False
    elif re.search("well-separated", output):
        return True
    
    print("Error checking well-separation.")
    return None

def addAssumption(specification, assumption):
    assumption = sp.unformat_spec(assumption)
    specification.append(assumption)

def writeSpectrafile(filename, specification):
    pass

def main():
    specification = "Examples/Protocol.spectra"
    print(check_realizibility(specification))

if __name__ == "__main__":
    main()
