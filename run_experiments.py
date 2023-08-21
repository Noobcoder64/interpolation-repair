import os
import time
import subprocess
import concurrent.futures
# import pandas as pd

# List of input folders
INPUT_FOLDERS = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL"
]

# List of algorithms
ALGORITHMS = [
    "INTERPOLATION-NOINF",
    # "INTERPOLATION",
    # "GLASS",
    # "JVTS",
    # "ALUR",
]

# Output parent folder
OUTPUT_PARENT_FOLDER = "outputs/"

# Set the timeout
TIMEOUT = 10

SUMMARY_FILENAME = "repairs_summary.csv"

def process_file(input_file, algorithm, output_folder, output_file):
    start_time = time.time()
    
    if "INTERPOLATION" in algorithm:
        command = f"python interpolation_repair.py -i {input_file} -o {output_folder} -t {TIMEOUT}"
    else:
        command = f"python spec_repair.py -i {input_file} -a {algorithm} -o {output_folder} -t {TIMEOUT}"

    print(command)

    with open(output_file, "w") as output:
        try:
            subprocess.run(command, shell=True, check=True, stdout=output)
        except subprocess.CalledProcessError:
            print(f"Error repairing {input_file}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processed {os.path.basename(input_file)} using {algorithm} algorithm in {elapsed_time:.2f} seconds")


def process_folder(input_folder, algorithm):
    # Create an output folder for each combination of input folder and algorithm
    output_folder = os.path.join(OUTPUT_PARENT_FOLDER, os.path.basename(input_folder), algorithm)
    os.makedirs(output_folder, exist_ok=True)
    
    # Get a list of .spectra files in the input folder
    spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
    
    # Use ThreadPoolExecutor to process files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for spectra_file in spectra_files:
            input_file = os.path.join(input_folder, spectra_file)
            output_file = os.path.join(output_folder, os.path.splitext(spectra_file)[0] + "_output.txt")
            executor.submit(process_file, input_file, algorithm, output_folder, output_file)


def summarize_folder(input_folder):
            
    output_folder = os.path.join(OUTPUT_PARENT_FOLDER, os.path.basename(input_folder), algorithm)
    os.makedirs(output_folder, exist_ok=True)

    # Output CSV file path
    output_file = os.path.join(output_folder, SUMMARY_FILENAME)

    # Initialize a list to hold DataFrames for each CSV file
    data_frames = []

    # Get a list of .spectra files in the input folder
    spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]

    # Iterate through each .spectra file
    for spectra_file in spectra_files:
        spec_name = os.path.splitext(spectra_file)[0]

        # Find a CSV file that contains the spectra filename as a substring
        matching_csv_file = [csv_file for csv_file in os.listdir(output_folder) if spec_name in csv_file and csv_file.endswith(".csv")]

        if matching_csv_file:
            csv_filepath = os.path.join(output_folder, matching_csv_file[0])
            df = pd.read_csv(csv_filepath, sep=";", index_col=False)
            if "IsSolution" in df.columns:
                # Count the number of rows where 'IsSolution' is True
                num_repairs = len(df[df["IsSolution"] == True])
            else:
                # If 'IsSolution' column is not present, consider all rows as num_repairs
                num_repairs = len(df)
        else:
            num_repairs = 0

        # Create a DataFrame with spec name and num_repairs
        data = {"Specification": [spec_name], "NumRepairs": [num_repairs]}
        spec_df = pd.DataFrame(data)
        
        # Append the DataFrame to the list
        data_frames.append(spec_df)

    # Concatenate all DataFrames into a single DataFrame
    combined_data = pd.concat(data_frames, ignore_index=True)

    # Sort the DataFrame by the "Specification" column
    combined_data = combined_data.sort_values(by="Specification")

    # Save the combined data to the output CSV file
    combined_data.to_csv(output_file, index=False)
    print(f"Repairs summary saved to {output_file}")


total_start_time = time.time()

for input_folder in INPUT_FOLDERS:
    for algorithm in ALGORITHMS:
        process_folder(input_folder, algorithm)

# for input_folder in INPUT_FOLDERS:
#     for algorithm in ALGORITHMS:
#         summarize_folder(input_folder)

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")