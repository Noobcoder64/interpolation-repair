import re

# TODO: Separate patterns

class GR1Specification:
    def __init__(self, text):
        self.file_path = None
        self.text = text
        self.name = None
        self.inputs = []
        self.outputs = []
        self.init_assumptions = []
        self.invariant_assumptions = []
        self.fairness_assumptions = []
        self.init_guarantees = []
        self.invariant_guarantees = []
        self.fairness_guarantees = []
        self._parse_spec()

    @classmethod
    def from_file(self, file_path):
        """
        Alternate constructor to initialize a GR1Specification from a file.

        :param file_path: Path to the specification file.
        :return: An instance of GR1Specification.
        """
        self.file_path = file_path
        with open(file_path, 'r') as file:
            text = file.read()
        return self(text)

    def _interpolation_format(self, lines):
        lines = [re.sub(r"GF\s*(.*)", r"G(F(\1))", line) for line in lines]
        lines = [re.sub(r'(\w+)=true', r'\1', x) for x in lines]
        lines = [re.sub(r'(\w+)=false', r'!\1', x) for x in lines]
        lines = [re.sub(r'next\s*\(([^\)]*)\)=true', r'next(\1)', x) for x in lines]
        lines = [re.sub(r'next\s*\(([^\)]*)\)=false', r'next(!\1)', x) for x in lines]
        lines = [re.sub(r"next\s*\(", "X(", line) for line in lines]
        return lines

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
        if match:
            self.name = match.group(1)
        else:
            self.name = 'Unnamed'

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
        assumptions = assumption_pattern.findall(self.text)
        assumptions = self._interpolation_format(assumptions)

        for assumption in assumptions:
            assumption = assumption.strip()
            if re.search(r'G\s*\(\s*F\s*\(', assumption):
                self.fairness_assumptions.append(assumption)
            elif re.search(r'G\s*\(', assumption):
                self.invariant_assumptions.append(assumption)
            else:
                self.init_assumptions.append(assumption)
        

    def _parse_guarantees(self):
        """Parse the guarantees from the specification."""
        guarantee_pattern = re.compile(r'(?:guarantee|gar)\s+(.*?)\s*;', re.IGNORECASE | re.DOTALL)
        guarantees = guarantee_pattern.findall(self.text)
        guarantees = self._interpolation_format(guarantees)

        for guarantee in guarantees:
            guarantee = guarantee.strip()
            if re.search(r'G\s*\(\s*F\s*\(', guarantee):
                self.fairness_guarantees.append(guarantee)
            elif re.search(r'G\s*\(', guarantee):
                self.invariant_guarantees.append(guarantee)
            else:
                self.init_guarantees.append(guarantee)

    def add_assumptions(self, assumptions):
        """
        Add assumptions to the GR(1) specification.

        :param assumption: Assumption to add.
        """
        for assumption in assumptions:
            assumption = assumption.strip()
            if re.search(r'G\s*\(\s*F\s*\(', assumption):
                self.fairness_assumptions.append(assumption)
            elif re.search(r'G\s*\(', assumption):
                self.invariant_assumptions.append(assumption)
            else:
                self.init_assumptions.append(assumption)

    def _spectra_format(self, lines):
        """
        Transform assumptions and guarantees into the Spectra format.

        :param spec: List of assumptions or guarantees.
        :return: Transformed list in Spectra format.
        """
        # lines = [re.sub(r"G\(F(\(.*\))\)", r"GF \1", line) for line in lines]
        # lines = [re.sub(r"X\(", r"next(", line) for line in lines]
        return lines

    def to_spectra(self):
        # Prepare the specification in Spectra format
        lines = [f"module {self.name}\n\n"]

        # Add inputs
        for input in self.inputs:
            lines.append(f"env boolean {input};\n")
        lines.append("\n")

        # Add outputs
        for output in self.outputs:
            lines.append(f"sys boolean {output};\n")
        lines.append("\n")

        # Add assumptions
        for assumption in self._spectra_format(self.init_assumptions):
            lines.append(f"assumption\n\t{assumption};\n")
        for assumption in self._spectra_format(self.invariant_assumptions):
            lines.append(f"assumption\n\t{assumption};\n")
        for assumption in self._spectra_format(self.fairness_assumptions):
            lines.append(f"assumption\n\t{assumption};\n")
        lines.append("\n")

        # Add guarantees
        for guarantee in self._spectra_format(self.init_guarantees):
            lines.append(f"guarantee\n\t{guarantee};\n")
        for guarantee in self._spectra_format(self.invariant_guarantees):
            lines.append(f"guarantee\n\t{guarantee};\n")
        for guarantee in self._spectra_format(self.fairness_guarantees):
            lines.append(f"guarantee\n\t{guarantee};\n")
        lines.append("\n")

        return "".join(lines)

    def to_spectra_file(self, file_path):
        """
        Write the GR(1) specification to a file in the Spectra format.

        :param file_path: Path to the output file.
        """
        spectra_text = self.to_spectra()
        with open(file_path, 'w') as file:
            file.write(spectra_text)

    def __str__(self):
        """Construct a string representation of the GR(1) specification."""
        spec_str = f"GR(1) Specification: {self.name}\n"
        spec_str += "=" * 50 + "\n"
        spec_str += f"Inputs:    {len(self.inputs)}\n"
        spec_str += f"Outputs:   {len(self.outputs)}\n"
        spec_str += "-" * 50 + "\n"
        spec_str += "Assumptions:\n"
        spec_str += f"  Initial:   {len(self.init_assumptions)}\n"
        spec_str += f"  Invariant: {len(self.invariant_assumptions)}\n"
        spec_str += f"  Fairness:  {len(self.fairness_assumptions)}\n"
        spec_str += "-" * 50 + "\n"
        spec_str += "Guarantees:\n"
        spec_str += f"  Initial:   {len(self.init_guarantees)}\n"
        spec_str += f"  Invariant: {len(self.invariant_guarantees)}\n"
        spec_str += f"  Fairness:  {len(self.fairness_guarantees)}\n"
        spec_str += "=" * 50 + "\n"
        return spec_str

