from TypeResolver.Python.Base import PythonTypeResolver
from TypeResolver.Python.Call import PythonCallResolver
from TypeResolver.Python.Attribute import PythonAttributeResolver
from TypeResolver.Python.Identifier import PythonIdentifierResolver
from my_types.python import python_node_type

class PythonAssignmentResolver(PythonTypeResolver):

    def resolve(self, node, source_identifiers) -> python_node_type:
        identifiers = (node, "")
        right_ids = None
        left_assignment = node.named_children[0]
        if(left_assignment.text == source_identifiers[1]):
            right_assignment = node.named_children[1]
            match right_assignment.type:
                case "call":
                    resolver = PythonCallResolver()
                    identifiers = resolver.resolve(right_assignment)
                case "attribute":
                    resolver = PythonAttributeResolver()
                    identifiers = resolver.resolve(right_assignment)
                case "identifier":
                    resolver = PythonIdentifierResolver()
                    identifiers = resolver.check_scope_up(node.parent, (right_assignment, right_assignment.text), None)
                case _:
                    return (node, "")
        return identifiers