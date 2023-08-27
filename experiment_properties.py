import io_utils as io
import timeit
import random
import os
import specification as sp
import re

# Set random seed for repeatability
# random.seed(1000)

output_folder = "outputs/"
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

timeout = 600 # 10 minutes

# This is a reference to the original specification file
specfile = ""
datafile = os.path.join(output_folder, case_study_name + "_INTERPOLATION" + ".csv")
checkpointfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_checkpoint.csv")
satfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_sat.csv")
weaknessfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_weakness.csv")
wellsepfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_wellsep.csv")
statsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_stats.csv")
equivclassesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_equivclasses.csv")
distancesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_distances.csv")
cstimesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_cstimes.csv")
uniquesolsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_uniquesols.csv")

experimentstatsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_expstats.csv")

if case_study_name != "":
    spec = sp.read_file(specfile)
    spec = sp.interpolation_spec(spec)

    inputVarsList = io.extractInputVariablesFromFile(spec)
    outputVarsList = io.extractOutputVariablesFromFile(spec)
    varsList = inputVarsList + outputVarsList
    initialGR1Units = io.extractAssumptionList(spec)
    guaranteesList = io.extractGuaranteesList(spec)

counterstrategies = []

start_experiment = timeit.default_timer()
elapsed_time = 0

def configure(spectra_file, timeout_in=600, output_folder="outputs/", debug=False):
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
    global uniquesolsfile

    global experimentstatsfile

    global inputVarsList
    global outputVarsList
    global varsList
    global initialGR1Units
    global guaranteesList

    global timeout
    global start_experiment
    global elapsed_time
    
    specfile = spectra_file
    case_study_name = os.path.splitext(os.path.basename(specfile))[0]
    datafile = os.path.join(output_folder, case_study_name + "_INTERPOLATION" + ".csv")
    checkpointfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_checkpoint.csv")
    satfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_sat.csv")
    weaknessfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_weakness.csv")
    wellsepfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_wellsep.csv")
    statsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_stats.csv")
    equivclassesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_equivclasses.csv")
    distancesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_distances.csv")
    cstimesfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_cstimes.csv")
    uniquesolsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_uniquesols.csv")

    experimentstatsfile = os.path.join(output_folder, case_study_name + "_" + refinement_method + "_exp" + str(exp_number) + "_expstats.csv")

    spec = sp.read_file(specfile)
    spec = sp.interpolation_spec(spec)

    inputVarsList = io.extractInputVariablesFromFile(spec)
    outputVarsList = io.extractOutputVariablesFromFile(spec)
    varsList = inputVarsList + outputVarsList
    initialGR1Units = io.extractAssumptionList(spec)
    guaranteesList = io.extractGuaranteesList(spec)

    if debug:
        print("+++++++++++ " + case_study_name)
        print("=== INPUT VARS ===")
        for var in inputVarsList:
            print(var)
        print()
        print("=== OUTPUT VARS ===")
        for var in outputVarsList:
            print(var)
        print()
        print("=== ASSUMPTIONS ===")
        for asm in initialGR1Units:
            print(asm)
        print()
        print("=== GUARANTEES ===")
        for gar in guaranteesList:
            print(gar)
        print()

    timeout = timeout_in
    start_experiment = timeit.default_timer()
    elapsed_time = 0
