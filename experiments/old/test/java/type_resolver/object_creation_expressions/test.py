from pathlib import Path
import unittest
from my_enums.java import JavaGrammarKeywords
from my_enums.shared import ProgrammingLanguage
from old.Generator import Generator
from TypeResolver.Java.utils import JavaTypeResolverTypes
from ComponentsFactory.Java import JavaComponentsFactory
from src.utils.tree_sitter import find_all_children_of_type
from src.utils.general import walkDirectoryForFileNames
from Context.Java import JavaContext
import os


class Test(unittest.TestCase):
    def setUp(self) -> None:
        javaFactory = JavaComponentsFactory()
        self.parser = javaFactory.create_tree_sitter_parser()
        self.object_creation_expression_type_resolver = javaFactory.create_type_resolver(
            JavaTypeResolverTypes.OBJECT_CREATION_EXPRESSION)
    
    def test_parent_child(self):
        object_creation_expression_type_resolver, parser = self.object_creation_expression_type_resolver, self.parser
        JavaContext.files = walkDirectoryForFileNames(str(Path(__file__).parent.parent.parent.joinpath("shared_files", "parent_child")))
        generator = Generator(ProgrammingLanguage.JAVA)
        generator.preprocessor.preprocess()


        child_path = str(Path(__file__).parent.parent.parent.joinpath("shared_files", "parent_child", "child", "Child.java"))
        parent_path = str(Path(__file__).parent.parent.parent.joinpath("shared_files", "parent_child", "Parent", "Parent.java"))

        with open(child_path, 'rb') as file: 
            root = (parser.parse(file.read())).root_node
            oce_nodes = find_all_children_of_type(root, JavaGrammarKeywords.OBJECT_CREATION_EXPRESSION)

            first_expect = ("CallGraph.test.java.shared_files.parent_child.child", "", "Child")
            self.assertEqual(object_creation_expression_type_resolver.resolve(oce_nodes[0]), first_expect)

            second_expect = ("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedPublicClass")
            self.assertEqual(object_creation_expression_type_resolver.resolve(oce_nodes[1]), second_expect)

            third_expect = ("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedPublicClass")
            self.assertEqual(object_creation_expression_type_resolver.resolve(oce_nodes[2]), third_expect)

            fourth_expect = ("CallGraph.test.java.shared_files.parent_child.child", "Child", "ChildNestedPublic")
            self.assertEqual(object_creation_expression_type_resolver.resolve(oce_nodes[3]), fourth_expect)

        


        self.object_creation_expression_type_resolver.resolve