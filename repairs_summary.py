import os
import time
import pandas as pd

# List of input folders
INPUT_FOLDERS = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL"
]

# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-NOINF",
    "INTERPOLATION",
    "GLASS",
    "JVTS",
    "ALUR",
]

# Output parent folder
OUTPUT_PARENT_FOLDER = "outputs/"

SUMMARY_FILENAME = "repairs_summary"

def create_summary_dataframe(spectra_files, output_folder):
    data_frames = []
    for spectra_file in spectra_files:
        spec_name = os.path.splitext(spectra_file)[0]

        matching_csv_file = [csv_file for csv_file in os.listdir(output_folder) if spec_name in csv_file and csv_file.endswith(".csv")]
        if matching_csv_file:
            csv_filepath = os.path.join(output_folder, matching_csv_file[0])
            df = pd.read_csv(csv_filepath, sep=",", index_col=False)
            repaired_df = df[df["IsSolution"] == True]
            num_repairs = len(repaired_df)
            min_num_variables = repaired_df["NumVariables"].min()
        else:
            min_num_variables = 0
            num_repairs = 0

        data = {"Specification": [spec_name], "NumRepairs": [num_repairs], "MinNumVariables": [min_num_variables], "Repaired": [num_repairs > 0]}
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
    output_folder = os.path.join(OUTPUT_PARENT_FOLDER, os.path.basename(input_folder), algorithm)
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