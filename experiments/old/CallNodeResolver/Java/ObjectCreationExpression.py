from CallNodeResolver.Java.Base import JavaCallNodeResolver, JavaCallNodeResolverResults
from tree_sitter import Node
from my_enums.java import JAVA_ERR_METHOD_KEY, JAVA_ERR_FULL_TYPE
from my_types.java import JavaFullType, JavaMethodKey
from src.utils.tree_sitter import find_first_child_of_type
from my_enums.java import JavaGrammarKeywords

class JavaObjectCreationNodeResolver(JavaCallNodeResolver):
    def find(self, node: Node) -> JavaCallNodeResolverResults:
        """
        Returns key to a constructor method.

        Utilizes JavaObjectCreationExpressionTypeResolver.
        However, remember that while JavaObjectCreationExpressionTypeResolver returns the class's full_type,
        JavaObjectCreationNodeResolver wants to return a method_key. So, there's a bit of
        additionally parsing.
        """

        from TypeResolver.Java.ObjectCreationExpression import JavaObjectCreationExpressionTypeResolver

        resolver = JavaObjectCreationExpressionTypeResolver()
        result = resolver.resolve(node)
        if result == JAVA_ERR_FULL_TYPE:
            return {"key": JAVA_ERR_METHOD_KEY}
        _, _, shorthand = result

        argument_list_node = find_first_child_of_type(
            node, JavaGrammarKeywords.ARGUMENT_LIST, 1
        )
        assert argument_list_node
        argument_list_str = argument_list_node.text.decode("utf8")
        # with no extra whitespace and the wrapping parenthesis
        argument_list_str = argument_list_str.replace(" ", "")
        n_args = len(
            [
                arg
                for arg in argument_list_str[1 : len(argument_list_str) - 1].split(",")
                if arg
            ]
        )

        return {"key": JavaMethodKey(result, shorthand, n_args)}
