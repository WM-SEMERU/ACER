'''
SCHA (Simple Class Hierarchy Analysis) and SCHA from entry. 
SCHA won't be found in the literature since I came up with it. It's unique to source-level callgraph analysis.
It is simple in that classes are verified by only their shorthand. This is sounds since it over-estimates. 

For example, for a call_site like `a.b()`, where `a` turns out to be a `foo.MyClass`, the call_site is 
considered to be executing `MyClass.b` (not `foo.MyClass.b`). This can save significant preprocessing time — 
which you can observe by inspecting the difference of SCHA and CHA.

SCHA is strictly sounder than NR, since, NR actually doesn't consider inherited methods.
'''

import argparse
from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from itertools import chain
import logging
import re
from typing import Dict, List, NamedTuple, Optional, Tuple

from tree_sitter import Node

from .IdentifierAliased import JavaIdentifierTypeResolver
from acer import MethodDictValue, Preprocessor, TraversalMethod, logging_levels
from ..shared import FullType, MethodKey, count_args, get_contained_by, get_files, get_package_name, JavaGrammarKeywords, group_by_type_capture_up_to_depth
from acer import Generator, PreprocessResult, Preprocessor
from src.tree_sitter_utils import find_all_ancestors_of_types, find_all_children_of_types, find_first_child_of_type

parser = argparse.ArgumentParser(description="Script to handle fallback and output file arguments")

# Adding the 'fallback' argument
parser.add_argument('--fallback', dest='fallback', action='store_true',
                    help='whether or not to fall back to NR. Default is False.')
parser.add_argument('--no-fallback', dest='fallback', action='store_false')
parser.set_defaults(fallback=False)
parser.add_argument('-o', '--output_path', type=str, required=True,
                    help='The path of the file to write to')
parser.add_argument('input_dir', type=str, help='The path of the directory to analyze')
parser.add_argument('--only_variable_identifier', dest="only_variable_identifier", action='store_true', help='Only analyze variable identifier receivers')
parser.add_argument('--from-all', dest='from_all', action='store_true', default=False,
                    help='If true, analyze from all methods. Else, start from all methods named "main".')

args = parser.parse_args()

@dataclass 
class HierarchyValue():
    parents: List[str]
    children: List[str]

class models_cache(NamedTuple):
    alias2full: Dict[str, List[FullType]]
    hierarchy: Dict[str,  HierarchyValue] # Parent type -> Sub types

@dataclass
class MyMethodDictValue(MethodDictValue):
    inherited: bool

class AlmostKey(NamedTuple):
    contained_by: FullType
    method_name: str 
    method_params_count: int


@dataclass
class SCHAPreprocessResult(PreprocessResult[MethodKey, AlmostKey, MyMethodDictValue]): 
    models_cache: models_cache
    nr_unique_dict: Dict[Tuple[str, int], List[MethodKey]] # extra caching for when falling back to nr

def get_full(l: List[str], cache: models_cache) -> List[FullType]:
    return list(chain(*filter(None, [cache.alias2full.get(alias, None) for alias in l])))

def get_subtypes(base: str, cache: models_cache) -> List[str]: 
    def _recur(t: str, traversed: List[str]) -> List[str]:
        if t in traversed: return []
        traversed.append(t)
        subtypes = chain(*map(lambda n: _recur(n, traversed), cache.hierarchy[t].children))
        return [t, *subtypes]
    return _recur(base, [])[1:]

def get_supertypes(base: str, cache: models_cache) -> List[str]: 
    def _recur(t: str, traversed: List[str]) -> List[str]:
        if t in traversed: return []
        traversed.append(t)
        supertypes = chain(*map(lambda n: _recur(n, traversed), cache.hierarchy[t].parents))
        return [t, *supertypes]
    return _recur(base, [])[1:] 

