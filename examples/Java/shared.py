"""
This is a temporary file that will be refactored after we do some major refactoring that 
moves each subcomponent into its own file.
"""

from collections import defaultdict
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from tree_sitter import Language, Node
from src.tree_sitter_utils import (
    find_all_ancestors_of_types,
    find_closest_ancestor_of_type,
    find_first_child_of_type,
)

class FullType(NamedTuple):
    package_name: str
    contained_by: str 
    shorthand: str
    
    def __str__(self) -> str:
        p = self.package_name if self.package_name else None
        return '.'.join(filter(None, [p, self.contained_by, self.shorthand]))
    
    __repr__ = __str__
        
class MethodKey(NamedTuple):
    contained_by: FullType
    method_name: str 
    method_params: Tuple[str] # List[str] is not hashable.

    def __str__(self) -> str:
        # method_params = ','.join(self.method_params)
        method_params_wo_name = [el.split()[0].strip() if el.split() else "" for el in self.method_params]
        method_params_wo_generics = [el.split("<")[0].strip() if el.split() else "" for el in method_params_wo_name]
        method_params = f"({','.join(method_params_wo_generics)})"
        return f"({','.join([str(self.contained_by), self.method_name, method_params])})"
    
    __repr__ = __str__

JAVA_ERR_METHOD_KEY: MethodKey = MethodKey(FullType("", "", ""), "", ("",))
JAVA_ERR_FULL_TYPE = FullType("", "", "")

def get_package_name(context_node: Node) -> str: 
    def package_name_from_program_node(program_node: Optional[Node]) -> str:
        if not program_node:
            return "unnamed"
        
        package_declaration_node = find_first_child_of_type(program_node, "package_declaration")
        if not package_declaration_node: return "unnamed"
        package_identifier_node = find_first_child_of_type(package_declaration_node, "identifier", 1) or find_first_child_of_type(package_declaration_node, "scoped_identifier", 1)
        assert package_identifier_node, "Fail, wasn't able to find an package name node of type identifier or scoped_identifier, but there should be one."

        return package_identifier_node.text.decode("utf8")

    program_node = find_closest_ancestor_of_type(context_node, "program") or context_node
    
    return package_name_from_program_node(program_node)

def get_contained_by(context_node: Optional[Node]) -> FullType:
    '''
    Get the `FullType` of the closest container (self-exclusive).
    By self-exclusive, I mean that if `context_node` is some model node, this method does not return itself.
    '''

    if not context_node:
        return JAVA_ERR_FULL_TYPE

    outer_nodes = reversed(
        find_all_ancestors_of_types(
            context_node,
            [
                "class_declaration",
                "interface_declaration",
            ],
        )
    )
    outer_name_nodes = map(
        lambda node: find_first_child_of_type(node, "identifier", 1),
        outer_nodes,
    )
    outer_names = ".".join(list(map(
        lambda node: node.text.decode("utf8") if node else "",
        outer_name_nodes,
    )))
    split = outer_names.rsplit(".", maxsplit=1)
    package_name = get_package_name(context_node)

    if len(split) == 1: 
        shorthand = split[0]
        return FullType(package_name, "", shorthand)
    else: 
        contained_in, shorthand = split
        return FullType(package_name, contained_in, shorthand)
    
packages_to_importables = Dict[str, List[FullType]]

from enum import Enum, EnumMeta
class MetaEnum(EnumMeta):
    def __contains__(cls, item: Any):
        try:
            cls(item)  # type: ignore
        except ValueError:
            return False
        return True


class StrEnum(str, Enum, metaclass=MetaEnum):
    '''
    How to check if string exists in Enum of strings?
    https://stackoverflow.com/questions/63335753/how-to-check-if-string-exists-in-enum-of-strings/63336176#63336176
    To test if string equals to a particular Enum, simply inherit from the str class as I did in StrEnum
    '''
    @classmethod
    def from_str(cls, str: str): 
        return cls(str)
    
class JavaGrammarKeywords(StrEnum):
    VARIABLE_DECLARATOR = "variable_declarator"
    TYPE_IDENTIFIER = "type_identifier"
    METHOD_DECLARATION = "method_declaration"
    IDENTIFIER = "identifier"
    PACKAGE_DECLARATION = "package_declaration"
    SCOPED_IDENTIFIER = "scoped_identifier"
    CLASS_DECLARATION = "class_declaration"
    INTERFACE_DECLARATION = "interface_declaration"
    LINE_COMMENT = "line_comment"
    BLOCK_COMMENT = "block_comment"
    IMPORT_DECLARATION = "import_declaration"
    CLASS_BODY = "class_body"
    INTERFACE_BODY = "interface_body"
    MODIFIERS = "modifiers"
    PROGRAM = "program"
    OBJECT_CREATION_EXPRESSION = "object_creation_expression"
    SCOPED_TYPE_IDENTIFIER = "scoped_type_identifier"
    BLOCK = "block"
    FORMAL_PARAMETERS = "formal_parameters"
    FORMAL_PARAMETER = "formal_parameter"
    SPREAD_PARAMETER = "spread_parameter"
    ARGUMENT_LIST = "argument_list"
    CONSTRUCTOR_DECLARATION = "constructor_declaration"
    ENHANCED_FOR_STATEMENT = "enhanced_for_statement"
    ENUM_DECLARATION = "enum_declaration"
    LOCAL_VARIABLE_DECLARATION = "local_variable_declaration"

type_query = """[
                    (integral_type)@type
                    (generic_type(type_identifier)@type)
                    (array_type)@type
                    (floating_point_type)@type
                    (boolean_type)@type
                    (type_identifier)@type
                    (scoped_type_identifier)@type
                    (void_type)@type
                ]
             """

def group_by_type_capture_up_to_depth(
    root: Node, queryStr: str, maxDepth: int, language: Language
) -> Dict[str, List[Node]]:
    """
    group_by_type_capture, but only up to a certain depth
    You can use this to simulate almost capturing exclusively at the root node

    By "at the root node", I mean, if a class_declaration has many nested class_declaration nodes,
    The query ignores the nested ones. However, this would a maxDepth of less than 2, because
    2 layers lay between a class_declaration and a potential nested class_declaration

    Note that this function captures all nodes as usual, and then start filtering them based on depth.
    There is probably no way to optimize this unless we wirte our own query engine.
    """

    tree_sitter_query = language.query(queryStr)
    captures = tree_sitter_query.captures(root)
    res: Dict[str, List[Node]] = defaultdict(list)
    for node, type in captures:

        def is_node_in_depth(node: Optional[Node], depth: int) -> bool:
            if not node or depth < 0:
                return False
            if node.id == root.id:
                return True
            return is_node_in_depth(node.parent, depth - 1)

        if is_node_in_depth(node, maxDepth):
            res[type].append(node)

    return dict(res)

import os
import re

def get_files(from_directory: str, include_pat: re.Pattern[str]) -> List[str]:
    file_list: List[str] = []
    print(from_directory)
    # Compile the regex pattern

    # Walk through the directory
    for root, _, files in os.walk(from_directory):
        for file in files:
            # Get the full file path
            file_path = os.path.join(root, file)
            # Check if the file path doesn't match the regex pattern
            if include_pat.search(file_path):
                file_list.append(file_path)
    
    return file_list

def count_args(method_arguments: Node) -> int:
    return method_arguments.named_child_count
