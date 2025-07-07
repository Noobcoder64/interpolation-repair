import sys
import os
import argparse
from collections import deque
import experiment_properties as exp
# from gr1_specification import GR1Specification
from spectra_specification import SpectraSpecification
from config import InitialSpec, RepairConfig, OutputWriter
from refinement import RefinementNode
import csv
import spectra_utils as spectra
import random
from typing import List, Dict, Any
from nodes_csv_writer import NodesCSVWriter, ParamsMetricsCSVWriter
import time
import pandas as pd
from pathlib import Path
import re
import spot
import specification as sp
import shutil
import logging
import statistics

logging.basicConfig(level=logging.INFO)

TEMP_DIR = "temp"

varpattern = re.compile(r"\b(?!TRUE|FALSE)\w+")

def get_distinct_vars(formula):
    """Returns the set of all distinct variables appearing in formula"""
    if isinstance(formula, list):
        formula = " ".join(formula)
    varset = set(varpattern.findall(formula))
    varset.discard("X")
    varset.discard("G")
    varset.discard("F")
    varset.discard("next")
    varset.discard("alw")
    varset.discard("alwEv")
    return varset

def implies(phi, psi):
    # Build the negation of (phi implies psi), i.e., phi ∧ ¬psi
    implication_neg = spot.formula(f"({phi}) & !({psi})")
    # Build the automaton from this formula
    aut = spot.translate(implication_neg)
    # If the language is empty, phi implies psi
    return aut.is_empty()