class SCHAPreprocessor(Preprocessor[MethodKey, AlmostKey, MyMethodDictValue]):
    def preprocess(self, files: List[str]) -> SCHAPreprocessResult:
        file_roots = self.files_to_roots(files)
        self.models_cache = self.make_models_cache(file_roots)
        preprocessRes, nr_unique_dict = self.make_preprocess_result(file_roots)
        return SCHAPreprocessResult(preprocessRes.method_dict, preprocessRes.unique_dict, self.models_cache, nr_unique_dict) 

    def make_preprocess_result(self, file_nodes: List[Node]) -> Tuple[PreprocessResult[MethodKey, AlmostKey, MyMethodDictValue], Dict[Tuple[str, int], List[MethodKey]]]:
        method_dict: Dict[MethodKey, MyMethodDictValue] = defaultdict()
        unique_dict: Dict[AlmostKey, List[MethodKey]] = defaultdict(list)
        nr_unique_dict: Dict[Tuple[str, int], List[MethodKey]] = defaultdict(list)
        class2Mkeys: Dict[FullType, List[MethodKey]] = defaultdict(list)
        for root_node in file_nodes:
            method_nodes = find_all_children_of_types(root_node, {"method_declaration", "constructor_declaration"})

            for method_node in method_nodes:
                method_container = get_contained_by(method_node)
                if method_node.type == "static_initializer": 
                    key = MethodKey(method_container, "<clinit>", tuple())
                else:
                    method_name_node = find_first_child_of_type(
                        method_node, "identifier", 1
                    )
                    method_name = (
                        method_name_node.text.decode("utf8") if method_name_node else ""
                    )
                    assert method_node.parent and method_node.parent.parent
                    if method_node.parent.parent.type not in ["class_declaration", "interface_declaration"]: 
                        logging.warning(f"Skipping over method \"{method_name}\". This preprocessor is not suited to classify non-traditional methods like SAM.")
                        continue
                    method_params_node = find_first_child_of_type(
                        method_node, "formal_parameters", 1
                    )

                    method_container = get_contained_by(method_node)

                    method_params_text = (
                        method_params_node.text.decode("utf8")
                        if method_params_node
                        else ""
                    )
                    method_params_text = method_params_text[1: len(method_params_text) - 1] # remove parens

                    method_params = tuple([arg for arg in method_params_text.split(",") if arg])

                    # Append to method_dict, this is where the over-approximation of SCHA comes in!
                    key = MethodKey(
                        method_container,
                        method_name if method_node.type=="method_declaration" else "<init>",
                        method_params,
                    )
                    almost_key = AlmostKey(method_container, method_name, len(method_params))
                    class2Mkeys[method_container].append(key)
                    nr_unique_dict[(method_name, len(method_params))].append(key)
                    unique_dict[almost_key].append(key)
                
                if key in method_dict: 
                    logging.warning(f"There is already a method of key {key} cached. The key should be unique. Overriding for now.")
                method_dict[key] = MyMethodDictValue(node=method_node, inherited=False)

        for class_, mkeys in class2Mkeys.items():
            subtypes = get_full(get_subtypes(class_.shorthand, self.models_cache), self.models_cache)

            for st in subtypes: 
                for mkey in mkeys: 
                    if (st, mkey.method_name, mkey.method_params) not in method_dict:
                        # TODO: Technically, class_node should be the closest one, and that might not be the root!
                        # For example, say we have hierarchy A -> B -> C. If we come to subtype C of A, and C.method doesn't exist, 
                        # we currently assign A.method node to C.method. 
                        class_node = method_dict[MethodKey(class_, mkey.method_name, mkey.method_params)].node
                        method_dict[MethodKey(st, mkey.method_name, mkey.method_params)] = MyMethodDictValue(node=class_node, inherited=True)
                        unique_dict[AlmostKey(st, mkey.method_name, len(mkey.method_params))].append(MethodKey(st, mkey.method_name, mkey.method_params))
        return (PreprocessResult(method_dict, unique_dict), nr_unique_dict)

    def make_models_cache(self, file_nodes: List[Node]) -> models_cache:
        alias2full: Dict[str, List[FullType]] = defaultdict(list)
        hierarchy: Dict[str, HierarchyValue] = defaultdict(lambda: HierarchyValue([], []))
        for file_node in file_nodes: 
            package = get_package_name(file_node)
            top_model_nodes = find_all_children_of_types(file_node, {"class_declaration", "interface_declaration"})
            for model_node in top_model_nodes: 
                model_identifier_node = model_node.child_by_field_name("name")
                assert model_identifier_node
                model_shorthand = model_identifier_node.text.decode("utf8") # The declaration uses the shorthand
                containing_models_nodes = reversed(
                    find_all_ancestors_of_types(
                        model_node,
                        [
                            JavaGrammarKeywords.CLASS_DECLARATION,
                            JavaGrammarKeywords.INTERFACE_DECLARATION,
                        ],
                    )
                )
                model_containers_names_nodes = map(
                    lambda node: node.child_by_field_name(JavaGrammarKeywords.IDENTIFIER),
                    containing_models_nodes,
                )
                model_containers_names = map(
                    lambda node: node.text.decode("utf8") if node else "",
                    model_containers_names_nodes,
                )
                model_container = ".".join(list(model_containers_names))

                alias2full[model_shorthand].append(FullType(package, model_container, model_shorthand))

                if model_node.type == JavaGrammarKeywords.CLASS_DECLARATION:
                    inheritance_query = "(class_declaration (modifiers)?@modifiers (superclass (type_identifier)@super_class)? (super_interfaces (type_list (type_identifier)@interface))?)"
                    inheritance_captures = group_by_type_capture_up_to_depth(
                        model_node, inheritance_query, 3, self.language
                    )

                    super_class: Optional[str] = None
                    implements: List[str] = []
                    if "super_class" in inheritance_captures:
                        super_class = inheritance_captures["super_class"][
                            0
                        ].text.decode("utf8")
                    if "interface" in inheritance_captures:
                        implements = list(
                            filter(None, map(
                                lambda n: n.text.decode("utf8"),
                                inheritance_captures["interface"],
                            ))
                        )
                    for parent in list(filter(None, [super_class, *implements])):
                        hierarchy[model_shorthand].parents.append(parent)
                        hierarchy[parent].children.append(model_shorthand)

                elif model_node.type == JavaGrammarKeywords.INTERFACE_DECLARATION:
                    inheritance_query = "(extends_interfaces (type_list (type_identifier)@interface))"
                    inheritance_captures = group_by_type_capture_up_to_depth(
                        model_node, inheritance_query, 3, self.language
                    )

                    extend_interfaces: List[str] = (
                        list(
                            filter(None, map(
                                lambda n: n.text.decode("utf8"),

                                inheritance_captures["interface"],
                            ))
                        )
                        if "interface" in inheritance_captures
                        else []
                    )
                    for parent in extend_interfaces: 
                        hierarchy[model_shorthand].parents.append(model_shorthand)
                        hierarchy[parent].children.append(model_shorthand)


        return models_cache(alias2full, hierarchy)
    
