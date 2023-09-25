from utils.java import aliased_type_to_full_type

from my_enums.java import type_query, JavaGrammarKeywords
from utils.tree_sitter import (
    group_by_type_capture_up_to_depth,
    find_closest_ancestor_of_type,
)
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver

from my_types.java import JavaFullType

class JavaFormalParameterTypeResolver(JavaTypeResolver):
    def resolve(self, formal_parameter_node: Node) -> JavaFullType:
        # Precondition: Formal parameters are contained in method_declaration node and have type identifier
        method_declaration_node = find_closest_ancestor_of_type(
            formal_parameter_node, JavaGrammarKeywords.METHOD_DECLARATION
        ) or find_closest_ancestor_of_type(
            formal_parameter_node, JavaGrammarKeywords.CONSTRUCTOR_DECLARATION
        )
        assert method_declaration_node and method_declaration_node.parent
        query = f"(formal_parameter {type_query})"
        captures = group_by_type_capture_up_to_depth(formal_parameter_node, query, 3)
        assert "type" in captures
        type_identifier_node = captures["type"][0]

        # Parse basic info
        type_identifier = type_identifier_node.text.decode("utf8")

        # We start from the method node's parent because the type of a parameter can't be defined in the method body
        return aliased_type_to_full_type(
            type_identifier, method_declaration_node.parent
        )
