import json
import os
from packaging import version
import sys


def typeToClassName(type: str): 
    '''
    E.g., from `array_creation_expression` to `ArrayCreationExpressionNode`.
    '''
    return "".join(word.capitalize() for word in type.split("_")) + "Node"

def terminalTypeToTypeStr(json_obj): 

    type_name = "".join(word.capitalize() for word in json_obj["type"].split("_")) + "Node"
    return f"type {type_name} = MyNode"

def productTypeToClassDefStr(json_obj):
    '''
    A product type is a type with fields of other types, and is thus a composite tpe.
    '''
    if not json_obj["named"]: return ""

    class_name = "".join(word.capitalize() for word in json_obj["type"].split("_")) + "Node"
    class_def = f"class {class_name}(MyNode):\n"

    for field, details in json_obj["fields"].items():
        # field_name = "".join(word.capitalize() for word in field.split("_"))
        field_name = field
        # field_type = "".join(word.capitalize() for word in details["types"][0]["type"].split("_")) + "Node"
        field_type = " | ".join([typeToClassName(type["type"]) for type in details["types"] if type["named"]])
        if not field_type: # Field had no named type 
            continue

        if details["multiple"]:
            field_type = f"List[{field_type}]"
        if not details["required"]:
            field_type = f"Optional[{field_type}]"
        class_def += f"    {field_name}: {field_type}\n"

    if "children" in json_obj:
        for typeObj in json_obj["children"]["types"]:
            type, named = typeObj["type"], typeObj["named"]
            if not named: continue
            field_name = f"{type}_list" if json_obj["children"]["multiple"] else type
            field_type = typeToClassName(type)
            if json_obj["children"]["multiple"]:
                field_type = f"List[{field_type}]"
            if not json_obj["children"]["required"]:
                field_type = f"Optional[{field_type}]"
            class_def += f"    {field_name}: {field_type}\n"

    return class_def

def sumTypeToClassDef(json_obj, python_version):
    '''
    A sum type is a type that can be one of several alternative types.
    '''
    if version.parse(python_version) < version.parse("3.5"):
        raise ValueError("Python versions below 3.5 are not supported")

    node_type = "".join(word.capitalize() for word in json_obj["type"].split("_")) + "Node"
    # node_type = json_obj["type"]

    subtypes = []
    for subtype in json_obj["subtypes"]:
        if subtype["named"]:
            subtype_name = "".join(word.capitalize() for word in subtype["type"].split("_")) + "Node"
            subtypes.append(subtype_name)

    if version.parse(python_version) <= version.parse("3.9"):
        return f"type {node_type} = Union[{', '.join(subtypes)}]"
    else:
        return f"type {node_type} = {' | '.join(subtypes)}"

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "node-types.json")

# Load the JSON data from the file
with open(json_path, "r") as f:
    json_arr = json.load(f)


python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

res = [sumTypeToClassDef(json_obj, python_version) if "subtypes" in json_obj else (productTypeToClassDefStr(json_obj) if ("fields" in json_obj and json_obj["fields"] or ("children" in json_obj and json_obj["children"])) else terminalTypeToTypeStr(json_obj)) for json_obj in json_arr if json_obj["named"]]

print(""" 
from typing import Any, List, Optional
from tree_sitter import TreeCursor

class MyNode:
    '''
    `MyNode` is tree-sitter's `Node` but without the `children` array.
    Instead, `MyNode` can directly access children nodes using either their field name (e.g., declarator) or type (e.g., break_statement).

    Further, I also removed the `children` helper methods and properties from MyNode that our CallGraph application never uses.
    For example, we never use `start_byte` and `has_error`. 

    Only purpose of removing these is to make for cleaner auto-suggestions.
    '''
    # @property
    # def start_byte(self) -> int: ...
    # @property
    # def start_point(self) -> tuple[int, int]: ...
    # @property
    # def end_byte(self) -> int: ...
    # @property
    # def end_point(self) -> tuple[int, int]: ...
    # @property
    # def has_changes(self) -> bool: ...
    # @property
    # def has_error(self) -> bool: ...
    # @property
    # def id(self) -> int: ...
    # @property
    # def is_missing(self) -> bool: ...
    # @property
    # def is_named(self) -> bool: ...
    @property
    def child_count(self) -> int: ...
    @property
    def named_child_count(self) -> bool: ...
    @property
    # def children(self) -> list[MyNode]: ...  
    # @property
    # def named_children(self) -> list[MyNode]: ...
    # @property
    def next_named_sibling(self) -> MyNode | None: ...
    @property
    def next_sibling(self) -> MyNode | None: ...
    @property
    def parent(self) -> MyNode | None: ...
    @property
    def prev_named_sibling(self) -> MyNode | None: ...
    @property
    def prev_sibling(self) -> MyNode | None: ...
    @property
    def text(self) -> bytes | Any: ...  # can be None, but annoying to check
    @property
    def type(self) -> str: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def sexp(self) -> str: ...
    def walk(self) -> TreeCursor: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
""")


for ele in res: print(ele)

