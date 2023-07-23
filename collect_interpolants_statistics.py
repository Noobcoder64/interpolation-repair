"""This script collects the following statistics per case study explored via interpolation:
- Total number of nodes expanded
- Total number of interpolants computed
- Number of "No interpolant" (presumably due to "SAT" problems)
- Number of non-state-separable interpolants
- Total number of state components across interpolants
- Total number of non-I/O-separable components across interpolants
"""

import sys
import os
import csv

inputdir = sys.argv[1]

outfile = open(inputdir + "/interpolants_statistics.csv", "w")
outfile.write("Filename;ExpandedNodes;TotalInterpolantsComputed;NoInterpolant;NonStateSeparable;TotalStateComponents;NonIOSeparableComponents;CounterstrategyNotComputed;NumSolutions\n")

for filename in os.listdir(inputdir):
    print("+++++++++ " + filename)
    if "interpolation" in filename:
        datafile = open(inputdir + "/" + filename, "r")
        reader = csv.reader(datafile,delimiter=";")

        try:
            headers = next(reader)
            idx_is_realizable = headers.index("IsRealizable")
            idx_is_solution = headers.index("IsSolution")
            if "Notes" not in headers:
                idx_notes = len(headers) # The notes entry in my CSV files has no header. It is the last entry in all other
                                     # lines, which have one element more than the headers line
            else:
                idx_notes = headers.index("Notes")

            expanded_nodes = 0
            total_interpolants_computed = 0
            no_interpolant = 0
            non_state_separable = 0
            total_state_components = 0
            non_io_separable_components = 0
            counterstrategy_not_computed = 0
            num_solutions = 0

            for line in reader:
                notes = line[idx_notes]
                if eval(line[idx_is_realizable]) == False:
                    if notes != "node not expanded":
                        expanded_nodes += 1
                        if "No such file or directory" in notes or "counterstrategy not computed" in notes:
                            counterstrategy_not_computed += 1
                            continue
                        if notes == "No interpolant":
                            no_interpolant += 1
                            continue
                        total_interpolants_computed += 1
                        if notes == "Non-state-separable":
                            non_state_separable += 1
                            continue
                        if notes.startswith("state components:"):
                            state_components_numbers = [int(s) for s in notes.split() if s.isdigit()]
                            total_state_components += state_components_numbers[0]
                            non_io_separable_components += state_components_numbers[1]
                else:
                    if eval(line[idx_is_solution]) == True:
                        num_solutions += 1

            outfile.write(str(filename)+";"
                          + str(expanded_nodes)+";"
                          + str(total_interpolants_computed)+";"
                          + str(no_interpolant)+";"
                          + str(non_state_separable)+";"
                          + str(total_state_components)+";"
                          + str(non_io_separable_components)+";"
                          + str(counterstrategy_not_computed)+";"
                          + str(num_solutions)+"\n")
            print("File analysis complete")

        except Exception:
            print("The file is not a raw data file")
        finally:
            datafile.close()

outfile.close()