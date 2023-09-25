"""
This is a temporary file that will be refactored after we do some major refactoring that 
moves each subcomponent into its own file.
"""

from itertools import chain
from typing import Dict, List, Optional, Tuple
from tree_sitter import Node
from my_enums.python import PythonGrammarKeywords
from utils.tree_sitter import (
    find_all_ancestors_of_types,
    find_closest_ancestor_of_type,
    find_first_child_of_type,
    group_by_type_capture,
    find_all_children_of_type,
)

from typing import TYPE_CHECKING
from my_types.python import shorthand, python_full_type, contained_by, aliased_type

def get_first_identifier_in_chain(node : Node) -> Node:
    attribute_node = node
    while(attribute_node.type != "identifier"):
        attribute_node = attribute_node.children[0]	
    return attribute_node

def get_contained_by(node : Node) -> str:
    if not node:
        return ""

    contained_by_nodes = reversed(
        find_all_ancestors_of_types(
            node,
            [
                PythonGrammarKeywords.CLASS_DEFINITION,
            ],
        )
    )
    contained_by_name_nodes = map(
        lambda node: find_first_child_of_type(node, PythonGrammarKeywords.IDENTIFIER),
        contained_by_nodes,
    )
    contained_by_names = map(
        lambda node: node.text.decode("utf8") if node else "",
        contained_by_name_nodes,
    )
    
    contained_by = ".".join(list(contained_by_names))
    return contained_by
    
def get_containing_calls(node : Node) -> List[Node]:
    calls = find_all_children_of_type(node, "call")
    return calls

def resolve_type_of_alias_up_to(node : Node, scope : str):
    sibling_node = node.prev_named_sibling
    while(sibling_node):
        if(sibling_node.type != "expression_statement") : continue



def traverse_contained_by(containing_models: aliased_type) -> List[aliased_type]:
    """
    Go from A.B.C -> [A.B.C, A.B, A, ""]
    """
    splits = containing_models.split(".")
    res = []
    for i in range(len(splits), -1, -1):
        res.append(".".join(splits[:i]))
    return res


