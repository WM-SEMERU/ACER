from __future__ import annotations
import logging
from my_enums.java import StrEnum

class JavaTypeResolverTypes(StrEnum):
    DECIMAL_FLOATING_POINT_LITERAL = "decimal_floating_point_literal"
    OBJECT_CREATION_EXPRESSION = "object_creation_expression"
    IDENTIFIER = "identifier"
    LOCAL_VARIABLE_DECLARATION = "local_variable_declaration"
    METHOD_INVOCATION = "method_invocation"
    ASSIGNMENT_EXPRESSION = "assignment_expression"
    NULL_LITERAL = "null_literal"
    FIELD_ACCESS = "field_access"
    CAST_EXPRESSION = "cast_expression"
    PARENTHESIZED_EXPRESSION = "parenthesized_expression"
    THIS = "this"

    @staticmethod
    def from_str(str: str) -> JavaTypeResolverTypes:
        if str not in JavaTypeResolverTypes: 
            logging.warn(f"{str.upper()} is not in JavaTypeResolverTypes.")
        return JavaTypeResolverTypes[str.upper()]