@dataclass 
class Metric(): 
    # call_site_type: int -- Shouldn't be possible that a 
    unhandled_receiver_misses: int
    edges_from_nr_fallback: int
    method_invocation_edges: int 
    object_creation_expression_edges: int

class SCHAGenerator(Generator[MethodKey, AlmostKey, MyMethodDictValue]):
    def __init__(self, preprocessor: Preprocessor[MethodKey, AlmostKey, MyMethodDictValue], call_site_types: List[str] = ..., caller_types: List[str] = ..., logging_level: logging_levels = "INFO", traversal_method: TraversalMethod = "BFS") -> None:
        super().__init__(preprocessor, call_site_types, caller_types, logging_level, traversal_method)
        self.metrics = Metric(0, 0, 0, 0)
    def _seek_call_sites(self, caller: Node):
        return [(None, v) for v in find_all_children_of_types(caller, {"method_invocation", "object_creation_expression"})]


    def _resolve_call_site(self, call_site: Node, caller_key: MethodKey | None = None) -> Tuple[List[AlmostKey], List[MethodKey]]:
        self.preprocessor: SCHAPreprocessor # For type-checking purposes
        self.preprocessorResults: SCHAPreprocessResult # For type-checking purposes
        models_cache = self.preprocessorResults.models_cache
        
        match call_site.type:
            case "method_invocation": 
                method_name_node = call_site.child_by_field_name("name")
                assert method_name_node
                method_name = method_name_node.text.decode("utf8")
                method_caller = call_site.child_by_field_name("object")
                method_arguments = call_site.child_by_field_name("arguments")
                assert method_arguments
                n_args = count_args(method_arguments)
                if method_caller:
                    if method_caller.type == "identifier": # a.b() | Suppose that "a" is instance of class A and that B, C inherit from A.
                        caller_shorthand_type = JavaIdentifierTypeResolver().resolve(method_caller, args.only_variable_identifier) # A
                        subtypes = get_subtypes(caller_shorthand_type, models_cache) # B, C
                        class_types = get_full([caller_shorthand_type, *subtypes], models_cache) # [(_._.A), (_._.B), (_._.C)]
                    else: 
                        self.metrics.unhandled_receiver_misses += 1
                        # fallback to NR
                        nr_keys = self.preprocessorResults.nr_unique_dict.get((method_name, n_args), [])
                        self.metrics.edges_from_nr_fallback += len(nr_keys)
                        self.metrics.method_invocation_edges += len(nr_keys)
                        if args.fallback:
                            return ([], nr_keys)
                        else: 
                            return ([], [])
                else: # b(), note that b() could be defined in a lot of places.
                    # TODO: This only sources through super classes. For no-caller methods, they may be actually be invoking some container class's method.
                    method_contained_by = get_contained_by(call_site)
                    subtypes_full =  get_full(get_subtypes(method_contained_by.shorthand, models_cache), models_cache)
                    class_types = [method_contained_by, *subtypes_full]
                
                keys = [AlmostKey(class_, method_name, n_args) for class_ in class_types]
                self.metrics.method_invocation_edges += len(keys)
                return (keys, [])


            case "object_creation_expression": 
                type_node = call_site.child_by_field_name("type")
                assert(type_node)
                class_name = ""
                method_arguments = call_site.child_by_field_name("arguments")
                assert method_arguments
                n_args = count_args(method_arguments)
                if type_node.type == "scoped_type_identifier": # If "new A.B.C(), grab C"
                    type_identifier_nodes = type_node.children_by_field_name("type_identifier")
                    class_name = type_identifier_nodes[len(type_identifier_nodes) - 1].text.decode("utf8")
                elif type_node.type == "type_identifier": 
                    class_name = type_node.text.decode("utf8")
                class_types = get_full([class_name], models_cache)
                keys = [AlmostKey(class_, "<init>", n_args) for class_ in class_types]
                self.metrics.object_creation_expression_edges += len(keys)
                return (keys, [])
            case _: 
                # self.metrics.call_site_type += 1
                return ([], [])
    

