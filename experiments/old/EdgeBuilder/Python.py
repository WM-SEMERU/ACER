import os
from collections import defaultdict
from old.Environment import Environment
from utils.tree_sitter import find_closest_ancestor_of_type
from CallNodeResolver.Base import CallNodeTypes
from tree_sitter import Node

from Context.Python import PythonContext
from CallNodeResolver.Python.Base import PythonCallNodeResolver
from utils.tree_sitter import find_closest_ancestor_of_type
from tree_sitter import Node
import logging
from EdgeBuilder.Base import EdgeBuilder

from my_types.python import python_edge_dict, python_method_key

class PythonBuilder(EdgeBuilder):
    ct = 0
    call_node_resolver = PythonCallNodeResolver()

    def buildEdges(self) -> python_edge_dict:
        edge_dict = defaultdict(tuple)
        method_import_q = Environment.language.query("""
            (function_definition
                name: (identifier) @method_name
                parameters: (parameters) @method_params) @method
            (import_statement 
                name: (dotted_name) @import)
            (import_from_statement
                module_name: (dotted_name) @import)
            """)
        call_q = Environment.language.query("""
            (call
                function: [
                    (identifier) @function_name
                    (attribute
                    attribute: (identifier) @function_name)
                ]
                arguments: (argument_list) @arguments) @function
            (assignment
                left: (identifier) @function_name
                right: (lambda
                    parameters: (lambda_parameters) @arguments)
            ) @function
            """)

        for path in PythonContext.files:
            if path.split('.')[-1] != 'py':
                continue
            with open(path, 'rb') as file:
                src = file.read()
                tree = Environment.parser.parse(src)
                captures = method_import_q.captures(tree.root_node)

                method_indices = [i for i, capture in enumerate(
                    captures) if capture[1] == 'method']

                PythonContext.local_path = path

                caller_key : python_method_key
                calleee_key : python_method_key
                
                def create_caller_key(method_node : Node, path : str) -> python_method_key:

                    caller_method_name = method_node.named_children[0].text.decode("utf8") 
                    caller_class = find_closest_ancestor_of_type(method_node, "class_definition")
                    caller_class = caller_class.named_children[0].text.decode(
                        "utf8") if caller_class else ""
                    caller_path_split = os.path.split(path)
                    caller_key = (
                        caller_path_split[0], 
                        caller_path_split[1], 
                        caller_class, 
                        caller_method_name, 
                        )
                    return caller_key
                
                def create_callee_key(path : str, class_name : str, method_name : str) -> python_method_key:
                    callee_path_split = os.path.split(path)
                    callee_key = (
                        callee_path_split[0], 
                        callee_path_split[1], 
                        class_name, 
                        method_name, 
                    )
                    return callee_key		

                for i in method_indices:
                    method_node = captures[i][0]
                    caller_key = create_caller_key(
                                method_node, 
                                path
                            )
                    call_entry = PythonContext.method_dict.get(caller_key)
                    assert(call_entry is not None)
                    caller_index = call_entry.index
                    calls = call_q.captures(method_node)
                    call_indices = [i for i, calls in enumerate(
                        calls) if calls[1] == 'function']
                    for i in call_indices:
                        call_node = calls[i][0]
                        method_name = calls[i+1][0].text.decode("utf8")
                        callee_attributes = self.call_node_resolver.find(call_node)
                        PythonContext.call_cache[
                                        call_node.text.decode("utf-8")
                                    ] = callee_attributes
                        if(not all(map(lambda x: x == "", callee_attributes))):
                            callee_key = create_callee_key(
                                            callee_attributes[0], 
                                            callee_attributes[1], 
                                            method_name
                                        )
                            callee_values = PythonContext.method_dict.get(callee_key)
                            logging.basicConfig(encoding='utf-8', level=logging.INFO)
                            if(callee_values is not None):
                                edge_value = (
                                        caller_index, 
                                        callee_values["index"], 
                                        callee_values["type"]
                                    )
                                edge_dict[self.ct] = edge_value
                                self.ct += 1
                                logging.info("(%d, %d, %s) : Added to Edge Dictionary", 
                                        edge_value[0], 
                                        edge_value[1], 
                                        edge_value[2]
                                    )
                            else:
                                logging.warning("(%s, %s, %s, %s) : Not Found in Method Dictionary", 
                                        callee_key[0], 
                                        callee_key[1], 
                                        callee_key[2], 
                                        callee_key[3]
                                    )

        return dict(edge_dict)
