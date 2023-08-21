import os
import timeit
import argparse
from collections import deque
import experiment_properties as exp
from refinement import RefinementNode
import concurrent.futures

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
    datafields = [
        "Id",
        "UniqueRefinement",
        "NumVariables",
        "Timestamp",
        "Length",
        "Parent",
        "NumChildren",
        "IsRealizable",
        "IsSatisfiable",
        "IsSolution",
        "TimeRealizabilityCheck",
        "TimeSatisfiabilityCheck",
        "TimeCounterstrategy",
        "CounterstrategyNumStates",
        "TimeRefine",
        "TimeGenerationMethod"
    ]
    
    datafile.write(";".join(datafields) + "\n")

    initial_spec_node = RefinementNode()

    # Root of the refinement tree: it contains the initial spec
    refinement_queue = deque([initial_spec_node])

    nodes = 0
    elapsed_time = 0
    while refinement_queue and nodes < MAX_NODES and elapsed_time < exp.timeout:
        cur_node = refinement_queue.pop()
        nodes += 1

        if cur_node.unique_refinement not in explored_refs:
            print("++++ ELAPSED TIME:", elapsed_time)
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
                        remaining_timeout = exp.timeout - elapsed_time
                        candidate_ref_nodes = refine_future.result(timeout=remaining_timeout)
                        refinement_queue.extendleft(candidate_ref_nodes)
                elif cur_node.isSatisfiable():
                    print("++ REALIZABLE REFINEMENT: SAT CHECK")
                    solutions.append(cur_node.gr1_units)
                else:
                    print("++ VACUOUS SOLUTION")
            except concurrent.futures.TimeoutError:
                print("++ Refine operation exceeded remaining timeout")
            except Exception as e:
                # cur_node.writeNotes(str(e))
                print(e)

            cur_node.saveRefinementData(datafile, datafields)
            explored_refs.append(cur_node.unique_refinement)
        else:
            print("++ DUPLICATE NODE")
            duplicate_refs.append(cur_node.unique_refinement)

        elapsed_time = timeit.default_timer() - start_experiment

    # start_time_nonexpanded_nodes = timeit.default_timer()
    # print("++++ SAVING NON EXPANDED NODES DATA: "+str(len(partial_refinements_queue))+" nodes")
    # for i, nonexpanded_node in enumerate(partial_refinements_queue):
    #     try:
    #         print("++ Node "+str(i+1)+"/"+str(len(partial_refinements_queue)))
    #         with open(nonexpanded_node.getNotesFileId(), "w") as notesfile:
    #             notesfile.write("node not expanded")
    #         if not (nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement) in explored_refs:
    #             if timeit.default_timer() - start_time_nonexpanded_nodes < 1800: # Check realz. of nonexplored nodes only for extra 30 mins
    #                 nonexpanded_node.isRealizable()
    #                 if nonexpanded_node.isRealizable():
    #                     nonexpanded_node.isSatisfiable()
    #             nonexpanded_node.saveRefinementData(datafile, datafields)
    #             explored_refs.append((nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement))
    #         else:
    #             print("++ DUPLICATE NODE")
    #             duplicate_refs.append((nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement))
    #     except Exception as e:
    #         print(str(e))

    # print("++++ SAVING SEARCH SUMMARY DATA")
    # experimentstatsfile = open(exp.experimentstatsfile, "w")
    # print("Nodes explored;" + str(nodes) + "\n"\
    #                         + "Total time;" + str(elapsed_time) + "\n"\
    #                         + "Duplicate nodes;" + str(len(duplicate_refs)) + "\n"\
    #                         + "\n".join([str(x) for x in duplicate_refs]))
    # experimentstatsfile.write("Nodes explored;" + str(nodes) + "\n"
    #                         + "Total time;" + str(elapsed_time) + "\n"
    #                         + "Duplicate nodes;" + str(len(duplicate_refs)) + "\n"
    #                           + "\n".join([str(x) for x in duplicate_refs]))
    # experimentstatsfile.close()

    datafile.close()

def main():
    parser = argparse.ArgumentParser(description="Run interpolation_repair.py on .spectra file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout in minutes (default: 10)")

    args = parser.parse_args()

    exp.configure(args.input, args.timeout * 60, args.output)

    FifoDuplicateCheckRefinement()

if __name__=="__main__":
    main()
