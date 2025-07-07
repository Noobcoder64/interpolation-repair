import re
import spectra_utils as spectra
from counterstrategy import Counterstrategy, CounterstrategyState
from specification import spectra_format

class SpectraSpecification:
    def __init__(self, name="Unnamed", inputs=None, outputs=None, assumptions=None, guarantees=None):
        self.file_path = None
        self.text = None
        self.lines = []
        self.name = name
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.assumptions = assumptions or []
        self.guarantees = guarantees or []

    @classmethod
    def from_text(cls, text):
        """
        Alternate constructor to initialize a SpectraSpecification from text.

        :param text: Text of the specification.
        :return: An instance of SpectraSpecification.
        """
        instance = cls()
        instance.text = text
        instance._parse_spec()
        return instance

    @classmethod
    def from_lines(cls, lines):
        """
        Alternate constructor to initialize a SpectraSpecification from lines.

        :param lines: List of lines representing the specification.
        :return: An instance of SpectraSpecification.
        """
        text = ''.join(lines)
        instance = cls.from_text(text)
        instance.lines = lines
        return instance

    @classmethod
    def from_file(cls, file_path):
        """
        Alternate constructor to initialize a SpectraSpecification from a file.

        :param file_path: Path to the specification file.
        :return: An instance of SpectraSpecification.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
        instance = cls.from_lines(lines)
        instance.file_path = file_path
        return instance

    def to_lines(self, use_alw=False):
        """
        Prepare the specification in Spectra format as a list of lines.
        If self.lines is already set, return it directly.
        """
        # Otherwise, generate the lines
        lines = [f"module {self.name}\n"]
        lines.append("\n")

        # Add inputs
        for input in self.inputs:
            lines.append(f"env boolean {input};\n")
        lines.append("\n")

        # Add outputs
        for output in self.outputs:
            lines.append(f"sys boolean {output};\n")
        lines.append("\n")

        # Add assumptions
        assumptions = spectra_format(self.assumptions) if use_alw else self.assumptions
        for assumption in assumptions:
            lines.append("assumption\n")
            lines.append(f"\t{assumption};\n")
        lines.append("\n")

        # Add guarantees
        guarantees = spectra_format(self.guarantees) if use_alw else self.guarantees
        for guarantee in guarantees:
            lines.append("guarantee\n")
            lines.append(f"\t{guarantee};\n")
        # lines.append("\n")

        self.lines = lines
        return self.lines

    def to_text(self, use_alw=False):
        """
        Convert the specification to a textual format.
        If self.text is already set, return it directly.
        """
        # Otherwise, generate the text from lines
        self.text = ''.join(self.to_lines(use_alw))
        return self.text

    def to_file(self, file_path, use_alw=False):
        """
        Write the Spectra specification to a file.

        :param file_path: Path to the output file.
        """
        with open(file_path, 'w') as file:
            file.write(self.to_text(use_alw))
        self.file_path = file_path
        return self.file_path

    def is_realizable(self, timeout=600):
        """
        Check if the specification is realizable using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        return spectra.check_realizability(self.file_path, timeout)

    def is_satisfiable(self):
        """
        Check if the specification is satisfiable using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        return spectra.check_satisfiability(self.file_path)

    def is_y_sat(self):
        """
        Check if the specification is Y-satisfiable using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        return spectra.check_y_sat(self.file_path)

    def is_well_separated(self):
        """
        Check if the specification is well-separated using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        return spectra.check_well_separation(self.file_path)

    def compute_unrealizable_core(self):
        """
        Compute the unrealizable core of the specification using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        line_nums = spectra.compute_unrealizable_core(self.file_path)
        return [self.lines[i].strip().rstrip(';') for i in line_nums]

    def compute_assumptions_core(self):
        """
        Compute the assumptions core of the specification using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")
        line_nums = spectra.compute_assumptions_core(self.file_path)
        return [self.lines[i].strip().rstrip(';') for i in line_nums]

    def compute_counterstrategy(self, min_out_vars=True, timeout=600):
        """
        Compute a counterstrategy for the specification using spectra_utils.
        """
        if not self.file_path:
            raise ValueError("File path is not set. Save the specification to a file first.")

        cs_text = spectra.compute_counterstrategy(self.file_path, min_out_vars, timeout)
        return self._parse_counterstrategy(cs_text)

    def _parse_spec(self):
        """Parse the entire specification by delegating to specific parsing functions."""
        self._parse_module_name()
        self._parse_inputs()
        self._parse_outputs()
        self._parse_assumptions()
        self._parse_guarantees()

    def _parse_module_name(self):
        """Parse the module name from the specification."""
        match = re.search(r'module\s+(\w+)', self.text)
        self.name = match.group(1) if match else 'Unnamed'

    def _parse_inputs(self):
        """Parse the input variables from the specification."""
        input_pattern = re.compile(r'(?:env)\s+boolean\s+(\w+)\s*;', re.IGNORECASE)
        self.inputs = input_pattern.findall(self.text)

    def _parse_outputs(self):
        """Parse the output variables from the specification."""
        output_pattern = re.compile(r'(?:sys|aux)\s+boolean\s+(\w+)\s*;', re.IGNORECASE)
        self.outputs = output_pattern.findall(self.text)

    def _parse_assumptions(self):
        """Parse the assumptions from the specification."""
        assumption_pattern = re.compile(r'(?:assumption|asm)\s+(.*?)\s*;', re.IGNORECASE | re.DOTALL)
        self.assumptions = assumption_pattern.findall(self.text)

    def _parse_guarantees(self):
        """Parse the guarantees from the specification."""
        guarantee_pattern = re.compile(r'(?:guarantee|gar)\s+(.*?)\s*;', re.IGNORECASE | re.DOTALL)
        self.guarantees = guarantee_pattern.findall(self.text)

    def _parse_counterstrategy(self, text):
        """
        Create a Counterstrategy instance from raw text.

        :param text: The raw counterstrategy text.
        :param input_vars: List of input variable names.
        :param output_vars: List of output variable names.
        :param use_influential: Whether to compute influential outputs.
        :return: An instance of Counterstrategy.
        """
        state_pattern = re.compile(r"(Initial )?(Dead )?State (\w+) <(.*?)>\s+With (?:no )?successors(?: : |.)(.*)(?:\n|$)")
        assignment_pattern = re.compile(r"(\w+):(\w+)")

        states = {}
        state_matches = re.finditer(state_pattern, text)

        for match in state_matches:
            is_initial = match.group(1) is not None
            is_dead = match.group(2) is not None
            state_name = match.group(3)
            vars = dict(re.findall(assignment_pattern, match.group(4)))

            inputs = {x: vars[x] == "true" for x in self.inputs}
            outputs = {y: vars[y] == "true" for y in self.outputs if y in vars}
            successors = match.group(5).split(", ") if match.group(5) else []

            state = CounterstrategyState(state_name, inputs, outputs, successors, is_initial, is_dead)
            states[state.name] = state

        return Counterstrategy(states)

    def copy(self):
        return SpectraSpecification(
            name=self.name,
            inputs=list(self.inputs),
            outputs=list(self.outputs),
            assumptions=list(self.assumptions),
            guarantees=list(self.guarantees),
        )
