from TypeResolver.Java.utils import JavaTypeResolverTypes
from utils.java import aliased_type_to_full_type

from my_enums.java import type_query
from Context.Java import JavaContext
from utils.tree_sitter import (
    group_by_type_capture_up_to_depth,
)
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver

from my_types.java import JavaFullType


class JavaLocalVariableDeclarationTypeResolver(JavaTypeResolver):
    def resolve(self, local_variable_declaration_node: Node) -> JavaFullType:
        """
        Try to return the type of the right hand side's expression.
        Because `Cat c = new BaseAnimal()` is valid, and should be regarded as type `BaseAnimal`.
        If no right hand side, return full type of the left hand symbol.
        """

        # TODO: Think about if this TypeResolver should just delegate work to a "JavaVariableDeclaratorTypeResolver"
        # As of right now, I think there's no need to go that modular.

        # If right hand side, pass work to right hand side's type resolver
        captures = group_by_type_capture_up_to_depth(
            local_variable_declaration_node,
            "(local_variable_declaration (variable_declarator (identifier) (_)@right_hand_side))",
            2,
        )

        # IMPORTANT: Always use the right hand side first, if possible. This allows us a more accurate analysis. 
        # E.g., if ```Shape p = new Circle();``` is interpretted such that `p` is a `Circle`, 
        # then, `p.draw()` represents a more accurate `Circle.draw` rather than `Shape.draw`.
        if "right_hand_side" in captures:
            resolver = JavaContext.componentsFactory.create_type_resolver(
                JavaTypeResolverTypes.from_str(captures["right_hand_side"][0].type)
            )
            rhs_type = resolver.resolve(captures["right_hand_side"][0])
            if rhs_type: return rhs_type # Only return rhs type is resolved. This avoids problems like early returning on ```Shape p = null;```
        
        # If no rhs (or rhs is null), grab the aliased type and resolve its full type
        aliased_type_capture = group_by_type_capture_up_to_depth(
            local_variable_declaration_node,
            f"(local_variable_declaration {type_query})",
            3,
        )
        assert "type" in aliased_type_capture

        assert local_variable_declaration_node.parent

        aliased_type_str = aliased_type_capture["type"][0].text.decode("utf8")
        return aliased_type_to_full_type(
            aliased_type_str, local_variable_declaration_node.parent
        )
