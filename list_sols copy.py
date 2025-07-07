import os
import ast
import spot
import pandas as pd
from specification import unspectra
import time
import sys

# ========================= UTILS ===========================

def safe_literal_eval(value):
    try:
        return ast.literal_eval(value)
    except Exception:
        return None

def containts_aux_variables(refinements):
    if refinements is None:
        return None

    for assumption in refinements:
        if "aux" in assumption or  "CONSTRAINT" in assumption:
            return True
    return False

# =========================================================

# output_folder = "outputs-interpolation/INTERPOLATION-MIN-INF/"
# output_folder = "outputs-interpolation/INTERPOLATION-MIN/"
# output_folder = "outputs-interpolation/INTERPOLATION-ALLGARS-INF/"
# output_folder = "outputs-interpolation/INTERPOLATION-ALLGARS/"
output_folder = "outputs-symbolic/JVTS/"
# output_folder = "outputs-symbolic/JVTS/run-9/AMBA-1"


def implies(phi, psi):
    # Build the negation of (phi implies psi), i.e., phi ∧ ¬psi
    implication_neg = spot.formula(f"({phi}) & !({psi})")
    
    # Build the automaton from this formula
    aut = spot.translate(implication_neg)
    
    # If the language is empty, phi implies psi
    return aut.is_empty()

start_time = time.perf_counter()

for root, dirs, files in os.walk(output_folder):

    for file in files:
        # print(file)
        if not file.endswith("_nodes.csv"):
            continue

        print(root + "/" + file)

        nodes_df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False, on_bad_lines='skip')
        nodes_df['Refinement'] = nodes_df['Refinement'].apply(safe_literal_eval)
        nodes_df['Refinement'] = nodes_df['Refinement'].apply(unspectra)
        print(nodes_df["Refinement"])
        nodes_df['Refinement'] = nodes_df['Refinement'].apply(sorted)
        print(nodes_df["Refinement"])

        nodes_df['Refinement'] = nodes_df['Refinement'].apply(lambda r: " & ".join(r) if r else "")
        print(nodes_df["Refinement"])
        # nodes_df['Refinement'] = nodes_df['Refinement'].apply(lambda r: spot.parse_formula(r) if r else "")
        # print(nodes_df["Refinement"])


        refs = []
        ids = []
        ref_set = set() 

        for row in nodes_df.itertuples(index=True):
            cur_id = row.Index
            cur_ref = row.Refinement

            # try:
            #     cur_ref = sorted(row["Refinement"])
            # except:
            #     continue

            # cur_ref = row["Refinement"]

            if cur_ref == "":
                continue

            # Quick check for exact match (fast)
            if cur_ref in ref_set:
                continue

            found_equiv = False

            for i, ref in enumerate(refs):
                # print("OG CUR REF", cur_ref)
                # cur_ref = unspectra(cur_ref)
                # print("CURR REF", cur_ref)

                # print("OG Ref", ref)
                # ref = unspectra(ref)
                # print("Ref", ref)

                if cur_ref == "" or ref == "":
                    continue

                # if cur_ref == ref or spot.are_equivalent(cur_ref, ref):
                if cur_ref != ref and implies(cur_ref, ref):
                # if cur_ref == ref:

                    # input()

                    found_equiv = True
                    if len(ref) > len(cur_ref):
                        ids[i] = cur_id
                        refs[i] = cur_ref
                        ref_set.remove(ref)  # remove old longer ref from set
                        ref_set.add(cur_ref)  # add new shorter ref
            
            if not found_equiv:
                ids.append(cur_id)
                refs.append(cur_ref)
                ref_set.add(cur_ref)

        print(len(nodes_df["Refinement"]))
        print(len(refs))
        print(refs)

        if (len(nodes_df["Refinement"]) < len(refs)):
            raise Exception("Nodes explored < unique nodes explored")

        unique_nodes_df = nodes_df.loc[ids]
        unique_nodes_file = file.replace("nodes", "uniquenodes")  
        # unique_nodes_df.to_csv(os.path.join(root, unique_nodes_file), index=False)

        sols_df = nodes_df[nodes_df["IsSolution"] == True].copy()
        sols_df["ContainsAux"] = sols_df["Refinement"].apply(containts_aux_variables)
        sols_df = sols_df[sols_df["ContainsAux"] == False]
        sols_file = file.replace("nodes", "sols")
        # sols_df.to_csv(os.path.join(root, sols_file), index=False)

        unique_sols_df = unique_nodes_df[unique_nodes_df["IsSolution"] == True].copy()
        unique_sols_df["ContainsAux"] = unique_sols_df["Refinement"].apply(containts_aux_variables)
        unique_sols_df = unique_sols_df[unique_sols_df["ContainsAux"] == False]
        unique_sols_file = file.replace("nodes", "uniquesols")        
        # unique_sols_df.to_csv(os.path.join(root, unique_sols_file), index=False)

        print("TIME TAKEN:", time.perf_counter() - start_time)

        sys.exit(0)