import os
import time
import pandas as pd

# List of input folders
INPUT_FOLDERS = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL",
    "inputs/SYNTECH15-1UNREAL-ORIGINAL",
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

SMALL_REPAIR_VALUE = 10

def summarize(input_folder):
    if not os.path.exists(input_folder):
        print("Folder does not exist:", input_folder)
        return
    
    input_folder_name = os.path.basename(input_folder)
     
    summary_columns = ["Algorithm", "NumRepaired", "NumSmallRepairs"]
    summary_data = []
    for algorithm in ALGORITHMS:
        output_folder = os.path.join(OUTPUT_PARENT_FOLDER, input_folder_name, algorithm)

        repairs_summary_file = os.path.join(output_folder, f"{SUMMARY_FILENAME}_{input_folder_name}_{algorithm}.csv")

        if not os.path.exists(repairs_summary_file):
            print("File does not exist:", repairs_summary_file)
            continue

        df = pd.read_csv(repairs_summary_file)
        repaired_specs = df[df["Repaired"] == True]
        num_repaired = len(repaired_specs)
        
        num_small_repaired = len(df[(df["MinNumVariables"] <= SMALL_REPAIR_VALUE) & (df["MinNumVariables"] > 0)])
        summary_data.append([algorithm, num_repaired, num_small_repaired])

    benchmark_summary_file = os.path.join(OUTPUT_PARENT_FOLDER, input_folder_name, f"benchmark_summary_{input_folder_name}.csv")
    
    df = pd.DataFrame(summary_data, columns=summary_columns)
    df.to_csv(benchmark_summary_file, index=False)
    
    print(f"Benchmark summary for {input_folder_name} saved to {benchmark_summary_file}")


for input_folder in INPUT_FOLDERS:
    summarize(input_folder)