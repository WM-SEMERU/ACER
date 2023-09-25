# Provide file, ast_type, and component of ast_type
# The component gets freq'd on. 

# For example: 
# file: a.java
# ast_type: method_invocation
# component: caller

# Slight caveat: We allow for custom resolver func for the component 
# So that a >1 layer nested node may be freq'd.

import os
from pprint import pprint
import re
from typing import Callable, Counter, Optional
from tqdm import tqdm

from tree_sitter import Node
from src.new_framework.examples.shared import get_files

from src.new_framework.tree_sitter_utils import find_all_children_of_type, load_tree_sitter


def bruh(file_node: Node, ast_type: str, component_resolver: Callable[[Node], Optional[Node]]):
    bases = find_all_children_of_type(file_node, ast_type)
    resolved = map(component_resolver, bases)
    freq: Counter[str] = Counter()
    for r in resolved: 
        if r: 
            freq[r.type] += 1 
        else: freq["<None>"] += 1

    return freq

l, p = load_tree_sitter("/home/andrewchen/personal/csci-435_callgraph_generator/build/my-languages.so", "java")

dir = os.path.join(os.path.expanduser("~"), "usr", "lib", "jvm", "jdk-11", "lib", "temp")
files = get_files(dir, re.compile(r'\.java$'))
merge: Counter[str] = Counter()
for path in tqdm(files): 
    with open(path, "rb") as file:
        root = p.parse(file.read()).root_node
        merge = merge + bruh(root, "method_invocation", lambda n: n.child_by_field_name("object"))
pprint(merge)

sum = merge.total()
dist = {k: v/sum for k, v in merge.items()}
pprint(dist)