# Example usage
if __name__ == "__main__":
    spec_text = """
    module Lift

    env boolean b1;
    env boolean b2;
    env boolean b3;

    sys boolean f1;
    sys boolean f2;
    sys boolean f3;

    assumption
        (((!(b1) & !(b2)) & !(b3)));
    assumption
        G (((b1 & f1) -> !(next(b1))));
    assumption
        G (((b2 & f2) -> !(next(b2))));
    assumption
        G (((b3 & f3) -> !(next(b3))));
    assumption
        G (((b1 & !(f1)) -> next(b1)));
    assumption
        G (((b2 & !(f2)) -> next(b2)));
    assumption
        G (((b3 & !(f3)) -> next(b3)));

    guarantee
        (((f1 & !(f2)) & !(f3)));
    guarantee
        G (((!((f1 & f2)) & !((f1 & f3))) & !((f2 & f3))));
    guarantee
        G ((f1 -> next(f1 | f2)));
    guarantee
        G ((f2 -> next(f1 | f2 | f3)));
    guarantee
        G ((f3 -> next(f2 | f3)));
    guarantee
        G ((((((f1 & next(f2)) | (f2 & next(f3))) | (f2 & next(f1))) | (f3 & next(f2))) -> ((b1 | b2) | b3)));
    guarantee
        GF ((b1 -> f1));
    guarantee
        GF ((b2 -> f2));
    guarantee
        GF ((b3 -> f3));
    guarantee
        GF (f1);
    guarantee
        GF (f2);
    guarantee
        GF (f3);
    """

    spec = GR1Specification(spec_text)
    print(spec)  # Prints the specification in the desired format
