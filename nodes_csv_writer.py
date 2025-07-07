import csv
from refinement import RefinementNode


class ParamsMetricsCSVWriter:
    def __init__(self, file_path):
        self.filename = file_path
        self.csvfile = open(file_path, mode='w', newline='')
        self.csvwriter = csv.writer(self.csvfile)
        self.csvwriter.writerow([
            "Filename",
            "NumRepairs",
            "NodesExplored",
            "Effectiveness",
            "RepairLimit",
            "TimeToFirst",
            "Runtime",
            "Timeout",
            "TimedOut",
            "DuplicateNodes",
            "NumInterpolantsComputed",
            "NumNonStateSeparable",
        ])

    def write_metrics(self, metrics):
        """
        Write metrics to the CSV file.

        Args:
            metrics: An object or dictionary containing the required metrics.
        """
        self.csvwriter.writerow([
            metrics.get("filename"),
            metrics.get("num_repairs"),
            metrics.get("nodes_explored"),
            metrics.get("effectiveness"),
            metrics.get("repair_limit"),
            metrics.get("time_to_first"),
            metrics.get("runtime"),
            metrics.get("timeout"),
            metrics.get("timed_out"),
            metrics.get("duplicate_nodes"),
            metrics.get("num_interpolants_computed"),
            metrics.get("num_non_state_separable"),
        ])

    def close(self):
        self.csvfile.close()


class NodesCSVWriter:
    def __init__(self, file_path):
        self.filename = file_path
        self.csvfile = open(file_path, mode='w', newline='')
        self.csvwriter = csv.writer(self.csvfile)
        self.csvwriter.writerow([
            "Id",
            "ParentId",
            # "ElapsedTime",
            "Refinement",
            "Length",
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
        ])

    def write_node(self, refinement_node: RefinementNode):
        self.csvwriter.writerow([
            refinement_node.id,
            refinement_node.gr1_units,
            # refinement_node.elapsed_time,
            len(refinement_node.gr1_units),
            refinement_node.parent_id,
            refinement_node.num_refinements_generated,
            refinement_node.is_y_sat,
            refinement_node.is_realizable,
            refinement_node.is_satisfiable,
            refinement_node.is_well_separated,
            refinement_node.is_realizable and refinement_node.is_satisfiable, # DOUBLE CHECK
            refinement_node.time_y_sat_check,
            refinement_node.time_realizability_check,
            refinement_node.time_satisfiability_check,
            refinement_node.time_well_separation_check,
            refinement_node.time_counterstrategy,
            refinement_node.counterstrategy_num_states,
            refinement_node.time_refine,
            refinement_node.time_generation,
            refinement_node.time_interpolation,
            refinement_node.interpolant_computed,
            refinement_node.interpolant_is_false,
            refinement_node.non_state_separable,
            refinement_node.no_interpolant,
            refinement_node.num_state_components,
            refinement_node.num_non_io_separable,
            refinement_node.interpolant,
        ])

    def close(self):
        self.csvfile.close()
