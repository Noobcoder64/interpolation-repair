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

logging.basicConfig(level=logging.INFO)

TEMP_DIR = "temp"

varpattern = re.compile(r"\b(?!TRUE|FALSE)\w+")

def get_distinct_vars(formula):
    """Returns the set of all distinct variables appearing in formula"""
    varset = set(varpattern.findall(formula))
    varset.discard("X")
    varset.discard("G")
    varset.discard("F")
    varset.discard("next")
    varset.discard("alw")
    varset.discard("alwEv")
    return varset

def create_node_record(cur_node: RefinementNode, elapsed_time, queue_size, depth, time_node, error):
    return {
        "node_id": cur_node.id,
        "parent_node_id": cur_node.parent_id,
        "elapsed_time": elapsed_time,
        "queue_size": queue_size,
        "depth": depth,
        "length": len(cur_node.gr1_units),
        "num_vars": len(get_distinct_vars(" ".join(cur_node.gr1_units))),
        "is_y_sat": cur_node.isYSat(),
        "is_satisfiable": cur_node.isSatisfiable(),
        "is_realizable": cur_node.isRealizable(),
        "is_well_separated": cur_node.isWellSeparated(),
        "unreal_core_size": len(cur_node.unreal_core) if cur_node.unreal_core else None,
        "cs_num_states": len(cur_node.counterstrategy.states) if cur_node.counterstrategy else None,
        "is_interpolant_state_separable": cur_node.is_interpolant_state_separable,
        "num_state_components": cur_node.num_state_components,
        "num_non_io_separable_state_components": cur_node.num_non_io_separable_state_components,
        "is_interpolant_fully_separable": cur_node.is_interpolant_fully_separable,
        "num_refs_generated": cur_node.num_refs_generated,
        "time_y_sat_check": cur_node.time_y_sat_check,
        "time_realizability_check": cur_node.time_realizability_check,
        "time_satisfiability_check": cur_node.time_satisfiability_check,
        "time_well_separation_check": cur_node.time_well_separation_check,
        "time_unreal_core": cur_node.time_unreal_core,
        "time_counterstrategy": cur_node.time_counterstrategy,
        "time_interpolation": cur_node.time_interpolation,
        "time_generation": cur_node.time_generation,
        "time_refine": cur_node.time_refine,
        "time_repair_core": cur_node.time_repair_core,
        "time_node": time_node,
        "refinement": cur_node.gr1_units,
        "interpolant": cur_node.interpolant,
        "error": error,
    }

