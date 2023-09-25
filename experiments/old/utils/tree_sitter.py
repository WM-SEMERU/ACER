from collections import defaultdict
from typing import Dict, List, Optional, Set
from tree_sitter import Node, TreeCursor
from old.Environment import Environment


def find_closest_ancestor_of_type(root: Optional[Node], ancestorType: str) -> Optional[Node]:
    """
    Return the closest ancestor to the node `root` that has type `ancestorType`

    `root` itself IS NOT a candidate for the closest ancestor

    Note: The implementation does not use TreeCursor. TreeCursor's `goto_parent` can only go up
    to the original node it was created on.
    """

    root = (
        root and root.parent
    )  # Skip over root itself since root is not an ancestor candidate

    while root and root.type != ancestorType:
        root = root.parent  # goto_parent -> False if no parent, return None
        if not root:
            return None

    return root


def find_all_ancestors_of_types(
    root: Optional[Node], ancestorTypes: List[str]
) -> List[Node]:
    """
    Return the all ancestors to the node `root` that has type `ancestorType`, in the order from closest to furthest

    `root` itself IS NOT an ancestor to itself.

    Note: The implementation does not use TreeCursor. TreeCursor's `goto_parent` can only go up
    to the original node it was created on.
    """

    ancestors: List[Node] = []
    while root:
        root = root.parent  # Note that root itself is skipped
        if root and root.type in ancestorTypes:
            ancestors.append(root)

    return ancestors


default_unused = -999


def find_first_child_of_type(root: Node, childType: str, level: int=default_unused) -> Optional[Node]:
    """
    Return the first child to the node `root` that has type `childType` within a positive depth of `level`.

    `root` itself IS NOT a candidate as the first child.

    You would usually want to specify `level` to avoid getting back a deeply nested result that you don't actually want. 
    For example, checkout: https://github.com/WM-SEMERU/csci-435_callgraph_generator/commit/7f372c91959facafa06d2782b1f854a9abafdd41

    TODO: Write with TreeCursor to avoid memory overhead since there's no tail recursion here
    """

    assert level == default_unused or level > 0  # Level must be positive
    isLevelUsed = level != default_unused

    def recur(root: Node, level: int) -> Optional[Node]:
        if not root:
            return None
        if isLevelUsed and level < 0:
            return None
        if isLevelUsed and level == 0:  # reaching level 0 is the end
            return root if root.type == childType else None
        for child in root.children:
            if child.type == childType:
                return child
            res = recur(child, level - 1)
            if res:
                return res

    return recur(root, level)


def find_all_children_of_type(
    root: Optional[Node], childType: str, level: int=default_unused
) -> List[Node]:
    """
    Return the all children to the node `root` that has type `childType` within a positive depth of `level`.
    The return order is the same as the search order, which is breadth-first, level order.

    This means that the return order maintains the hierarchy of `root`.

    `root` itself IS NOT a child to itself.

    TODO: Write with TreeCursor to avoid memory overhead since there's no tail recursion here
    """

    if not root:
        return []

    assert level == default_unused or level > 0  # Level must be positive
    isLevelUsed = level != default_unused

    res: List[Node] = []

    # Note that we start with root.children, not root, since root is not a candidate
    # Also, we do a copy, or else q.pop is equivalent to root.children.pop, which is actually mutating
    q = [c for c in root.children]

    while not isLevelUsed or level >= 0:
        for _ in range(len(q)):
            top = q.pop(0)
            if top.type == childType:
                res.append(top)

            for child in top.named_children:
                q.append(child)

            if isLevelUsed and level < 0:
                return res
        if not q:
            return res
        level -= 1

    return res


def find_all_children_of_types(
    root: Optional[Node], childTypes: List[str], level: int=default_unused
) -> List[Node]:
    """
    Return the all children to the node `root` that has type `childType` within a positive depth of `level`.
    The return order is the same as the search order, which is breadth-first, level order.

    This means that the return order maintains the hierarchy of `root`.

    `root` itself IS NOT a child to itself.

    TODO: Write with TreeCursor to avoid memory overhead since there's no tail recursion here
    """

    if not root:
        return []

    childTypesS: Set[str] = set(childTypes)  # Convert childTypes to set for faster lookups
    res: List[Node] = []
    cursor = root.walk()
    isLevelUsed = level != default_unused


    def traverse(cursor: TreeCursor, level: int):
        if isLevelUsed and level < 0:
            return

        if cursor.node.type in childTypesS:
            res.append(cursor.node)

        if cursor.goto_first_child():
            traverse(cursor, level - 1)
            while cursor.goto_next_sibling():
                traverse(cursor, level - 1)
            cursor.goto_parent()

    traverse(cursor, level)

    return res


def get_deepest_children(root: Node) -> Node:
    if not root.children:
        return root
    return get_deepest_children(root.children[len(root.children) - 1])


def get_all_children_at_level(root: Node, level: int) -> List[Node]:
    if not root:
        return []
    if level < 0:
        print(f"invalid level {level}")
        exit(1)

    res: List[Node] = []

    def recur(root: Node, level: int):
        if level == 0:
            res.append(root)
        else:
            for child in root.children:
                recur(child, level - 1)

    recur(root, level)
    return res


def get_all_children_at_level_of_type(
    root: Node, childType: str, level: int
) -> List[Node]:
    if not root:
        return []
    if level < 0:
        print(f"invalid level {level}")
        exit(1)

    res: List[Node] = []

    def recur(root: Node, level: int):
        if level == 0:
            if root.type == childType:
                res.append(root)
        else:
            for child in root.children:
                recur(child, level - 1)

    recur(root, level)
    return res


def group_by_type_capture(root: Optional[Node], queryStr: str) -> Dict[str, List[Node]]:
    """
    Do a tree_sitter capture and reformat results into `{ node_type: [node1, node2], node_type2: [node3, node4] }`
    Note that the type is user-specified after the @, and not the grammatical type of the node
    """
    if not root: return {}

    tree_sitter_query = Environment.language.query(queryStr)
    captures = tree_sitter_query.captures(root)
    res: Dict[str, List[Node]] = defaultdict(list)
    for node, type in captures:
        res[type].append(node)

    return dict(res)


def group_by_type_capture_up_to_depth(
    root: Node, queryStr: str, maxDepth: int
) -> Dict[str, List[Node]]:
    """
    group_by_type_capture, but only up to a certain depth
    You can use this to simulate almost capturing exclusively at the root node

    By "at the root node", I mean, if a class_declaration has many nested class_declaration nodes,
    The query ignores the nested ones. However, this would a maxDepth of less than 2, because
    2 layers lay between a class_declaration and a potential nested class_declaration

    Note that this function captures all nodes as usual, and then start filtering them based on depth.
    There is probably no way to optimize this unless we wirte our own query engine.
    """

    tree_sitter_query = Environment.language.query(queryStr)
    captures = tree_sitter_query.captures(root)
    res: Dict[str, List[Node]] = defaultdict(list)
    for node, type in captures:

        def is_node_in_depth(node: Optional[Node], depth: int) -> bool:
            if not node or depth < 0:
                return False
            if node.id == root.id:
                return True
            return is_node_in_depth(node.parent, depth - 1)

        if is_node_in_depth(node, maxDepth):
            res[type].append(node)

    return dict(res)