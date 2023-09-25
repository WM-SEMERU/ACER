from TypeResolver.Python.Base import PythonTypeResolver

from my_types.python import python_node_type


class PythonCallResolver(PythonTypeResolver):
	def resolve(self, call_node) -> python_node_type:
		#container = call_node.named_children[0] if(
			#call_node.named_child_count > 2) else None
		called = call_node.named_children[call_node.named_child_count - 2]
		#arguments = node.named_children[call_node.named_child_count - 1]
		return (called, called.text)
