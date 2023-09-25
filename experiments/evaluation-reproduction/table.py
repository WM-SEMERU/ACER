import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Script to create 2D comparison table")

parser.add_argument('--base_tsv', type=str, required=True)
parser.add_argument('-o', '--output_path', type=str, required=True,
                    help='The path of the file to write to')

args = parser.parse_args()
# Load the TSV file into a pandas DataFrame
df = pd.read_csv(args.base_tsv, sep='\t', header=None)

# Extract the tool names
tool_names = ["Soot", "OSA", "SPOON", "JCG", "WALA", "JDT", "PACER-NR", "PACER-NR-ALL", "PACER-SCHA", "PACER-SCHA-ALL"]

# Create a dictionary where the key is a tool name and the value is a set of edges that this tool has
edges_by_tool = {tool: set() for tool in tool_names}
for _, row in df.iterrows():
    edge = row[0]
    tools = row[2:]
    for tool, has_edge in zip(tool_names, tools):
        if has_edge == 'X':
            edges_by_tool[tool].add(edge)



# Create a 6x6 DataFrame
intersection_df = pd.DataFrame(index=tool_names, columns=tool_names)

# Calculate the percentage of intersections
for tool_i in tool_names:
    for tool_j in tool_names:
        if tool_i == tool_j: 
            intersection_df.loc[tool_i, tool_j] = len(edges_by_tool[tool_i])
            continue
        intersection_count = len(edges_by_tool[tool_i] & edges_by_tool[tool_j])
        total_count = len(edges_by_tool[tool_i])
        intersection_percentage = (intersection_count / total_count) * 100
        intersection_df.loc[tool_i, tool_j] = intersection_percentage

intersection_df.to_csv(args.output_path)
