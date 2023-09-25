# Convert WALA edges -> PACER edges

# WALA example: 
# (com/sun/tools/javac/comp.Check, validateAnnotationMethod, (Lcom/sun/tools/javac/util/JCDiagnostic$DiagnosticPosition, Lcom/sun/tools/javac/code/Symbol$MethodSymbol))
# ->
#(java/beans/beancontext.BeanContextSupport, iterator, ())


# replace / with .
# replace $ with .
# Remove L.
# Only look at argument shorthands

from typing import List, Optional, Set

from tqdm import tqdm


def shorthand(type: str) -> str:
    # get the shorthand only
    type = type.replace("/", ".").replace("$", ".")
    if "." in type: return type.rsplit(".", maxsplit=1)[1]
    return type

symbol2name = {
    "B": "byte",
    "C": "char", 
    "D": "double", 
    "F": "float", 
    "I": "int",
    "J": "long",
    "S": "short", 
    "Z": "boolean",
    "V": "void"
}

def norm(s: str) -> str:
    # (com/sun/tools/javac/comp.Check, validateAnnotationMethod, (Lcom/sun/tools/javac/util/JCDiagnostic$DiagnosticPosition, Lcom/sun/tools/javac/code/Symbol$MethodSymbol))
    type, method_name, method_args = s[1:len(s)-1].split(",", maxsplit=2)


    type = type.replace("/", ".").replace("$", ".")
    type = ".".join((filter(lambda x: not x.isdigit(), type.split("."))))
    type = type[1:] if type[0] == "L" else type
    

    method_args = method_args[1:len(method_args)-1]
    method_args = ",".join(map(lambda arg: symbol2name[arg] if arg in symbol2name else arg , map(shorthand, method_args.split(",")))) if method_args else method_args

    return f"({type},{method_name},({method_args}))"

def one(type: str) -> Optional[str]:
    if "->" not in type: return None
    left, right = type.split("->")
    return f"{norm(left)}->{norm(right)}"
    
def convert(input_path: str, output_path: str):
    f = open(input_path, mode="r")
    output: Set[str] = set()
    for line in tqdm(f.readlines()):
        r = one(line.strip().replace(" ", ""))
        if r: output.add(r)
    with open(output_path, mode="w") as wf:
        wf.write('\n'.join(list(output)))

if __name__ == "__main__":
    convert("/home/andrew/repo-research/WALA-start/results", "converted-wala")