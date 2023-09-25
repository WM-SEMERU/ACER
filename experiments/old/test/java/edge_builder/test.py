from pathlib import Path
from pprint import pprint
from typing import Dict
import unittest
from EdgeBuilder.Java import JavaEdgeBuilder
from Preprocessor.Java import JavaPreprocessor
from my_enums.shared import ProgrammingLanguage
from my_types.java import JavaFullType, java_edge_dict, JavaMethodKey
from old.Generator import Generator
from Context.Java import JavaContext
from utils.general import walkDirectoryForFileNames


class Test(unittest.TestCase):
    def test_parent_child(self):
        Generator(ProgrammingLanguage.JAVA)
        preprocessor = JavaPreprocessor()
        JavaContext.files = walkDirectoryForFileNames(
            str(Path(__file__).parent.parent.joinpath("shared_files", "parent_child"))
        )
        preprocessor.preprocess()

        # Just 2 edges
        expected: java_edge_dict = {
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "", "Child"),
                "childMethod",
                2,
            ): set([
                JavaMethodKey(
                    JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "", "Child"),
                    "Child",
                    0,
                ),
                JavaMethodKey(
                    JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedPublicClass"),
                    "NestedPublicClass",
                    0,
                ),
                JavaMethodKey(
                    JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "Child", "ChildNestedPublic"),
                    "ChildNestedPublic",
                    0,
                ),
                JavaMethodKey(
                    JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedPublicClass", "NestedNestedPublicClass"),
                    "nestednestedpublicmethod",
                    0,
                ),
            ]),
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedPublicClass", "NestedNestedPublicClass"),
                "nestednestedpublicmethod",
                0,
            ): set([
                JavaMethodKey(
                    JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedDefaultClass", "NestedNestedPublicClass"),
                    "nestednestedmethod",
                    0,
                )
            ]),
        }

        EdgeBuilder = JavaEdgeBuilder()
        edge_dict = EdgeBuilder.buildEdges()

        pprint(edge_dict)

        pprint(expected)

        self.assertEqual(edge_dict, expected)
