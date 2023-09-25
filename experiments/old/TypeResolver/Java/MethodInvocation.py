import logging
from utils.java import aliased_type_to_full_type

from my_enums.java import JAVA_ERR_METHOD_KEY
from utils.tree_sitter import *
from tree_sitter import Node
from my_types.java import JavaFullType
from TypeResolver.Java.Base import JavaTypeResolver
from utils.java import *
from CallNodeResolver.Java.MethodInvocation import JavaMethodInvocationNodeResolver

class JavaMethodInvocationTypeResolver(JavaTypeResolver):
    """
    Return the full return type of a.method1()

    Resolving process is similar to MethodInvocationCallNodeResolver, except, after locating the unique method,
    we also get its return type (by querying method_dict). So in fact, I use MethodInvocationCallNodeResolver
    """

    def resolve(self, method_invocation_node: Node) -> JavaFullType:
        call_node_resolver_results = JavaMethodInvocationNodeResolver().find(
            method_invocation_node
        )
        method_key = call_node_resolver_results["key"]
        if method_key == JAVA_ERR_METHOD_KEY:
            return JAVA_ERR_FULL_TYPE
        if method_key not in JavaContext.method_dict:
            logging.warning(f"method_key {method_key} is not found in method_dict. This can happen when a method doesn't exist in the source code (e.g., stdlib functions).")
            return JAVA_ERR_FULL_TYPE
        return_type_short_hand = JavaContext.method_dict[method_key]["return_type"]
        return aliased_type_to_full_type(return_type_short_hand, method_invocation_node)