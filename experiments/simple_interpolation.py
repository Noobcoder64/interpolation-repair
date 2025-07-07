import os
import subprocess
import mlflow

mlflow.set_tracking_uri("sqlite:///mlruns/mlruns.db")

# mlflow ui --backend-store-uri sqlite:///mlruns/mlruns.db

specifications_dir = "./specifications/SIMPLE/"

spectra_files = [f for f in os.listdir(specifications_dir) if f.endswith("Lift.spectra")]

output_dir = "./outputs/"

timeout = 600

repair_limit = -1

# MLflow experiment name
experiment_name = "SIMPLE Interpolation"

# Set the MLflow experiment
mlflow.set_experiment(experiment_name)

# Loop over each .spectra file and run the experiment
for spectra_file in spectra_files:
    input_path = os.path.join(specifications_dir, spectra_file)

    # Start a new MLflow run for this experiment
    with mlflow.start_run():

        # Log dataset as a parameter
        dataset_name = spectra_file  # or you could use the base name of the file
        mlflow.log_param("dataset", dataset_name)
        mlflow.log_param("dataset_path", input_path)

        # Log parameters
        mlflow.log_param("input_file", spectra_file)
        mlflow.log_param("timeout", timeout)
        mlflow.log_param("repair_limit", repair_limit)

        # Define the command
        command = [
            "python", "interpolation_repair.py",
            "-i", input_path,
            "-o", output_dir,
            "-t", str(timeout),
            "-rl", str(repair_limit)
        ]
        print(command)

        # Run the experiment for the current file
        print(f"Running experiment for {spectra_file}...")
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Experiment for {spectra_file} completed successfully.")
            print(result.stdout)

            # Log the output (stdout or any artifact)
            mlflow.log_artifact(f"{output_dir}{spectra_file.replace('.spectra', '_interpolation_nodes.csv')}")
            mlflow.log_artifact(f"{output_dir}{spectra_file.replace('.spectra', '_interpolation_params_metrics.csv')}")
            # mlflow.log_artifact(f"{output_dir}/stdout.log")

            mlflow.log_metric("time_taken", 200)

        except subprocess.CalledProcessError as e:
            print(f"Error running experiment for {spectra_file}: {e}")
            mlflow.log_param("error", e.stderr)
