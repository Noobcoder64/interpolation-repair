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

TEMP_DIR = "temp"

# print("Resetting temp...")
# temp_folder = 'temp'
# for temp_file in os.listdir(temp_folder):
#     temp_file_path = os.path.join(temp_folder, temp_file)
#     try:
#         if os.path.isfile(temp_file_path):
#             os.remove(temp_file_path)
#     except Exception as e:
#         print(e)
# print("Reset complete!")

varpattern = re.compile(r"\b(?!TRUE|FALSE)\w+")

def getDistinctVariablesInFormula(formula):
    """Returns the set of all distinct variables appearing in formula"""
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

def create_node_record(cur_node, elapsed_time, queue_size, depth, error=None):
    return {
        "node_id": cur_node.id,
        "parent_node_id": cur_node.parent_id,
        "elapsed_time": elapsed_time,
        "queue_size": queue_size,
        "depth": depth,
        "length": len(cur_node.gr1_units),
        "num_vars": len(getDistinctVariablesInFormula(" ".join(cur_node.gr1_units))),
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
        "num_refs_generated": cur_node.num_refinements_generated,
        "time_y_sat_check": cur_node.time_y_sat_check,
        "time_realizability_check": cur_node.time_realizability_check,
        "time_satisfiability_check": cur_node.time_satisfiability_check,
        "time_well_separation_check": cur_node.time_well_separation_check,
        "time_unreal_core": cur_node.time_unreal_core,
        "time_counterstrategy": cur_node.time_counterstrategy,
        "time_interpolation": cur_node.time_interpolation,
        "time_generation": cur_node.time_generation,
        "time_refine": cur_node.time_refine,
        "time_repair_core": 0,
        "time_node": (time.perf_counter() - cur_node.time_node_start),  # or pass start time if needed
        "refinement": cur_node.gr1_units,
        "interpolant": cur_node.interpolant,
        "error": error,
    }