def counterstrategy_guided_refinement(
    initial_spec: SpectraSpecification,
    output_dir: str = "outputs",
    timeout: int = 600,
    repair_limit: int = -1,
    temp_dir: str = "temp",
    ):

    print()
    print("Starting Counterstrategy Guided Refinement")
    print("------------------------------------------")
    print(f"Repairing specification : {initial_spec.file_path}")
    print(f"Timeout                 : {timeout} seconds")
    print(f"Repair Limit            : {repair_limit if repair_limit > 0 else 'No Limit'}")
    print()

    start_time = time.perf_counter()

    initial_spec_node = RefinementNode()
    refinement_queue = deque([initial_spec_node])
    solutions: List[str] = []

    num_iterations = 0

    node_records: List[Dict[str, Any]] = []

    first_repair = None
    nodes_to_first_repair = None
    depth_to_first_repair = None
    time_to_first_repair = None
    length_first_repair = None
    vars_first_repair = None


    while refinement_queue \
        and not (repair_limit > 0 \
        and len(solutions) == repair_limit):

        elapsed_time = time.perf_counter() - start_time
        if elapsed_time >= timeout:
            print(f"Timeout reached: {elapsed_time:.2f}s >= {timeout}s")
            break

        time_node_start = time.perf_counter()
        num_iterations += 1

        cur_node = refinement_queue.pop()
        depth = len(cur_node.gr1_units)
        error = None

        print()
        print(f"Iteration #{num_iterations}")
        print("----------------------------")
        print(f"Elapsed Time        : {elapsed_time * 1000} ms")
        print(f"Queue Size          : {len(refinement_queue)}")
        print(f"Depth               : {len(cur_node.gr1_units)}")
        print(f"Processing Node ID  : {cur_node.id}")
        print(f"Current Refinement  : {cur_node.gr1_units}")
        print()
        
        # Create the refined spec
        refined_spec = SpectraSpecification(
            name=initial_spec.name,
            inputs=initial_spec.inputs,
            outputs=initial_spec.outputs,
            assumptions=initial_spec.assumptions + cur_node.gr1_units,
            guarantees=initial_spec.guarantees,
        )
        refined_spec_path = f"{temp_dir}/{cur_node.id}.spectra"
        refined_spec.to_file(refined_spec_path)
        cur_node.set_spec(refined_spec)
        print(f"Refined specification saved to: {refined_spec_path}")

        try:
            remaining_time = int(timeout - elapsed_time)

            if cur_node.isYSat():
                print("Specification is y-satisfiable")

                if not cur_node.isRealizable(timeout=remaining_time):
                    print("Specification is unrealizable")

                    print("Computing unrealizable core...", end='', flush=True)
                    cur_node.getUnrealizableCore()
                    print(" done")

                    cur_node.minimiseSpec()

                    core_spec_path = f"{temp_dir}/{cur_node.id}_core.spectra"
                    cur_node.spec.to_file(core_spec_path, use_alw=True)
                    print(f"Minimised specification saved to: {core_spec_path}")
                    
                    print("Computing counterstrategy...", end='', flush=True)
                    cur_node.getCounterstrategy(timeout=remaining_time)
                    print(" done")

                    candidate_ref_nodes = cur_node.generateRefinedNodes()
                    print(f"Generated {len(candidate_ref_nodes)} candidate refinements")

                    refinement_queue.extendleft(candidate_ref_nodes)

                else:
                    print("Specification is realizable")
                    cur_node.isSatisfiable()
                    cur_node.isWellSeparated()

                    before_repair_core = len(cur_node.gr1_units)
                    cur_node.getRepairCore()
                    num_redundant_assumptions = before_repair_core - len(cur_node.gr1_units)
                    print(f"Found {num_redundant_assumptions} redundant assumptions with repair core")

                    if first_repair is None:
                        print("*** First repair found ***")
                        first_repair = cur_node.gr1_units
                        nodes_to_first_repair = num_iterations
                        depth_to_first_repair = depth
                        time_to_first_repair = time.perf_counter() - start_time
                        length_first_repair = len(cur_node.gr1_units)
                        vars_first_repair = len(get_distinct_vars(" ".join(cur_node.gr1_units)))

                    solutions.append(cur_node.gr1_units)

            else:
                print("Specification is NOT y-satisfiable")

        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            print(error)

        node_record = create_node_record(
            cur_node,
            elapsed_time * 1000,
            len(refinement_queue),
            depth,
            time.perf_counter() - time_node_start,
            error
        )
        node_records.append(node_record)

    return {
        "node_records": node_records,
        "solutions": solutions,
        "first_repair": first_repair,
        "nodes_to_first_repair": nodes_to_first_repair,
        "depth_to_first_repair": depth_to_first_repair,
        "time_to_first_repair": time_to_first_repair,
        "length_first_repair": length_first_repair,
        "vars_first_repair": vars_first_repair,
    }

