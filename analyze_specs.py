import os
import pandas as pd
import re

def remove_comments(file_contents):
    return re.sub(r"/\*.*?\*/", "", file_contents, flags=re.DOTALL)

def count_keywords(file_contents):
    keyword_counts = {"env ": 0, "sys ": 0, "aux ": 0, "assumption": 0, "guarantee": 0}
    lines = file_contents.split('\n')
    for line in lines:
        for keyword in keyword_counts.keys():
            keyword_counts[keyword] += line.count(keyword)
    return keyword_counts

def process_folder(folder_path):
    data = []
    for root, _, files in os.walk(folder_path):
        files.sort()
        for file_name in files:
            if file_name.endswith(".spectra"):
                file_path = os.path.join(root, file_name)
                # Extract the parent directory (immediate folder name) as Benchmark
                benchmark = os.path.basename(root)
                with open(file_path, "r") as file:
                    file_contents = file.read()
                    # cleaned_contents = remove_comments(file_contents)
                    keyword_counts = count_keywords(file_contents)
                    # Append a dictionary with all information, including the Benchmark
                    data.append({"Benchmark": benchmark, "Filename": file_name, **keyword_counts})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    
    # Rename the columns at the end
    df = df.rename(columns={
        "env ": "env",
        "sys ": "sys",
        "aux ": "aux",
        "assumption": "assumptions",
        "guarantee": "guarantees"
    })
    
    return df

folder_path = "inputs/"
result_df = process_folder(folder_path)
result_df = result_df[result_df["Benchmark"] != "Y-UNSAT"]
result_df.to_csv("specifications_info.csv", index=False)

print(result_df)
