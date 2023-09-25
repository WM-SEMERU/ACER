import logging
from typing import Tuple
from CallNodeResolver.Python.Base import PythonCallNodeResolver
from Context.Python import PythonContext
from my_enums.python import PythonModelTypes
from utils.python import get_contained_by

class PythonFunctionInvocationResolver(PythonCallNodeResolver):
    def find(self, node) -> Tuple[str, str]:

        identifier_node = node.named_children[0]
        identifer_node_text = identifier_node.text.decode("utf-8")

        global_cache = PythonContext.cache["models_cache"]
        global_cache_value = global_cache.get(
            (PythonContext.local_path, "", identifer_node_text)
        )

        """
            First Check to see if its a function or class 
            defined within file 
        """
        if global_cache_value:
            match global_cache_value["type"]:
                case PythonModelTypes.CLASS:
                    # Class Constructors visible to top level
                    return (PythonContext.local_path, identifer_node_text)
                case PythonModelTypes.FUNCTION:
                    # Function (not contained in a class)
                    return (PythonContext.local_path, "")
                case PythonModelTypes.VARIABLE:
                    logging.warning("Class or Function Expected but received Variable")
                    return ("", "")

        """
            Check for Nested Class Constructors
        """

        contained_by = get_contained_by(node)
        global_cache_value = global_cache.get(
            (PythonContext.local_path, contained_by, identifer_node_text)
        )
        if global_cache_value:
            match global_cache_value["type"]:
                case PythonModelTypes.CLASS:
                    # Class Constructors visible to top level
                    return (PythonContext.local_path, identifer_node_text)
                case PythonModelTypes.FUNCTION:
                    logging.warning("Class Expected but received Variable")
                    return ("", "")
                case PythonModelTypes.VARIABLE:
                    logging.warning("Class or Function Expected but received Variable")
                    return ("", "")

        """
            If not defined within file, must be an imported function
            So Check Imports 
        """
        # TODO implement path to importables

        return ("", " ")
