import os
from pathlib import Path
from pprint import pformat
import unittest
from src.utils.general import walkDirectoryForFileNames
from my_enums.java import JavaModelTypes
from my_enums.shared import ProgrammingLanguage
from Context.Java import JavaContext
from Preprocessor.Java import JavaPreprocessor
from old.Generator import Generator
from my_types.java import (
    JavaFullType,
    JavaMethodKey,
    class_cache_field,
    interface_cache_field,
    models_cache,
)
from deepdiff import DeepDiff


class Test(unittest.TestCase):
    def setUp(self) -> None:
        # Just to init underlying structures
        Generator(ProgrammingLanguage.JAVA)
        self.preprocessor = JavaPreprocessor()
        JavaContext.files = walkDirectoryForFileNames(
            os.path.join(os.path.dirname(__file__), "files")
        )

    def test_one(self):
        JavaContext.files = walkDirectoryForFileNames(
            os.path.join(os.path.dirname(__file__), "files")
        )
        expected: models_cache = {
            JavaFullType(
                "CallGraph.test.java.preprocessor.models_cache.files", "", "A"
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {
                        "field1": {"type": "int", "modifiers": ["public", "static"]},
                        "another": {"type": "A", "modifiers": ["public"]},
                    },
                    "extends": JavaFullType(
                        "CallGraph.test.java.preprocessor.models_cache.files.nested1",
                        "",
                        "C",
                    ),
                    "implements": [
                        JavaFullType(
                            "CallGraph.test.java.preprocessor.models_cache.files",
                            "",
                            "B",
                        )
                    ],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.preprocessor.models_cache.files", "", "B"
            ): interface_cache_field(
                **{
                    "modifiers": ["public"],
                    "constants": {
                        "field1": {
                            "type": "int",
                            "modifiers": ["public", "final", "static"],
                        },
                        "field2": {"type": "A", "modifiers": []},
                    },
                    "extends": [
                        JavaFullType(
                            "CallGraph.test.java.preprocessor.models_cache.files",
                            "",
                            "BContract",
                        )
                    ],
                    "type": JavaModelTypes.INTERFACE,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.preprocessor.models_cache.files", "", "BContract"
            ): interface_cache_field(
                **{
                    "modifiers": [],
                    "constants": {},
                    "extends": [],
                    "type": JavaModelTypes.INTERFACE,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.preprocessor.models_cache.files.nested1", "", "C"
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
        }

        self.preprocessor.preprocess()
        self.assertEqual(expected, JavaContext.cache.models_cache)

    def test_parent_child(self):
        JavaContext.files = walkDirectoryForFileNames(
            str(
                Path(__file__).parent.parent.parent.joinpath(
                    "shared_files", "parent_child"
                )
            )
        )
        expected: models_cache = {
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child", "", "Child"
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {
                        "field1": {
                            "type": "Parent.NestedPublicClass",
                            "modifiers": ["private"],
                        },
                        "field2": {
                            "type": "CallGraph.test.java.shared_files.parent_child.parent.Parent.NestedPublicClass",
                            "modifiers": ["private"],
                        },
                    },
                    "extends": JavaFullType(
                        "CallGraph.test.java.shared_files.parent_child.parent",
                        "",
                        "Parent",
                    ),
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(
                        [
                            JavaMethodKey(
                                JavaFullType(
                                    "CallGraph.test.java.shared_files.parent_child.child",
                                    "",
                                    "Child",
                                ),
                                "childMethod",
                                2,
                            )
                        ]
                    ),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child",
                "Child",
                "ChildNestedDefault",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "type": JavaModelTypes.CLASS,
                    "implements": [],
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.child",
                "Child",
                "ChildNestedPublic",
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {},
                    "extends": None,
                    "type": JavaModelTypes.CLASS,
                    "implements": [],
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "",
                "PublicField",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "",
                "DefaultField",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "",
                "ProtectedField",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent", "", "Parent"
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {
                        "field1": {"type": "PublicField", "modifiers": ["public"]},
                        "field2": {"type": "DefaultField", "modifiers": []},
                        "field3": {"type": "ProtectedField", "modifiers": []},
                        "field4": {
                            "type": "NestedDefaultClass",
                            "modifiers": ["private"],
                        },
                        "field5": {
                            "type": "NestedPublicClass",
                            "modifiers": ["protected"],
                        },
                    },
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedDefaultClass",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent.NestedDefaultClass",
                "NestedNestedPublicClass",
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(
                        [
                            JavaMethodKey(
                                JavaFullType(
                                    "CallGraph.test.java.shared_files.parent_child.parent",
                                    "Parent.NestedDefaultClass",
                                    "NestedNestedPublicClass",
                                ),
                                "nestednestedmethod",
                                0,
                            )
                        ]
                    ),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent",
                "NestedPublicClass",
            ): class_cache_field(
                **{
                    "modifiers": ["public"],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(
                        [
                            JavaMethodKey(
                                JavaFullType(
                                    "CallGraph.test.java.shared_files.parent_child.parent",
                                    "Parent",
                                    "NestedPublicClass",
                                ),
                                "nestedpublicmethod",
                                2,
                            )
                        ]
                    ),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent.NestedPublicClass",
                "NestedNestedDefaultClass",
            ): class_cache_field(
                **{
                    "modifiers": [],
                    "fields": {},
                    "extends": None,
                    "implements": [],
                    "type": JavaModelTypes.CLASS,
                    "methods": set(),
                }
            ),
            JavaFullType(
                "CallGraph.test.java.shared_files.parent_child.parent",
                "Parent.NestedPublicClass",
                "NestedNestedPublicClass",
            ): class_cache_field(
                modifiers=["public"],
                fields={},
                extends=None,
                implements=[],
                type=JavaModelTypes.CLASS,
                methods=set(
                    [
                        JavaMethodKey(
                            JavaFullType(
                                "CallGraph.test.java.shared_files.parent_child.parent",
                                "Parent.NestedPublicClass",
                                "NestedNestedPublicClass",
                            ),
                            "nestednestedpublicmethod",
                            0,
                        )
                    ]
                ),
            ),
        }
        self.preprocessor.preprocess()
        diff = DeepDiff(JavaContext.cache.models_cache, expected)
        self.assertEqual({}, diff, pformat(diff))
