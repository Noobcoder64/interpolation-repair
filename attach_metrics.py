import sys
import os
import re
import pandas as pd
import ast
import experiment_properties as exp
from weakness_for_refinement import Weakness, computeWeakness_probe

sys.setrecursionlimit(1500)

# List of input folders
INPUT_FOLDERS = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL",
    # "inputs/AMBA-ORIGINAL",
    # "inputs/SYNTECH15-UNREAL-ORIGINAL",
    # "inputs/SYNTECH15-1UNREAL-ORIGINAL"
]

# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-ALLGARS",
    # "INTERPOLATION-NONINF",
    "INTERPOLATION",
    # "GLASS",
    "JVTS",
    # "ALUR",
]

def count_num_variables(refinements):
    total_variables = set()
    
    refinements = [re.sub(r"G\(F\s*\((.*)\)\)", r"\1", x) for x in refinements]
    refinements = [re.sub(r"G\((.*)\)", r"\1", x) for x in refinements]
    refinements = [re.sub(r"X\((.*)\)", r"\1", x) for x in refinements]
    
    for assumption in refinements:
        assumption = re.sub(r'G\((.*)\)|X\((.*)\)|G\(F\((.*)\)\)', r'\1', assumption)
        variables = re.findall(r'\b\w+\b', assumption)
        total_variables.update(variables)

    return len(total_variables)

def process_csv_file(csv_file_path, spectra_file_path):
    print("Processing:", csv_file_path)
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path, sep=",", index_col=False)
    df.columns
    # Convert the 'UniqueRefinement' column to a list of lists
    df['UniqueRefinement'] = df['UniqueRefinement'].apply(ast.literal_eval)
    df['NumVariables'] = None

    # Configure experiment properties
    exp.configure(spectra_file_path)
    
    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        refinements = row['UniqueRefinement']
        if not isinstance(refinements, list):
            continue
        
        num_variables = None
        d1 = None
        d2 = None
        nummaxentropysccs = None
        d3 = None
        if refinements != []:
            num_variables = count_num_variables(refinements)

            try:
                weakness = computeWeakness_probe(" & ".join(refinements), exp.varsList)[0]
                d1 = weakness.d1
                d2 = weakness.d2
                nummaxentropysccs = weakness.nummaxentropysccs
                d3 = weakness.d3
            except:
                print("Failed to compute weakness")

        df.at[index, 'NumVariables'] = num_variables
        df.at[index, 'd1'] = d1
        df.at[index, 'd2'] = d2
        df.at[index, 'nummaxentropysccs'] = nummaxentropysccs
        df.at[index, 'd3'] = d3
        
    # Write the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, sep=",", index=False)
    print("Processed:", csv_file_path)

def main():
    
    for input_folder in INPUT_FOLDERS:
        input_folder_name = os.path.basename(input_folder)

        for algorithm in ALGORITHMS:
            output_folder = os.path.join("outputs", input_folder_name, algorithm)
            spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]

            for spectra_file in spectra_files:
                spectra_file_name = os.path.splitext(spectra_file)[0]
                spectra_file_path = os.path.join(input_folder, spectra_file)
                
                csv_file_name = f"{spectra_file_name}_{algorithm}.csv"
                csv_file_path = os.path.join(output_folder, csv_file_name)

                if not os.path.exists(csv_file_path):
                    print("File does not exist:", csv_file_path)
                    continue
                
                process_csv_file(csv_file_path, spectra_file_path)

if __name__ == "__main__":
    main()
