"""
This is a temporary file that will be refactored after we do some major refactoring that 
moves each subcomponent into its own file.
"""

from itertools import chain
import logging
from typing import Callable, Dict, Generator, Iterable, List, Optional, Tuple, TypeVar
from tree_sitter import Node
from Context.Java import JavaContext
from my_enums.java import JAVA_ERR_FULL_TYPE, JAVA_VAR_ARG_COUNT, JavaGrammarKeywords, JavaModelTypes
from utils.tree_sitter import (
    find_all_ancestors_of_types,
    find_closest_ancestor_of_type,
    find_first_child_of_type,
    group_by_type_capture,
)

from my_types.java import class_cache_field, enum_cache_field, interface_cache_field, JavaFullType, aliased_type


def get_package_name(context_node: Node) -> str: 
    def package_name_from_program_node(program_node: Optional[Node]) -> str:
        if not program_node:
            return "unnamed"

        package_capture = group_by_type_capture(
            program_node,
            "(package_declaration [(identifier)@package_name (scoped_identifier)@package_name])",
        )
        package_name = (
            package_capture["package_name"][0].text.decode("utf8")
            if "package_name" in package_capture
            else "unnamed"
        )
        return package_name

    program_node = find_closest_ancestor_of_type(context_node, JavaGrammarKeywords.PROGRAM) or context_node
    
    return package_name_from_program_node(program_node)

def get_contained_by(context_node: Optional[Node]) -> JavaFullType:
    '''
    Get the `JavaFullType` of the closest container (self-exclusive).
    By self-exclusive, I mean that if `context_node` is some model node, this method does not return itself.
    '''

    if not context_node:
        return JAVA_ERR_FULL_TYPE

    outer_nodes = reversed(
        find_all_ancestors_of_types(
            context_node,
            [
                JavaGrammarKeywords.CLASS_DECLARATION,
                JavaGrammarKeywords.INTERFACE_DECLARATION,
            ],
        )
    )
    outer_name_nodes = map(
        lambda node: find_first_child_of_type(node, JavaGrammarKeywords.IDENTIFIER, 1),
        outer_nodes,
    )
    outer_names = ".".join(list(map(
        lambda node: node.text.decode("utf8") if node else "",
        outer_name_nodes,
    )))
    split = outer_names.rsplit(".", maxsplit=1)
    package_name = get_package_name(context_node)

    if len(split) == 1: 
        shorthand = split[0]
        return JavaFullType(package_name, "", shorthand)
    else: 
        contained_in, shorthand = split
        return JavaFullType(package_name, contained_in, shorthand)


