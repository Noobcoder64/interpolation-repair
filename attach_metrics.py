import sys
import os
import re
import pandas as pd
import ast
import experiment_properties as exp
from weakness_for_refinement import Weakness, computeWeakness_probe
from experiment_config import INPUT_FOLDERS, ALGORITHMS, OUTPUT_PARENT_FOLDER
import concurrent.futures

ATTACH_NUM_VARIABLES = True
ATTACH_NUM_ASSUMPTIONS = True
ATTACH_WEAKNESS = True

sys.setrecursionlimit(2000)

def is_csv_file_empty(file_path):
    with open(file_path, "r") as file:
        first_line = file.readline()
        return len(first_line) == 0

def count_num_variables(refinements):
    total_variables = set()
    
    refinements = [re.sub(r"G\(F\s*\((.*)\)\)", r"\1", x) for x in refinements]
    refinements = [re.sub(r"G\((.*)\)", r"\1", x) for x in refinements]
    refinements = [re.sub(r"X\((.*)\)", r"\1", x) for x in refinements]
    
    for assumption in refinements:
        variables = re.findall(r'\b\w+\b', assumption)
        total_variables.update(variables)

    return len(total_variables)

def containts_aux_variables(refinements):
    for assumption in refinements:
        if "aux" in assumption or  "CONSTRAINT" in assumption:
            return True
    return False

def process_csv_file(csv_file_path, spectra_file_path):
    if is_csv_file_empty(csv_file_path): 
        return

    print("Processing:", csv_file_path)
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path, sep=",", index_col=False)
    df.columns
    # Convert the 'UniqueRefinement' column to a list of lists
    df['UniqueRefinement'] = df['UniqueRefinement'].apply(ast.literal_eval)

    # Configure experiment properties
    exp.configure(spectra_file_path)
    
    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        refinements = row['UniqueRefinement']
        if not isinstance(refinements, list) or row["IsSolution"] == False:
            df.at[index, 'NumVariables'] = None
            df.at[index, 'NumAssumptions'] = None
            df.at[index, 'ContainsAux'] = None
            df.at[index, 'd1'] = None
            df.at[index, 'd2'] = None
            df.at[index, 'nummaxentropysccs'] = None
            df.at[index, 'd3'] = None
            continue
        
        num_variables = None
        num_assumptions = None
        contains_aux = False
        d1 = None
        d2 = None
        nummaxentropysccs = None
        d3 = None
        if refinements != []:
            contains_aux = containts_aux_variables(refinements)
            if ATTACH_NUM_VARIABLES:
                num_variables = count_num_variables(refinements)
            if ATTACH_NUM_ASSUMPTIONS:
                num_assumptions = len(refinements)

            if ATTACH_WEAKNESS:
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(computeWeakness_probe, " & ".join(refinements), exp.varsList)
                        weakness = future.result(timeout=20000)[0]
                        print("Computed weakness")
                        d1 = weakness.d1
                        d2 = weakness.d2
                        nummaxentropysccs = weakness.nummaxentropysccs
                        d3 = weakness.d3
                except concurrent.futures.TimeoutError:
                    print("Timed out.")
                except:
                    print("Failed to compute weakness")

        df.at[index, 'NumVariables'] = num_variables
        df.at[index, 'NumAssumptions'] = num_assumptions
        df.at[index, 'ContainsAux'] = contains_aux
        df.at[index, 'd1'] = d1
        df.at[index, 'd2'] = d2
        df.at[index, 'nummaxentropysccs'] = nummaxentropysccs
        df.at[index, 'd3'] = d3
        
    # Write the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, sep=",", index=False)
    print("Processed:", csv_file_path)

def main():

    for i in range(1, 2):

        for input_folder in INPUT_FOLDERS:
            input_folder_name = os.path.basename(input_folder)

            for algorithm in ALGORITHMS:
                
                output_folder = os.path.join(OUTPUT_PARENT_FOLDER, f"run-{i}", input_folder_name, algorithm)
                spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]
                spectra_files.sort()

                for spectra_file in spectra_files:
                    spectra_file_name = os.path.splitext(spectra_file)[0]
                    spectra_file_path = os.path.join(input_folder, spectra_file)
                    
                    if "INTERPOLATION" in algorithm:
                        algorithm = "INTERPOLATION"
                    csv_file_name = f"{spectra_file_name}_{algorithm}.csv"
                    csv_file_path = os.path.join(output_folder, csv_file_name)

                    if not os.path.exists(csv_file_path):
                        print("File does not exist:", csv_file_path)
                        continue
                    
                    process_csv_file(csv_file_path, spectra_file_path)

if __name__ == "__main__":
    main()