class InterpolationRepair:
    def __init__(
            self,
            initial_spec: SpectraSpecification,
            output_dir: str = "outputs",
            timeout: int = 600,
            repair_limit: int = -1,
            temp_dir: str = "temp",
            verbose: int = 0,
    ):
        self.initial_spec = initial_spec
        self.output_dir = output_dir
        self.timeout = timeout
        self.repair_limit = repair_limit
        self.temp_dir = temp_dir
        self.verbose = verbose

        # Results placeholders
        self.node_records = []
        self.solutions = []
        self.first_repair = None
        self.nodes_to_first_repair = None
        self.depth_to_first_repair = None
        self.time_to_first_repair = None
        self.length_first_repair = None
        self.vars_first_repair = None
        self.non_redundant_repairs = None
        self.runtime = None

    def run(self):
        self._counterstrategy_guided_refinement()
        self._compute_non_redundant_repairs()
        self._log_summary()
        self._save_nodes_csv()
        self._save_stats_csv()

    def _log(self, level, message, *args, **kwargs):
        if self.verbose >= level:
            print(message, *args, **kwargs)

    def _counterstrategy_guided_refinement(self):
        self._log(1, "\nStarting Counterstrategy Guided Refinement")
        self._log(1, "------------------------------------------")
        self._log(1, f"Repairing specification : {self.initial_spec.file_path}")
        self._log(1, f"Timeout                 : {self.timeout} seconds")
        self._log(1, f"Repair Limit            : {self.repair_limit if self.repair_limit > 0 else 'No Limit'}\n")

        start_time = time.perf_counter()
        initial_node = RefinementNode()
        refinement_queue = deque([initial_node])
        num_iterations = 0

        while refinement_queue \
            and not (self.repair_limit > 0 \
            and len(self.solutions) == self.repair_limit):

            elapsed_time = time.perf_counter() - start_time
            if elapsed_time >= self.timeout:
                self._log(1, f"Timeout reached: {elapsed_time:.2f}s >= {self.timeout}s")
                break

            time_node_start = time.perf_counter()
            num_iterations += 1

            cur_node = refinement_queue.pop()
            depth = len(cur_node.gr1_units)
            error = None

            self._log(2, f"\nIteration #{num_iterations}")
            self._log(2, "----------------------------")
            self._log(2, f"Elapsed Time        : {elapsed_time * 1000:.0f} ms")
            self._log(2, f"Queue Size          : {len(refinement_queue)}")
            self._log(2, f"Depth               : {depth}")
            self._log(2, f"Processing Node ID  : {cur_node.id}")
            self._log(2, f"Current Refinement  : {cur_node.gr1_units}\n")
            
            self._create_refined_spec(cur_node)

            try:
                remaining_time = int(self.timeout - elapsed_time)

                if cur_node.isYSat():
                    self._log(2, "Specification is y-satisfiable")

                    if not cur_node.isRealizable(timeout=remaining_time):
                        self._log(2, "Specification is unrealizable")

                        self._log(2, "Computing unrealizable core...", end='', flush=True)
                        cur_node.getUnrealizableCore()
                        self._log(2, " done")

                        cur_node.minimiseSpec()
                        core_spec_path = f"{self.temp_dir}/{cur_node.id}_core.spectra"
                        cur_node.spec.to_file(core_spec_path, use_alw=True)
                        self._log(2, f"Minimised specification saved to: {core_spec_path}")

                        self._log(2, "Computing counterstrategy...", end='', flush=True)
                        cur_node.getCounterstrategy(timeout=remaining_time)
                        self._log(2, " done")

                        candidate_ref_nodes = cur_node.generateRefinedNodes()
                        self._log(2, f"Generated {len(candidate_ref_nodes)} candidate refinements")

                        refinement_queue.extendleft(candidate_ref_nodes)

                    else:
                        self._log(2, "Specification is realizable")
                        cur_node.isSatisfiable()
                        cur_node.isWellSeparated()

                        before_repair_core = len(cur_node.gr1_units)
                        cur_node.getRepairCore()
                        # Store in node?
                        num_redundant_assumptions = before_repair_core - len(cur_node.gr1_units)
                        self._log(2, f"Found {num_redundant_assumptions} redundant assumptions with repair core")

                        if self.first_repair is None:
                            self._log(1, "\n*** FIRST REPAIR FOUND ***\n")
                            self._record_first_repair(
                                cur_node.gr1_units,
                                num_iterations,
                                depth,
                                time.perf_counter() - start_time,
                            )

                        self.solutions.append(cur_node.gr1_units)

                else:
                    self._log(2, "Specification is NOT y-satisfiable")

            except Exception as e:
                error = f"{type(e).__name__}: {e}"
                self._log(1, error)

            # self._record_node()
            self._record_node(
                cur_node,
                elapsed_time * 1000,
                len(refinement_queue),
                depth,
                time.perf_counter() - time_node_start,
                error
            )
        
        self.runtime = time.perf_counter() - start_time

        return self

    def _create_refined_spec(self, node: RefinementNode):
        refined_spec = SpectraSpecification(
            name=self.initial_spec.name,
            inputs=self.initial_spec.inputs,
            outputs=self.initial_spec.outputs,
            assumptions=self.initial_spec.assumptions + node.gr1_units,
            guarantees=self.initial_spec.guarantees,
        )
        refined_spec_path = f"{self.temp_dir}/{node.id}.spectra"
        refined_spec.to_file(refined_spec_path)
        node.set_spec(refined_spec)
        self._log(2, f"Refined specification saved to: {refined_spec_path}")

    def _record_node(self, node: RefinementNode, time, queue_size, depth, time_node, error):
        node_record =  {
            "node_id": node.id,
            "parent_node_id": node.parent_id,
            "elapsed_time": time,
            "queue_size": queue_size,
            "depth": depth,
            "length": len(node.gr1_units),
            "num_vars": len(get_distinct_vars(" ".join(node.gr1_units))),
            "is_y_sat": node.isYSat(),
            "is_satisfiable": node.isSatisfiable(),
            "is_realizable": node.isRealizable(),
            "is_well_separated": node.isWellSeparated(),
            "unreal_core_size": len(node.unreal_core) if node.unreal_core else None,
            "cs_num_states": len(node.counterstrategy.states) if node.counterstrategy else None,
            "is_interpolant_state_separable": node.is_interpolant_state_separable,
            "num_state_components": node.num_state_components,
            "num_non_io_separable_state_components": node.num_non_io_separable_state_components,
            "is_interpolant_fully_separable": node.is_interpolant_fully_separable,
            "num_refs_generated": node.num_refs_generated,
            "time_y_sat_check": node.time_y_sat_check,
            "time_realizability_check": node.time_realizability_check,
            "time_satisfiability_check": node.time_satisfiability_check,
            "time_well_separation_check": node.time_well_separation_check,
            "time_unreal_core": node.time_unreal_core,
            "time_counterstrategy": node.time_counterstrategy,
            "time_interpolation": node.time_interpolation,
            "time_generation": node.time_generation,
            "time_refine": node.time_refine,
            "time_repair_core": node.time_repair_core,
            "time_node": time_node,
            "refinement": node.gr1_units,
            "interpolant": node.interpolant,
            "error": error,
        }
        self.node_records.append(node_record)

    def _record_first_repair(self, repair, num_iterations, depth, time):
        self.first_repair = repair
        self.nodes_to_first_repair = num_iterations
        self.depth_to_first_repair = depth
        self.time_to_first_repair = time
        self.length_first_repair = len(repair)
        self.vars_first_repair = len(get_distinct_vars(repair))

    def _log_summary(self):
        self._log(1, "\n=== Refinement Summary ===")
        self._log(1, f"Total repairs found       : {len(self.solutions)}")
        self._log(1, f"Nodes explored            : {len(self.node_records)}")
        # self._log(1, f"Time elapsed              : {self.runtime:.2f} seconds")
        if self.first_repair:
            self._log(1, f"Time to first repair      : {self.time_to_first_repair:.2f} seconds")
        else:
            self._log(1, "No repairs found.")
        self._log(1, "==========================\n")

    def _compute_non_redundant_repairs(self):
        self._log(1, "Computing non-redundant repairs...")
        self.non_redundant_repairs = []
        for sol in [" & ".join(sp.unspectra(sol)) for sol in self.solutions]:
            if any(implies(sol, repair) for repair in self.non_redundant_repairs):
                continue
            self.non_redundant_repairs = [repair for repair in self.non_redundant_repairs if not implies(repair, sol)]
            self.non_redundant_repairs.append(sol)
        self._log(1, f"Found {len(self.non_redundant_repairs)} non-redundant repair(s) out of {len(self.solutions)} total repairs")

    def _save_nodes_csv(self):
        self._log(1, "Saving node data to CSV...")
        nodes_df = pd.DataFrame(self.node_records)
        nodes_csv_path = f"{self.output_dir}/{Path(self.initial_spec.file_path).stem}_interpolation_nodes.csv"
        nodes_df.to_csv(nodes_csv_path, index=False)
        self._log(1, f"Node data successfully saved at: {nodes_csv_path}\n")

    def _save_stats_csv(self):
        self._log(1, "Saving search summary data")

        nodes_df = pd.DataFrame(self.node_records)
        stats_csv_path = f"{self.output_dir}/{Path(self.initial_spec.file_path).stem}_interpolation_stats.csv"

        num_nodes_explored = len(nodes_df)

        stats_record = {
            "file_path": self.initial_spec.file_path,
            "timeout": self.timeout,
            "repair_limit": self.repair_limit,

            "num_repairs": len(self.solutions),
            "num_non_redundant_repairs": len(self.non_redundant_repairs),
            "num_nodes_explored": num_nodes_explored,
            "effectiveness": (len(self.non_redundant_repairs) / (num_nodes_explored - 1)) if num_nodes_explored > 1 else 0,
            "num_y_unsat": (nodes_df["is_y_sat"] == False).sum(),
            "max_depth": nodes_df["depth"].max(),
            "num_not_state_separable": (nodes_df["is_interpolant_state_separable"] == False).sum(),
            "num_not_fully_separable": (nodes_df["is_interpolant_fully_separable"] == False).sum(),
            "num_errors": nodes_df["error"].notnull().sum(),

            "nodes_to_first_repair": self.nodes_to_first_repair,
            "depth_to_first_repair": self.depth_to_first_repair,
            "time_to_first_repair": self.time_to_first_repair,
            "length_first_repair": self.length_first_repair,
            "vars_first_repair": self.vars_first_repair,
        }

        repair_lengths = [len(r) for r in self.non_redundant_repairs]
        repair_vars_counts = [len(get_distinct_vars(r)) for r in self.non_redundant_repairs]

        stats_record.update({
            "min_repair_length": min(repair_lengths) if repair_lengths else None,
            "avg_repair_length": statistics.mean(repair_lengths) if repair_lengths else None,
            "max_repair_length": max(repair_lengths) if repair_lengths else None,

            "min_repair_vars": min(repair_vars_counts) if repair_vars_counts else None,
            "avg_repair_vars": statistics.mean(repair_vars_counts) if repair_vars_counts else None,
            "max_repair_vars": max(repair_vars_counts) if repair_vars_counts else None,
        })

        num_fields = [
            "unreal_core_size",
            "cs_num_states",
            # interpolant_size
            "num_state_components",
            "num_non_io_separable_state_components",
            "num_refs_generated"
        ]

        for metric in num_fields:
            stats_record[f"min_{metric}"] = nodes_df[metric].min()
            stats_record[f"avg_{metric}"] = nodes_df[metric].mean()
            stats_record[f"max_{metric}"] = nodes_df[metric].max()

        time_fields = [
            "time_y_sat_check", "time_realizability_check", "time_satisfiability_check",
            "time_well_separation_check",  "time_unreal_core", "time_counterstrategy", "time_interpolation",
            "time_generation", "time_refine", "time_repair_core", "time_node"
        ]

        for field in time_fields:
            stats_record[f"avg_{field}"] = nodes_df[field].mean()

        stats_record["runtime"] = self.runtime

        for field in time_fields:
            stats_record[f"total_{field}"] = nodes_df[field].sum()

        for field in time_fields:
            stats_record[f"pct_{field}"] = 100 * stats_record[f"total_{field}"] / self.runtime

        df = pd.DataFrame([stats_record])
        df.to_csv(stats_csv_path, index=False)
        self._log(1, "Stats saved to:", stats_csv_path)


