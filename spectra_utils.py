import re
import specification as sp
import experiment_properties as exp
from counterstrategy import CounterstrategyState, Counterstrategy

import threading
import os

import jpype
import jpype.imports

import atexit

EXTRA_TIME = 60

jpype.startJVM(classpath=["spectra/dependencies/*", "spectra/spectra-tool.jar"])
SpectraTool = jpype.JClass('tau.smlab.syntech.Spectra.cli.SpectraTool')

import java.util
from java.util import ArrayList
from java.lang import Integer

print()

def check_realizability(spec_file_path, timeout):
    return SpectraTool.checkRealizability(spec_file_path, timeout)

def check_satisfiability(spec_file_path):
    return SpectraTool.checkSatisfiability(spec_file_path)

def check_well_separation(spec_file_path):
    return SpectraTool.checkWellSeparation(spec_file_path)

def check_y_sat(spec_file_path):
    return SpectraTool.checkYSatisfiability(spec_file_path)

def compute_unrealizable_core(spec_file_path):
    output = str(SpectraTool.computeUnrealizableCore(spec_file_path))

    # Extract the core line numbers from the output
    core_found = re.compile(r"< ([^>]*) >").search(output)
    if not core_found:
        return None

    # Parse the line numbers from the core
    line_nums = [int(x) for x in core_found.group(1).split(" ")]
    line_nums = list(set(line_nums))
    line_nums.sort()

    return line_nums

def compute_assumptions_core(spec_file_path):
    output = str(SpectraTool.computeAssumptionsCore(spec_file_path))
    match = re.search(r"<\s*([^>]*)\s*>", output)
    if not match:
        return None

    try:
        line_nums = sorted(set(int(x) for x in match.group(1).split()))
    except ValueError:
        return None

    return line_nums

class CounterstrategyTimeoutException(Exception):
    pass

def compute_counterstrategy(spec_file_path, min_sys_vars, timeout):
    try:
        return str(SpectraTool.computeCounterstrategy(spec_file_path, min_sys_vars, timeout))
    except java.util.concurrent.TimeoutException as e:
        # If Java throws a timeout, raise your Python timeout exception
        raise CounterstrategyTimeoutException("Counterstrategy computation timed out")

# def compute_repair_core(spec_file_path, repair_lines):
#     output = str(SpectraTool.computeRepairCore(spec_file_path, ArrayList(list(map(Integer, repair_lines)))))
#     match = re.search(r"<\s*([^>]*)\s*>", output)
#     if not match:
#         return None

#     try:
#         line_nums = sorted(set(int(x) for x in match.group(1).split()))
#     except ValueError:
#         return None

#     return line_nums

def shutdown():
    def force_exit():
        print("Shutdown taking too long, forcing exit.")
        os._exit(1)
    
    print("Shutting down SpectraTool...")
    timer = threading.Timer(10, force_exit)
    timer.start()
    
    SpectraTool.shutdownNow()
    jpype.shutdownJVM()
    
    print("JVM shutdown initiated...")
    timer.cancel()
    print("JVM shutdown complete.")

atexit.register(shutdown)

