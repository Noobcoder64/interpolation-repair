import os
import timeit
import argparse
from collections import deque
import experiment_properties as exp
from refinement import RefinementNode
import concurrent.futures
import csv

MAX_NODES = 3000 # Max nodes to expand in the experiment

# print("Resetting temp...")
# temp_folder = 'temp'
# for temp_file in os.listdir(temp_folder):
#     temp_file_path = os.path.join(temp_folder, temp_file)
#     try:
#         if os.path.isfile(temp_file_path):
#             os.unlink(temp_file_path)
#     except Exception as e:
#         print(e)
# print("Reset complete!")


def FifoDuplicateCheckRefinement():
    """This implements the refinement strategy that uses model checking against ancestors
    to generate nodes"""
    start_experiment = exp.start_experiment

    solutions = []
    explored_refs = []
    duplicate_refs = []

    datafile = open(exp.datafile, "w")
    csv_writer = csv.writer(datafile)
    datafields = [
        "Id",
        "UniqueRefinement",
        "Timestamp",
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

    initial_spec_node = RefinementNode()

    # Root of the refinement tree: it contains the initial spec
    refinement_queue = deque([initial_spec_node])

    nodes = 0
    exp.elapsed_time = 0
    while refinement_queue and nodes < MAX_NODES and exp.elapsed_time < exp.timeout:
        cur_node = refinement_queue.pop()
        nodes += 1

        if cur_node.isRealizable():
            print(exp.specfile + " IS REALIZABLE")
        
        if not cur_node.isWellSeparated():
            print(exp.specfile + " IS NOT WELL-SEPARATED")

        return

        if cur_node.unique_refinement not in explored_refs:
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
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        print("++ COUNTERSTRATEGY COMPUTATION - REFINEMENT GENERATION")
                        refine_future = executor.submit(cur_node.refine)
                        remaining_timeout = exp.timeout - exp.elapsed_time
                        candidate_ref_nodes = refine_future.result(timeout=remaining_timeout)
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
        else:
            print("++ DUPLICATE NODE")
            duplicate_refs.append(cur_node.unique_refinement)

        exp.elapsed_time = timeit.default_timer() - start_experiment

    datafile.close()

def main():
    parser = argparse.ArgumentParser(description="Run interpolation_repair.py on .spectra file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=float, default=10, help="Timeout in minutes (default: 10)")
    parser.add_argument("-allgars", action="store_true", help="Use all guarantees")
    parser.add_argument("-min", action="store_true", help="Minimize specification")
    parser.add_argument("-inf", action="store_true", help="Use influential output variables")

    args = parser.parse_args()
    exp.configure(args.input, args.timeout*60, args.output, args.allgars, args.min, args.inf, debug=False)
    FifoDuplicateCheckRefinement()

if __name__=="__main__":
    main()
