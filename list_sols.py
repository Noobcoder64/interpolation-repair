import os
import ast
# import spot
import pandas as pd
# from specification import unspectra

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
# output_folder = "outputs-symbolic/JVTS/"

output_folder = "outputs-interpolation-new/INTERPOLATION-MIN-INF/"


for root, dirs, files in os.walk(output_folder):

    for file in files:

        if not file.endswith("nodes.csv"):
            continue

        print(root + "/" + file)

        nodes_df = pd.read_csv(os.path.join(root, file), sep=",", index_col=False)
        nodes_df['Refinement'] = nodes_df['Refinement'].apply(safe_literal_eval)

        refs = []
        ids = []

        for cur_id, row in nodes_df.iterrows():

            cur_ref = sorted(row["Refinement"])

            found_equiv = False

            for i, ref in enumerate(refs):

                # if cur_ref == ref or spot.are_equivalent(cur_ref, ref):
                if cur_ref == ref:
                    found_equiv = True
                    if len(ref) > len(cur_ref):
                        ids[i] = cur_id
                        refs[i] = cur_ref
            
            if not found_equiv:
                ids.append(cur_id)
                refs.append(cur_ref)

        print(len(nodes_df["Refinement"]))
        print(len(refs))
        unique_nodes_df = nodes_df.loc[ids]
        unique_nodes_file = file.replace("nodes", "uniquenodes")  
        unique_nodes_df.to_csv(os.path.join(root, unique_nodes_file), index=False)

        sols_df = nodes_df[nodes_df["IsSolution"] == True].copy()
        sols_df["ContainsAux"] = sols_df["Refinement"].apply(containts_aux_variables)
        sols_df = sols_df[sols_df["ContainsAux"] == False]
        sols_file = file.replace("nodes", "sols")
        sols_df.to_csv(os.path.join(root, sols_file), index=False)

        unique_sols_df = unique_nodes_df[unique_nodes_df["IsSolution"] == True].copy()
        unique_sols_df["ContainsAux"] = unique_sols_df["Refinement"].apply(containts_aux_variables)
        unique_sols_df = unique_sols_df[unique_sols_df["ContainsAux"] == False]
        unique_sols_file = file.replace("nodes", "uniquesols")        
        unique_sols_df.to_csv(os.path.join(root, unique_sols_file), index=False)
