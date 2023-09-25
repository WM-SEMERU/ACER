# Temp java utils to get difference between repo outputs

from typing import List
import pandas as pd
import argparse

def edge_csv_diff(csv_1_path: str, csv_2_path: str) -> List:
    '''
    In csv2 but not in csv1
    '''
    df1 = pd.read_csv(csv_1_path)
    df2 = pd.read_csv(csv_2_path)

    # Read
    df1_l = []
    df2_l = list()
    for _, row in df1.iterrows():
        df1_l.append((row["caller"], row["callee"]))
    for _, row in df2.iterrows():
        df2_l.append((row["caller"], row["callee"]))
    df2_l = sorted(list(set(df2_l)))

    return [x for x in sorted(df2_l) if x not in df1_l]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required arguments
    parser.add_argument("--generated_path", required=True, type=str, help="Path to the generated edge file")
    parser.add_argument(
        "--ground_truth_path", required=True, type=str, help="Path to the ground truth edge file"
    )

    # Optional argument with default value
    parser.add_argument(
        "-d",
        "--comparison_direction",
        choices=["generated_to_ground_truth", "ground_truth_to_generated"],
        default="generated_to_ground_truth",
        help="Comparison direction of the edges",
    )

    args = parser.parse_args()

    diff = (
        edge_csv_diff(
            args.generated_path,
            args.ground_truth_path
            
        )
        if args.comparison_direction == "generated_to_ground_truth"
        else edge_csv_diff(args.ground_truth_path, args.generated_path)
    )
    print(f"{len(diff)} edges are missing from {' '.join(args.comparison_direction.split('_'))}:\n")
    for fromm, to in diff:
        print(f"{fromm} : {to}")
