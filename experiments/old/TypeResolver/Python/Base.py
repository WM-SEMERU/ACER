from abc import abstractmethod
from typing import Tuple
from TypeResolver.Base import TypeResolver

class PythonTypeResolver(TypeResolver):
    @abstractmethod
    def resolve(self, node) -> Tuple:
        pass
