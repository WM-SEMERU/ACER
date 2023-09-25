from pathlib import Path
import unittest
from my_enums.shared import ProgrammingLanguage
from my_types.java import JavaFullType, JavaMethodDict, JavaMethodKey
from Context.Java import JavaContext
from Preprocessor.Java import JavaPreprocessor
from old.Generator import Generator
from deepdiff import DeepDiff
from src.utils.general import walkDirectoryForFileNames

class Test(unittest.TestCase):
    def test(self):
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
        expected = {
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.child", "", "Child"),
                "childMethod",
                2,
            ): {"modifiers": ["private"], "return_type": "void"},
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedDefaultClass", "NestedNestedPublicClass"),
                "nestednestedmethod",
                0,
            ): {"modifiers": ["private"], "return_type": "void"},
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent", "NestedPublicClass"),
                "nestedpublicmethod",
                2,
            ): {"modifiers": ["public"], "return_type": "void"},
            JavaMethodKey(
                JavaFullType("CallGraph.test.java.shared_files.parent_child.parent", "Parent.NestedPublicClass", "NestedNestedPublicClass"),
                "nestednestedpublicmethod",
                0,
            ): {"modifiers": ["public"], "return_type": "void"},
        }

        method_dict = self.preprocessor.makeMethodDict()
        diff = DeepDiff(method_dict, expected, exclude_regex_paths=[r"\['node'\]"])
        self.assertEqual(diff, {})  # there should be no diff
