'''
Java Support Types
'''

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Set, Tuple, TypedDict, Union, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from my_enums.java import JavaModelTypes


package_name = str

"""
The containers of the shorthand. E.g., if C is declared within B and B is declared within A, 
the containers of C is A.B, and so its `contained_by` is A.B.
"""

"""
The shorthand is never nested, it is the most abbreviated way a type can be aliased. 
The type A.B.C has type C.
"""

class JavaFullType(NamedTuple):
    package_name: str
    contained_by: str 
    shorthand: str

    def __bool__(self): 
        return not (self.package_name == "" and self.contained_by == "" and self.shorthand == "")
    
    def __str__(self) -> str:
        return str((self.package_name, self.contained_by, self.shorthand))
        

"""
The `JavaFullType` is required to ascertain the uniqueness of a type.

`JavaFullType` example: `(edu.com, Parent.nested, ClassB)`. This corresponds to the type ClassB belonging to the model nested, 
belonging to the model Parent, belonging to the package edu.com. Btw, a model is a class, interface, or enum.
"""

aliased_type = str
'''
Str of types that look like: "A", "B.A", "C.A.B". Empty string permitted. 
The `aliased_type` could in fact be representative of the full type.
'''

class importable_fields(TypedDict):
    type: "JavaModelTypes"
    modifiers: List[str]
    # file_path: str

packages_to_importables = Dict[package_name, List[JavaFullType]]

class model_field_items(TypedDict):
    type: str
    modifiers: List[str]

@dataclass
class class_cache_field():
    fields: Dict[str, "model_field_items"]
    extends: Optional[JavaFullType]
    implements: List[JavaFullType]
    type: "Literal[JavaModelTypes.CLASS]"
    modifiers: List[str]
    methods: Set["JavaMethodKey"]

@dataclass
class interface_cache_field():
    constants: Dict[str, "model_field_items"]
    extends: List[JavaFullType]
    type: "Literal[JavaModelTypes.INTERFACE]"
    modifiers: List[str]
    methods: Set["JavaMethodKey"]

@dataclass
class enum_cache_field():
    enum_constants: Set[str]
    implements: List[JavaFullType]
    modifiers: List[str]
    type: "Literal[JavaModelTypes.ENUM]"
    methods: Set["JavaMethodKey"]

model_cache_field = Union[class_cache_field, interface_cache_field, enum_cache_field]

models_cache = Dict[JavaFullType, model_cache_field]

method_params_count = int

### Java cache
@dataclass
class JavaCache():
    packages_to_importables: packages_to_importables
    # model is my umbrella term for class, interface, and enum,inspired by: https://stackoverflow.com/a/12405590/9007785
    models_cache: models_cache

### Java method dict
from tree_sitter import Node

class JavaMethodDictValue(TypedDict):
    node: Node
    modifiers: List[str]
    return_type: str
"""
Java's `method_dict` keeps a mapping between unique method identifiers to the underlying method nodes
"""

class JavaMethodKey(NamedTuple):
    contained_by: JavaFullType
    method_name: str 
    method_params_count: int

    def __str__(self) -> str:
        return f"({self.contained_by.package_name}, {'.'.join(filter(None, [self.contained_by.contained_by, self.contained_by.shorthand]))}, {self.method_name}, {self.method_params_count})"
"""
E.g., (JavaFullType(com.project, _, ClassA), ClassA, 0) represents the constructor method of ClassA.
"""


JavaMethodDict = Dict[JavaMethodKey, JavaMethodDictValue]

java_edge_dict = Dict[JavaMethodKey, Set[JavaMethodKey]]
'''
Java's `edge_dict` models a call graph, and uses an adjacency list to do so.
'''
