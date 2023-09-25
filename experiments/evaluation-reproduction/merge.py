import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Script to merge SCHA.py/NR.py results into prebuilt .tsv")

parser.add_argument('--base_tsv', type=str, required=True)
parser.add_argument('--pacer_results_path', type=str, required=True)
parser.add_argument('-o', '--output_path', type=str, required=True,
                    help='The path of the file to write to')
parser.add_argument("-t", '--tool_name', type=str, required=True)
parser.add_argument("-n", "--the_number", type=int, required=True, help="This is so very temporary..") # original code uses 8

args = parser.parse_args()

# Load the PACER's results
with open(args.pacer_results_path, 'r') as f:
    pacer_edges = f.read().splitlines()

# Load the simplified TSV file
df = pd.read_csv(args.base_tsv, sep='\t', header=None)

# Add a new column for PACER's results
df.insert(args.the_number, args.tool_name, '')

# Create a dictionary where the keys are the edges and the values are the indices in the DataFrame
edge_to_index = {edge: index for index, edge in df[0].to_dict().items()}

# Prepare a list to store new rows
new_rows = []

# Define the columns for the new rows
columns = list(df.columns[:-1]) + [df.columns[-1]]

# Merge PACER's results into the DataFrame
for edge in pacer_edges:
    if "->" not in edge: continue

    index = edge_to_index.get(edge)
    if index is not None:
        # If the edge is already in the DataFrame, mark it as present for PACER
        df.loc[index, args.tool_name] = 'X'
        # Increment the X count
        df.loc[index, 1] += 1
    else:
        # If the edge is not in the DataFrame, add a new row for it
        new_row = [edge, 1] + [''] * (args.the_number - 2) + ['X', 0, '']  # there should be 6 empty strings for the six tools, 'X' for PACER, an empty string for the placeholder column, and 0 for the random number
        new_rows.append(new_row)


# Append new rows to the DataFrame
df = pd.concat([df, pd.DataFrame(new_rows, columns=columns)], ignore_index=True)

# Save the DataFrame to a new TSV file
df.to_csv(args.output_path, sep='\t', index=False, header=False)
