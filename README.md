# ACER

ACER is an AST-based Call Graph Generator Framework. Let's build up to what this means —

- **Call Graph**: A control-flow graph that represents calling relationships between subroutines in a computer program. See its full definition [here](https://www.wikiwand.com/en/Call_graph). Formally, it's a graph $G = (V, E)$ wherein each vertex $v \in V$ represents a method, and an edge $e = (v_1, v_2) \in E$ signifies that the method $v_1$ invokes the method $v_2$.
- Call Graph **Generator**: A program that takes in a representation of another computer program and produces the call graph of the input program.
- **AST-based** Call Graph Generator: Call Graph Generators that operate upon ASTs. To clarify, the input to the generator could be the raw program itself. But more commonly, the inputs are richer representations: AST (Abstract Syntax Tree) or some IR (intermediate representation). For example, Java generators (WALA, Soot, etc) operate on the JVM Bytecode IR. On the other hand, ACER only supports ASTs.
- AST-based Call Graph Generator **Framework** (ACER): A library with a rich set of utilities to help develop AST-based Call Graph Generators.

The novelty of ACER is in:
1. Providing a framework to ease interacting with concrete syntax trees of a target repository,
2. Guide call graph generator implementation by exposing two abstract classes: `Preprocessor` and `Generator` (a total of 3 abstract methods to implement), along with a bunch of generics, that all theoretic generators should extend from. After implementing the 3 abstract methods, you have yourself a call graph generator. Additionally, certain generator logic is abstract away. For example, the logic to recurisively explore nodes and the logic to avoid re-entering an already visited node.

Note that ACER favors creating callgraphs at the application-level. Application-level callgraphs refer to callgraphs generated between user-written source, a library call from user-written code is not application-level (in the paper, we call this in-between level). This is because, ACER directly provides you the concrete syntax trees of your target source code/repo, but the libraries your code may depend on is not pulled it, thus, it is impossible to fully resolve library calls. And since a callgraph is usually thought of as pairs of fully resolved methods, ACER favors application-level callgraphs.
However, perhaps you can certainly type the callgraph object to be pairs of library/application methods, where library methods are unresolved. Since ACER provides you full freedom in defining the rules for catching method invocations, you can catch all calls, and just denote the non-resolvable methods to be of the "library". 

## Installation
This is a Python library that we have yet to (but will soon) package to PyPI. As of right now, develop your generator within this repo, or, just copy the 3 files in `src/` and install the packages in `requirements.txt`.

## Examples
Examples reside within the `examples/` folder. Instructions to run them are local to the `examples/` folder. If you wish to write a generator using ACER, you should certainly read these examples.

## Plan
- [ ] Develop a [$\alpha$-conversion](https://www.wikiwand.com/en/Name_resolution_(programming_languages)#Alpha_renaming_to_make_name_resolution_trivial) module to the `Preprocessor` class entirely.

Rationale: The `Preprocessor` class exist to help name resolution, but the user will still need to write a lot of code utilizing these preprocessed structures in their extended `Generator` class. But, if names never overlapped, name resolution becomes a trivial process. Renaming overlapped names is exactly what $\alpha$-conversion does.

Challenges: What should the I/O of this module look like? Should a complete, $\alpha$-converted copy of the original source be outputed? Should a tree-sitter `Tree`, represented in `S-expression`, be outputed?

- [ ] Develop a Java CHA generator.
- [ ] Develop a Java RTA generator.
- [ ] Develop a Java k-CFA generator.
- [ ] Develop a Python CHA generator that handles `eval()`.

Note that handling `eval()` might be a bit simpler with ASTs, because, the expression within `eval()` could be parsed as a AST, and recurisvely fed into your `Generator`.
- [ ] Develop a Javascript CHA generator that handles `eval()`.
- [ ] Develop a Scheme k-CFA generator.
- [ ] Develop a Haskell generator.


## Resources

- [Tree-Sitter](https://github.com/tree-sitter/tree-sitter)
- [SCAM'23 Paper](https://arxiv.org/pdf/2308.15669.pdf)
