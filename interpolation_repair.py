import os
import timeit
import argparse
from collections import deque
import experiment_properties as exp
from refinement import RefinementNode
import csv
import jpype

MAX_NODES = 3000 # Max nodes to expand in the experiment

print("Resetting temp...")
temp_folder = 'temp'
for temp_file in os.listdir(temp_folder):
    temp_file_path = os.path.join(temp_folder, temp_file)
    try:
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
    except Exception as e:
        print(e)
print("Reset complete!")

def enough_repairs(solutions):
    return exp.repair_limit > 0 and len(solutions) == exp.repair_limit

def FifoDuplicateCheckRefinement():
    """This implements the refinement strategy that uses model checking against ancestors
    to generate nodes"""

    initial_spec_node = RefinementNode()

    if initial_spec_node.isRealizable():
        print("Specification is already realizable. No fix required.")
        return
    
    initial_spec_node.timestamp = 0
    initial_spec_node.timestamp_realizability_check = 0

    solutions = []
    explored_refs = []
    duplicate_refs = []

    datafile = open(exp.datafile, "w")
    csv_writer = csv.writer(datafile)
    datafields = [
        "Id",
        "UniqueRefinement",
        "Timestamp",
        "TimestampRealizabilityCheck",
        "Length",
        "Parent",
        "NumChildren",
        "IsRealizable",
        "IsSatisfiable",
        "IsWellSeparated",
        "IsSolution",
        "TimeRealizabilityCheck",
        "TimeSatisfiabilityCheck",
        "TimeWellSeparationCheck",
        "TimeCounterstrategy",
        "CounterstrategyNumStates",
        "TimeRefine",
        "TimeGenerationMethod"
    ]
    
    csv_writer.writerow(datafields)

    # Root of the refinement tree: it contains the initial spec
    refinement_queue = deque([initial_spec_node])

    nodes = 0
    exp.reset_start_experiment()

    while refinement_queue \
      and not enough_repairs(solutions) \
      and nodes < MAX_NODES \
      and exp.get_elapsed_time() < exp.timeout:
        
        cur_node = refinement_queue.pop()
        nodes += 1

        if cur_node.unique_refinement in explored_refs:
            print("++ DUPLICATE NODE")
            duplicate_refs.append(cur_node.unique_refinement)
            continue

        print("++++ ELAPSED TIME:", exp.elapsed_time)
        print("++++ QUEUE LENGTH:", len(refinement_queue))
        print("++++ Solutions:", len(solutions))
        print("++++ Duplicates:", len(duplicate_refs))
        print("++++ Node number:", nodes)
        print("++++ Refinement:", cur_node.gr1_units)
        print("++++ Length:", cur_node.length)

        try:
            print("++ REALIZABILITY CHECK")
            if not cur_node.isRealizable():
                print("++ COUNTERSTRATEGY COMPUTATION - REFINEMENT GENERATION")
                candidate_ref_nodes = cur_node.refine()
                refinement_queue.extendleft(candidate_ref_nodes)
            elif cur_node.isSatisfiable():
                cur_node.isWellSeparated()
                print("++ REALIZABLE REFINEMENT: SAT CHECK")
                solutions.append(cur_node.gr1_units)
            else:
                print("++ VACUOUS SOLUTION")
        except Exception as e:
            # cur_node.writeNotes(str(e))
            print(e)

        cur_node.saveRefinementData(csv_writer, datafields)
        explored_refs.append(cur_node.unique_refinement)

    datafile.close()
    jpype.shutdownJVM()
    print("++++ FINISHED EXECUTION")
    print("++++ RUNTIME:", exp.get_elapsed_time())

def main():
    parser = argparse.ArgumentParser(description="Run interpolation_repair.py on .spectra file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=float, default=10, help="Timeout in minutes (default: 10)")
    parser.add_argument("-rl", "--repair-limit", type=int, default=-1, help="Repair limit (default: -1)")
    parser.add_argument("-allgars", action="store_true", help="Use all guarantees")
    parser.add_argument("-min", action="store_true", help="Minimize specification")
    parser.add_argument("-inf", action="store_true", help="Use influential output variables")

    args = parser.parse_args()
    exp.configure(args.input, args.repair_limit, args.timeout*60, args.output, args.allgars, args.min, args.inf, debug=False)
    FifoDuplicateCheckRefinement()

if __name__=="__main__":
    main()
