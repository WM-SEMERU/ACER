from abc import ABC
from tree_sitter import Parser, Language
from ComponentsFactory.Base import ComponentsFactory
from ComponentsFactory.Java import JavaComponentsFactory
from my_types.java import JavaCache, JavaMethodDict
from Context.Base import Context

class JavaContext(Context):
    '''
    Singleton that stores preprocessor structures, reusable tree sitter objects, and frequently reused meta information like `files`
    '''

    method_dict: JavaMethodDict = {}
    files = []
    cache: JavaCache = JavaCache(packages_to_importables={}, models_cache={})
    componentsFactory: JavaComponentsFactory = JavaComponentsFactory()
    extension: str
