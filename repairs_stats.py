import os
import re
import ast
import time
import pandas as pd
from experiment_config import *
from specification import unspectra
from io_utils import extractVariablesFromFormula
from weakness_for_refinement import Weakness, compareViaImplication

SUMMARY_FILENAME = "repairs_summary"

def is_csv_file_empty(file_path):
    with open(file_path, "r") as file:
        first_line = file.readline()
        return len(first_line) == 0

def extract_system(spec_name:str):
    for system in SYSTEMS:
        if spec_name.lower().startswith(system.lower()):
            return system
    return None

def map_to_weakness(row):
    return Weakness(row['d1'], row['d2'], row['nummaxentropysccs'], row['d3'])

def create_summary_dataframe(spectra_files, output_folder):
    data_frames = []
    for spectra_file in spectra_files:
        spec_name = os.path.splitext(spectra_file)[0]
        nodes_explored = 0
        num_repairs = 0
        min_num_variables = 0
        max_num_variables = 0
        min_num_assumptions = 0
        max_num_assumptions = 0
        max_weakness = None
        matching_csv_file = [csv_file for csv_file in os.listdir(output_folder) if spec_name in csv_file and csv_file.endswith(".csv")]
        if matching_csv_file:
            csv_filepath = os.path.join(output_folder, matching_csv_file[0])
            if not is_csv_file_empty(csv_filepath):
                df = pd.read_csv(csv_filepath, sep=",", index_col=False)
                if df.empty:
                    continue
                repaired_df = df[(df["IsSolution"] == True)]
                nodes_explored = len(df)
                num_repairs = len(repaired_df)
                min_num_variables = repaired_df["NumVariables"].min()
                max_num_variables = repaired_df["NumVariables"].max()
                min_num_assumptions = repaired_df["NumAssumptions"].min()
                max_num_assumptions = repaired_df["NumAssumptions"].max()
                repaired_df["Weakness"] = repaired_df.apply(map_to_weakness, axis=1)
                max_weakness = repaired_df["Weakness"].max()

        system = extract_system(spec_name)

        data = {
            "System": [system] if system else ["Unknown"],
            "Specification": [spec_name],
            "NodesExplored": [nodes_explored],
            "NumRepairs": [num_repairs],
            "MinNumVariables": [min_num_variables],
            "MaxNumVariables": [max_num_variables],
            "MinNumAssumptions": [min_num_assumptions],
            "MaxNumAssumptions": [max_num_assumptions],
            "MaxWeakness": [max_weakness],
            "Repaired": [num_repairs > 0]
        }
        spec_df = pd.DataFrame(data)
        data_frames.append(spec_df)
    summary = pd.concat(data_frames, ignore_index=True)
    return summary.sort_values(by="Specification")

def save_summary_to_csv(summary, input_folder, algorithm, output_folder):
    input_folder_name = os.path.basename(input_folder)
    output_file = os.path.join(output_folder, f"{SUMMARY_FILENAME}_{input_folder_name}_{algorithm}.csv")
    summary.to_csv(output_file, index=False)
    print(f"Repairs summary saved to {output_file}")


def get_benchmark_name(filename):
    return filename.split('/')[-2]

def get_run_number(path):
    match = re.search(r"run-(\d+)", path)
    return int(match.group(1)) if match else None

def get_basename(filename):
    return os.path.basename(filename)

def containts_aux_variables(refinements):
    if refinements is None:
        return None

    for assumption in refinements:
        if "aux" in assumption or  "CONSTRAINT" in assumption:
            return True
    return False

var_pattern = re.compile("\w+")

def safe_literal_eval(value):
    try:
        return ast.literal_eval(value)
    except Exception:
        return None

def contains_false(refinements):
    if refinements is None:
        return None

    for assumption in refinements:
        if "FALSE" in assumption:
            return True
    return False

def count_num_variables(assumptions):
    # return 0
    if assumptions is None:
        return None
    
    total_vars = list()
    for assumption in assumptions:
        vars = extractVariablesFromFormula(assumption)
        total_vars.extend(vars)

    return len(vars)

