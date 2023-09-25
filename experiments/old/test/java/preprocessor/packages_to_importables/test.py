from pathlib import Path
from pprint import pprint
import unittest
from my_enums.java import JavaModelTypes
from my_enums.shared import ProgrammingLanguage
from Context.Java import JavaContext
from Preprocessor.Java import JavaPreprocessor
from old.Generator import Generator
from deepdiff import DeepDiff
from my_types.java import JavaFullType, packages_to_importables
from src.utils.general import walkDirectoryForFileNames

class Test(unittest.TestCase):
    def test_one(self):
        # Just to init underlying structures
        Generator(ProgrammingLanguage.JAVA)
        self.preprocessor = JavaPreprocessor()
        JavaContext.files = walkDirectoryForFileNames(
            str(Path(__file__).parent.joinpath("files"))
        )
        expected: packages_to_importables = {
            "unnamed": [],
            "CallGraph.test.java.preprocessor.packages_to_importables.files": [
                JavaFullType("CallGraph.test.java.preprocessor.packages_to_importables.files", "", "A"),
                JavaFullType("CallGraph.test.java.preprocessor.packages_to_importables.files", "", "B"),
            ],
            "CallGraph.test.java.preprocessor.packages_to_importables.files.nested1": [
                JavaFullType("CallGraph.test.java.preprocessor.packages_to_importables.files.nested1", "", "C")
            ],
        }

        packages2importables = self.preprocessor.makePackgesToImportables()
        # packages_to_importables actually also caches the importable's file path, which is user dependent and must be ignored
        diff = DeepDiff(
            packages2importables, expected, exclude_regex_paths=[r"\['file_path'\]"], ignore_order=True
        )
        self.assertEqual({}, diff)  # there should be no diff

    def test_two(self):
        # Just to init underlying structures
        Generator(ProgrammingLanguage.JAVA)
        self.preprocessor = JavaPreprocessor()
        JavaContext.files = walkDirectoryForFileNames(
            str(
                Path(__file__).parent.parent.parent.joinpath(
                    "shared_files", "parent_child"
                )
            )
        )
        expected: packages_to_importables = {
            "unnamed": [],
            "CallGraph.test.java.shared_files.parent_child.child": [
                JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "", "Child"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "Child", "ChildNestedDefault"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "Child", "ChildNestedPublic")
            ],
            "CallGraph.test.java.shared_files.parent_child.parent": [
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "", "PublicField"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "", "DefaultField"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "", "ProtectedField"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "", "Parent"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedDefaultClass"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedPublicClass"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedDefaultClass", "NestedNestedPublicClass"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedPublicClass", "NestedNestedDefaultClass"), 
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedPublicClass", "NestedNestedPublicClass"),
            ],
        }

        packages2importables = self.preprocessor.makePackgesToImportables()
        # packages_to_importables actually also caches the importable's file path, which is user dependent and must be ignored
        diff = DeepDiff(
            packages2importables, expected, exclude_regex_paths=[r"\['file_path'\]"], ignore_order=True
        )
        pprint(diff)
        self.assertEqual({}, diff)  # there should be no diff
