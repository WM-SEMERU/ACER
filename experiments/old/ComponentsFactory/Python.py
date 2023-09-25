from __future__ import annotations
from tree_sitter import Language
from ComponentsFactory.Base import ComponentsFactory
from pathlib import Path
from TypeResolver.Python.utils import PythonTypeResolverTypes

from Preprocessor.Base import Preprocessor
from EdgeBuilder.Base import EdgeBuilder
from TypeResolver.Base import TypeResolver
from CallNodeResolver.Base import CallNodeResolver, CallNodeTypes

class PythonComponentsFactory(ComponentsFactory):

    def create_preprocessor(self) -> Preprocessor:
        from Preprocessor.Python import PythonPreprocessor
        return PythonPreprocessor()

    def create_edge_builder(self) -> EdgeBuilder:
        from EdgeBuilder.Python import PythonBuilder

        return PythonBuilder()

    def create_type_resolver(self, typeResolverType: PythonTypeResolverTypes) -> TypeResolver:
        from TypeResolver.Python.Identifier import PythonIdentifierResolver
        from TypeResolver.Python.Assignment import PythonAssignmentResolver
        from TypeResolver.Python.Attribute import PythonAttributeResolver
        from TypeResolver.Python.Call import PythonCallResolver
        from TypeResolver.Python.ImportFrom import PythonImportFromResolver

        if typeResolverType == typeResolverType.IDENTIFIER:
            return PythonIdentifierResolver()
        elif typeResolverType == typeResolverType.ASSIGNMENT:
            return PythonAssignmentResolver()
        elif typeResolverType == typeResolverType.ATTRIBUTE:
            return PythonAttributeResolver()
        elif typeResolverType == typeResolverType.CALL:
            return PythonCallResolver()
        elif typeResolverType == typeResolverType.IMPORT_FROM:
            return PythonImportFromResolver()
        print(
            f"No type resolver created for type {typeResolverType} yet, exiting.")
        exit(1)


    def create_language(self) -> Language:
        return Language(str(Path(__file__).parent.parent.parent.joinpath("build", "my-languages.so")), 'python')

    def create_call_node_resolver(self, callNodeType: CallNodeTypes) -> CallNodeResolver:
        from CallNodeResolver.Python.Base import PythonCallNodeResolver
        # PythonCallNodeKeyFinder has more subclasses, and we need to make the correct, specific one
        return PythonCallNodeResolver.makeSpecificCallNodeResolver(callNodeType)
    
    def create_extension(self) -> str:
        return '.py'