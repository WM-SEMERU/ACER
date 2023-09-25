'''
Python Support Types
'''

from typing import Dict, List, Literal, Tuple, TypedDict, Union
from my_enums.python import PythonModelTypes
from tree_sitter import Node

from my_types.shared import shorthand, contained_by, method_name, aliased_type

"""
    Python Specific Types
"""

path_name, file_name = str, str

node_text = str

class_container = str



python_full_type = Tuple[path_name, class_container, shorthand]
"""
    The `python_full_type` is the python equivalent of JavaFullType 
    `python_full_type` example: `(Relative/Import/ , Parent.nested, ClassB)`. 
    This corresponds to the type ClassB belonging to the model nested, 
    belonging to the model Parent, within the relative path of Relative/Import/, 
"""


return_types= List[str]
"""
    Return types is a list of strings containg Class Names 
    corresponding to the class type a function is returning 
"""

decorators  = List[str]
"""
    Decorators is a list of strings containg Decorators 
    Changing the Invocation Type of the function it is describing
    Examples Include: @abstractmethod, @staticmethod, and @classmethod
"""


class python_importable_fields(TypedDict):
    type: PythonModelTypes
"""
    Objects that can be imported into a python file, 
    PythonModelTypes include : decorated_definitons (functions with decorators), 
    functions, classes, and expression_statements, and variables (class or global)
"""

class python_function_cache_field(TypedDict):
    return_types: return_types
    decorators: decorators
    type: Literal[PythonModelTypes.FUNCTION]
"""
    Functions have 2 relevant pieces of information 
    for resolving being return types and decorator, 
    which can be used to decide whether a function should include
    an automatic self paramaeter in deciding the value of #arguments,
     or in a call chaining i.e getclass().function() 
"""

class python_variable_cache_field(TypedDict):
    assigned_type: str
    type: Literal[PythonModelTypes.VARIABLE]
"""
    Variables Have only 1 piece of relevant information 
    which is the type they are refering to
"""

class python_class_cache_field(TypedDict):
    class_name : str
    type: Literal[PythonModelTypes.CLASS]
"""
    Classes have one relevant piece of information 
    witch is its own class name
"""

python_model_cache_field = Union[python_class_cache_field, python_function_cache_field, python_variable_cache_field]

python_models_cache = Dict[Tuple[path_name, contained_by, shorthand], python_model_cache_field]
"""
    Stores a mapping of (path, contained_by, shorthand) to one of the cache_field types,
    and example of this might lookg like (path/direcotry, Doctor, Dentist) : Dentist, PythonModelTypes.CLASS
    Where Dentist is a class nested within Doctor located on the path : path/directory. 
"""

path_to_importables = Dict[path_name, Tuple[class_container, shorthand]]

importable_to_contained_by = Dict[shorthand, Tuple[path_name, class_container]];

class python_method_dict_value:
    index : int
    node : Node
    method_name : str
    invoke_type : str
"""
    Type of Value Stored in Key to Value pairing in edge dict, 
    index is the index attributed to the function that is being called 
    (later refered to as the callee_index/caller_index)
    node is the Node refering to the function_defintion
    mathod_name is the name of the method/function
    inovke_type is the invocation type of the call 
"""

class python_edge_dict_value:
    caller_index : int 
    callee_index : int
    invoke_type : str
"""
    Type of Value Stored in Key to Value pairing in edge dict, 
    caller_index is the index attributed to the function in which the call occurs 
    callee_index is the index attributed to the function that is being called 
    inovke_type is the invocation type of the call 
"""

call_text = str

python_node_type = Tuple[Node, node_text]
"""
    Defines the Searching Node Type for 
    souce_identifiers that the Resolvers are trying to find a match for,
"""

python_type_resolver_results = Tuple[path_name, contained_by]
"""
    Defines the path, class_name tuple that is returned by Idenitifer Resovler
"""

python_method_key = Tuple[path_name, file_name, contained_by, method_name]
"""
    Defines Key Type for Key to Value pairing ing method dict
"""

python_method_dict = Dict[python_method_key, python_method_dict_value]
"""
    Method Dict Stores a Key to Value pairing as described above, 
    an example may be 
    ("path/direcotry", "file.py", "ClassName", functionName(), 2) 
        -> "caller_index" : 2 , "callee_index" : 5 , "invoke_type" : "invokestatic"
"""

python_edge_dict = Dict[int, python_edge_dict_value]
"""
    Edge Dict stores a Key to Value pairing with the int value being 
    the nth call found
"""

local_call_cache = Dict[call_text, python_type_resolver_results]

class PythonLocalCache(TypedDict):
    local_call_cahce : local_call_cache


class PythonCache(TypedDict):
    models_cache : python_models_cache
"""
    Python Model Cache 
"""