def alias_map_from_program_node(
    program_node: Node,
) -> Dict[aliased_type, JavaFullType]:
    """
    Given `root`, which might contain some import_declaration, generate the alias mapping.

    Example output:
    {
        "Child": (src.shared_files, "", Child)
        "Child.Nested": (src.shared_files, "Child", "Nested")
    }
    """
    importables: Dict[aliased_type, JavaFullType] = dict()

    # First, include other importables from the same package
    package_name = get_package_name(program_node)

    for (_, _contained_by, _shorthand) in JavaContext.cache.packages_to_importables[package_name]:
        importables[_shorthand] = JavaFullType(package_name, _contained_by, _shorthand)

    # Second at last, analyze import statements
    import_capture = group_by_type_capture(
        program_node,
        "(import_declaration [(identifier)@identifier (scoped_identifier)@scoped_identifier])",
    )
    """
    java import statements combine the package and nested classes
    import Container.A.B; // Could mean import class B of class A of package Container, or class B of package Container.A
    import Container.AnotherContainer.*; // Could mean import all from package Container.AnotherContainer, or import all from class AnotherContainer of package Container

    Our code must check all possibilities and find the one that's possible.
    """
    for node in import_capture["identifier"] if "identifier" in import_capture else []:
        path = node.text.decode("utf8")
        # Single identifier without asterisk, e.g., "import A" means nothing.
        if node.next_named_sibling and node.next_named_sibling.type == "asterisk":
            for (_, contained_by, shorthand) in JavaContext.cache.packages_to_importables[path]:
                importables[shorthand] = JavaFullType(path, contained_by, shorthand)
    for node in (
        import_capture["scoped_identifier"]
        if "scoped_identifier" in import_capture
        else []
    ):
        path = node.text.decode("utf8")
        # if no asterisk, like Container.A.B, start splitting at the last dot, into Container.A
        import_all = bool(
            node.next_named_sibling and node.next_named_sibling.type == "asterisk"
        )
        dots_count = path.count(".")
        # if import all, entire path could be package, so start splitting at 0 maxsplits
        for maxsplit in range(0 if import_all else 1, dots_count):
            splits = path.rsplit(".", maxsplit=maxsplit)
            package = ".".join(splits[: len(splits) - maxsplit])

            # query against cache to see if it's possible
            if package in JavaContext.cache.packages_to_importables:
                if import_all:
                    for (_, contained_by, shorthand) in JavaContext.cache.packages_to_importables[package]:
                        importables[shorthand] = JavaFullType(package, contained_by, shorthand)

                        for (
                            package_,
                            contained_by_,
                            shorthand_,
                        ) in get_inners(
                            JavaFullType(package, contained_by, shorthand)
                        ):
                            importables[".".join([contained_by_, shorthand_])] = JavaFullType(
                                package_,
                                contained_by_,
                                shorthand_,
                            )
                else:
                    rest = splits[len(splits) - maxsplit :]
                    contained_by = ".".join(rest[: len(rest) - 1])  # all until last
                    shorthand = rest[len(rest) - 1]
                    importables[shorthand] = JavaFullType(package, contained_by, shorthand)

                    for (
                        package_,
                        contained_by_,
                        shorthand_,
                    ) in get_inners(JavaFullType(package, contained_by, shorthand)):
                        importables[".".join([contained_by_, shorthand_])] = JavaFullType(
                            package_,
                            contained_by_,
                            shorthand_,
                        )
                break

    return importables

def compare_aliased_type_segments(
    aliased_type_a: aliased_type, 
    aliased_type_b: aliased_type,
    segment_transform: Callable[[List[str]], Iterable[str]] = lambda x: x
) -> bool:
    """
    Determines if the type `aliased_type_a` has matching segments with `aliased_type_b`.

    The `segment_transform` argument is used to specify the order of the segments to be checked.
    By default, it checks from the start (like `does_aliased_type_A_start_with_B`). 
    If `segment_transform` is `reversed`, it checks from the end (like `does_aliased_type_A_end_with_B`).
    """

    a_splits = list(segment_transform(aliased_type_a.split(".")))
    b_splits = list(segment_transform(aliased_type_b.split(".")))

    if len(b_splits) > len(a_splits):
        return False

    for (a_segment, b_segment) in zip(a_splits, b_splits):
        if a_segment != b_segment:
            return False
    return True

def does_aliased_type_A_start_with_B(
    aliased_type_a: aliased_type, aliased_type_b: aliased_type
) -> bool:
    """
    Determines if the type `aliased_type_a` starts with the type `aliased_type_b`.
    """
    if not (aliased_type_b and aliased_type_a):
        return True
    return compare_aliased_type_segments(aliased_type_a, aliased_type_b)

def does_aliased_type_A_end_with_B(
    aliased_type_a: aliased_type, aliased_type_b: aliased_type
) -> bool:
    """
    Analogous to `does_aliased_type_A_start_with_B`
    """
    if not aliased_type_b:
        return True
    return compare_aliased_type_segments(aliased_type_a, aliased_type_b, segment_transform=reversed)

def get_inners(model: JavaFullType) -> Generator[JavaFullType, None, None]:
    """
    Return models physically lying in `model`'s body. 
    Btw, this method was previously named `get_all_children_models` — a confusing decision since "children" infers inheritance.

    I/O Example:
    `(edu.com, container_1, container_2)` -> `[(edu.com, container_1.container_2, foo), (edu.com, container_1.container_2, bar)]`
    
    Note that the following does NOT work
    `(edu.com, _, _)` -> `[(edu.com, _, A), (edu.com, _, B)]` (top level classes)
    """

    if not (model.contained_by or model.shorthand): 
        logging.debug(f"Encountered empty type of package {model.package_name} querying get_inners")
        return

    search_package, search_containing_models, search_shorthand = model

    if not (search_containing_models or search_shorthand): return 

    for (package, contained_by, shorthand) in JavaContext.cache.packages_to_importables[search_package]:
        if search_containing_models and does_aliased_type_A_start_with_B(contained_by, f"{search_containing_models}.{search_shorthand}"): 
            yield JavaFullType(package, contained_by, shorthand)
        elif does_aliased_type_A_start_with_B(contained_by, search_shorthand):
            yield JavaFullType(package, contained_by, shorthand)

