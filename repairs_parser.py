
import os
import sys
import re
import csv
import spot
import specification as sp
import weakness_for_refinement as wr
import experiment_properties as exp



def main():
    sys.setrecursionlimit(1500)
    print("Current recursion depth limit:", sys.getrecursionlimit())
    directory = sys.argv[1]

    csv_file = open(directory + 'output.csv', 'w')
    csv_writer = csv.writer(csv_file)

    # Write headers
    headers = ["specification", "numRepairs", "numVariables", "d1", "d2", "nummaxentropysccs", "d3"]
    csv_writer.writerow(headers)

    txt_files = [filename for filename in os.listdir(directory) if filename.endswith(".txt")]
    txt_files.sort()
    for filename in txt_files:
        # filename = "GyroUnrealizable_Var1_710_GyroAspect_unrealizable_repairs.txt"
        if not filename.endswith(".txt"):
            continue
        spectra_file = filename.replace("_repairs.txt", ".spectra")
        parent_directory = os.path.dirname(os.path.abspath(directory))
        exp.changeCaseStudy(parent_directory + "/translations/" + spectra_file)
        print("=======================")
        print("FILENAME: ", filename)
        csv_row = [spectra_file]
        repairs = parse(directory + filename)
        if not repairs:
            csv_row.append(0)
            csv_row.append(0)
            csv_row.append(0)
            csv_row.append(0)
            csv_row.append(0)
            csv_row.append(0)
        else:
            repairs = [r for r in repairs if r is not None]
            counts = []
            weaknesses = []
            for assumptions in repairs:
                count = 0
                for asm in assumptions:
                    count += countNumberOfVariables(asm)
                counts.append(count)
                print("NUM VARIABLES: ", count)
                try:
                    w = wr.computeWeakness_probe(" & ".join(assumptions), exp.varsList)[0]
                    print("WEAKNESS: ", w)
                    weaknesses.append(w)
                except RecursionError:
                    print("RecursionError: Maximum recursion depth exceeded.")
                    print("Could not compute weakness")
                except OSError as e:
                    print(e)

            csv_row.append(len(repairs))
            csv_row.append(min(counts))
            max_weakness = wr.Weakness(0, 0, 0, 0)
            if weaknesses:
                max_weakness = max(weaknesses)
            print("MAX WEAKNESS: ", max_weakness)
            csv_row.append(max_weakness.d1)
            csv_row.append(max_weakness.d2)
            csv_row.append(max_weakness.nummaxentropysccs)
            csv_row.append(max_weakness.d3)
        print("=======================")

        csv_writer.writerow(csv_row)
        # break

    csv_file.close()


def parse(filename):
    with open(filename, "r") as file:
        text = file.read()

    match = re.search(r"Found (\d+) repair suggestions", text)
    if not match:
        return

    num_repairs = int(match.group(1))
    if num_repairs <= 0:
        return

    repair_pattern = re.compile(r"Repair #\d+\s*\[\s*(.*?)\s*\]", re.DOTALL)
    repairs = repair_pattern.findall(text)

    for i, repair in enumerate(repairs, start=1):
        # print(f"Repair #{i}:")
        asm_pattern = re.compile(r"asm\s*(.*?);", re.DOTALL)
        assumptions = asm_pattern.findall(repair)
        assumptions = [re.sub(r'\n\t*', "", x) for x in assumptions]
        assumptions = [re.sub(r'(\w+)=true', r'\1', x) for x in assumptions]
        assumptions = [re.sub(r'(\w+)=false', r'!\1', x) for x in assumptions]
        assumptions = [re.sub(r'next\((\w+)\)=true', r'X(\1)', x) for x in assumptions]
        assumptions = [re.sub(r'next\((\w+)\)=false', r'X(!(\1))', x) for x in assumptions]
        assumptions = [re.sub("and", "& ", x) for x in assumptions]
        # assumptions = [spot.formula(x).simplify().to_str(parenth=True) for x in assumptions]
        assumptions = [re.sub(r"G\s*\(", r"G(", x) for x in assumptions]
        assumptions = [re.sub(r"GF\s*\((.*)\)", r"G(F(\1))", x) for x in assumptions]
        repairs[i-1] = assumptions
        # for asm in assumptions:
        #     print(asm)
        # print()
    return repairs

def countNumberOfVariables(assumption):
    variable_names = re.findall(r'\b\w+\b', assumption)
    return len(set(variable_names))


if __name__ == '__main__':
    main()