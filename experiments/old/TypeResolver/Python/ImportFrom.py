from TypeResolver.Python.Base import PythonTypeResolver

from my_types.python import python_node_type

class PythonImportFromResolver(PythonTypeResolver):
	def resolve(self, node, source_identifiers) -> python_node_type:
		identifier = node.named_children[1]
		identifiers = (node, "")
		match identifier.type:
			case "aliased_import":
				resolve_node = identifier if (
					identifier.named_children[1].text == source_identifiers[1]) else node
			case _:
				resolve_node = node
		identifiers = (resolve_node.named_children[0], resolve_node.named_children[0].text) if(
			resolve_node.named_children[1].text == source_identifiers[1] 
			or identifier.named_children[0].text == source_identifiers[1]) else (node, "")
		return identifiers