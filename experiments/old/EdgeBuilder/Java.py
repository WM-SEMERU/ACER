import logging
from collections import defaultdict
from EdgeBuilder.Base import EdgeBuilder
from Context.Java import JavaContext
from CallNodeResolver.utils import CallNodeTypes
from tree_sitter import Node
from my_enums.java import JAVA_ERR_METHOD_KEY, JavaGrammarKeywords

from utils.java import (
    formal_parameters_count,
    get_contained_by,
)
from utils.tree_sitter import find_closest_ancestor_of_type, find_first_child_of_type

from my_types.java import JavaFullType, java_edge_dict, JavaMethodKey
from old.Environment import Environment

class JavaEdgeBuilder(EdgeBuilder):
    def buildEdges(self) -> java_edge_dict:
        query = Environment.language.query(
            """
            (method_invocation
                name: (identifier) @function_name
                arguments: (argument_list)) @method_invocation
            (object_creation_expression
                type: [(generic_type) (type_identifier) (scoped_type_identifier)]
                arguments: (argument_list)) @object_creation_expression
            """
        )
        edge_dict: java_edge_dict = defaultdict(set)
        for path in JavaContext.files:
            print(f"Building edge in file {path}")
            with open(path, "rb") as file:
                src = file.read()
                tree = Environment.parser.parse(src)
                captures = query.captures(tree.root_node)
                for i in range(len(captures)):
                    callee: Node = captures[i][0]
                    type = captures[i][1]
                    if type not in CallNodeTypes:
                        continue

                    callee_container = get_contained_by(callee)

                    containing_method_node = find_closest_ancestor_of_type(
                        callee, JavaGrammarKeywords.METHOD_DECLARATION
                    ) or find_closest_ancestor_of_type(
                        callee, JavaGrammarKeywords.CONSTRUCTOR_DECLARATION
                    )
                    containing_method_name_node = find_first_child_of_type(
                        containing_method_node, JavaGrammarKeywords.IDENTIFIER, 1
                    )
                    if not (containing_method_node and containing_method_name_node):
                        print(
                            f"Warning: The following method is ignored because it is not contained within a function\n\t{callee.text}\n "
                        )
                        continue
                    assert containing_method_node and containing_method_name_node
                    containing_method_name = containing_method_name_node.text.decode(
                        "utf8"
                    )
                    containig_method_params_node = find_first_child_of_type(
                        containing_method_node, JavaGrammarKeywords.FORMAL_PARAMETERS, 1
                    )
                    assert containig_method_params_node
                    containing_method_param_count = formal_parameters_count(
                        containig_method_params_node
                    )
                    callerKey = JavaMethodKey(
                        callee_container,
                        containing_method_name,
                        containing_method_param_count,
                    )
                    CallNodeResolver = (
                        JavaContext.componentsFactory.create_call_node_resolver(
                            CallNodeTypes.from_str(type)
                        )
                    )
                    calleeKey = CallNodeResolver.find(callee)["key"]

                    if calleeKey != JAVA_ERR_METHOD_KEY:
                        print(f"new edge: {callerKey} : {calleeKey}")
                        edge_dict[callerKey].add(calleeKey)
                    else: 
                        logging.debug(f"An edge couldn't be drawn between {callerKey} and callee {callee.text.decode('utf8')} because the callee couldn't be resolved.")

        return dict(edge_dict)