call_site_types = ["method_invocation", "object_creation_expression"] # Optional
caller_types = ["method_declaration"] # Optional
def calc_entry_points(preprocessResult: PreprocessResult[MethodKey, AlmostKey, MyMethodDictValue]): 
    empty: List[MethodKey] = []
    return list(reduce(lambda acc, cur: [cur, *acc] if cur.method_name == "main" else acc, preprocessResult.method_dict.keys(), empty))


if __name__ == "__main__":
    pre = SCHAPreprocessor("build/my-languages.so", 'java')
    # logging.info("yoo")

    # Testing on test/repos/guava-retrying
    # files = get_files("test/repos/guava-retrying", re.compile(r'\.java$'))
    # file = "src/new_framework/examples/JavaSCHA/test.java"
    generator = SCHAGenerator(pre, call_site_types, caller_types)
    res = generator.generate(get_files(args.input_dir, include_pat=re.compile(r'\.java$')), lambda p: list(p.method_dict.keys()) if args.from_all else [k for k in p.method_dict if k.method_name=="main"])
    
    big_print_str = ""
    for from_, tos in res.items():
        from_str = str(from_)
        for to in tos:
            big_print_str += f"{from_str}->{str(to)}\n" 
    with open(args.output_path, "w") as wf: 
        wf.write(big_print_str) 
    # print("total edges:", sum(len(edges) for edges in res.values()))
    # pprint(generator.metrics)