def aliased_type_to_container_and_shorthand(
    aliased_type: aliased_type,
) -> Tuple[str, str]:
    if not aliased_type:
        return ("", "")
    if "." not in aliased_type:
        return ("", aliased_type)
    splits = aliased_type.split(".")
    return (".".join(splits[: len(splits) - 1]), splits[len(splits) - 1])

def get_parents(model: JavaFullType) -> List[JavaFullType]:
    '''
    Ignores empty ("", "", "") extends
    '''
    if model not in JavaContext.cache.models_cache: return []
    cache = JavaContext.cache.models_cache[model]
                
    if type(cache) is interface_cache_field: 
        return cache.extends
    elif type(cache) is class_cache_field:
        res = cache.implements
        if cache.extends: 
            res.append(cache.extends)
        return res
    elif type(cache) is enum_cache_field:
        return cache.implements
    return []

def aliased_type_to_full_type(
    aliased_type: aliased_type, start_context_node: Node
) -> JavaFullType:
    """
    Resolve the full type, given its `aliased_type` and the `start_context_node` to start resolving from.
    Note that `aliased_type` is usually the shorthand, but could be the full type

    Internally, the algorithm travels up from the `start_context_node` and searching for file level declarations of `aliased_type`.
    If `aliased_type` is not declared at the file level, the algorithm queries the imports to find the declaration.

    This algorithm has an unexpected large amount of code. Unfortunately, simple solutions like traversing through `packages_to_importables` for 
    local models does not suffice. This is due to the edge case where nested classes have the same name (Class A and B both with inner class C, this is grammatically valid).
    """

    (
        aliased_type_container,
        aliased_type_shorthand,
    ) = aliased_type_to_container_and_shorthand(aliased_type)


    # BEGIN: Check if type is declared locally (within the same file). Find by traversing the models in the file.
    container = get_contained_by(start_context_node)
    package_name = get_package_name(start_context_node)

    for model in traverse_inners_of_outers_and_ancestors(container):
        _, contained_in, shorthand = model 
        if does_aliased_type_A_end_with_B(contained_in, aliased_type_container) and shorthand == aliased_type_shorthand:
            return model
    # END: Check if type is declared locally (within the same file). Find by traversing the models in the file.

    # BEGIN: Check if type is declared outside of the file and imported (explicitly or implicitly)
    program_node = find_closest_ancestor_of_type(
        start_context_node, JavaGrammarKeywords.PROGRAM
    )
    assert program_node
    importables = alias_map_from_program_node(program_node)

    if aliased_type in importables:
        return importables[aliased_type]

    def is_aliased_type_full_type(
        full_type_candidate: str,
    ) -> Tuple[bool, JavaFullType]:
        dots_count = full_type_candidate.count(".")
        if dots_count == 0: 
            # Only possibly full_type if current package is unnamed and full_type_candidate is also in unnamed 
            if package_name == "unnamed" and full_type_candidate in JavaContext.cache.packages_to_importables["unnamed"]: 
                return (True, JavaFullType("unnamed", "", full_type_candidate))
            else: 
                return (False, JAVA_ERR_FULL_TYPE)
        for maxsplit in range(1, dots_count):
            splits = full_type_candidate.rsplit(".", maxsplit=maxsplit)
            package = ".".join(splits[: len(splits) - maxsplit])
            rest = splits[len(splits) - maxsplit :]
            contained_by = ".".join(rest[: len(rest) - 1])  # all until last
            shorthand = rest[len(rest) - 1]

            if (
                package in JavaContext.cache.packages_to_importables
                and JavaFullType(package, contained_by, shorthand)
                in JavaContext.cache.packages_to_importables[package]
            ):
                return (True, JavaFullType(package, contained_by, shorthand))

        return (False, JAVA_ERR_FULL_TYPE)
    # END: Check if type is declared outside of the file and imported (explicitly or implicitly)

    # At last, check if type is already written in full type form
    is_full_type, full_type = is_aliased_type_full_type(aliased_type)
    if is_full_type:
        return full_type

    return JAVA_ERR_FULL_TYPE

