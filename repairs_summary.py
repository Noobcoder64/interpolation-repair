import os
import time
import pandas as pd
from experiment_config import INPUT_FOLDERS, ALGORITHMS, SYSTEMS, OUTPUT_PARENT_FOLDER
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
        min_weakness = None
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
                # min_num_assumptions = repaired_df["NumAssumptions"].min()
                # max_num_assumptions = repaired_df["NumAssumptions"].max()
                repaired_df["Weakness"] = repaired_df.apply(map_to_weakness, axis=1)
                min_weakness = repaired_df["Weakness"].min()

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
            "MinWeakness": [min_weakness],
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

def summarize_folder(input_folder, algorithm):
    for i in range(1, 2):
        output_folder = os.path.join(OUTPUT_PARENT_FOLDER, f"run-{i}", os.path.basename(input_folder), algorithm)
        os.makedirs(output_folder, exist_ok=True)

        spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
        summary = create_summary_dataframe(spectra_files, output_folder)
        
        save_summary_to_csv(summary, input_folder, algorithm, output_folder)


total_start_time = time.time()

for input_folder in INPUT_FOLDERS:
    for algorithm in ALGORITHMS:
        summarize_folder(input_folder, algorithm)

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")