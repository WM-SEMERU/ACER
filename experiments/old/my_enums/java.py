from my_enums.shared import StrEnum
from my_types.java import JavaFullType, JavaMethodKey

class JavaGrammarKeywords(StrEnum):
    VARIABLE_DECLARATOR = "variable_declarator"
    TYPE_IDENTIFIER = "type_identifier"
    METHOD_DECLARATION = "method_declaration"
    IDENTIFIER = "identifier"
    PACKAGE_DECLARATION = "package_declaration"
    SCOPED_IDENTIFIER = "scoped_identifier"
    CLASS_DECLARATION = "class_declaration"
    INTERFACE_DECLARATION = "interface_declaration"
    LINE_COMMENT = "line_comment"
    BLOCK_COMMENT = "block_comment"
    IMPORT_DECLARATION = "import_declaration"
    CLASS_BODY = "class_body"
    INTERFACE_BODY = "interface_body"
    MODIFIERS = "modifiers"
    PROGRAM = "program"
    OBJECT_CREATION_EXPRESSION = "object_creation_expression"
    SCOPED_TYPE_IDENTIFIER = "scoped_type_identifier"
    BLOCK = "block"
    FORMAL_PARAMETERS = "formal_parameters"
    FORMAL_PARAMETER = "formal_parameter"
    SPREAD_PARAMETER = "spread_parameter"
    ARGUMENT_LIST = "argument_list"
    CONSTRUCTOR_DECLARATION = "constructor_declaration"
    ENHANCED_FOR_STATEMENT = "enhanced_for_statement"
    ENUM_DECLARATION = "enum_declaration"

class JavaModelTypes(StrEnum):
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"

JAVA_VAR_ARG_COUNT = 256

# Placeholder for errors!
JAVA_ERR_METHOD_KEY: JavaMethodKey = JavaMethodKey(JavaFullType("", "", ""), "", -1)
JAVA_ERR_FULL_TYPE = JavaFullType("", "", "")

"""
Underlying type identifier query. Used many different queries, for example, we use this to find the underlying, aliased type of
object_creation_expression, field declaration, etc.
"""

type_query = """[
                    (integral_type)@type
                    (generic_type(type_identifier)@type)
                    (array_type)@type
                    (floating_point_type)@type
                    (boolean_type)@type
                    (type_identifier)@type
                    (scoped_type_identifier)@type
                    (void_type)@type
                ]
             """
'''
Queries for any type, retrievable by @type.
'''