
import os
import time
import subprocess
import concurrent.futures
from experiment_config import INPUT_FOLDERS, ALGORITHMS, FLAGS, OUTPUT_PARENT_FOLDER, RUN, TIMEOUT


def process_file(input_file, algorithm, output_folder, output_file):
    
    if "INTERPOLATION" in algorithm:
        command = f"python interpolation_repair.py -i {input_file} -o {output_folder} -t {TIMEOUT} {FLAGS}"
    else:
        command = f"python spec_repair.py -i {input_file} -a {algorithm} -o {output_folder} -t {TIMEOUT}"

    print(command)
    
    start_time = time.time()
    
    with open(output_file, "w") as output:
        try:
            subprocess.run(command, shell=True, check=True, stdout=output)
        except subprocess.CalledProcessError:
            print(f"Error repairing {input_file}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processed {os.path.basename(input_file)} using {algorithm} algorithm in {elapsed_time:.2f} seconds")


def process_algorithm(algorithm, input_folder):

    output_folder = os.path.join(OUTPUT_PARENT_FOLDER, algorithm, f"run-{RUN}", os.path.basename(input_folder))
    os.makedirs(output_folder, exist_ok=True)
    
    spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
    spectra_files.sort()

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    for spectra_file in spectra_files:
        input_file = os.path.join(input_folder, spectra_file)
        spectra_file_name = os.path.splitext(os.path.basename(spectra_file))[0]
        output_file_name = f"{spectra_file_name}_{algorithm}_output.txt"
        output_file = os.path.join(output_folder, output_file_name)
        # executor.submit(process_file, input_file, algorithm, output_folder, output_file)
        if not [csv_file for csv_file in os.listdir(output_folder) if spectra_file_name in csv_file and csv_file.endswith(".csv")]:
            process_file(input_file, algorithm, output_folder, output_file)

total_start_time = time.time()

for algorithm in ALGORITHMS:
    for input_folder in INPUT_FOLDERS:
        process_algorithm(algorithm, input_folder)

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")