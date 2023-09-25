from __future__ import annotations
from my_enums.shared import StrEnum

class PythonTypeResolverTypes(StrEnum):
    IDENTIFIER = "identifier"
    CALL = "call"
    ASSIGNMENT = "assignment"
    ATTRIBUTE = "attribute"
    IMPORT_FROM = "import_from"

    @staticmethod
    def from_str(str: str) -> PythonTypeResolverTypes:
        return PythonTypeResolverTypes[str.upper()]