def counterstrategy_guided_refinement(
    initial_spec: SpectraSpecification,
    output_dir: str = "outputs",
    timeout: int = 600,
    repair_limit: int = -1,
    ):

    print()
    print("++ Starting Counterstrategy Guided Refinement")
    print("++ ------------------------------------------")
    print(f"++ Repairing specification : {initial_spec.file_path}")
    print(f"++ Timeout                 : {timeout} seconds")
    print(f"++ Repair Limit            : {repair_limit if repair_limit > 0 else 'No Limit'}")
    print()

    start_time = time.perf_counter()

    initial_spec_node = RefinementNode()
    refinement_queue = deque([initial_spec_node])
    solutions: List[str] = []

    explored_refs = []
    duplicate_refs = []
    num_iterations = 0
    time_to_first_repair = None

    nodes_csv_path = f"{output_dir}/{initial_spec.name}_interpolation_nodes.csv"
    node_records: List[Dict[str, Any]] = []

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
        print("###########################################")
        print(f"++ Iteration           : #{num_iterations}")
        print(f"++ Processing Node ID  : {cur_node.id}")
        print(f"++ Queue Size          : {len(refinement_queue)}")
        print(f"++ Elapsed Time        : {elapsed_time * 1000} ms")
        print(f"++ Current Refinement  : {cur_node.gr1_units}")
        print(f"++ Depth               : {len(cur_node.gr1_units)}")
        print("###########################################")
        print()
            
        refined_spec = SpectraSpecification(
            name=initial_spec.name,
            inputs=initial_spec.inputs,
            outputs=initial_spec.outputs,
            assumptions=initial_spec.assumptions + cur_node.gr1_units,
            guarantees=initial_spec.guarantees,
        )
        refined_spec_path = f"{TEMP_DIR}/{cur_node.id}.spectra"
        refined_spec.to_file(refined_spec_path)
        cur_node.set_spec(refined_spec)

        print(f"++ Refined specification saved to: {refined_spec_path}")

        remaining_time = int(timeout - elapsed_time)

        try:

            print("++ Checking y-satisfiability...")
            if cur_node.isYSat():
                print("++ Specification is y-satisfiable")

                print("++ Checking realizability...")
                if not cur_node.isRealizable(timeout=remaining_time):
                    print("++ Specification is unrealizable")

                    print("++ Computing unrealizable core...")
                    cur_node.getUnrealizableCore()
                    print("++ Unrealizable core computed")

                    print("++ Minimising specification...")
                    cur_node.minimiseSpec()
                    print("++ Specification minimised")

                    core_spec_path = f"{TEMP_DIR}/{cur_node.id}_core.spectra"
                    cur_node.spec.to_file(core_spec_path, use_alw=True)
                    print(f"++ Minimised specification saved to: {core_spec_path}")
                    
                    print("++ Computing counterstrategy...")
                    cur_node.getCounterstrategy(timeout=remaining_time)
                    print("++ Counterstrategy computed")

                    print("++ Generating alternative refinements...")
                    candidate_ref_nodes = cur_node.generateRefinedNodes()
                    print(f"++ Generated {len(candidate_ref_nodes)} candidate refinements")

                    refinement_queue.extendleft(candidate_ref_nodes)

                else:
                    print("++ Specification is realizable")

                    cur_node.isSatisfiable()
                    cur_node.isWellSeparated()

                    if time_to_first_repair is None:
                        # Incorrect
                        time_to_first_repair = elapsed_time

                    # Repair core
                    time_repair_core_start = time.perf_counter()
                    # print("GR:", current_ref.gr1_units)
                    # fixed_asm_lines = [i+1 for i, line in enumerate(initial_spec.lines) if "assumption" in line]
                    # repair_lines = [i+1 for i, line in enumerate(current_ref.spec.lines) if "assumption" in line]
                    # print("FIXED:", fixed_asm_lines)
                    # print("REPAIR:", repair_lines)
                    # repair_lines = list(set(repair_lines) - set(fixed_asm_lines))
                    # print("REPAIR:", repair_lines)
                    # repair_core = spectra.compute_repair_core(current_ref.spec.file_path, repair_lines)
                    # print("REPAIR CORE:", repair_core)
                    # print("LINES: ",[current_ref.spec.lines[i].replace('\t', '').replace(';', '').replace('\n', '') for i in repair_core])
                    # current_ref.gr1_units = [current_ref.spec.lines[i].replace('\t', '').replace(';', '').replace('\n', '') for i in repair_core]
                    # print(current_ref.gr1_units)
                    time_repair_core = time.perf_counter() - time_repair_core_start

                    # 8
                    solutions.append(cur_node.gr1_units)

            else:
                print("++ Specification is NOT y-satisfiable")

            explored_refs.append(cur_node.gr1_units)

        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            print(f"++ {error}")

        node_record = {
                "node_id": cur_node.id,
                "parent_node_id": cur_node.parent_id,
                "elapsed_time": elapsed_time,
                "queue_size": len(refinement_queue),
                "depth": depth,
                "length": len(cur_node.gr1_units),
                "num_vars": len(getDistinctVariablesInFormula(" ".join(cur_node.gr1_units))),
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
                "time_repair_core": 0,
                "time_node": (time.perf_counter() - time_node_start),
                "refinement": cur_node.gr1_units,
                "interpolant": cur_node.interpolant,
                "error": error,
            }
        node_records.append(node_record)

        # break

    # nodes_csv_writer.close()

    spec_stem = Path(initial_spec.file_path).stem

    print("Saving nodes to CSV...")
    nodes_df = pd.DataFrame(node_records)
    nodes_csv_path = f"{output_dir}/{spec_stem}_interpolation_nodes.csv"
    nodes_df.to_csv(nodes_csv_path, index=False)
    print("Nodes saved to:", nodes_csv_path)

    print()
    print("++++ SAVING SEARCH SUMMARY DATA")

    solutions = [" & ".join(sp.unspectra(sol)) for sol in solutions]

    print("++ Found solutions:", solutions)

    non_redundant_repairs = []

    for sol in solutions:
        if any(implies(sol, repair) for repair in non_redundant_repairs):
            continue
        non_redundant_repairs = [repair for repair in non_redundant_repairs if not implies(repair, sol)]
        non_redundant_repairs.append(sol)

    print(non_redundant_repairs)

    params_metrics_csv_path = f"{output_dir}/{spec_stem}_interpolation_params_metrics.csv"
    metrics = {
        "filename": initial_spec.name,
        "num_repairs": len(solutions),
        "num_non_redundant_repairs": len(non_redundant_repairs),
        "num_nodes_explored": num_iterations,
        "effectiveness": (len(solutions) / (num_iterations - 1)) if num_iterations > 1 else 0,
        "repair_limit": repair_limit,
        "time_to_first": time_to_first_repair,
        "runtime": elapsed_time,
        "timeout": timeout,
        "timed_out": elapsed_time >= timeout,
        "duplicate_nodes": len(duplicate_refs),
        "num_interpolants_computed": 0,
        "num_non_state_separable": 0,
    }

    df = pd.DataFrame([metrics])
    df.to_csv(params_metrics_csv_path, index=False)
    print("Params and metrics saved to:", params_metrics_csv_path)

    summary_stats = {
        "filename": spec_stem,
        "total_nodes": len(nodes_df),
    }

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

    time_fields = [
        "time_y_sat_check", "time_realizability_check", "time_satisfiability_check",
        "time_well_separation_check",  "time_unreal_core", "time_counterstrategy", "time_interpolation",
        "time_generation", "time_repair_core", "time_refine", "time_node"
    ]

    # Aggregate
    for field in avg_fields:
        summary_stats[f"avg_{field}"] = nodes_df[field].mean()

    for field in bool_sum_fields:
        summary_stats[f"sum_{field}"] = nodes_df[field].sum()

    for field in time_fields:
        summary_stats[f"total_{field}"] = nodes_df[field].sum()

    for field in time_fields:
        summary_stats[f"avg_{field}"] = nodes_df[field].mean()

    for field in time_fields:
        total_time = summary_stats.get(f"total_{field}", 0)
        if elapsed_time > 0:
            summary_stats[f"pct_{field}"] = 100 * total_time / (elapsed_time * 1000)
        else:
            summary_stats[f"pct_{field}"] = 0.0

    # Filter rows where interpolant was computed
    interpolant_rows = nodes_df[nodes_df["interpolant"].notnull()]

    # Count total computed
    summary_stats["num_interpolants_computed"] = len(interpolant_rows)

    state_sep_bool = interpolant_rows["is_interpolant_state_separable"].apply(lambda x: False if x is None else x).astype(bool)
    fully_sep_bool = interpolant_rows["is_interpolant_fully_separable"].apply(lambda x: False if x is None else x).astype(bool)

    summary_stats["num_not_state_separable"] = (~state_sep_bool).sum()
    summary_stats["num_not_fully_separable"] = (~fully_sep_bool).sum()

    summary_stats["num_errors"] = nodes_df["error"].notnull().sum()

    stats_df = pd.DataFrame([summary_stats])
    stats_csv_path = f"{output_dir}/{spec_stem}_interpolation_stats.csv"
    stats_df.to_csv(stats_csv_path)
    print("Summary stats saved to:", stats_csv_path)

    # if refine_error:
    #     sys.exit(0)

    # spectra.shutdown()

    # 10
    return solutions


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
        print(f"++ Clearing existing temp folder: {TEMP_DIR}")
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    print(f"++ Created temp folder: {TEMP_DIR}")
    print()

    args = parser.parse_args()

    input_file_path = Path(args.input)

    print(f"++ Reading initial specification from {input_file_path}...")
    initial_spec = SpectraSpecification.from_file(input_file_path)

    temp_path = Path("temp") / input_file_path.name
    initial_spec.to_file(str(temp_path))
    print(f"++ Initial specification copied to {temp_path}")

    print()
    print("++ Specification summary")
    print("++ ---------------------")
    print(f"++  Name        : {initial_spec.name}")
    print(f"++  Inputs      : {len(initial_spec.inputs)}")
    print(f"++  Outputs     : {len(initial_spec.outputs)}")
    print(f"++  Assumptions : {len(initial_spec.assumptions)}")
    print(f"++  Guarantees  : {len(initial_spec.guarantees)}")
    print(f"++  Lines       : {len(initial_spec.lines)}")
    print()

    if initial_spec.is_realizable(args.timeout):
        print("++ Specification is already realizable. No repair needed.\n")
        return
    
    if not initial_spec.is_y_sat():
        print("++ Adding assumptions will NOT fix this specification.\n")
        return

    counterstrategy_guided_refinement(initial_spec, 
                                      output_dir=args.output,
                                      timeout=args.timeout,
                                      repair_limit=args.repair_limit)

    # return and print solutions

if __name__=="__main__":
    main()
