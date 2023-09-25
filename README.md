# ACER

ACER is an AST-based Call Graph Generator Framework. Let's build up to what this means —

- **Call Graph**: A control-flow graph that represents calling relationships between subroutines in a computer program. See its full definition [here](https://www.wikiwand.com/en/Call_graph). Formally, it's a graph $G = (V, E)$ wherein each vertex $v \in V$ represents a method, and an edge $e = (v_1, v_2) \in E$ signifies that the method $v_1$ invokes the method $v_2$.
- Call Graph **Generator**: A program that takes in a representation of another computer program and produces the call graph of the input program.
- **AST-based** Call Graph Generator: Call Graph Generators that operate upon ASTs. To clarify, the input to the generator could be the raw program itself. But more commonly, the inputs are richer representations: AST (Abstract Syntax Tree) or some IR (intermediate representation). For example, Java generators (WALA, Soot, etc) operate on the JVM Bytecode IR. On the other hand, ACER only supports ASTs.
- AST-based Call Graph Generator **Framework** (ACER): A library with a rich set of utilities to help develop AST-based Call Graph Generators.


## Installation
This is a Python library that we have yet to (but will soon) package to PyPI. As of right now, develop your generator within this repo, or, just copy the 3 files in `src/` and install the packages in `requirements.txt`.

## Examples
Examples reside within the `examples/` folder. Instructions to run them are local to the `examples/` folder. If you wish to write a generator using ACER, you should certainly read these examples.

## Resources

- [Tree-Sitter](https://github.com/tree-sitter/tree-sitter)
- [SCAM'23 Paper](https://arxiv.org/pdf/2308.15669.pdf)
