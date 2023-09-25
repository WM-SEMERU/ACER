from TypeResolver.Python.Base import PythonTypeResolver
from utils.python import * 

from my_types.python import *

class PythonIdentifierResolver(PythonTypeResolver):

        
    def resolve(self, node) -> python_type_resolver_results:
        #type_node checks the type of the call (ex: a.functionM() -> Method, functionM() -> Function)   
        source_node = find_first_child_of_type(node, "attribute", 1)
        check_class =  source_node is not None
        source_node = find_first_child_of_type(source_node, "identifier", 1) if(
            check_class) else find_first_child_of_type(node, "identifier", 1)
        if source_node is None:
            return ("", "")
        source_identifiers = (source_node, source_node.text)
        class_name = self.check_scope_up(node, source_identifiers, "expression_statement") if(
            check_class) else (node, "")
        #Must Start from Function_definition for recursive case
        if(check_class):
            path_name = "" if(
                class_name[1] == "") else self.check_scope_all(node, class_name, "function_definition")
        else:
            path_name = self.check_scope_all(node, source_identifiers, "function_definition")

        class_name = class_name[0].text.decode("utf8") if(
            class_name[1] != "") else ""
        if(path_name):
            path_name = path_name[0].text.decode("utf-8").replace(".", "\\") + ".py" if(
                path_name[1] != "sp") else path_name[1]
        return (path_name, class_name)

    """
	A function that redirects the code to the 
	correct resolver based on the node type
	PARAMETER
	node : current searching node 
	source_node : text program is searching for a match 
	"""
    def handle_type(self, node, source_identifiers) -> python_node_type:
        from TypeResolver.Python.Assignment import PythonAssignmentResolver
        from TypeResolver.Python.ImportFrom import PythonImportFromResolver
        
        identifiers = (node, "")
        match node.type:
            case "function_definition":
                # Called Function is within same file
                if(node.named_children[0].text == source_identifiers[1]):
                    return (node, "sp")
            case "class_definition":
				# Called Method is within a class in the same file
                if(node.named_children[0].text == source_identifiers[1]):
                    return (node, "sp")
            case "import_from_statement":
				# Attempt to find Called Method's Class or Path is located Within an imported Module 
                from_import_resolver = PythonImportFromResolver()
                identifiers = from_import_resolver.resolve(node, source_identifiers)
            case "import_statement":
			    #TODO add import statement Resolver
                pass
            case "expression_statement":
				#Attempt to find Called Method's Class In A Assignment 
                assignment_resolver = PythonAssignmentResolver()
                identifiers = assignment_resolver.resolve(node.named_children[0], source_identifiers) if(
					node.named_children[0].type == "assignment") else (node, "")
            case "for_statement":
                #TODO add for statement Resolver
                pass
            case "attribute":
                #TODO add attribute statement Resolver
                pass
        return identifiers

    """
	Previous : (Above the node statement in the Code)
	A function that first checks nodes next to it on the 
	Tree, before checking Nodes previous to them 
	Python Prioritizes the Most recent declaration when determining 
	Call Resolution within scopes outside of a local method/function scope
	If not found next to (below in cod), Checks previous nodes for a match 
	PARAMETERS
	node : current searching node 
	source_node : node program is searching for a match 
	scope : Scope Level Program Needs to Search 
	"""
    def check_scope_all(self, node, source_identifiers, scope) -> python_node_type:
        identifiers = (node, "")
        global_scope = find_closest_ancestor_of_type(node, scope)
        if global_scope is None:
            return identifiers
        while(global_scope.next_named_sibling and (identifiers[1] == "")):
            global_scope = global_scope.next_named_sibling
            identifiers = self.handle_type(global_scope, source_identifiers)
        if(identifiers[1] == ""):		
            identifiers = self.check_scope_up(node, source_identifiers, scope)
        return identifiers

    """
	Previous : (Above the node statement in the Code)
	
	Checks Nodes Previous to the Searching Node
	If No Node on that level is found it recursively calls
	the parent of searching node until a match is found
	PARAMETERS
	node : current searching node 
	source_node : node program is searching for a match 
	scope : Scope Level Program Needs to Search 
	"""
    def check_scope_up(self, node, source_identifiers, scope) -> python_node_type:
        identifiers = (node, "")
        local_scope = find_closest_ancestor_of_type(node, scope) if(
            scope) else node
        if local_scope is None:
            return identifiers
        while(local_scope.prev_named_sibling and (identifiers[1] == "")):
            local_scope = local_scope.prev_named_sibling
            identifiers = self.handle_type(local_scope, source_identifiers)
        if(identifiers[1] == ""):
            assert(local_scope.parent is not None)
            identifiers = self.check_scope_all(local_scope, source_identifiers, local_scope.parent.type) if(
				local_scope.parent.type != "module") else (node, "")
        return identifiers
        