import os
import time
import subprocess
import concurrent.futures

# List of input folders
input_folders = [
    # "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL"
]

# List of algorithms
algorithms = ["GLASS", "JVTS", "ALUR"]

# Output parent folder
output_parent_folder = "outputs"

# Set the timeout
TIMEOUT = 10

def process_file(input_file, algorithm, output_folder):
    start_time = time.time()
    
    # Construct the command to run spec_repair.py
    command = f"python spec_repair.py -i {input_file} -a {algorithm} -o {output_folder} -t {TIMEOUT}"

    print(f"Repairing {input_file} using {algorithm} algorithm...")

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Error executing spec_repair.py for {input_file}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processed {os.path.basename(input_file)} using {algorithm} algorithm in {elapsed_time:.2f} seconds")


def process_folder(input_folder, algorithm):
    # Create an output folder for each combination of input folder and algorithm
    output_folder = os.path.join(output_parent_folder, os.path.basename(input_folder), algorithm)
    os.makedirs(output_folder, exist_ok=True)
    
    # Get a list of .spectra files in the input folder
    spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
    
    # Use ThreadPoolExecutor to process files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for spectra_file in spectra_files:
            input_file = os.path.join(input_folder, spectra_file)
            executor.submit(process_file, input_file, algorithm, output_folder)

total_start_time = time.time()

for input_folder in input_folders:
    for algorithm in algorithms:
        process_folder(input_folder, algorithm)
            
total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")