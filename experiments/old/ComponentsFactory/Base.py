from __future__ import annotations
from abc import ABC, abstractmethod
from tree_sitter import Parser, Language

from Preprocessor.Base import Preprocessor
from EdgeBuilder.Base import EdgeBuilder
from TypeResolver.Base import TypeResolver
from CallNodeResolver.Base import CallNodeResolver, CallNodeTypes

class ComponentsFactory(ABC):
    """
    Makes sub components using the AbstractFactory pattern. Users use this with `Context.componentsFactory`.
    """

    @abstractmethod
    def create_preprocessor(self) -> Preprocessor:
        pass

    @abstractmethod
    def create_edge_builder(self) -> EdgeBuilder:
        pass

    @abstractmethod
    def create_type_resolver(self, nodeType: str) -> TypeResolver:
        pass


    @abstractmethod 
    def create_language(self) -> Language:
        pass
        
    @abstractmethod
    def create_extension(self) -> str:
        pass

    @abstractmethod 
    def create_call_node_resolver(self, callNodeType: CallNodeTypes) -> CallNodeResolver:
        pass


    def create_tree_sitter_parser(self) -> Parser:
        p = Parser()
        p.set_language(self.create_language()) # If this is expensive, could be optimized by caching Language in Context
        return p