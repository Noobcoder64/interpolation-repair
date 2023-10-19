import os
import time
import pandas as pd
from experiment_config import *

def get_benchmark_name(filename):
    return filename.split('/')[-2]

def summarize_folder(output_folder):
        
        if not os.path.exists(output_folder):
            print("Output folder does not exist")
            return

        dfs = []

        for root, dirs, files in os.walk(output_folder):
            for file in files:
                if file.endswith("stats.csv"):
                     df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False)
                     df.insert(0, "Benchmark", df['Filename'].apply(get_benchmark_name))
                     dfs.append(df)

        summary_df = pd.concat(dfs, ignore_index=True)
        summary_df = summary_df.sort_values(by="Filename")
        summary_df = summary_df.sort_values(by=["Benchmark", "Filename"])
        summary_df.to_csv(os.path.join(output_folder, "repairs_summary.csv"), index=False)

        average_df = summary_df.groupby('Filename')[["NumRepairs", "TimeToFirst", "Runtime", "NodesExplored", "DuplicateNodes"]].mean()
        average_df = average_df.reset_index()
        average_df['Runs'] = summary_df.groupby('Filename').size().values
        average_df["TimeToFirst"] = round(average_df["TimeToFirst"] * 1000)
        average_df.to_csv(os.path.join(output_folder, "repairs_average.csv"), index=False)

total_start_time = time.time()

summarize_folder("outputs-scalability/INTERPOLATION-MIN-INF/")

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")