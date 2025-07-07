import io_utils as io
import timeit
import os
import specification as sp
from pathlib import Path

class InitialSpec:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = Path(file_path).stem
        self.lines = None
        self.input_vars = None
        self.output_vars = None
        self.all_vars = None
        self.assumptions = None
        self.guarantees = None
        
        self._parse_specification()

    def _parse_specification(self):
        # Read the file and parse it using the specification module
        self.lines = sp.read_file(self.file_path)
        self.lines = sp.interpolation_spec(self.lines)
        
        # Extract the input, output, assumptions, and guarantees
        self.input_vars = io.extractInputVariablesFromFile(self.lines)
        self.output_vars = io.extractOutputVariablesFromFile(self.lines)
        self.all_vars = self.input_vars + self.output_vars
        self.assumptions = io.extractAssumptionList(self.lines)
        self.guarantees = io.extractGuaranteesList(self.lines)
    
    def __str__(self):
        spec_str = f"----------------------------\n   SPECIFICATION: {self.name}\n----------------------------\n\n"

        spec_str += "### INPUT VARIABLES ###\n"
        if self.input_vars:
            spec_str += "\n".join([f"- {var}" for var in self.input_vars]) + "\n"
        else:
            spec_str += "- No input variables found.\n"

        spec_str += "\n### OUTPUT VARIABLES ###\n"
        if self.output_vars:
            spec_str += "\n".join([f"- {var}" for var in self.output_vars]) + "\n"
        else:
            spec_str += "- No output variables found.\n"

        spec_str += "\n### ASSUMPTIONS ###\n"
        if self.assumptions:
            spec_str += "\n".join([f"- {asm}" for asm in self.assumptions]) + "\n"
        else:
            spec_str += "- No assumptions found.\n"

        spec_str += "\n### GUARANTEES ###\n"
        if self.guarantees:
            spec_str += "\n".join([f"- {gar}" for gar in self.guarantees]) + "\n"
        else:
            spec_str += "- No guarantees found.\n"

        spec_str += "----------------------------\n"
        return spec_str


class RepairConfig:
    def __init__(
        self,
        spectra_file_path: str,
        output_folder: str = None,
        timeout: int = 600,
        repair_limit: int = -1,
        generation_method: str = "interpolation",
        search_method: str = "bfs",
        minimize_spec: bool = True,
        use_influential: bool = True,
        use_all_gars: bool = False,
    ):
        """
        Initializes the RepairConfig instance with the provided parameters.
        If no parameters are provided, default values are used.
        
        spectra_file_path: Path to the spectra file used for configuration (required).
        """
        # Check that spectra_file_path is provided
        if not spectra_file_path:
            raise ValueError("spectra_file_path is a required argument")
        
        # Initialize instance variables
        self.case_study_name = Path(spectra_file_path).stem
        self.output_folder = Path(output_folder) if output_folder else Path.cwd()
        
        if timeout < 0:
            raise ValueError("Timeout must be a non-negative value.")
        
        if repair_limit < -1:
            raise ValueError("Repair limit must be -1 (unlimited) or a positive integer.")
        
        # Assign values to the instance variables
        self.timeout = timeout
        self.repair_limit = repair_limit
        self.generation_method = generation_method
        self.search_method = search_method
        self.minimize_spec = minimize_spec
        self.use_influential = use_influential
        self.use_all_gars = use_all_gars

    def __str__(self):
        """
        Return a string representation of the current config in a readable format.
        """
        return (
            f"Repair Configuration:\n"
            f"---------------------------\n"
            f"Case Study Name     : {self.case_study_name}\n"
            f"Output Folder       : {self.output_folder}\n"
            f"Timeout             : {self.timeout}s\n"
            f"Repair Limit        : {self.repair_limit}\n"
            f"Generation Method   : {self.generation_method}\n"
            f"Search Method       : {self.search_method}\n"
            f"Minimize Spec       : {'Yes' if self.minimize_spec else 'No'}\n"
            f"Use Influential     : {'Yes' if self.use_influential else 'No'}\n"
            f"Use All GARS        : {'Yes' if self.use_all_gars else 'No'}\n"
            f"---------------------------\n"
        )


class OutputWriter:
    

    def __init__(self, output_folder: str):
        """
        Initializes the OutputWriter instance with the provided output folder.
        Generates default file paths based on the configuration.
        """
        self.output_folder = Path(output_folder) if output_folder else Path.cwd()
        self.stats_file_path = {}
        self._generate_default_paths()

    def _generate_default_paths(self):
        """Generate default file paths based on the configuration."""
        refinement_method = f"{self.generation_method}-{self.search_method}"
        self.file_paths = {
            "datafile": self.output_folder / f"{self.case_study_name}_interpolation_nodes.csv",
            "statsfile": self.output_folder / f"{self.case_study_name}_interpolation_stats.csv",
        }

    def get_file_path(self, key: str) -> Path:
        """Retrieve a file path by its key."""
        if key not in self.file_paths:
            raise KeyError(f"File path for key '{key}' does not exist.")
        return self.file_paths[key]

    def add_file_path(self, key: str, file_name: str) -> None:
        """Add a custom file path."""
        self.file_paths[key] = self.output_folder / file_name

    def __repr__(self) -> str:
        return (
            f"OutputConfig("
            f"case_study_name={self.case_study_name}, "
            f"output_folder={self.output_folder}, "
            f"generation_method={self.generation_method}, "
            f"search_method={self.search_method}, "
            f"file_paths={self.file_paths})"
        )
    

initial_spec= None
repair_config = None
output_config = None