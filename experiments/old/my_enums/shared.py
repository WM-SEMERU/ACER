from abc import abstractmethod
from enum import Enum, EnumMeta
class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)  # type: ignore
        except ValueError:
            return False
        return True


class StrEnum(str, Enum, metaclass=MetaEnum):
    '''
    How to check if string exists in Enum of strings?
    https://stackoverflow.com/questions/63335753/how-to-check-if-string-exists-in-enum-of-strings/63336176#63336176
    To test if string equals to a particular Enum, simply inherit from the str class as I did in StrEnum
    '''
    @classmethod
    def from_str(cls, str: str): 
        return cls(str)

class ProgrammingLanguage(StrEnum): 
    JAVA = "java" 
    PYTHON = "python"

class InvokeType(StrEnum):
    INVOKENONSTATIC = "invokenonstatic"
    INVOKESTATIC = "invokestatic"
    INVOKECLASS = "invokeclass"
    INVOKEABSTRACT = "invokeabstract"
    INVOKEVIRTUAL = "inovokevirtual"
    INVOKEINTERFACE = "invokeinterface"
    INVOKESPECIAL = "invokespecial"
    INVOKEDYNAMIC = "invokedynamic"
    INVOKEMAGIC = "invokemagic"


    @staticmethod
    def equivalent(string : str, str : str) -> str:
        match string:
            case "@staticmethod":
                return InvokeType.INVOKESTATIC.value
            case "@classmethod":
                return InvokeType.INVOKECLASS.value
            case "@abstractmethod":
                return InvokeType.INVOKEABSTRACT.value
            case other:
                if str:
                    return InvokeType.INVOKEVIRTUAL.value
                else:
                    return InvokeType.INVOKENONSTATIC.value
                
class Algorithm(StrEnum):
    '''
    Some algorithms might not apply to certain languages, but most are shared.
    '''
    RA = "Reachability Analysis" # Named-Based resolution
    CHA = "Class Hierarchy Analysis"
    RTA = "Rapid Type Analysis"
    XTA = "Separate sets for methods and fields analysis"

# With StrEnum, the following succeeds.
if __name__ == "__main__":
    print("java" == ProgrammingLanguage.JAVA)
    print("java" in ProgrammingLanguage)