def summarize_folder(output_folder):
        
        if not os.path.exists(output_folder):
            print("Output folder does not exist")
            return

        dfs = []

        for root, dirs, files in os.walk(output_folder):

            run = get_run_number(root)

            for file in files:

                if not file.endswith("stats.csv"):
                    continue

                print(root + "/" + file)

                stats_df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False)

                stats_df.insert(0, "Benchmark", stats_df['Filename'].apply(get_benchmark_name))
                
                stats_df.insert(1, "Run", run)

                nodes_file = file.replace("stats", "nodes")
                nodes_df = pd.read_csv(os.path.join(root, nodes_file), sep=",", index_col=False)
                nodes_df['Refinement'] = nodes_df['Refinement'].apply(safe_literal_eval)
                nodes_df["ContainsFalse"] = nodes_df["Refinement"].apply(contains_false)

                # unique_nodes_file = file.replace("stats", "uniquenodes")
                # unique_nodes_df = pd.read_csv(os.path.join(root, unique_nodes_file), sep=",", index_col=False)
                # stats_df["UniqueNodesExplored"] = len(unique_nodes_df)

                sols_file = file.replace("stats", "sols")
                sols_df = pd.read_csv(os.path.join(root, sols_file), sep=",", index_col=False)

                # unique_sols_file = file.replace("stats", "uniquesols")
                # unique_sols_df = pd.read_csv(os.path.join(root, unique_sols_file), sep=",", index_col=False)

                stats_df["NumRepairs"] = len(sols_df)
                # stats_df["UniqueSols"] = len(unique_sols_df)

                stats_df["Effectiveness"] = stats_df["NumRepairs"] / stats_df["NodesExplored"]
                # stats_df["UniqueEffectiveness"] = stats_df["UniqueSols"] / stats_df["UniqueNodesExplored"]


                if not sols_df.empty:
                    first_row_sols = sols_df.iloc[0]
                    stats_df["NodesToFirst"] = (nodes_df['Id'] == first_row_sols['Id']).idxmax() + 1

                column_name = 'Depth' if 'Depth' in nodes_df.columns else 'Length'

                if not sols_df[column_name].empty:
                    stats_df["DepthToFirst"] = sols_df[column_name].iloc[0]

                
                stats_df["NumYUnsat"] = len(nodes_df[nodes_df["IsYSat"] == False])
                stats_df["NumYUnsatNoFalse"] = len(nodes_df[(nodes_df["IsYSat"] == False) & (nodes_df["ContainsFalse"] == False)])

                # stats_df["NumSat"] = len(nodes_df[nodes_df["IsSatisfiable"] == False])

                stats_df["NumFullyNonIOSeparable"] = len(nodes_df[nodes_df["NumNonIoSeparable"] > nodes_df["NumStateComponents"]])
                stats_df["NumFullyNonIOSeparable"] = len(nodes_df[nodes_df["NumNonIoSeparable"] > nodes_df["NumStateComponents"]])

                sols_df['Refinement'] = sols_df['Refinement'].apply(safe_literal_eval)
                sols_df["NumVariables"] = sols_df['Refinement'].apply(count_num_variables)
                stats_df["MinNumVariables"] = sols_df["NumVariables"].min()

                dfs.append(stats_df)

        summary_df = pd.concat(dfs, ignore_index=True)
        summary_df = summary_df.sort_values(by=["Benchmark", "Filename", "Run"])
        summary_df.to_csv(os.path.join(output_folder, "repairs_summary.csv"), index=False)

        columns = [
            "NumRepairs",
            # "UniqueSols",
            "TimeToFirst",
            "Runtime",
            "NodesExplored",
            # "UniqueNodesExplored",
            "Effectiveness",
            # "UniqueEffectiveness",
            "NodesToFirst",
            "DepthToFirst",
            "NumYUnsat",
            "NumYUnsatNoFalse",
            "NumInterpolantsComputed",
            "NumNonStateSeparable",
            "NumFullyNonIOSeparable",
        ]

        average_df = summary_df.groupby('Filename')[columns].mean()
        average_df['Runs'] = summary_df.groupby('Filename').size().values
        average_df['MinNumVariables'] = summary_df.groupby('Filename')['MinNumVariables'].min()
        average_df = average_df.reset_index()
        average_df.insert(0, "Benchmark", average_df['Filename'].apply(get_benchmark_name))
        average_df["Filename"] = average_df["Filename"].apply(get_basename)

        # Uncomment for times in milliseconds
        # average_df["TimeToFirst"] = round(average_df["TimeToFirst"] * 1000)
        # average_df["Runtime"] = round(average_df["Runtime"] * 1000)

        average_df.to_csv(os.path.join(output_folder, "repairs_average.csv"), index=False)



total_start_time = time.time()

summarize_folder("outputs-interpolation/INTERPOLATION-MIN-INF/")
# summarize_folder("outputs-interpolation/INTERPOLATION-MIN/")
# summarize_folder("outputs-interpolation/INTERPOLATION-ALLGARS-INF/")
# summarize_folder("outputs-interpolation/INTERPOLATION-ALLGARS/")
# summarize_folder("outputs-symbolic/GLASS/")
# summarize_folder("outputs-symbolic/JVTS/")

# summarize_folder("outputs-scalability/INTERPOLATION-MIN-INF/")
# summarize_folder("outputs-scalability/GLASS/")
# summarize_folder("outputs-scalability/JVTS/")

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")