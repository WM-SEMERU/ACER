__version__ = "0.1.0"
# Needed for relative importing (relative importing is used in, for example, the unittests)
# More info: https://stackoverflow.com/a/19190695/9007785
import os, sys 
# Adds CallGraph to sys path so that we can do for example:
# `python3 -m unittest test.java.type_resolver.object_creation_expressions.test` in csci_callgraph_generatorj
sys.path.append(os.path.dirname(os.path.realpath(__file__)))