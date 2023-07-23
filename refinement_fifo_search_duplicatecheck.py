import experiment_properties as exp
import interpolation
from refinement import Refinement
from collections import deque # For efficient FIFO queuing
import timeit, gc, os
import sys

if len(sys.argv) > 1:
    exp.changeCaseStudy(sys.argv[1])
    print("+++++++++++ " + sys.argv[1])

max_nodes = 3000 # Max nodes to expand in the experiment
timeout = 1800 # Seconds before timeout (30 min)

print("Resetting temp...")
folder = 'temp'
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)
print("Reset complete!")

def FifoDuplicateCheckRefinement():
    """This implements the refinement strategy that uses model checking against ancestors
    to generate nodes"""
    start_experiment = exp.start_experiment

    solutions = []
    explored_refs = [] # Each element is a tuple (total_cs_eliminated, unique_refinement)
    duplicate_refs = []

    datafile = open(exp.datafile, "w")
#    Use this if the experiment uses minimal, since you want to record ancestorcounterstrategieseliminated
    # datafields = [ "Id", "Refinement", "UniqueRefinement", "Timestamp", "TimestampRealizabilityCheck", "Length", "Parent", "NumChildren", "AncestorCounterstrategiesEliminated", "TotalObservedCounterstrategies", "RedundantAssumptionsEliminated", "IsRealizable", "IsSatisfiable", "IsSolution", "TimeRealizabilityCheck", "TimeSatisfiabilityCheck", "TimeCounterstrategy", "CounterstrategyNumStates", "TimeRefine", "TimeGenerationMethod"]
    # Use this if the exploration strategy is just BFS
    datafields = [ "Id", "Refinement", "UniqueRefinement", "Timestamp", "Length", "Parent", "NumChildren", "IsRealizable", "IsSatisfiable", "IsSolution", "TimeRealizabilityCheck", "TimeSatisfiabilityCheck", "TimeCounterstrategy", "CounterstrategyNumStates", "TimeRefine", "TimeGenerationMethod"]
    datafile.write(";".join(datafields) + "\n")

    initial_spec_node = Refinement()

    # Root of the refinement tree: it contains the initial spec
    partial_refinements_queue = deque([initial_spec_node])

    nodes = 0
    elapsed_time = 0
    while not not partial_refinements_queue and nodes < max_nodes and elapsed_time < timeout:
        cur_node = partial_refinements_queue.pop()
        nodes += 1

        if not (cur_node.ancestor_counterstrategies_eliminated_total, cur_node.unique_refinement) in explored_refs:
            print("++++ ELAPSED TIME " + str(elapsed_time))
            print("++++ QUEUE LENGTH " + str(len(partial_refinements_queue)))
            print("++++ Solutions " + str(len(solutions)))
            print("++++ Duplicates " + str(len(duplicate_refs)))
            print("++++ Node number " + str(nodes))
            print("++++ Refinement " + str(cur_node.gr1_units))
            print("++++ Length " + str(cur_node.length))

            # try:
            print("++ REALIZABILITY CHECK")
            if not cur_node.isRealizable():
                print("++ COUNTERSTRATEGY COMPUTATION - REFINEMENT GENERATION")
                candidate_ref_nodes = cur_node.refine()
                partial_refinements_queue.extendleft(candidate_ref_nodes)
            elif cur_node.isSatisfiable():
                print("++ REALIZABLE REFINEMENT: SAT CHECK")
                solutions.append(cur_node.gr1_units)
            else:
                print("++ VACUOUS SOLUTION")
            # except Exception as e:
            #     cur_node.writeNotes(str(e))

            cur_node.saveRefinementData(datafile, datafields)
            explored_refs.append((cur_node.ancestor_counterstrategies_eliminated_total, cur_node.unique_refinement))
        else:
            print("++ DUPLICATE NODE")
            duplicate_refs.append((cur_node.ancestor_counterstrategies_eliminated_total, cur_node.unique_refinement))

        elapsed_time = timeit.default_timer() - start_experiment

    start_time_nonexpanded_nodes = timeit.default_timer()
    print("++++ SAVING NON EXPANDED NODES DATA: "+str(len(partial_refinements_queue))+" nodes")
    for i, nonexpanded_node in enumerate(partial_refinements_queue):
        try:
            print("++ Node "+str(i+1)+"/"+str(len(partial_refinements_queue)))
            with open(nonexpanded_node.getNotesFileId(), "w") as notesfile:
                notesfile.write("node not expanded")
            if not (nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement) in explored_refs:
                if timeit.default_timer() - start_time_nonexpanded_nodes < 1800: # Check realz. of nonexplored nodes only for extra 30 mins
                    nonexpanded_node.isRealizable()
                    if nonexpanded_node.isRealizable():
                        nonexpanded_node.isSatisfiable()
                nonexpanded_node.saveRefinementData(datafile, datafields)
                explored_refs.append((nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement))
            else:
                print("++ DUPLICATE NODE")
                duplicate_refs.append((nonexpanded_node.ancestor_counterstrategies_eliminated_total, nonexpanded_node.unique_refinement))
        except Exception as e:
            print(str(e))

    print("++++ SAVING SEARCH SUMMARY DATA")
    experimentstatsfile = open(exp.experimentstatsfile, "w")
    print("Nodes explored;" + str(nodes) + "\n"\
                            + "Total time;" + str(elapsed_time) + "\n"\
                            + "Duplicate nodes;" + str(len(duplicate_refs)) + "\n"\
                            + "\n".join([str(x) for x in duplicate_refs]))
    experimentstatsfile.write("Nodes explored;" + str(nodes) + "\n"
                            + "Total time;" + str(elapsed_time) + "\n"
                            + "Duplicate nodes;" + str(len(duplicate_refs)) + "\n"
                              + "\n".join([str(x) for x in duplicate_refs]))
    experimentstatsfile.close()


    datafile.close()

def main():
    FifoDuplicateCheckRefinement()

if __name__=="__main__":
    main()
