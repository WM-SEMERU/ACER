from abc import ABC
from typing import Dict, List
from tree_sitter import Language, Parser

from ComponentsFactory.Base import ComponentsFactory

class Context(ABC):
	extension: str 
	componentsFactory: ComponentsFactory
	files: List[str]
	method_dict: Dict