import os
import pandas as pd
import ast
import experiment_properties as exp
from weakness_for_refinement import computeWeakness_probe

input_folders = [
    "inputs/AMBA",
    # "inputs/SYNTECH15-UNREAL",
    # "inputs/SYNTECH15-1UNREAL"
]

ALGORITHMS = [
    "INTERPOLATION-NOINF",
    # "INTERPOLATION",
    # "GLASS",
    # "JVTS",
    # "ALUR",
]


def process_csv_file(csv_file_path, spectra_file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path, sep=";", index_col=False)
    
    # Convert the 'UniqueRefinement' column to a list of lists
    df['UniqueRefinement'] = df['UniqueRefinement'].apply(ast.literal_eval)
    
    # Configure experiment properties
    exp.configure(spectra_file_path)
    
    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        refinements = row['UniqueRefinement']
        if isinstance(refinements, list) and refinements != []:
            weakness = computeWeakness_probe(" & ".join(refinements), exp.varsList)[0]
            df.at[index, 'd1'] = weakness.d1
            df.at[index, 'd2'] = weakness.d2
            df.at[index, 'nummaxentropysccs'] = weakness.nummaxentropysccs
            df.at[index, 'd3'] = weakness.d3
    
    # Write the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, sep=",", index=False)

def main():
    
    for input_folder in input_folders:
        base_folder_name = os.path.basename(input_folder)

        for algorithm in ALGORITHMS:

            output_folder = os.path.join("outputs", base_folder_name, algorithm)
            spectra_files = [file for file in os.listdir(input_folder) if file.endswith(".spectra")]

            for spectra_file in spectra_files:
                spectra_file_path = os.path.join(input_folder, spectra_file)
                spec_name = os.path.splitext(spectra_file)[0]
                matching_csv_file = [csv_file for csv_file in os.listdir(output_folder) if spec_name in csv_file and csv_file.endswith(".csv")]

                if matching_csv_file:
                    csv_file_path = os.path.join(output_folder, matching_csv_file[0])
                    process_csv_file(csv_file_path, spectra_file_path)

if __name__ == "__main__":
    main()
