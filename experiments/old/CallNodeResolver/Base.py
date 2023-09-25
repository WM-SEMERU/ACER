from abc import ABC, abstractmethod
from CallNodeResolver.utils import CallNodeResolverResults, CallNodeTypes
from tree_sitter import Node

class CallNodeResolver(ABC):
    """
    `CallNodeResolver` outputs a key that can be queried against `method_dict`, given a call node.
    A call node is either a method_invocation node or a object_creation_expression node (for Java)

    Additionally (in Sprint #4), we decided that the call type (invokevirtual, invokespecial, etc)
    must be outputed, this is now too a responsibility of the `CallNodeResolver`.
    """

    @staticmethod
    @abstractmethod
    def makeSpecificCallNodeResolver(callNodeType: CallNodeTypes) -> CallNodeResolverResults:
        pass

    @abstractmethod
    def find(self, node: Node) -> CallNodeResolverResults:
        pass
