from TypeResolver.Java.utils import JavaTypeResolverTypes
from utils.java import aliased_type_to_full_type

from my_enums.java import type_query
from utils.tree_sitter import *
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver
from utils.java import *
from Context.Java import JavaContext

from my_types.java import JavaFullType


class JavaObjectCreationExpressionTypeResolver(JavaTypeResolver):
    """
    Node examples
    - new A()
    - Z.new X.Y()
    - new A().new B()
    - In general, (maybe_expression).new (scoped or type identifier)()
    """

    def resolve(self, object_creation_expression_node: Node) -> JavaFullType:
        """
        If no left side to resolve first, like in `new A()`, just return `A`'s full type.
        However, in like `Z.new X.Y()`, we have to resolve `Z` first, and then we can simply attach the string X.Y to Z's full type
        """
        query = "(object_creation_expression (_)?@left_side type:[(type_identifier)(scoped_type_identifier)]@right_type)"
        captures = group_by_type_capture_up_to_depth(
            object_creation_expression_node, query, 1
        )
        if "left_side" in captures:
            resolver = JavaContext.componentsFactory.create_type_resolver(
                JavaTypeResolverTypes.from_str(captures["left_side"][0].type)
            )
            left_side_full_type = resolver.resolve(captures["left_side"][0])
            right_side_type = captures["right_type"][0].text.decode("utf8")

        aliased_type_captures = group_by_type_capture_up_to_depth(
            object_creation_expression_node,
            f"(object_creation_expression {type_query})",
            3,
        )

        assert "type" in aliased_type_captures
        type_identifier_node = aliased_type_captures["type"][0]

        assert type_identifier_node
        type_identifier = type_identifier_node.text.decode("utf8")

        return aliased_type_to_full_type(
            type_identifier, object_creation_expression_node
        )
