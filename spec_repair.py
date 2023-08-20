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

def run_spec_repair(spectra_file, algorithm, timeout, output_file):
    command = f"java -jar {SPEC_REPAIR_PATH} {spectra_file} {algorithm} {timeout}"

    with open(output_file, "w") as output:
        try:
            subprocess.run(command, shell=True, check=True, stdout=output)
        except subprocess.CalledProcessError:
            print(f"Error executing SpecRepair.java for {spectra_file}")


def create_csv_from_output(output_file, csv_output_file):

    with open(output_file, "r") as file:
        text = file.read()

    match = re.search(r"Found (\d+) repair suggestions", text)
    if not match:
        return

    num_repairs = int(match.group(1))
    if num_repairs <= 0:
        return

    repair_pattern = re.compile(r"Repair #\d+\s*\[\s*(.*?)\s*\]", re.DOTALL)
    asm_pattern = re.compile(r"asm\s*(.*?);", re.DOTALL)
    
    repairs = repair_pattern.findall(text)

    with open(csv_output_file, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Id", "UniqueRefinement", "NumVariables"])

        for i, repair in enumerate(repairs, start=1):
            assumptions = asm_pattern.findall(repair)
            assumptions = normalize_assumptions(assumptions)
            num_variables = count_num_variables(assumptions)
            csv_writer.writerow([str(uuid.uuid4()), assumptions, num_variables])

    
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

def count_num_variables(assumptions):
    total_variables = set()

    assumptions = [re.sub(r"G\(F\s*\((.*)\)\)", r"\1", x) for x in assumptions]
    assumptions = [re.sub(r"G\((.*)\)", r"\1", x) for x in assumptions]
    assumptions = [re.sub(r"X\((.*)\)", r"\1", x) for x in assumptions]

    for assumption in assumptions:
        variables = re.findall(r'\b\w+\b', assumption)
        total_variables.update(variables)

    return len(total_variables)


def main():
    parser = argparse.ArgumentParser(description="Run SpecRepair.java on .spectra file specifications in a folder.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-a", "--algorithm", required=True, choices=["GLASS", "JVTS", "ALUR"], help="Algorithm (GLASS, JVTS, or ALUR)")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout in minutes (optional)")

    args = parser.parse_args()

    spectra_file_name = os.path.basename(args.input)

    output_file = os.path.join(args.output, os.path.splitext(spectra_file_name)[0] + "_output.txt")
    run_spec_repair(args.input, args.algorithm, args.timeout, output_file)

    csv_output_file = os.path.join(args.output, os.path.splitext(spectra_file_name)[0] + ".csv")
    create_csv_from_output(output_file, csv_output_file)

if __name__ == "__main__":
    main()