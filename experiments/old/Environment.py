from tree_sitter import Language, Parser


class Environment:
    """
    The reason I have a Singleton Environment, in addition to a Context, is that the Context is holding on to too many things.

    And it leads to the following problems:

    In language specific files, I can always specifically and directly access JavaContext or PythonContext.

    However, in language agnostic files, this becomes a pain. Take utils/tree_sitter.py for example:
        Tree sitter queries needs to get the language object from the Context, but utils/tree_sitter.py has no idea if it should ask from JavaContext or PythonContext.
        
    Turns out, however, utils/tree_sitter.py is currently the only place where this issue occurs. To mitigate this, I move the language and parser into another singleton, which I call Environment.
    """

    language: Language
    parser: Parser
