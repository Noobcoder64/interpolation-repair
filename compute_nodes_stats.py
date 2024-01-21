import os
import pandas as pd

# output_folder = "outputs-interpolation/INTERPOLATION-MIN-INF/"
output_folder = "outputs-symbolic/JVTS/"

for root, dirs, files in os.walk(output_folder):
    for node_file in [f for f in files if f.endswith('_nodes.csv')]:
        stats_file = node_file.replace('_nodes.csv', '_stats.csv')
        if stats_file not in files:
            print(f"Found: {os.path.join(root, node_file)}")
            print(f"Missing: {os.path.join(root, stats_file)}")

            nodes_csv = os.path.join(root, node_file)
            nodes_df = pd.read_csv(nodes_csv)

            repair_nodes = nodes_df[nodes_df["IsSolution"] == True]
            num_repairs = len(repair_nodes)
            time_to_first = repair_nodes["ElapsedTime"].iloc[0] if num_repairs > 0 else None
            runtime = nodes_df["ElapsedTime"].iloc[-1]

            benchmark_name = root.split("/")[-1]
            spectra_file = node_file.replace('_nodes.csv', '.spectra')

            stats_df = pd.DataFrame({
                'Filename': [f"inputs/{benchmark_name}/{spectra_file}"],
                'NumRepairs': [num_repairs],
                'RepairLimit': [-1],
                'TimeToFirst': [time_to_first],
                'Runtime': [runtime],
                'Timeout': [600],
                'TimedOut': [None],
                'NodesExplored': [len(nodes_df)],
            })

            stats_csv = os.path.join(root, stats_file)
            stats_df.to_csv(stats_csv, index=False)
            print(f"Stats CSV created and saved: {stats_csv}")