from utils.java import aliased_type_to_full_type
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver
from TypeResolver.Java.Base import JavaTypeResolver
from my_types.java import JavaFullType


class JavaCastExpressionTypeResolver(JavaTypeResolver):
    def resolve(self, cast_expression_node: Node) -> JavaFullType:
        type = cast_expression_node.child_by_field_name("type").text.decode("utf8")

        return aliased_type_to_full_type(type, cast_expression_node)
