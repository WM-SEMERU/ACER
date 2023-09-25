from tree_sitter import Node
from src.tree_sitter_utils import find_all_children_of_type, find_closest_ancestor_of_type, get_deepest_children
from ..shared import JavaGrammarKeywords

class JavaIdentifierTypeResolver():
    def resolve(self, identifier_node: Node, only_variable_identifier: bool) -> str:
        """
        Resolve steps
        1. Find the usually shorthand, declared type. This can be found in the method args, at the local declaration, or in the field declarations.
        2. Just pass to the corresponding type resolver
        """

        # Parse basic info.
        match_identifier = identifier_node.text.decode("utf8")

        # In method args.
        container_method_node = find_closest_ancestor_of_type(
            identifier_node, JavaGrammarKeywords.METHOD_DECLARATION
        ) or find_closest_ancestor_of_type(
            identifier_node, JavaGrammarKeywords.CONSTRUCTOR_DECLARATION
        )
        if container_method_node:
            formal_parameter_nodes = find_all_children_of_type(
                container_method_node, "formal_parameter", 2
            )
            for node in formal_parameter_nodes:
                formal_parameter_identifier_node = node.child_by_field_name("name")
                assert formal_parameter_identifier_node
                formal_parameter_identifier = formal_parameter_identifier_node.text.decode("utf8")
                if formal_parameter_identifier == match_identifier:
                    type_identifier_node = node.child_by_field_name("type") 
                    assert type_identifier_node
                    return type_identifier_node.text.decode("utf8")

        # In local declaration
        cur_node = identifier_node
        while cur_node and cur_node.type not in [JavaGrammarKeywords.METHOD_DECLARATION, JavaGrammarKeywords.CONSTRUCTOR_DECLARATION]:
            match cur_node.type: 
                case JavaGrammarKeywords.LOCAL_VARIABLE_DECLARATION:
                    variable_declarator_node = cur_node.child_by_field_name("declarator")
                    assert variable_declarator_node
                    variable_identifier_node = variable_declarator_node.child_by_field_name("name")
                    assert variable_identifier_node
                    variable_identifier = variable_identifier_node.text.decode("utf8")
                    if match_identifier == variable_identifier:
                        type_identifier_node = cur_node.child_by_field_name("type")
                        assert type_identifier_node
                        return type_identifier_node.text.decode("utf8")
                    
                case JavaGrammarKeywords.ENHANCED_FOR_STATEMENT: 
                    for_identifier_node = cur_node.child_by_field_name("name")
                    assert for_identifier_node
                    for_identifier = for_identifier_node.text.decode("utf8") 
                    if match_identifier == for_identifier:
                        type_identifier_node = cur_node.child_by_field_name("type")
                        assert type_identifier_node
                        return type_identifier_node.text.decode("utf8")
                    
                case _: pass

            if cur_node.prev_named_sibling:
                cur_node = get_deepest_children(cur_node.prev_named_sibling)
            else:
                cur_node = cur_node.parent
        
        # Control flow could often reach here. This class is not meant to be exhaustive in its resolving.
        return "" if only_variable_identifier else match_identifier # identifier_node is a class.
    