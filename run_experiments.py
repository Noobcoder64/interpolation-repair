import os
import time
import subprocess
import concurrent.futures

# List of input folders
INPUT_FOLDERS = [
    # "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    # "inputs/SYNTECH15-1UNREAL"
]

# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-NOINF",
    # "INTERPOLATION",
    "GLASS",
    "JVTS",
    "ALUR",
]

# Output parent folder
OUTPUT_PARENT_FOLDER = "outputs/"

# Set the timeout
TIMEOUT = 10


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
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    for spectra_file in spectra_files:
        input_file = os.path.join(input_folder, spectra_file)
        spectra_file_name = os.path.splitext(os.path.basename(spectra_file))[0]
        output_file_name = f"{spectra_file_name}_{algorithm}_output.txt"
        output_file = os.path.join(output_folder, output_file_name)
        # executor.submit(process_file, input_file, algorithm, output_folder, output_file)
        process_file(input_file, algorithm, output_folder, output_file)

total_start_time = time.time()

for input_folder in INPUT_FOLDERS:
    for algorithm in ALGORITHMS:
        process_folder(input_folder, algorithm)

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")