def formal_parameters_count(formal_parameters_node: Node) -> int:
    """
    (int a, int b) -> 2
    (int ...a) -> special number 256
    """
    assert formal_parameters_node.type == JavaGrammarKeywords.FORMAL_PARAMETERS
    cnt = 0
    for child in formal_parameters_node.children:
        match child.type:
            case JavaGrammarKeywords.FORMAL_PARAMETER:
                cnt += 1
            case JavaGrammarKeywords.SPREAD_PARAMETER:
                return JAVA_VAR_ARG_COUNT

    return cnt

def argument_list_count(argument_list_node: Node) -> int:
    """
    Basically the same as `formal_parameters_count`.
    (int a, int b) -> 2
    """
    assert argument_list_node.type == JavaGrammarKeywords.ARGUMENT_LIST
    return argument_list_node.named_child_count

def traverse_outers(model: JavaFullType) -> Generator[JavaFullType, None, None]: 
    package_name, contained_in, _ = model 
    split = contained_in.rsplit(".", maxsplit=1)
    if split == [""]: return 
    elif len(split) == 1: 
        new_contained_in, new_shorthand = "", split[0]
    else: 
        new_contained_in, new_shorthand = split

    next_outer_model = JavaFullType(package_name, new_contained_in, new_shorthand)
    yield next_outer_model
    yield from traverse_outers(next_outer_model)

def traverse_parents(model: JavaFullType) -> Generator[JavaFullType, None, None]: 
    '''
    Ignores empty ("", "", "") extends
    '''
    if model not in JavaContext.cache.models_cache: return
    cache = JavaContext.cache.models_cache[model]
                
    if type(cache) is interface_cache_field: 
        yield from cache.extends
    elif type(cache) is class_cache_field:
        yield from filter(None, [*cache.implements, cache.extends])
    elif type(cache) is enum_cache_field:
        yield from cache.implements

T = TypeVar('T')
def recursive(generator: Callable[[T], Generator[T, None, None]]) -> Callable[[T], Generator[T, None, None]]: 
    def _inner(value: T) -> Generator[T, None, None]:
        for next in generator(value):
            yield next 
            yield from generator(next)
    
    return _inner

traverse_ancestors = recursive(traverse_parents)
    
def traverse_outers_and_ancestors(model: JavaFullType) -> Generator[JavaFullType, None, None]:
    '''
    Does not return `model` itself.
    Returns
    1) `model`'s ancestors are returned
    2) `model`'s outers and each of the outer's ancestors are returned

    Importantly, the outers of the ancestors are never returned.
    '''

    yield from traverse_ancestors(model)
    
    for outer_model in traverse_outers(model): 
        yield outer_model
        yield from traverse_ancestors(outer_model)

def unique(generator: Callable[[T], Generator[T, None, None]]) -> Callable[[T], Generator[T, None, None]]: 
    '''
    Decorates a generator to return unique items.
    '''
    def _inner(value: T) -> Generator[T, None, None]: 
        seen = set()
        for next in generator(value):
            if next not in seen: 
                yield next 
                seen.add(next)
    
    return _inner

@unique
def traverse_inners_of_outers_and_ancestors(model: JavaFullType) -> Generator[JavaFullType, None, None]:
    '''
    Returns
    1) `model` itself
    2) The inner models within `model`.
    3) The inner models within `model`'s ancestors
    4) Repeat 1-2 for all of `model`'s outer model 

    Importantly, akin to `traverse_outers_and_ancestors`, the outers of the ancestors are never returned
    '''
    for model in [model, *traverse_outers(model)]: 
        yield model
        yield from get_inners(model)
        for model in traverse_ancestors(model):
            yield model
            yield from get_inners(model)

