import os
import re
import ast
import time
import pandas as pd
from experiment_config import *
from io_utils import extractVariablesFromFormula


def get_benchmark_name(filename):
    return filename.split('/')[-2]

def get_run_number(path):
    match = re.search(r"run-(\d+)", path)
    return int(match.group(1)) if match else None

def get_basename(filename):
    return os.path.basename(filename)

def containts_aux_variables(refinements):
    if refinements is None:
        return None

    for assumption in refinements:
        if "aux" in assumption or  "CONSTRAINT" in assumption:
            return True
    return False

var_pattern = re.compile("\w+")

def safe_literal_eval(value):
    try:
        return ast.literal_eval(value)
    except Exception:
        return None

def contains_false(refinements):
    if refinements is None:
        return None

    for assumption in refinements:
        if "FALSE" in assumption:
            return True
    return False

def count_num_variables(assumptions):

    if assumptions is None:
        return None
    
    total_vars = list()
    for assumption in assumptions:
        vars = extractVariablesFromFormula(assumption)
        total_vars.extend(vars)

    return len(vars)

def summarize_folder(output_folder):
        
        if not os.path.exists(output_folder):
            print("Output folder does not exist")
            return

        dfs = []

        for root, dirs, files in os.walk(output_folder):

            run = get_run_number(root)

            for file in files:

                if not file.endswith("stats.csv"):
                    continue

                print(root + "/" + file)

                # Read 'stats' file
                stats_df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False)

                # Add Benchmark column
                stats_df.insert(0, "Benchmark", stats_df['Filename'].apply(get_benchmark_name))
                
                # Add Run column
                stats_df.insert(1, "Run", run)

                # Read 'nodes' file
                nodes_file = file.replace("stats", "nodes")
                nodes_df = pd.read_csv(os.path.join(root, nodes_file), sep=",", index_col=False)
                # nodes_df['Refinement'] = nodes_df['Refinement'].apply(safe_literal_eval)
                # nodes_df["ContainsFalse"] = nodes_df["Refinement"].apply(contains_false)

                #
                if "GLASS" in root:
                    nodes_df["Refinement"] = nodes_df["Refinement"].apply(safe_literal_eval)
                    nodes_df["NumAssumptions"] = nodes_df["Refinement"].apply(lambda ref: len(ref) if ref else 0)
                    stats_df["MinNumAssumptions"] = nodes_df["NumAssumptions"].min()
                    nodes_df["NumVariables"] = nodes_df["Refinement"].apply(count_num_variables)
                    stats_df["MinNumVariables"] = nodes_df["NumVariables"].min()

                    dfs.append(stats_df)
                    continue

                # Read 'uniquenodes' file
                unique_nodes_file = file.replace("stats", "uniquenodes")
                if os.path.exists(os.path.join(root, unique_nodes_file)):
                    unique_nodes_df = pd.read_csv(os.path.join(root, unique_nodes_file), sep=",", index_col=False)
                    stats_df["UniqueNodesExplored"] = len(unique_nodes_df)
                else:
                    stats_df["UniqueNodesExplored"] = stats_df["NodesExplored"]

                # Read 'sols' file
                sols_file = file.replace("stats", "sols")
                sols_df = pd.read_csv(os.path.join(root, sols_file), sep=",", index_col=False)

                # Read 'uniquesols' file
                unique_sols_file = file.replace("stats", "uniquesols")
                unique_sols_df = pd.read_csv(os.path.join(root, unique_sols_file), sep=",", index_col=False)

                stats_df["NumRepairs"] = len(sols_df)
                stats_df["UniqueSols"] = len(unique_sols_df)

                stats_df["Effectiveness"] = stats_df["NumRepairs"] / (stats_df["NodesExplored"] - 1)
                stats_df["UniqueEffectiveness"] = stats_df["UniqueSols"] / (stats_df["UniqueNodesExplored"] - 1)

                if not sols_df.empty:
                    first_row_sols = sols_df.iloc[0]
                    stats_df["NodesToFirst"] = (nodes_df['Id'] == first_row_sols['Id']).idxmax() + 1

                column_name = 'Depth' if 'Depth' in nodes_df.columns else 'Length'

                if not sols_df[column_name].empty:
                    stats_df["DepthToFirst"] = sols_df[column_name].iloc[0]

                # Maximum depth
                stats_df["MaxDepth"] = nodes_df.iloc[-1][column_name]

                # Number of refinements generated per depth
                stats_df["RefsPerDepth"] = nodes_df.groupby(column_name).size().mean()

                stats_df["NumYUnsat"] = len(nodes_df[nodes_df["IsYSat"] == False])

                sols_df['Refinement'] = sols_df['Refinement'].apply(safe_literal_eval)
                sols_df["NumVariables"] = sols_df['Refinement'].apply(count_num_variables)
                stats_df["MinNumVariables"] = sols_df["NumVariables"].min()

                # Uncomment if interpolation
                
                # stats_df["NumYUnsatNoFalse"] = len(nodes_df[(nodes_df["IsYSat"] == False) & (nodes_df["ContainsFalse"] == False)])
                
                # stats_df["NumFullyNonIOSeparable"] = len(nodes_df[nodes_df["NumNonIoSeparable"] > nodes_df["NumStateComponents"]])
                
                # stats_df["TotalTimeCounterstrategy"] = nodes_df["TimeCounterstrategy"].sum()
                # stats_df["TotalTimeCounterstrategyComputed"] = nodes_df["TimeCounterstrategy"].sum()
                # last_counterstrategy_time = stats_df["Runtime"].iloc[-1] - nodes_df["TimestampRealizabilityCheck"].iloc[-1]
                # stats_df.loc[stats_df["TimedOut"], "TotalTimeCounterstrategyComputed"] += last_counterstrategy_time

                # stats_df["TotalTimeGenerationMethod"] = nodes_df["TimeGenerationMethod"].sum()

                dfs.append(stats_df)

        summary_df = pd.concat(dfs, ignore_index=True)
        summary_df = summary_df.sort_values(by=["Benchmark", "Filename", "Run"])
        summary_df.to_csv(os.path.join(output_folder, "repairs_summary.csv"), index=False)

        exclude_columns = [
            "Benchmark",
            "Filename",
            "Run",
            "RepairLimit",
            "Timeout",
        ]

        include_columns = summary_df.columns.difference(exclude_columns)

        average_df = summary_df.groupby('Filename')[include_columns].mean()
        average_df['Runs'] = summary_df.groupby('Filename').size().values
        average_df['MinNumVariables'] = summary_df.groupby('Filename')['MinNumVariables'].min()
        average_df = average_df.reset_index()
        average_df.insert(0, "Benchmark", average_df['Filename'].apply(get_benchmark_name))
        average_df["Filename"] = average_df["Filename"].apply(get_basename)

        # Uncomment for times in milliseconds
        # average_df["TimeToFirst"] = round(average_df["TimeToFirst"] * 1000)
        # average_df["Runtime"] = round(average_df["Runtime"] * 1000)

        average_df.to_csv(os.path.join(output_folder, "repairs_average.csv"), index=False)


total_start_time = time.time()

# summarize_folder("outputs-interpolation/INTERPOLATION-MIN-INF/")
# summarize_folder("outputs-interpolation/INTERPOLATION-MIN/")
# summarize_folder("outputs-interpolation/INTERPOLATION-ALLGARS-INF/")
# summarize_folder("outputs-interpolation/INTERPOLATION-ALLGARS/")
# summarize_folder("outputs-symbolic/GLASS/")
summarize_folder("outputs-symbolic/JVTS/")

# summarize_folder("outputs-scalability/INTERPOLATION-MIN-INF/")
# summarize_folder("outputs-scalability/GLASS/")
# summarize_folder("outputs-scalability/JVTS/")

total_end_time = time.time()
total_elapsed_time = total_end_time - total_start_time
print(f"All tasks completed. Total elapsed time: {total_elapsed_time:.2f} seconds")