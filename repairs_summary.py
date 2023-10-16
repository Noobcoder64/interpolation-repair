import os
import time
import pandas as pd
from experiment_config import *
from weakness_for_refinement import Weakness

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

def summarize_folder(output_folder):
        
        if not os.path.exists(output_folder):
            print("Output folder does not exist")
            return

        dfs = []

        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith("stats.csv"):
                     df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False)
                     df.insert(0, "Benchmark", df['Filename'].apply(get_benchmark_name))
                     dfs.append(df)

        summary_df = pd.concat(dfs, ignore_index=True)
        summary_df = summary_df.sort_values(by="Filename")
        summary_df.to_csv(os.path.join(output_folder, "repairs_summary.csv"), index=False)

        average_df = summary_df.groupby('Filename')[["NumRepairs", "TimeToFirst", "Runtime", "NodesExplored", "DuplicateNodes"]].mean()
        average_df = average_df.reset_index()
        average_df.to_csv(os.path.join(output_folder, "average.csv"), index=False)

total_start_time = time.time()

# for algorithm in ALGORITHMS:
    # for input_folder in INPUT_FOLDERS:
        # summarize_folder(input_folder, algorithm)

summarize_folder("outputs-interpolation/INTERPOLATION-MIN-INF/")

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")