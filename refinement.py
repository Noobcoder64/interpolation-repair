import experiment_properties as exp
import interpolation
# import alur, varbias
import timeit
import uuid, re, os, ast
from counterstrategy import Counterstrategy
# import ref_utils.ratsy_utils as r
import io_utils as io
# import model_checking as mc
import itertools
from collections import deque
# from Weakness.src.weakness import computeD1_probe, computeD2_probe, Weakness
import numpy as np
import spectra_utils as spectra
import specification as sp

class Refinement:

    def __init__(self, gr1_units=[], counterstrategy_bdds=[], counterstrategy_degrees=dict(), parent_id=None, parent_unreal_core_names=None):
        self.id = uuid.uuid4()

        self.parent_id = parent_id
        self.parent_unreal_core_names = parent_unreal_core_names
        self.num_descendant_refinements = 0
        self.unrealizable_core_names = None
        # Data fields (can be read from/written to a file)
        self.gr1_units = gr1_units # List of all units/conjuncts in this refinement
        self.ancestor_counterstrategy_bdds = counterstrategy_bdds # The i-th element of this list is itself a list of all CSes removed by gr1_units[i]
                                                                  # Each CS is a tuple containing a marduk instance and two BDDs (marduk_instance, counterstrategy_init_state, counterstrategy_transition)
        self.counterstrategy_degrees = counterstrategy_degrees  # Dictionary: key: counterstrategy BDD tuple, value: degree of counterstrategy in bipartite graph


        self.weakness = None
        self.weakness_num_automata = None
        self.weakness_numstates_automata = None
        self.weakness_times_automata = None
        self.weakness_is_automaton_strongly_connected = None

        self.is_realizable = None
        self.is_satisfiable = None
        self.length = len(gr1_units)
        self.ancestor_counterstrategies_eliminated = [len(x) for x in self.ancestor_counterstrategy_bdds] # Number of counterstrategies eliminated by this refinement per gr1_unit
        self.ancestor_counterstrategies_eliminated_total = 0 # Number of distinct counterstrategies eliminated by the refinement
                                                    # Should coincide with the number of distinct counterstrategies in
                                                    # self.ancestor_counterstrategies_eliminated
        self.observed_counterstrategies_eliminated = None # Number of overall observed counterstrategies eliminated
                                                          # by this refinement
        self.total_observed_counterstrategies = None # Number of observed counterstrategies at the time of computing
                                                     # self.observed_counterstrategies_eliminated
        self.goodness = None # This field contains the goodness measure to use in a heuristic-based search.
                             # The higher the better

        self.is_parent_unrealcore_realizable = None

        # Stats fields (can be read from/written to a file)
        self.timestamp = timeit.default_timer() - exp.start_experiment
        self.timestamp_realizability_check = None
        self.time_counterstrategy = None
        self.counterstrategy_num_states = None
        self.time_realizability_check = None
        self.time_satisfiability_check = None
        # Total time to model check all children of this node.
        self.time_refine = None
        self.time_weakness = None
        self.time_goodness = None
        # Time for generation method (interpolation or multivarbias or other)
        self.time_generation_method = None
        self.redundant_assumptions_eliminated = None
        # Time for computing number of observed counterstrategies eliminated
        self.time_observed_counterstrategies_eliminated = None

        # Internal fields
        # Reference to the marduk instance that computed the counterstrategy
        self.marduk = None
        # Reference to the SpecDebugUtils object that computed the counterstrategy
        self.spec_debug_utils = None
        self.counterstrategy = None
        # BDD of counterstrategy (initial states, transition), type tuple (BDD, BDD)
        self.counterstrategy_bdd = None
        ## Explicit-state counterstrategy, type Counterstrategy
        # self.counterstrategy = None
        self.unreal_core = None
        # Used to check whether two nodes contain the same refinement
        self.unique_refinement = sorted(self.gr1_units)

        self.num_fairness = sum(x.startswith("G(F(") for x in self.gr1_units)

    # Methods to load node data from experiment file
    __re_first_cap = re.compile('(.)([A-Z][a-z]+)')
    __re_all_cap = re.compile('([a-z0-9])([A-Z])')

    def __convertCamelToSnakeCase(self, name):
        """Converts names like FieldName to field_name"""
        s1 = self.__re_first_cap.sub(r'\1_\2', name)
        return self.__re_all_cap.sub(r'\1_\2', s1).lower()

    def __convertSnakeToCamelCase(self, name):
        """Converts names like field_name to FieldName"""
        components = name.split('_')
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return ''.join(x.title() for x in components)

    def loadDataFieldsFromList(self, fieldnames, fieldvalues):
        """Loads data fields from a list
        fieldnames: a list of field names, as strings
        fieldvalues: a list of field values, as strings
        """
        fieldnames = [self.__convertCamelToSnakeCase(x) for x in fieldnames]
        for i,field in enumerate(fieldnames):
            if fieldvalues[i] == "N/A":
                setattr(self, field, None)
            elif field == "goodness" and exp.goodness_measure == "weakness":
                inf = np.inf
                eval_field = eval(fieldvalues[i])
                self.goodness = Weakness(eval_field[0], eval_field[1], eval_field[2], eval_field[3])
                self.weakness = self.goodness
            elif field == "refinement":
                self.gr1_units = eval(fieldvalues[i])
            else:
                try:
                    # literal_eval identifies Boolean and numeric types
                    setattr(self,field,ast.literal_eval(fieldvalues[i]))
                except Exception:
                    setattr(self, field, fieldvalues[i])

    def __readNotes(self):
        """Checks if there is a notefile regarding the current node. If so, returns its content"""
        if os.path.isfile(self.getNotesFileId()):
            with open(self.getNotesFileId()) as notefile:
                return " ".join(notefile.readlines())
        else:
            return ""

    def writeNotes(self, string):
        with open(self.getNotesFileId(), "a") as notesfile:
            notesfile.write(string + ";")


    def saveRefinementData(self, datafile, fields):
        """Saves the data contents of the 'fields' fields into datafile as a semicolon-separated string"""
        field_values = []
        fields = [self.__convertCamelToSnakeCase(x) for x in fields]
        for field in fields:
            if field == "refinement":
                field_value = self.gr1_units
            elif field == "parent":
                field_value = self.parent_id
            elif field == "num_children":
                field_value = self.num_descendant_refinements
            elif field == "is_solution":
                if self.is_realizable == True and self.is_satisfiable == True:
                    field_value = True
                elif self.is_realizable == False or self.is_satisfiable == False:
                    field_value = False
                else:
                    field_value = "N/A"
            else:
                field_value = getattr(self, field)
            if field_value is not None:
                field_values.append(str(field_value))
            else:
                field_values.append("N/A")
        datafile.write(";".join(field_values) + ";" + self.__readNotes() + "\n")

    #==========================================================================
    # Methods to deal with .rat and .dot files
    def __getTempSpecFileName(self):
        return "temp/" + str(self.id) + ".spectra"

    def __getCounterstrategyFileId(self):
        return "temp/" + str(self.id)

    def __getCounterstrategyFileName(self):
        return "temp/"+str(self.id)+"_with_signals.dot"

    def __generateSpecFile(self):
        """Create a specification XML Tree from the original specification and add the current refinement to it"""

        if not os.path.isfile(self.__getTempSpecFileName()):
            
            # specificationTree = r.readRATFile(exp.specfile)
            specification = sp.read_file(exp.specfile)
            specification = sp.unformat_spec(specification)
            assumptions = sp.unformat_spec(self.gr1_units)
            for asm in assumptions:
                specification.append("assumption\n")
                specification.append("\t" + asm + ";\n")
            # for unit_refinement in enumerate(self.gr1_units):
                # r.addRequirement(specificationTree, str(self.id)+"_"+str(unit_refinement[0]), unit_refinement[1], "A", "1")
                # spectra.addAssumption(specification, unit_refinement[1])

            # r.writeRATFile(self.__getTempSpecFileName(), specificationTree)
            sp.write_file(specification, self.__getTempSpecFileName())

    def getNotesFileId(self):
        return "temp/" + str(self.id) + "_notes.txt"

    #================================================================================================
    # Methods to return the refinement in various formats
    def getInitialAssumptionsAndRefinement(self):
        return " & ".join(exp.initialGR1Units) + ((" & " + " & ".join(self.gr1_units)) if not not self.gr1_units else "")

    def getRefinementAsFormula(self):
        return " & ".join(self.gr1_units)

    def getInitialAssumptionsNoFairness(self):
        return " & ".join([x for x in exp.initialGR1Units if not x.startswith("G(F(")])
    
    def checkRealizability(self, filename):
        return spectra.check_realizibility(filename)

    #===============================================================================================
    # Methods related to assumptions refinement
    def isRealizable(self):
        if self.is_realizable is not None:
            return self.is_realizable
        self.__generateSpecFile()
        realizability_check_start = timeit.default_timer()
        if self.checkRealizability(self.__getTempSpecFileName()):
        # if self.checkRealizability(exp.specfile):
            self.is_realizable = True
        else:
            self.is_realizable = False
        self.time_realizability_check = timeit.default_timer() - realizability_check_start

        self.timestamp_realizability_check = timeit.default_timer() - exp.start_experiment
        return self.is_realizable

    def isSatisfiable(self):
        if self.is_satisfiable is not None:
            return self.is_satisfiable
        time_satisfiability_check_start = timeit.default_timer()
        ret = spectra.check_satisfiability(self.__getTempSpecFileName())
        # a = self.getNondeterministicAutomatonWithInitials()
        # ret = not a.checkEmptiness()
        self.time_satisfiability_check = timeit.default_timer() - time_satisfiability_check_start
        self.is_satisfiable = ret
        return ret

    def getCounterstrategy(self):
        """Returns a counterstrategy object"""
        if not self.isRealizable():
            if not os.path.isfile(self.__getCounterstrategyFileName()):
                # if self.marduk is None:
                #     self.marduk = r.initMarduk(self.__getTempSpecFileName())
                counterstrategy_start = timeit.default_timer()
                # counterstrategy_created, bdd_cs_trans, bdd_cs_init_state = r.computeCounterstrategy(self.__getTempSpecFileName(), self.__getCounterstrategyFileId(), self.marduk)
                self.counterstrategy = Counterstrategy(self.__getTempSpecFileName()) # self.__getCounterstrategyFileName() , self.counterstrategy_bdd)
                self.time_counterstrategy = timeit.default_timer() - counterstrategy_start
                # self.counterstrategy_bdd = (self.marduk, bdd_cs_init_state, bdd_cs_trans)
                # self.counterstrategy_num_states = len(self.counterstrategy.states)
                # exp.counterstrategies.append(self.counterstrategy_bdd)
            return self.counterstrategy
        else:
            return None

    def getUnrealizableCore(self):
        """Gets an unrealizable core for the current node"""
        if not os.path.isfile(self.__getTempSpecFileName()):
            self.__generateSpecFile()
        if self.unreal_core is None:
            # self.unreal_core = [io.normalizeFormulaSyntax(x) for x in
            #                     r.getUnrealizableCore(self.__getTempSpecFileName())]
            self.unreal_core = spectra.extract_unrealizable_cores(self.__getTempSpecFileName())
        return self.unreal_core

    def getUnrealizableCoreNames(self):
        """Gets an unrealizable core in the form of a list of guarantee names"""
        if self.unrealizable_core_names is None:
            if not os.path.isfile(self.__getTempSpecFileName()):
                self.__generateSpecFile()
            self.unrealizable_core_names = r.getUnrealizableCoreNames(self.__getTempSpecFileName())
        return self.unrealizable_core_names

    def getCounterstrategyBdd(self):
        """Returns the counterstrategy's BDD"""
        if self.counterstrategy_bdd is not None:
            return self.counterstrategy_bdd
        else:
            self.getCounterstrategy()
            return self.counterstrategy_bdd

    def refine(self):
        """Produces a list of Refinement objects based on the selected refinement method"""

        refinements = []

        if exp.search_method == "minimal":
            # This method generates new refinements by removing all ancestor assumptions whose associated counterstrategies
            # are already removed by more recent assumptions
            self.getCounterstrategy()
            candidate_refs = self.generateAlternativeRefinements()
            time_refine_start = timeit.default_timer()
            for candidate_ref in candidate_refs:
                minimal_ref = self.__minimalRefinement(candidate_ref)
                # By construction a refinement generated from self eliminates in total one more counterstrategy than self
                minimal_ref.ancestor_counterstrategies_eliminated_total = self.ancestor_counterstrategies_eliminated_total + 1
                refinements.append(minimal_ref)
            self.time_refine = timeit.default_timer() - time_refine_start
        elif exp.search_method == "minimal-bfs":
            self.getCounterstrategy()
            candidate_refs = self.generateAlternativeRefinements()
            time_refine_start = timeit.default_timer()
            for candidate_ref in candidate_refs:
                minimal_ref = self.__minimalRefinement(candidate_ref)
                # By construction a refinement generated from self eliminates in total one more counterstrategy than self
                minimal_ref.ancestor_counterstrategies_eliminated_total = self.ancestor_counterstrategies_eliminated_total + 1
                refinements.append(minimal_ref)
                # Append also the refinement generated by just concatenating the new assumption
                refinements.append(self.__concatenateAssumption(candidate_ref))
            self.time_refine = timeit.default_timer() - time_refine_start
        elif exp.search_method == "bfs":
            self.getCounterstrategy()
            candidate_refs = self.generateAlternativeRefinements()
            time_refine_start = timeit.default_timer()
            for candidate_ref in candidate_refs:
                # Append the refinement generated by just concatenating the new assumption
                refinements.append(self.__concatenateAssumption(candidate_ref))
            self.time_refine = timeit.default_timer() - time_refine_start
        self.num_descendant_refinements = len(refinements)
        return refinements

    def __minimalRefinement(self, candidate_ref):
        """Returns a Refinement object with a minimal refinement after concatenating candidate_ref to self"""

        # To save computation time, reuse previous degrees and update them with the new results from model checking
        counterstrategy_degrees = self.counterstrategy_degrees.copy()

        # Counterstrategies removed by candidate_ref
        candidate_ref_counterstrategies = [self.counterstrategy_bdd]

        # Check all counterstrategies against new assumption
        for cs in counterstrategy_degrees:
            if not mc.gr1_model_check(cs[0],cs[2],cs[1],candidate_ref):
                candidate_ref_counterstrategies.append(cs)
                counterstrategy_degrees[cs] += 1

        # The new counterstrategy has degree 1 by construction
        counterstrategy_degrees[self.counterstrategy_bdd] = 1

        non_redundant_indices = []
        # Identify non-redundant assumptions
        for i in range(self.length):
            non_redundant = False
            for cs in self.ancestor_counterstrategy_bdds[i]:
                # If there is a counterstrategy with degree 1, this assumption is non-redundant
                if counterstrategy_degrees[cs] < 2:
                    non_redundant = True
                    break
            if non_redundant:
                non_redundant_indices.append(i)
            else:
                # If the assumption is redundant, it needs to be removed. Update the counterstrategy degrees accordingly
                for cs in self.ancestor_counterstrategy_bdds[i]:
                    counterstrategy_degrees[cs] -= 1

        # Construct a Refinement object with the nonredundant assumptions only
        non_redundant_assumptions = [self.gr1_units[i] for i in non_redundant_indices] + [candidate_ref]
        non_redundant_cs_bdds = [self.ancestor_counterstrategy_bdds[i] for i in non_redundant_indices] + [candidate_ref_counterstrategies]
        minimal_ref = Refinement(non_redundant_assumptions, non_redundant_cs_bdds, counterstrategy_degrees, self.id)
        # Record how many assumptions were redundant when generating this refinement
        minimal_ref.redundant_assumptions_eliminated = len(self.gr1_units) + 1 - len(non_redundant_assumptions)

        return minimal_ref

    def __concatenateAssumption(self, candidate_ref):
        """Generate a new refinement by just concatenating candidate_ref to self. Keep the bipartite graph consistent"""

        # To save computation time, reuse previous degrees and update them with the new results from model checking
        # counterstrategy_degrees = self.counterstrategy_degrees.copy()

        # Counterstrategies removed by candidate_ref
        # candidate_ref_counterstrategies = [self.counterstrategy_bdd]

        # Check all counterstrategies against new assumption
        # for cs in counterstrategy_degrees:
        #     if not mc.gr1_model_check(cs[0],cs[2],cs[1],candidate_ref):
        #         candidate_ref_counterstrategies.append(cs)
        #         counterstrategy_degrees[cs] += 1

        # The new counterstrategy has degree 1 by construction
        # counterstrategy_degrees[self.counterstrategy_bdd] = 1

        assumptions = self.gr1_units + [candidate_ref]
        # cs_bdds = self.ancestor_counterstrategy_bdds + [candidate_ref_counterstrategies]

        cs_bdds = []
        counterstrategy_degrees = dict()
        if exp.include_parent_unreal_core_check:
            ref = Refinement(assumptions, cs_bdds, counterstrategy_degrees, self.id, self.getUnrealizableCoreNames())
        else:
            ref = Refinement(assumptions, cs_bdds, counterstrategy_degrees, self.id)

        return ref

    def generateAlternativeRefinements(self):
        time_generation_method_start = timeit.default_timer()
        refinements = []
        if exp.generation_method == "interpolation":
            refinements = interpolation.GenerateAlternativeRefinements(self.counterstrategy, exp.initialGR1Units + self.gr1_units, self.getUnrealizableCore(), exp.inputVarsList, exp.outputVarsList)
        elif exp.generation_method == "multivarbias":
            biases = [varbias.VarBias() for x in range(exp.n_multivarbias)]
            for b in biases:
                print("Bias: " + str(b))
                refinements.extend(alur.GenerateAlternativeRefinements(self.counterstrategy, b.inv_vars, b.invx_cur_vars, b.invx_next_vars, b.fair_vars))
        elif exp.generation_method == "alur_all_vars":
            refinements.extend(alur.GenerateAlternativeRefinements(self.counterstrategy, exp.inputVarsList, exp.varsList, exp.inputVarsList, exp.inputVarsList))
        elif exp.generation_method == "interpolation-multivarbias" or exp.generation_method == "multivarbias-interpolation":
            refinements = interpolation.GenerateAlternativeRefinements(self.counterstrategy, exp.initialGR1Units + self.gr1_units, self.getUnrealizableCore(), exp.inputVarsList, exp.outputVarsList)
            biases = [varbias.VarBias() for x in range(exp.n_multivarbias)]
            for b in biases:
                print("Bias: " + str(b))
                refinements.extend(alur.GenerateAlternativeRefinements(self.counterstrategy, b.inv_vars, b.invx_cur_vars, b.invx_next_vars, b.fair_vars))

        self.time_generation_method = timeit.default_timer() - time_generation_method_start
        return refinements

    #================================================================================================
    # Methods for automaton computation
    def getNondeterministicAutomatonWithInitials(self):
        return nondet.NondeterministcTGBA("ltl",ltlFormula=self.getInitialAssumptionsAndRefinement(),var_set=exp.varsList)

    #================================================================================================
    # Methods for computing quantitative heuristics

    def isParentUnrealCoreRealizable(self):
        """Checks whether the current node's assumptions make the parent's unrealizable core realizable"""
        if self.parent_id is not None:
            if self.is_parent_unrealcore_realizable is None:
                parent_unreal_core = self.parent_unreal_core_names
                tree = r.readRATFile(self.__getTempSpecFileName())
                tree = r.toggleUnrealizableCore(tree,parent_unreal_core)
                r.writeRATFile(self.__getTempSpecFileName()+"_parentunrealcore",tree)
                self.is_parent_unrealcore_realizable = r.checkRealizability(self.__getTempSpecFileName()+"_parentunrealcore")
            return self.is_parent_unrealcore_realizable
        else:
            return True

    def computeObservedCounterstrategiesEliminated(self):
        if self.observed_counterstrategies_eliminated is None:
            self.total_observed_counterstrategies = len(exp.counterstrategies)
            self.observed_counterstrategies_eliminated = 0
            start_time_observed_counterstrategies_eliminated = timeit.default_timer()
            for cs in exp.counterstrategies:
                if not mc.gr1_model_check(cs[0], cs[2], cs[1], self.getRefinementAsFormula()):
                    self.observed_counterstrategies_eliminated += 1
            self.time_observed_counterstrategies_eliminated = timeit.default_timer() - start_time_observed_counterstrategies_eliminated
            return self.observed_counterstrategies_eliminated
        else:
            return self.observed_counterstrategies_eliminated

    # The metric of observed counterstrategies eliminated may need to be updated as new counterstrategies are computed
    def __updateObservedCounterstrategiesEliminated(self):
        if len(exp.counterstrategies) != self.total_observed_counterstrategies:
            # Additional time needed for computing this heuristic
            start_add_time_observed_counterstrategies_eliminated = timeit.default_timer()
            for cs in exp.counterstrategies[self.total_observed_counterstrategies:]:
                if not mc.gr1_model_check(cs[0], cs[2], cs[1], self.getRefinementAsFormula()):
                    self.observed_counterstrategies_eliminated += 1
            self.total_observed_counterstrategies = len(exp.counterstrategies)
            self.time_observed_counterstrategies_eliminated += timeit.default_timer() - start_add_time_observed_counterstrategies_eliminated

    def computeWeakness(self):
        start_time_weakness = timeit.default_timer()
        if self.weakness is None:
            self.weakness, self.weakness_num_automata, self.weakness_numstates_automata, self.weakness_times_automata, self.weakness_is_automaton_strongly_connected = computeWeakness_probe(self.getRefinementAsFormula(),exp.varsList)
        self.time_weakness = timeit.default_timer() - start_time_weakness
        return self.weakness

    def computeGoodness(self):
        start_time_goodness = timeit.default_timer()
        if exp.goodness_measure == "observed_counterstrategies_eliminated":
            self.goodness = self.computeObservedCounterstrategiesEliminated()
        elif exp.goodness_measure == "weakness":
            self.goodness = self.computeWeakness()
        self.time_goodness = timeit.default_timer() - start_time_goodness

    def updateGoodness(self):
        if exp.goodness_measure == "observed_counterstrategies_eliminated":
            self.__updateObservedCounterstrategiesEliminated()
            self.goodness = self.observed_counterstrategies_eliminated

    # The higher goodness the better the refinement.
    # In min-heap implementations of priority queues, the lower-ranked nodes are the first to be popped.
    # So the higher the goodness the lower the rank of a refinement
    def __le__(self, other):
        if self.goodness is not None and other.goodness is not None:
            return (self.goodness >= other.goodness)
        else:
            raise Exception("Refinements compared despite goodness not computed")

    def __lt__(self, other):
        if self.goodness is not None and other.goodness is not None:
            return (self.goodness > other.goodness)
        else:
            raise Exception("Refinements compared despite goodness not computed")

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other

    def __eq__(self, other):
        if self.goodness is not None and other.goodness is not None:
            return (self.goodness == other.goodness)
        else:
            raise Exception("Refinements compared despite goodness not computed")
