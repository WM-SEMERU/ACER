from my_enums.shared import StrEnum

class PythonGrammarKeywords(StrEnum):
    MODULE = "module"
    IMPORT_STATEMENT = "import_statement"
    IMPORT_PREFIX = "import_prefix"
    RELATIVE_IMPORT = "relative_import"
    FUTURE_IMPORT_STATEMENT = "future_import_statement"
    IMPORT_FROM_STATEMENT = "import_from_statement"
    ALIASED_IMPORT = "aliased_import"
    WILDCARD_IMPORT = "wildcard_import"
    EXPRESSION_STATEMENT = "expression_statement"
    NAMED_EXPRESSION = "named_expression"
    RETURN_STATEMENT = "return_statement"
    FUNCTION_DEFINITION = "function_definition"
    PARAMETERS = "parameters"
    GLOBAL_STATEMENT = "global_statement"
    DECORATED_DEFINITION = "decorated_definition"
    CLASS_DEFINITION = "class_definition"
    CLASS_BODY = "class_body"
    BLOCK = "block"
    ATTRIBUTE = "attribute"
    CALL = "call"
    IDENTIFIER = "identifier"
  
class PythonModelTypes(StrEnum):
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"


