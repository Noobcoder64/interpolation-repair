import os
import subprocess

# List of input folders
input_folders = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL"
]

# List of algorithms
algorithms = ["GLASS", "JVTS", "ALUR"]

# Output parent folder
output_parent_folder = "outputs"

# Set the timeout
TIMEOUT = 10

# Loop through input folders and algorithms
for input_folder in input_folders:
    for algorithm in algorithms:
        # Create an output folder for each combination of input folder and algorithm
        output_folder = os.path.join(output_parent_folder, os.path.basename(input_folder), algorithm)
        os.makedirs(output_folder, exist_ok=True)
        
        # Get a list of .spectra files in the input folder
        spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
        
        # Loop through the .spectra files and run spec_repair.py for each
        for spectra_file in spectra_files:
            input_file = os.path.join(input_folder, spectra_file)
            
            # Construct the command to run spec_repair.py
            command = f"python spec_repair.py -i {input_file} -a {algorithm} -o {output_folder} -t {TIMEOUT}"

            print(f"Repairing {spectra_file} using {algorithm} algorithm in {input_folder}...")
            
            try:
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError:
                print(f"Error executing spec_repair.py for {spectra_file}")
