from __future__ import annotations
from abc import abstractmethod
from CallNodeResolver.Base import CallNodeResolver
from CallNodeResolver.utils import CallNodeTypes
from tree_sitter import Node
from my_types.java import JavaMethodKey

from typing import TypedDict

class JavaCallNodeResolverResults(TypedDict):
    key: JavaMethodKey
    
class JavaCallNodeResolver(CallNodeResolver):
    @staticmethod
    def makeSpecificCallNodeResolver(callNodeType: CallNodeTypes) -> JavaCallNodeResolver:
        from CallNodeResolver.Java.MethodInvocation import JavaMethodInvocationNodeResolver
        from CallNodeResolver.Java.ObjectCreationExpression import JavaObjectCreationNodeResolver
        if callNodeType == CallNodeTypes.METHOD_INVOCATION:
            return JavaMethodInvocationNodeResolver()
        elif callNodeType == CallNodeTypes.OBJECT_CREATION_EXPRESSION:
            return JavaObjectCreationNodeResolver()
        print(f"Call Node of type {callNodeType} does not have correponding key finder")
        exit(1)

    @abstractmethod
    def find(
        self, node: Node
    ) -> JavaCallNodeResolverResults:
        pass
