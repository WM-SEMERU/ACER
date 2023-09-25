"""
Probably, used only once, in Generator.

When it comes to polymorphism, at least ONE class/function must encode all the specific options and be called in the beginning, 
so that the rest of the application is polymorphic. 

This function does that. Generator calls pickContext. The specific Context comes with an already instantiated componentsFactory for the specific language.
"""

from my_enums.shared import ProgrammingLanguage
from Context.Java import JavaContext
from Context.Python import PythonContext
from Context.Base import Context

def pickContext(language: ProgrammingLanguage) -> type[Context]:
    """
    Note that this is NOT a Context builder: A class is returned, not an instance!
    """

    match language:
        case ProgrammingLanguage.JAVA:
            return JavaContext
        case ProgrammingLanguage.PYTHON:
            return PythonContext
