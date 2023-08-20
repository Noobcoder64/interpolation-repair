import io_utils as io
import timeit
import random
import os
import specification as sp
import re

# Set random seed for repeatability
# random.seed(1000)

case_study_name = ""
generation_method = "interpolation"
n_multivarbias = 5
goodness_measure = ""
goodness_update_required = False
search_method = "bfs"
refinement_method = generation_method + ("-" + search_method if search_method != "" else "") + ("-" + goodness_measure if goodness_measure != "" else "")
exp_number = "tacas20_duplicatecheck"
limit_fairness = -1 # Max fairness conditions allowed in the experiment. -1 if unlimited
# include_parent_unreal_core_check = True
include_parent_unreal_core_check = False

# Decide whether the search should return initial conditions, invariants, and/or fairness conditions
# By default, they are all True
search_initials = True
search_invariants = True
search_fairness = True

# This is a reference to the original specification file
specfile = "Examples/"+case_study_name+".spectra"
datafile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+".csv"
checkpointfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_checkpoint.csv"
satfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_sat.csv"
weaknessfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_weakness.csv"
wellsepfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_wellsep.csv"
statsfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_stats.csv"
equivclassesfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_equivclasses.csv"
distancesfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_distances.csv"
cstimesfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_cstimes.csv"
uniquesolsfile = "outputs/" + case_study_name + "_"+refinement_method+"_exp"+str(exp_number)+"_uniquesols.csv"

experimentstatsfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_expstats.csv"

if case_study_name != "":
    spec = sp.read_file(specfile)
    spec = sp.interpolation_spec(spec)

    inputVarsList = io.extractInputVariablesFromFile(spec)
    outputVarsList = io.extractOutputVariablesFromFile(spec)
    varsList = inputVarsList + outputVarsList
    initialGR1Units = io.extractAssumptionList(spec)
    guaranteesList = io.extractGuaranteesList(spec)

counterstrategies = [] # This list contains all observed counterstrategy bdds for use in the experiment
                       # Each element is a triple (marduk_instance, bdd_initial_states, bdd_transition)

start_experiment = timeit.default_timer()

def changeCaseStudy(specification):
    global specfile
    global datafile
    global checkpointfile
    global satfile
    global weaknessfile
    global wellsepfile
    global statsfile
    global equivclassesfile
    global distancesfile
    global cstimesfile

    global experimentstatsfile

    global inputVarsList
    global outputVarsList
    global varsList
    global initialGR1Units
    global guaranteesList

    global start_experiment
    case_study_name = os.path.splitext(os.path.basename(specification))[0]
    specfile = specification
    datafile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + ".csv"
    checkpointfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_checkpoint.csv"
    satfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_sat.csv"
    weaknessfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_weakness.csv"
    wellsepfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_wellsep.csv"
    statsfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_stats.csv"
    equivclassesfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(
        exp_number) + "_equivclasses.csv"
    distancesfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(
        exp_number) + "_distances.csv"
    cstimesfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_cstimes.csv"
    uniquesolsfile = "outputs/" + case_study_name + "_"+refinement_method+"_exp"+str(exp_number)+"_uniquesols.csv"

    experimentstatsfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_expstats.csv"

    spec = sp.read_file(specfile)
    spec = sp.interpolation_spec(spec)

    inputVarsList = io.extractInputVariablesFromFile(spec)
    print("=== INPUT VARS ===")
    for var in inputVarsList:
        print(var)
    outputVarsList = io.extractOutputVariablesFromFile(spec)
    print("=== OUTPUT VARS ===")
    for var in outputVarsList:
        print(var)
    varsList = inputVarsList + outputVarsList
    initialGR1Units = io.extractAssumptionList(spec)
    print("=== ASSUMPTIONS ===")
    for asm in initialGR1Units:
        print(asm)
    guaranteesList = io.extractGuaranteesList(spec)
    print("=== GUARANTEES ===")
    for gar in guaranteesList:
        print(gar)

    start_experiment = timeit.default_timer()

def changeGenerationMethod(generation_method):
    global specfile
    global datafile
    global checkpointfile
    global satfile
    global weaknessfile
    global wellsepfile
    global statsfile
    global equivclassesfile
    global distancesfile
    global cstimesfile

    global experimentstatsfile

    global inputVarsList
    global outputVarsList
    global varsList
    global initialGR1Units
    global guaranteesList

    global start_experiment

    refinement_method = generation_method + ("-" + search_method if search_method != "" else "") + (
    "-" + goodness_measure if goodness_measure != "" else "")

    specfile = "Examples/" + case_study_name + ".rat"
    datafile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + ".csv"
    checkpointfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_checkpoint.csv"
    satfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_sat.csv"
    weaknessfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_weakness.csv"
    wellsepfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_wellsep.csv"
    statsfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_stats.csv"
    equivclassesfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(
        exp_number) + "_equivclasses.csv"
    distancesfile = "outputs/" + case_study_name + "_" + refinement_method + "_exp" + str(
        exp_number) + "_distances.csv"
    cstimesfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_cstimes.csv"
    uniquesolsfile = "outputs/" + case_study_name + "_"+refinement_method+"_exp"+str(exp_number)+"_uniquesols.csv"

    experimentstatsfile = "outputs/"+case_study_name+"_"+refinement_method+"_exp"+str(exp_number)+"_expstats.csv"

    spec = sp.read_file(specfile)
    spec = [re.sub(r"GF\s*\(([^\)]*)\)", r"G(F(\1))", line) for line in spec]
    spec = [re.sub(";", "", line) for line in spec]

    inputVarsList = io.extractInputVariablesFromFile(spec)
    outputVarsList = io.extractOutputVariablesFromFile(spec)
    varsList = inputVarsList + outputVarsList
    initialGR1Units = io.extractAssumptionList(spec)
    guaranteesList = io.extractGuaranteesList(spec)

    start_experiment = timeit.default_timer()
