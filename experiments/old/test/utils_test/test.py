from pathlib import Path
import unittest
from Context.Java import Context
from old.Environment import Environment
from my_enums.java import JavaGrammarKeywords
from my_enums.shared import ProgrammingLanguage
from old.Generator import Generator
from src.utils.tree_sitter import *


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        I cache all class_declaration nodes from ./files/A.java since they are used in all tests
        """
        Generator(ProgrammingLanguage.JAVA)
        file = open(
            Path(__file__).parent.joinpath("files", "A.java"), "rb"
        )
        src = file.read()
        tree = Environment.parser.parse(src)
        cls.root_node = tree.root_node
        file.close()

        cls.A_node = find_first_child_of_type(
            cls.root_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        cls.B_node = find_first_child_of_type(
            cls.A_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        cls.C1_node = find_first_child_of_type(
            cls.B_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        cls.D1_node = find_first_child_of_type(
            cls.C1_node, JavaGrammarKeywords.CLASS_DECLARATION
        )

        assert cls.A_node and cls.B_node and cls.C1_node and cls.D1_node
        cls.C2_node = cls.C1_node.next_named_sibling
        cls.D2_node = cls.D1_node.next_named_sibling
        cls.D3_node = find_first_child_of_type(
            cls.C2_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        assert cls.D3_node
        cls.D4_node = cls.D3_node.next_named_sibling

    def test_find_closest_ancestor_of_type(self):
        """
        The closest class_declaration ancestor to C1 is B.
        The closest class_declaration ancestor to B is A.
        """
        A_node, B_node, C1_node = self.A_node, self.B_node, self.C1_node

        B_node_again = find_closest_ancestor_of_type(
            C1_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        A_node_again = find_closest_ancestor_of_type(
            B_node, JavaGrammarKeywords.CLASS_DECLARATION
        )

        assert A_node_again and B_node_again

        self.assertEqual(A_node, A_node_again)
        self.assertEqual(B_node, B_node_again)

    def test_find_all_ancestors_of_types(self):
        """
        The class_declaration ancestors to C1 are A, B
        """

        A_node, B_node, C1_node = self.A_node, self.B_node, self.C1_node

        A_body_node = find_first_child_of_type(A_node, JavaGrammarKeywords.CLASS_BODY)
        B_body_node = find_first_child_of_type(B_node, JavaGrammarKeywords.CLASS_BODY)

        ancestors = find_all_ancestors_of_types(
            C1_node,
            [JavaGrammarKeywords.CLASS_DECLARATION, JavaGrammarKeywords.CLASS_BODY],
        )

        self.assertEqual(ancestors, [B_body_node, B_node, A_body_node, A_node])

    def test_find_first_child_of_type(self):
        """
        I don't used the cached nodes from setUpClass here since I'm testing the correctness of find_first_child_of_type
        """

        A_node = find_first_child_of_type(
            self.root_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        A_name_node = find_first_child_of_type(A_node, JavaGrammarKeywords.IDENTIFIER)
        B_node = find_first_child_of_type(A_node, JavaGrammarKeywords.CLASS_DECLARATION)
        B_name_node = find_first_child_of_type(B_node, JavaGrammarKeywords.IDENTIFIER)
        C1_node = find_first_child_of_type(
            B_node, JavaGrammarKeywords.CLASS_DECLARATION
        )
        C1_name_node = find_first_child_of_type(C1_node, JavaGrammarKeywords.IDENTIFIER)

        assert A_name_node and B_name_node and C1_name_node

        self.assertEqual(A_name_node.text.decode("utf8"), "A")
        self.assertEqual(B_name_node.text.decode("utf8"), "B")
        self.assertEqual(C1_name_node.text.decode("utf8"), "C1")

    def test_find_all_children_of_type(self):
        A_node, B_node, C1_node, C2_node, D1_node, D2_node, D3_node, D4_node = (
            self.A_node,
            self.B_node,
            self.C1_node,
            self.C2_node,
            self.D1_node,
            self.D2_node,
            self.D3_node,
            self.D4_node,
        )

        level_1_children = find_all_children_of_types(
            self.root_node, [JavaGrammarKeywords.CLASS_DECLARATION], 1
        )
        self.assertEqual(level_1_children, [A_node])

        level_3_children = find_all_children_of_types(
            self.root_node, [JavaGrammarKeywords.CLASS_DECLARATION], 3
        )
        self.assertEqual(level_3_children, [A_node, B_node])

        level_5_children = find_all_children_of_types(
            self.root_node, [JavaGrammarKeywords.CLASS_DECLARATION], 5
        )
        self.assertEqual(level_5_children, [A_node, B_node, C1_node, C2_node])

        all_children = find_all_children_of_types(
            self.root_node, [JavaGrammarKeywords.CLASS_DECLARATION]
        )
        self.assertEqual(
            all_children,
            [A_node, B_node, C1_node, C2_node, D1_node, D2_node, D3_node, D4_node],
        )

    def test_get_all_children_at_level_of_type(self):
        A_node, B_node, C1_node, C2_node, D1_node, D2_node, D3_node, D4_node = (
            self.A_node,
            self.B_node,
            self.C1_node,
            self.C2_node,
            self.D1_node,
            self.D2_node,
            self.D3_node,
            self.D4_node,
        )
        level_1_children = get_all_children_at_level_of_type(
            self.root_node, JavaGrammarKeywords.CLASS_DECLARATION, 1
        )
        self.assertEqual(level_1_children, [A_node])

        level_3_children = get_all_children_at_level_of_type(
            self.root_node, JavaGrammarKeywords.CLASS_DECLARATION, 3
        )
        self.assertEqual(level_3_children, [B_node])

        level_5_children = get_all_children_at_level_of_type(
            self.root_node, JavaGrammarKeywords.CLASS_DECLARATION, 5
        )
        self.assertEqual(level_5_children, [C1_node, C2_node])

        all_children = get_all_children_at_level_of_type(
            self.root_node, JavaGrammarKeywords.CLASS_DECLARATION, 7
        )
        self.assertEqual(all_children, [D1_node, D2_node, D3_node, D4_node])

    def test_group_by_type_capture(self):
        A_node, B_node, C1_node, C2_node, D1_node, D2_node, D3_node, D4_node = (
            self.A_node,
            self.B_node,
            self.C1_node,
            self.C2_node,
            self.D1_node,
            self.D2_node,
            self.D3_node,
            self.D4_node,
        )
        expected_class_declaration_nodes = [
            A_node,
            B_node,
            C1_node,
            D1_node,
            D2_node,
            C2_node,
            D3_node,
            D4_node,
        ]

        captures = group_by_type_capture(
            self.root_node,
            "((class_declaration (identifier)@class_name)@class_declaration)",
        )
        expected = {
            "class_declaration": expected_class_declaration_nodes,
            "class_name": list(
                map(
                    lambda n: find_first_child_of_type(
                        n, JavaGrammarKeywords.IDENTIFIER
                    ),
                    expected_class_declaration_nodes,
                )
            ),
        }

        self.assertEqual(captures, expected)

    def test_group_by_type_capture_up_to_depth(self):
        A_node, B_node, C1_node, C2_node, D1_node, D2_node, D3_node, D4_node = (
            self.A_node,
            self.B_node,
            self.C1_node,
            self.C2_node,
            self.D1_node,
            self.D2_node,
            self.D3_node,
            self.D4_node,
        )

        expected_level_1_capture = {"class_declaration": [A_node]}
        expected_level_2_capture = {
            "class_declaration": [A_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node],
                )
            ),
        }
        expected_level_3_capture = {
            "class_declaration": [A_node, B_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node],
                )
            ),
        }
        expected_level_4_capture = {
            "class_declaration": [A_node, B_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node, B_node],
                )
            ),
        }
        expected_level_5_capture = {
            "class_declaration": [A_node, B_node, C1_node, C2_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node, B_node],
                )
            ),
        }
        expected_level_6_capture = {
            "class_declaration": [A_node, B_node, C1_node, C2_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node, B_node, C1_node, C2_node],
                )
            ),
        }
        expected_level_7_capture = {
            "class_declaration": [A_node, B_node, C1_node, D1_node, D2_node, C2_node, D3_node, D4_node],
            "class_name": list(
                map(
                    lambda node: find_first_child_of_type(
                        node, JavaGrammarKeywords.IDENTIFIER
                    ),
                    [A_node, B_node, C1_node, C2_node],
                )
            ),
        }

        q = "((class_declaration (identifier)@class_name)@class_declaration)"
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                1,
            ),
            expected_level_1_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                2,
            ),
            expected_level_2_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                3,
            ),
            expected_level_3_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                4,
            ),
            expected_level_4_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                5,
            ),
            expected_level_5_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                6,
            ),
            expected_level_6_capture,
        )
        self.assertEqual(
            group_by_type_capture_up_to_depth(
                self.root_node,
                q,
                7,
            ),
            expected_level_7_capture,
        )