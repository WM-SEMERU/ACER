from abc import ABC
from tree_sitter import Parser, Language
from ComponentsFactory.Python import PythonComponentsFactory
from my_types.python import PythonCache, python_method_dict, path_name, local_call_cache
from Context.Base import Context

class PythonContext(Context):
    '''
    Singleton that stores preprocessor structures, reusable tree sitter objects, and frequently reused meta information like `files`
    '''

    method_dict: python_method_dict = {}
    files = []
    directory = ""
    extension: str
    python_uniques = {}
    imports_by_file = {}
    cache: PythonCache = {"models_cache": {}}
    componentsFactory = PythonComponentsFactory()

    # Local Context
    local_path : path_name = ""
    call_cache : local_call_cache = {}