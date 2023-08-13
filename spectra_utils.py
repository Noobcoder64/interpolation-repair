import subprocess
import re
import specification as sp

PATH_TO_CLI = "spectra/spectra-cli.jar"

def run_subprocess(cmd, newline, suppress=False, timeout=-1):
    # timed = timeout > 0

    if suppress:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.DEVNULL)#, start_new_session=timed)
    else:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)#, start_new_session=timed)
    # if timed:
    #     try:
    #         p.wait(timeout=timeout)
    #     except subprocess.TimeoutExpired:
    #         print("Subprocess Timeout")
    #         os.kill(p.pid, signal.CTRL_C_EVENT)
    #         subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
    #         return "Timeout"
    output = p.communicate()[0]
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
        # line_nums = [22, 24]
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
    cmd = "java -jar {} -i {} --counter-strategy".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\n")
    if re.search("Result: Specification is unrealizable", output):
        output = str(output).split("\n")
        
        counter_strategy = list(filter(re.compile(r"\s*->\s*[^{]*{[^}]*").search, output))
        # self.cs_list = [counter_strategy]
        
        # print(self.cs_trace_PI)
        return counter_strategy

def check_realizibility(specification):
    cmd = "java -jar {} -i {}".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\r\\n")
    # print("REALIZABILITY CHECK:", output)
    if re.search("Result: Specification is unrealizable", output):
        return False
    elif re.search("Result: Specification is realizable", output):
        return True
    
    print("Spectra file in wrong format for CLI realizability check:")
    return None

def check_satisfiability(specification):
    cmd = "java -jar {} -i {} --sat".format(PATH_TO_CLI, specification)
    output = run_subprocess(cmd, "\\r\\n")
    # print("SATISFIABILITY CHECK:", output)
    if re.search("No. The specification is not satisfiable.", output):
        return False
    elif re.search("Yes. The specification is satisfiable.", output):
        return True
    
    print("Spectra file in wrong format for CLI realizability check:")
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
