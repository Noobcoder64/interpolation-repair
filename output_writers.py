import csv
from pathlib import Path

class BaseWriter:
    def __init__(self, output_folder: str, file_name: str, headers: list):
        """
        Base class for writing CSV files.

        :param output_folder: Path to the output folder.
        :param file_name: Name of the CSV file to create.
        :param headers: List of column headers for the CSV file.
        """
        self.output_folder = Path(output_folder)
        self.file_name = self.output_folder / file_name
        self.headers = headers
        self.file = None
        self.writer = None

        # Ensure the output folder exists
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Open the file and write the headers
        self._open_file()

    def _open_file(self):
        """Open the CSV file and write the headers."""
        self.file = open(self.file_name, mode="w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.headers)

    def write_row(self, row: list):
        """Write a single row to the CSV file."""
        if not self.writer:
            raise ValueError("CSV writer is not initialized.")
        self.writer.writerow(row)

    def close(self):
        """Close the CSV file."""
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None

    def __del__(self):
        """Ensure the file is closed when the object is deleted."""
        self.close()

class NodesWriter(BaseWriter):
    def __init__(self, output_folder: str, case_study_name: str):
        super().__init__(
            output_folder=output_folder,
            file_name=f"{case_study_name}_interpolation_nodes.csv",
            headers=[
                "Id",
                "Refinement",
                "ElapsedTime",
                "Timestamp",
                "TimestampRealizabilityCheck",
                "Length",
                "Parent",
                "NumChildren",
                "IsYSat",
                "IsRealizable",
                "IsSatisfiable",
                "IsWellSeparated",
                "IsSolution",
                "TimeYSatCheck",
                "TimeRealizabilityCheck",
                "TimeSatisfiabilityCheck",
                "TimeWellSeparationCheck",
                "TimeCounterstrategy",
                "CounterstrategyNumStates",
                "TimeRefine",
                "TimeGenerationMethod",
                "TimeInterpolation",
                "InterpolantComputed",
                "InterpolantIsFalse",
                "NonStateSeparable",
                "NoInterpolant",
                "NumStateComponents",
                "NumNonIoSeparable",
                "Interpolant",
            ]
        )

class StatsWriter(BaseWriter):
    def __init__(self, output_folder: str, case_study_name: str):
        super().__init__(
            output_folder=output_folder,
            file_name=f"{case_study_name}_interpolation_stats.csv",
            headers=[
                "Filename",
                "NumRepairs",
                "RepairLimit",
                "TimeToFirst",
                "Runtime",
                "Timeout",
                "TimedOut",
                "NodesExplored",
                "DuplicateNodes",
                "NumInterpolantsComputed",
                "NumNonStateSeparable",
            ]
        )
