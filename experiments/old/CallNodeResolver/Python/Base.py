from typing import Tuple
from CallNodeResolver.Base import CallNodeResolver
from tree_sitter import Node
from Context.Python import PythonContext
from CallNodeResolver.utils import CallNodeTypes


class PythonCallNodeResolver(CallNodeResolver):

    """
    Method for Calls in the format caller.function()
    TODO test for xxx.caller.function()
    Resolving class name
        #Starts from call statement (i.e the a.function()) to then search up
        #for the closest assignment that a is defined in or if a is a class
        #the import statement the class is imported from
    Locates the identity of a in a.function(), where a = .xxx.caller
    As well as the path leading to a
    PARAMETERS
    node: Searching Node
    """
    @staticmethod 
    def makeSpecificCallNodeResolver(callNodeType: CallNodeTypes):
        return PythonCallNodeResolver()

    def find(self, node: Node) -> Tuple[str, str]:
        from CallNodeResolver.Python.FunctionInvocation import PythonFunctionInvocationResolver
        from CallNodeResolver.Python.MethodInvocation import PythonMethodInvocationResolver
        global_cahe = PythonContext.cache
        resolver = (
            PythonMethodInvocationResolver()
            if (node.named_children[0].type == "attribute")
            else PythonFunctionInvocationResolver()
        )
        identifiers = resolver.find(node)

        return identifiers