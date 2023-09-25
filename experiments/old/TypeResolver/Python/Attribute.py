from TypeResolver.Python.Base import PythonTypeResolver
from TypeResolver.Python.Identifier import PythonIdentifierResolver 

from my_types.python import *


class PythonAttributeResolver(PythonTypeResolver):
    def resolve(self, attribute_node) -> python_node_type:
        identfiers = (attribute_node, "")
        def handle_attribute(node, left_attribute, right_attribute) -> python_node_type:
            left_attribute_text = left_attribute.text.decode("utf8") if(
			    left_attribute) else None
            identifier_resolver = PythonIdentifierResolver()
            identifiers = (node, "")
            match left_attribute_text:
                case "self":
                    identifiers = identifier_resolver.check_scope_all(
                        node, (right_attribute, right_attribute.text), "function_definition")
                case "cls":
                    identifiers = identifier_resolver.check_scope_all(
                        node, (right_attribute, right_attribute.text), "function_definition")
                case None: 
                    identifiers = identifier_resolver.check_scope_all(
                        node, (right_attribute, right_attribute.text), "function_definition")
                case _:
                    pass
            return identifiers

        left_attribute = attribute_node.named_children[0]if(
            attribute_node.named_child_count > 1) else None
        right_attribute = attribute_node.named_children[attribute_node.named_child_count - 1]
        identifiers = handle_attribute(attribute_node.parent, left_attribute, right_attribute)

        return identifiers