from __future__ import annotations
from typing import Tuple, TypedDict
from my_enums.shared import StrEnum

class CallNodeTypes(StrEnum):
    METHOD_INVOCATION = "method_invocation"
    OBJECT_CREATION_EXPRESSION = "object_creation_expression"
    FUNCTION_INVOCATION = "function_invocation"
    CALL = "call"

    @staticmethod
    def from_str(str: str) -> CallNodeTypes:
        return CallNodeTypes[str.upper()]


class InvokeTypes(StrEnum):
    INVOKESTATIC = "invokestatic"
    INVOKEVIRTUAL = "invokevirtual"
    INVOKEINTERFACE = "invokeinterface"
    INVOKESPECIAL = "invokespecial"


class CallNodeResolverResults(TypedDict):
    key: Tuple # Just some tuple, different depending on language