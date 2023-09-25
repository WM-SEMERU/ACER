from utils.java import get_contained_by
from tree_sitter import Node
from TypeResolver.Java.Base import JavaTypeResolver

from my_types.java import JavaFullType


class JavaThisTypeResolver(JavaTypeResolver):
    def resolve(self, context_node: Node) -> JavaFullType:
        """
        Simply returns the full type of the closest containing model. 
        In this manner, the ThisTypeResolver is quite special since it doesn't require a node of type "this" as the input.
        It really is just `aliased_type_to_full_type` but simplified, since we know where the full type is already. 
        """
        return get_contained_by(context_node)
