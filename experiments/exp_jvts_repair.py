from pathlib import Path
import subprocess
import mlflow
import time
import pandas as pd

# Set up MLflow tracking
mlflow.set_tracking_uri("sqlite:///mlruns/mlruns.db")

# Define paths
specifications_dir = Path("./specifications/SIMPLE/")
# specifications_dir = Path("./specifications/AMBA-CAV17/")
# specifications_dir = Path("./specifications/AMBA-SYM19/")
# specifications_dir = Path("./specifications/SYNTECH15-UNREAL/")
# specifications_dir = Path("./specifications/SYNTECH15-REAL-VAR/")
algorithm = "JVTS"
output_dir = Path("./outputs/")
timeout = 600
repair_limit = -1

# Set MLflow experiment name
experiment_name = f"JVTS-Repair - {specifications_dir.name} - NEW METRICS"
mlflow.set_experiment(experiment_name)

# Collect all .spectra files
spectra_files = [
    f for f in specifications_dir.rglob("*.spectra")
    if "amba08" not in str(f)
    and "amba04_no_safety" not in str(f)
    # and "ColorSort" in str(f)
    # and "Gyro" in str(f)
    # and "Humanoid" in str(f)
    # and "PCar" in str(f) or "Pcar" in str(f)
]

# spectra_files = [
    # Path("specifications/SYNTECH15-UNREAL/HumanoidLTL_503_Humanoid_fixed_unrealizable.spectra"),
    # Path("specifications/SYNTECH15-UNREAL/ColorSortLTLUnrealizable2_791_ColorSort_unrealizable.spectra"),
# ]

spectra_files = sorted(spectra_files)

# Loop through each .spectra file
for spectra_file in spectra_files:
    input_path = spectra_file

    with mlflow.start_run(run_name=spectra_file.stem):
        # Log dataset and parameters
        dataset_name = spectra_file.name
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_param("dataset_path", str(input_path))
        mlflow.log_param("input_file", dataset_name)
        mlflow.log_param("timeout", timeout)
        mlflow.log_param("repair_limit", repair_limit)

        # Build command
        command = [
            "java", "-jar", "spectra/SpecRepair.jar",
            "-i", str(input_path),
            "-a", str(algorithm),
            "-o", str(output_dir),
            "-t", str(timeout),
            "-rl", str(repair_limit),
        ]
        print(" ".join(command))

        mlflow.log_param("command", " ".join(command))

        print(f"Running experiment for {dataset_name}...")

        # Start timing
        start_time = time.time()

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Experiment for {dataset_name} completed successfully.")
            # print(result.stdout)

            # Stop timing
            end_time = time.time()
            time_taken = end_time - start_time

            # Log output artifacts
            output_file_prefix = dataset_name.replace(".spectra", "")
            mlflow.log_artifact(output_dir / f"{output_file_prefix}_jvts_nodes.csv")

            mlflow.log_artifact(output_dir / f"{output_file_prefix}_jvts_stats.csv")

            stats_file = output_dir / f"{output_file_prefix}_jvts_stats.csv"

            # Check if file exists before reading
            if stats_file.exists():
                try:
                    metrics_df = pd.read_csv(stats_file)

                    for column in metrics_df.columns:
                        value = metrics_df[column].values[0]
                        
                        try:
                            # Attempt to convert to float (MLflow only logs numeric values)
                            numeric_value = float(value)
                            mlflow.log_metric(column, numeric_value)
                        except (ValueError, TypeError):
                            print(f"Skipping non-numeric metric: {column} = {value}")
                            mlflow.set_tag(f"non_numeric_{column}", str(value))

                except Exception as e:
                    print(f"Error reading or logging metrics from {stats_file}: {e}")
                    mlflow.set_tag("metric_logging_status", "FAILED")
            else:
                print(f"Metrics file not found: {stats_file}")
                mlflow.set_tag("metric_logging_status", "MISSING")

            log_file = output_dir / f"{output_file_prefix}_run.log"
            with open(log_file, "w") as f:
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\n\nSTDERR:\n")
                f.write(result.stderr)

            # Log the log file to MLflow
            mlflow.log_artifact(log_file)

        except subprocess.CalledProcessError as e:
            print(f"Error running experiment for {dataset_name}: {e}")
            mlflow.log_param("error", e.stderr)
            mlflow.set_tag("mlflow.runStatus", "FAILED")
        
        finally:
            # stop timer regardless of success or error
            end_time = time.perf_counter()
            time_taken = end_time - start_time
            # mlflow.log_metric("time_taken", round(time_taken, 2))
