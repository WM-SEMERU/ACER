from Context.Java import JavaContext
from TypeResolver.Java.utils import JavaTypeResolverTypes
from utils.java import aliased_type_to_full_type
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver
from TypeResolver.Java.Base import JavaTypeResolver
from my_types.java import JavaFullType


class JavaParenthesizedExpressionTypeResolver(JavaTypeResolver):
    def resolve(self, parenthesized_node: Node) -> JavaFullType:
        parenthesized_child = parenthesized_node.named_children[0]
        resolver = JavaContext.componentsFactory.create_type_resolver(
            JavaTypeResolverTypes.from_str(parenthesized_child.type)
        )

        return resolver.resolve(parenthesized_child)
