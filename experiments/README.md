# Experiments

This folder includes a few experiments:
- Reproduction suite for the results of the ACER paper (Evaluation results on JDK8 and ArgoUML),
- Type Hint Producer (input: tree-sitter grammar file, output: `hints.pyi` file). Note, though this producer works entirely, I have yet to use these hints in my generators,
- AST Frequency Counter: This was used to produce a few aside results for the paper (e.g., `88%` of callers are of type `identifier`).
- Visualizer: A tool to visualize your callgraph generator results, it is not unlike GraphViz.
- old: Before we developed `ACER`, we set out to just build two Generators, one Python and one Java. This old source code is in `old/`.