def main():
    parser = argparse.ArgumentParser(description="Run interpolation_repair.py on a .spectra file.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input .spectra file")
    parser.add_argument("-o", "--output", default=os.getcwd(), help="Path to the output folder (default: current directory)")
    parser.add_argument("-t", "--timeout", type=int, default=600, help="Timeout in seconds (default: 600 seconds)")
    parser.add_argument("-rl", "--repair-limit", type=int, default=-1, help="Repair limit (default: -1)")
    # TODO: Find better flag names
    parser.add_argument("-allgars", action="store_true", help="Use all guarantees")
    parser.add_argument("-min", action="store_true", help="Minimize specification")
    parser.add_argument("-inf", action="store_true", help="Use influential output variables")

    if os.path.exists(TEMP_DIR):
        print(f"Clearing existing temp folder: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    print(f"Created temp folder: {TEMP_DIR}")
    print()

    args = parser.parse_args()

    input_file_path = Path(args.input)

    print(f"Reading initial specification from: {input_file_path}...")
    initial_spec = SpectraSpecification.from_file(input_file_path)

    temp_path = Path("temp") / input_file_path.name
    initial_spec.to_file(str(temp_path))
    print(f"Initial specification copied to: {temp_path}")

    print()
    print("Specification summary")
    print("---------------------")
    print(f"Name        : {initial_spec.name}")
    print(f"Inputs      : {len(initial_spec.inputs)}")
    print(f"Outputs     : {len(initial_spec.outputs)}")
    print(f"Assumptions : {len(initial_spec.assumptions)}")
    print(f"Guarantees  : {len(initial_spec.guarantees)}")
    print(f"Lines       : {len(initial_spec.lines)}")
    print()

    if initial_spec.is_realizable(args.timeout):
        print("Specification is already realizable. No repair needed.\n")
        return
    
    if not initial_spec.is_y_sat():
        print("Adding assumptions will NOT fix this specification.\n")
        return

    ir = InterpolationRepair(
        initial_spec,
        output_dir=args.output,
        timeout=args.timeout,
        repair_limit=args.repair_limit,
        verbose=2,
    )
    ir.run()


if __name__=="__main__":
    main()
