from TypeResolver.Java.FormalParameter import JavaFormalParameterTypeResolver
from TypeResolver.Java.LocalVariableDeclaration import (
    JavaLocalVariableDeclarationTypeResolver,
)
from utils.java import aliased_type_to_full_type

from my_enums.java import JavaGrammarKeywords, type_query
from utils.tree_sitter import (
    find_all_children_of_type,
    find_first_child_of_type,
    get_deepest_children,
    find_closest_ancestor_of_type,
    group_by_type_capture_up_to_depth,
)
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver
from TypeResolver.Java.utils import JavaTypeResolverTypes
from Context.Java import JavaContext
from utils.java import *

from my_types.java import JavaFullType

class JavaIdentifierTypeResolver(JavaTypeResolver):
    def resolve(self, identifier_node: Node) -> JavaFullType:
        """
        Resolve steps
        1. Find the usually shorthand, declared type. This can be found in the method args, at the local declaration, or in the field declarations.
        2. Just pass to the corresponding type resolver
        """

        # Parse basic info.
        identifier = identifier_node.text.decode("utf8")

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
                formal_parameter_identifier_node = find_first_child_of_type(
                    node, JavaGrammarKeywords.IDENTIFIER, 1
                )
                formal_parameter_identifier = (
                    formal_parameter_identifier_node.text.decode("utf8")
                    if formal_parameter_identifier_node
                    else ""
                )
                if formal_parameter_identifier == identifier:
                    return JavaFormalParameterTypeResolver().resolve(node)

        # In local declaration
        cur_node = identifier_node
        while cur_node and cur_node.type not in [JavaGrammarKeywords.METHOD_DECLARATION, JavaGrammarKeywords.CONSTRUCTOR_DECLARATION]:
            match cur_node.type: 
                case JavaTypeResolverTypes.LOCAL_VARIABLE_DECLARATION:
                    variable_declarator_node = find_first_child_of_type(
                        cur_node, JavaGrammarKeywords.VARIABLE_DECLARATOR, 1
                    )
                    variable_identifier_node = find_first_child_of_type(
                        variable_declarator_node, JavaGrammarKeywords.IDENTIFIER, 1
                    )
                    variable_identifier = (
                        variable_identifier_node.text.decode("utf8")
                        if variable_identifier_node
                        else ""
                    )
                    if identifier == variable_identifier:
                        return JavaLocalVariableDeclarationTypeResolver().resolve(cur_node)
                case JavaGrammarKeywords.ENHANCED_FOR_STATEMENT: 
                    q = f"""(enhanced_for_statement {type_query} (identifier)@name)"""
                    captures = group_by_type_capture_up_to_depth(cur_node, q, 3)
                    name = captures["name"][0].text.decode("utf8") 
                    if identifier == name: 
                        aliased_type = captures["type"][0].text.decode("utf8")
                        return aliased_type_to_full_type(aliased_type, cur_node)

            if cur_node.prev_named_sibling:
                cur_node = get_deepest_children(cur_node.prev_named_sibling)
            else:
                cur_node = cur_node.parent
        
        # In field declaration, note that we have to potentially iterate through the fields of container model and ancestors
        identifier_container = get_contained_by(identifier_node)
        
        for model in [identifier_container, *traverse_outers_and_ancestors(identifier_container)]:
            cache = JavaContext.cache.models_cache[model]
            if type(cache) is class_cache_field and identifier in cache.fields:
                return aliased_type_to_full_type(cache.fields[identifier]["type"], identifier_node)
            elif type(cache) is interface_cache_field  and identifier in cache.constants:
                return aliased_type_to_full_type(cache.constants[identifier]["type"], identifier_node)

        # Else, the identifier itself is probably already an aliased type, directly, so just resolve it
        return aliased_type_to_full_type(identifier, identifier_node)
