from abc import abstractmethod
from TypeResolver.Base import TypeResolver

from typing import TYPE_CHECKING

from my_types.java import JavaFullType

class JavaTypeResolver(TypeResolver):
    @abstractmethod
    def resolve(self, node) -> JavaFullType:
        pass
