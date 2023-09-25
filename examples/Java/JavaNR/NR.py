'''
NR and NR from entry.

This algorithm is unexpectedly unsound. This is due to NR ignoring the fact that subclasses inherit methods. 
In bytecode-based generators, parent methods automatically appear in subclasses. 
Source-based generators need to manually fill that in.

RA (Reachability Analysis) is NR but with method inheritances figured out.
'''

import argparse
from collections import defaultdict
from functools import reduce
import logging
import re
from typing import Dict, List, Optional
from tree_sitter import Node
from ..shared import MethodKey, get_contained_by, get_files
from acer import Generator, MethodDictValue, Preprocessor, PreprocessResult
from src.tree_sitter_utils import find_all_children_of_types, find_first_child_of_type
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Script to handle fallback and output file arguments")

parser.add_argument('-o', '--output_path', type=str, required=True,
                    help='The path of the file to write to')
parser.add_argument('input_dir', type=str, help='The path of the directory to analyze')
parser.add_argument('--from-all', dest='from_all', action='store_true', default=False,
                    help='If true, analyze from all methods. Else, start from all methods named "main".')

args = parser.parse_args()

class NRPreprocessor(Preprocessor[MethodKey, str, MethodDictValue]):
    def preprocess(self, files: List[str]) -> PreprocessResult[MethodKey, str, MethodDictValue]:
        file_roots = self.files_to_roots(files)

        return self.make_preprocess_result(file_roots)

    def make_preprocess_result(self, file_nodes: List[Node]) -> PreprocessResult[MethodKey, str, MethodDictValue]:
        method_dict: Dict[MethodKey, MethodDictValue] = defaultdict()
        unique_dict: Dict[str, List[MethodKey]] = defaultdict(list)
        pbar = tqdm(file_nodes, desc="Making method dict")
        for root_node in pbar:
            method_nodes = find_all_children_of_types(root_node, {"method_declaration", "constructor_declaration", "static_initializer"})

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

                    method_params_text = (
                        method_params_node.text.decode("utf8")
                        if method_params_node
                        else ""
                    )
                    method_params_text = method_params_text[1: len(method_params_text) - 1] # remove parens

                    method_params = tuple([arg for arg in method_params_text.split(",") if arg])
                    # Append to method_dict
                    key = MethodKey(
                        method_container,
                        method_name if method_node.type=="method_declaration" else "<init>",
                        method_params,
                    )
                    unique_dict[method_name].append(key)
                    
                if key in method_dict: 
                    logging.warning(f"There is already a method of key {key} cached. The key should be unique. Overriding for now.")
                method_dict[key] = MethodDictValue(method_node)

        return PreprocessResult(method_dict=method_dict, unique_dict=unique_dict)

class NRGenerator(Generator[MethodKey, str, MethodDictValue]):
    def _resolve_call_site(self, call_site: Node, caller_key: Optional[MethodKey] = None):
        blank1: List[MethodKey] = []
        blank2: List[str] = []
        match call_site.type:
            case "method_invocation": 
                method_name_node = call_site.child_by_field_name("name")
                assert method_name_node
                method_name = method_name_node.text.decode("utf8")
                return ([method_name], blank1)

            case "object_creation_expression": 
                type_node = call_site.child_by_field_name("type")
                assert(type_node)
                method_name = ""
                if type_node.type == "scoped_type_identifier": # If "new A.B.C(), grab C"
                    type_identifier_nodes = type_node.children_by_field_name("type_identifier")
                    method_name = type_identifier_nodes[len(type_identifier_nodes) - 1].text.decode("utf8")
                elif type_node.type == "type_identifier": 
                    method_name = type_node.text.decode("utf8")
                return ([method_name], blank1)
            case _: 
                return (blank2, blank1)
    
    def _seek_call_sites(self, caller: Node):
        body = caller.child_by_field_name("body")
        return [(None, v) for v in find_all_children_of_types(body, {"method_invocation", "object_creation_expression"})]
    
call_site_types = ["method_invocation", "object_creation_expression"] # Optional
caller_types = ["method_declaration"] # Optional
def calc_entry_points(preprocessResult: PreprocessResult[MethodKey, str, MethodDictValue]): 
    empty: List[MethodKey] = []
    return list(reduce(lambda acc, cur: [cur, *acc] if cur.method_name == "main" else acc, preprocessResult.method_dict.keys(), empty))

if __name__ == "__main__":
    pre = NRPreprocessor("build/my-languages.so", 'java')

    files = get_files(args.input_dir, re.compile(r'\.java$'))

    generator = NRGenerator(pre, call_site_types, caller_types)

    res = generator.generate(get_files(args.input_dir, include_pat=re.compile(r'\.java$')), lambda p: list(p.method_dict.keys()) if args.from_all else [k for k in p.method_dict if k.method_name=="main"])

    big_print_str = ""
    for from_, tos in res.items():
        from_str = str(from_)
        for to in tos:
            big_print_str += f"{from_str}->{str(to)}\n" 
    with open(args.output_path, "w") as wf: 
        wf.write(big_print_str) 