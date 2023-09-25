from Context.Python import PythonContext
from utils.python import get_containing_calls
from typing import Tuple
from CallNodeResolver.Python.Base import PythonCallNodeResolver


class PythonMethodInvocationResolver(PythonCallNodeResolver):

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

    def find(self, node) -> Tuple[str, str]:
        global_cahe = PythonContext.cache
        identifiers = PythonContext.call_cache.get(node.text.decode("utf-8"))
        if identifiers:
            return identifiers
        identifiers = ("", "")
        calls = get_containing_calls(node)

        class_name = PythonContext.call_cache.get(node.text.decode("utf-8"))

        return ("", " ")