def implies(phi, psi):
    # Build the negation of (phi implies psi), i.e., phi ∧ ¬psi
    implication_neg = spot.formula(f"({phi}) & !({psi})")
    # Build the automaton from this formula
    aut = spot.translate(implication_neg)
    # If the language is empty, phi implies psi
    return aut.is_empty()

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

    start_time = time.perf_counter()
    result = counterstrategy_guided_refinement(initial_spec, 
                                      output_dir=args.output,
                                      timeout=args.timeout,
                                      repair_limit=args.repair_limit
                                      temp_dir=TEMP_DIR)
    runtime = time.perf_counter() - start_time

    print()
    print("Saving node data to CSV...")
    nodes_df = pd.DataFrame(result["node_records"])
    nodes_csv_path = f"{args.output}/{Path(args.input).stem}_interpolation_nodes.csv"
    nodes_df.to_csv(nodes_csv_path, index=False)
    print(f"Node data successfully saved at: {nodes_csv_path}\n")

    num_repairs = len(result["solutions"])

    print("Computing non-redundant repairs...")
    non_redundant_repairs = []
    for sol in [" & ".join(sp.unspectra(sol)) for sol in result["solutions"]]:
        if any(implies(sol, repair) for repair in non_redundant_repairs):
            continue
        non_redundant_repairs = [repair for repair in non_redundant_repairs if not implies(repair, sol)]
        non_redundant_repairs.append(sol)

    print(f"Found {len(non_redundant_repairs)} non-redundant repairs out of {num_repairs} total repairs")

    print()
    print("Saving search summary data")

    stats_csv_path = f"{args.output}/{Path(args.input).stem}_interpolation_stats.csv"

    num_nodes_explored = len(nodes_df)

    stats_record = {
        "file_path": initial_spec.name,
        "timeout": args.timeout,
        "repair_limit": args.repair_limit,

        "num_repairs": num_repairs,
        "num_non_redundant_repairs": len(non_redundant_repairs),
        "num_nodes_explored": num_nodes_explored,
        "effectiveness": (len(non_redundant_repairs) / (num_nodes_explored - 1)) if num_nodes_explored > 1 else 0,
        "num_y_unsat": (~nodes_df["is_y_sat"]).sum(),
        "max_depth": nodes_df["depth"].max(),
        # num_interpolants_computed
        # num_not_state_separable
        # num_not_fully_separable
        # num_errors

        "nodes_to_first_repair": result["nodes_to_first_repair"],
        "depth_to_first_repair": result["depth_to_first_repair"],
        "time_to_first_repair": result["time_to_first_repair"],
        "length_first_repair": result["length_first_repair"],
        "vars_first_repair": result["vars_first_repair"],

        # Incorrect
        # Non reduntant repairs
        "min_repair_length": nodes_df["length"].min(),
        "avg_repair_length": nodes_df["length"].mean(),
        "max_repair_length": nodes_df["length"].max(),

        "min_repair_vars": nodes_df["num_vars"].min(),
        "avg_repair_vars": nodes_df["num_vars"].mean(),
        "max_repair_vars": nodes_df["num_vars"].max(),

        # unreal core size

        "min_cs_num_states": nodes_df["cs_num_states"].min(),
        "avg_cs_num_states": nodes_df["cs_num_states"].mean(),
        "max_cs_num_states": nodes_df["cs_num_states"].max(),

        # interpolant size

        # num state components

        # num non io separable state components

        "min_num_refs_generated": nodes_df["num_refs_generated"].min(),
        "avg_num_refs_generated": nodes_df["num_refs_generated"].mean(),
        "max_num_refs_generated": nodes_df["num_refs_generated"].max(),
    }



    time_fields = [
        "time_y_sat_check", "time_realizability_check", "time_satisfiability_check",
        "time_well_separation_check",  "time_unreal_core", "time_counterstrategy", "time_interpolation",
        "time_generation", "time_refine", "time_repair_core", "time_node"
    ]

    for field in time_fields:
        stats_record[f"avg_{field}"] = nodes_df[field].mean()

    stats_record["runtime"] = runtime

    for field in time_fields:
        stats_record[f"total_{field}"] = nodes_df[field].sum()

    for field in time_fields:
        stats_record[f"pct_{field}"] = 100 * stats_record[f"total_{field}"] / runtime

    # Fields
    avg_fields = [
        "elapsed_time", "queue_size", "length",
        "unreal_core_size", "cs_num_states",
        "num_state_components", "num_non_io_separable_state_components",
        "num_refs_generated",
    ]

    bool_sum_fields = [
        "is_y_sat", "is_satisfiable", "is_realizable", "is_well_separated",
        "is_interpolant_state_separable", "is_interpolant_fully_separable"
    ]

    # # Aggregate
    # for field in avg_fields:
    #     summary_stats[f"avg_{field}"] = nodes_df[field].mean()

    # for field in bool_sum_fields:
    #     summary_stats[f"sum_{field}"] = nodes_df[field].sum()



    # # Filter rows where interpolant was computed
    # interpolant_rows = nodes_df[nodes_df["interpolant"].notnull()]

    # # Count total computed
    # summary_stats["num_interpolants_computed"] = len(interpolant_rows)

    # state_sep_bool = interpolant_rows["is_interpolant_state_separable"].apply(lambda x: False if x is None else x).astype(bool)
    # fully_sep_bool = interpolant_rows["is_interpolant_fully_separable"].apply(lambda x: False if x is None else x).astype(bool)

    # summary_stats["num_not_state_separable"] = (~state_sep_bool).sum()
    # summary_stats["num_not_fully_separable"] = (~fully_sep_bool).sum()

    # summary_stats["num_errors"] = nodes_df["error"].notnull().sum()

    df = pd.DataFrame([stats_record])
    df.to_csv(stats_csv_path, index=False)
    print("Stats saved to:", stats_csv_path)

    # return and print solutions

if __name__=="__main__":
    main()
