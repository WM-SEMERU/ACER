from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.absolute()))
import unittest
from my_enums.python import PythonGrammarKeywords
from my_enums.shared import ProgrammingLanguage
from old.Generator import Generator
from CallNodeResolver.utils import CallNodeTypes
from ComponentsFactory.Python import PythonComponentsFactory
from src.utils.tree_sitter import find_all_children_of_type
from src.utils.general import walkDirectoryForFileNames
from Context.Python import PythonContext



class Test(unittest.TestCase):
    def setUp(self) -> None:
        pythonFactory = PythonComponentsFactory()
        self.parser = pythonFactory.create_tree_sitter_parser()
        self.object_creation_expression_type_resolver = pythonFactory.create_call_node_resolver(CallNodeTypes.CALL)
    
    def test_local_function(self):
        object_creation_expression_type_resolver, parser = self.object_creation_expression_type_resolver, self.parser
        PythonContext.files = [str(Path(__file__).parent.joinpath("test_files", "local_function.py"))]
        generator = Generator(ProgrammingLanguage.PYTHON)
        generator.preprocessor.preprocess()
        edge_dict = generator.edgeBuilder.buildEdges()
        self.assertEquals(1, len(edge_dict))

    @unittest.skip("Ignores Constructors")
    def test_nested_constructor(self):
        object_creation_expression_type_resolver, parser = self.object_creation_expression_type_resolver, self.parser
        PythonContext.files = ["nested_constructor.py"]
        generator = Generator(ProgrammingLanguage.PYTHON)
        generator.preprocessor.preprocess()

    @unittest.skip("Ignores Constructors")
    def top_level_constructor(self):
        object_creation_expression_type_resolver, parser = self.object_creation_expression_type_resolver, self.parser
        PythonContext.files = ["top_level_constructor.py"]
        generator = Generator(ProgrammingLanguage.PYTHON)
        generator.preprocessor.preprocess()

    @unittest.skip("Not Implemented")
    def test_imported_functions(self):
        object_creation_expression_type_resolver, parser = self.object_creation_expression_type_resolver, self.parser
        PythonContext.files = walkDirectoryForFileNames("imported_function_test")
        generator = Generator(ProgrammingLanguage.PYTHON)
        generator.preprocessor.preprocess()





if __name__ == '__main__':
    unittest.main()