
from typing import List, Set, Tuple

from tqdm import tqdm

# TODO: Ignore lines that starts with M:
def structure(part: str) -> str: 
    # Now, both parts look like is C.D:method$000(A.B,boolean)
    remains, arguments = part.split("(", maxsplit=1)
    arguments = arguments[: len(arguments)-1]
    class_name, method_name = remains.rsplit(".", maxsplit=1)
    arguments_list = ",".join([item.rsplit(".", maxsplit=1)[-1] for item in arguments.split(",")])
    return f"({class_name},{method_name},({arguments_list}))"

def one(edge_str: str): 
    left, right = edge_str.split("->")
    left = left.split(")", maxsplit=1)[1]
    right = right.split(")", maxsplit=1)[1]
    return f"{structure(left)}->{structure(right)}"

def jcg_edges(output_path: str):
    f = open(output_path, "r") 
    lines = f.readlines()
    edges: List[Tuple[str, str]] = list()
    for l in tqdm(lines): 
        # Split the input string into two parts.
        left, right = l.split('->')

        # Ignore line number. E.g., M:(44)
        left = left.split(")" ,maxsplit=1)[1]
        right = right.split(")", maxsplit=1)[1]


        try: 
            edges.append((structure(left), structure(right)))
        except Exception: 
            pass

    f.close()
    return edges

def pacer_edges(output_path: str): 
    f = open(output_path, "r") 
    lines = f.readlines()
    edges: Set[Tuple[Tuple[str, str, str], Tuple[str, str, str]]] = set()
    for l in tqdm(lines): 
        if "->" not in l: continue
        left, right = l.split("->")
        def structure(part: str) -> tuple[str, str, str]: 
            # Now, both parts look like is C.D:method$000(A.B,boolean)
            container, name, arguments = part.split(",", maxsplit=2)
            arguments_list = arguments.split(",")
            arguments_list = ",".join(arguments_list)
            return container, name, arguments_list
        try: 
            edges.add((structure(left), structure(right)))
        except Exception: 
            pass
    return edges
# Test function
# pe = pacer_edges("scha-results")
# print(len(pe))
je = jcg_edges("output.txt")
for e in je: 
    print(e)


