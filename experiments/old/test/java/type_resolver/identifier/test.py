from pathlib import Path
import unittest
from Context.Java import JavaContext
from old.Generator import Generator
from my_enums.java import JavaGrammarKeywords
from my_enums.shared import ProgrammingLanguage
from TypeResolver.Java.utils import JavaTypeResolverTypes
from ComponentsFactory.Java import JavaComponentsFactory
from my_types.java import JavaFullType
from src.utils.tree_sitter import find_all_children_of_type, find_first_child_of_type
from src.utils.general import walkDirectoryForFileNames


class Test(unittest.TestCase):
    def setUp(self) -> None:
        javaFactory = JavaComponentsFactory()
        self.parser = javaFactory.create_tree_sitter_parser()
        self.identifier_type_resolver = javaFactory.create_type_resolver(
            JavaTypeResolverTypes.IDENTIFIER
        )

    def test_parent_child_1(self):
        parser, identifier_type_resolver = self.parser, self.identifier_type_resolver

        JavaContext.files = walkDirectoryForFileNames(str(Path(__file__).parent.parent.parent.joinpath("shared_files", "parent_child")))
        generator = Generator(ProgrammingLanguage.JAVA)
        generator.preprocessor.preprocess()



        expected_identifier_to_full_type = {
            "a": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child",
                "Child",
                "ChildNestedDefault",
            ),
            "b": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child",
                "Child",
                "ChildNestedPublic",
            ),
            "c": JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "", "Child"),
            "cnp": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child",
                "Child",
                "ChildNestedPublic",
            ),
            "field1": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ),
            "field2": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ),
            "field5": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ),
            "pc": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ),
            "pc2": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ),
            "nn": JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent", 
                "Parent.NestedPublicClass", 
                "NestedNestedPublicClass"
            )
        }
        child_path = str(
            Path(__file__).parent.parent.parent.joinpath(
                "shared_files", "parent_child", "child", "Child.java"
            )
        )

        with open(child_path, "rb") as file:
            root = (parser.parse(file.read())).root_node
            child_method_node = find_first_child_of_type(root, JavaGrammarKeywords.METHOD_DECLARATION)
            child_method_body_node = find_first_child_of_type(child_method_node, JavaGrammarKeywords.BLOCK, 1)
            identifier_nodes = find_all_children_of_type(
                child_method_body_node, JavaGrammarKeywords.IDENTIFIER
            )

            test_against = {}
            for node in identifier_nodes:
                identifier = node.text.decode("utf8")
                if identifier in expected_identifier_to_full_type: 
                    test_against[identifier] = identifier_type_resolver.resolve(node)

            self.assertEqual(expected_identifier_to_full_type, test_against)