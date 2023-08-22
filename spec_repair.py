import sys
import os
import re
import csv
import uuid
import argparse
import subprocess
import time

SPEC_REPAIR_PATH = "spectra/SpecRepair.jar"
ALGORITHMS = ["GLASS", "JVTS", "ALUR"]

def run_spec_repair(spectra_file, algorithm, timeout):
    command = f"java -jar {SPEC_REPAIR_PATH} {spectra_file} {algorithm} {timeout}"
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError:
        print(f"Error executing SpecRepair.java for {spectra_file}")
        return None

def create_csv_from_output(output, csv_output_file):
    match = re.search(r"Found (\d+) repair suggestions", output)
    if not match:
        return

    num_repairs = int(match.group(1))
    if num_repairs <= 0:
        return

    repair_pattern = re.compile(r"Repair #\d+\s*\[\s*(.*?)\s*\]", re.DOTALL)
    asm_pattern = re.compile(r"asm\s*(.*?);", re.DOTALL)
    
    repairs = repair_pattern.findall(output)

    with open(csv_output_file, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Id", "UniqueRefinement", "IsSolution"])

        for i, repair in enumerate(repairs, start=1):
            assumptions = asm_pattern.findall(repair)
            assumptions = normalize_assumptions(assumptions)
            csv_writer.writerow([str(uuid.uuid4()), assumptions, True])

    
def normalize_assumptions(assumptions):
    assumptions = [re.sub(r'\n\t*', "", x) for x in assumptions]
    assumptions = [re.sub(r'(\w+)=true', r'\1', x) for x in assumptions]
    assumptions = [re.sub(r'(\w+)=false', r'!\1', x) for x in assumptions]
    assumptions = [re.sub(r'next\((\w+)\)=true', r'X(\1)', x) for x in assumptions]
    assumptions = [re.sub(r'next\((\w+)\)=false', r'X(!(\1))', x) for x in assumptions]
    assumptions = [re.sub(r'and', '& ', x) for x in assumptions]
    assumptions = [re.sub(r"G\s*\(", r"G(", x) for x in assumptions]
    assumptions = [re.sub(r"GF\s*\((.*)\)", r"G(F(\1))", x) for x in assumptions]
    return assumptions

def main():
    parser = argparse.ArgumentParser(description="Run spec_repair.py on a .spectra file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-a", "--algorithm", required=True, choices=["GLASS", "JVTS", "ALUR"], help="Algorithm (GLASS, JVTS, or ALUR)")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout in minutes (default: 10)")

    args = parser.parse_args()

    output = run_spec_repair(args.input, args.algorithm, args.timeout)

    spectra_file_name = os.path.splitext(os.path.basename(args.input))[0]
    csv_file_name = f"{spectra_file_name}_{args.algorithm}.csv"
    csv_output_file = os.path.join(args.output, csv_file_name)
    create_csv_from_output(output, csv_output_file)

if __name__ == "__main__":
    main()