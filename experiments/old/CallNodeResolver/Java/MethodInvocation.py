from CallNodeResolver.utils import InvokeTypes
from CallNodeResolver.Java.Base import JavaCallNodeResolver, JavaCallNodeResolverResults
from tree_sitter import Node
from Context.Java import JavaContext
from TypeResolver.Java.utils import JavaTypeResolverTypes
from my_enums.java import JAVA_ERR_METHOD_KEY, JAVA_ERR_FULL_TYPE
from my_types.java import JavaFullType, JavaMethodKey
from utils.java import get_contained_by, traverse_outers_and_ancestors
from utils.tree_sitter import group_by_type_capture_up_to_depth


class JavaMethodInvocationNodeResolver(JavaCallNodeResolver):
    def find(self, node: Node) -> JavaCallNodeResolverResults:
        # get caller type, method name, and number of args
        captures = group_by_type_capture_up_to_depth(
            node,
            """
                (method_invocation (_)?@caller (identifier)@method_name (argument_list)@argument_list)
            """,
            2,
        )
        method_name = captures["method_name"][len(captures["method_name"])-1].text.decode("utf8")
        argument_list_str = captures["argument_list"][0].text.decode("utf8")
        # with no extra whitespace and the wrapping parenthesis
        argument_list_str = argument_list_str.replace(" ", "")
        n_args = len(
            [
                arg
                for arg in argument_list_str[1 : len(argument_list_str) - 1].split(",")
                if arg
            ]
        )

        caller_res: JavaFullType

        if "caller" not in captures or captures["caller"][0].type == JavaTypeResolverTypes.THIS:
            # implicit or explicit "this"
            # Note that the method might not be its immediate class's, so we iterate through the outer classes 
            # and each of their ancestors and query if the method could belong to the model. 
            call_site_container = get_contained_by(node)
            for model in [call_site_container, *traverse_outers_and_ancestors(call_site_container)]:
                if JavaMethodKey(model, method_name, n_args) in JavaContext.cache.models_cache[model].methods: 
                    caller_res = model
                    break 
            else:
                caller_res = JAVA_ERR_FULL_TYPE
        else: 
            # We dynamically resolve the caller's full type
            caller_node = captures["caller"][0] 
            try:
                caller_type_resolver = JavaContext.componentsFactory.create_type_resolver(
                    JavaTypeResolverTypes.from_str(caller_node.type)
                )
                caller_res = caller_type_resolver.resolve(caller_node)
            except: #TODO: Confidently removing this!
                print(f"Errored occured when figuring out the type of {node.text.decode('utf8')}. Returning temp err key.")
                return {"key": JAVA_ERR_METHOD_KEY}
        if caller_res == JAVA_ERR_FULL_TYPE:
            return {"key": JAVA_ERR_METHOD_KEY}

        key = JavaMethodKey(caller_res, method_name, n_args)

        return {"key": key}