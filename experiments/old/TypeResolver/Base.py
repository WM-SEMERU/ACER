from abc import ABC, abstractmethod
from typing import Tuple


class TypeResolver(ABC):
    """
    A TypeResolver's only method is `resolve`, which returns the full type a tree sitter Node resolves to.
    For example, given a java tree-sitter identifier node with text `foo`, a corresponding `IdentifierTypeResolver` returns the full type,
    `(driver.java, Driver, innerFoo)`, which means `foo`'s full type is a Class named `innerFoo` that resided locally within the `Driver` class of `driver.java`.
    """

    @abstractmethod
    def resolve(self, node) -> Tuple:
        pass