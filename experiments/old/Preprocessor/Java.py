from collections import defaultdict
from itertools import chain
from utils.java import aliased_type_to_container_and_shorthand, get_contained_by, alias_map_from_program_node
from my_enums.java import JAVA_ERR_FULL_TYPE, JavaGrammarKeywords, JavaModelTypes, type_query
from my_types.java import JavaMethodKey, enum_cache_field, packages_to_importables
from Context.Java import JavaContext
from utils.tree_sitter import *
from utils.general import map_dict
from Preprocessor.Base import Preprocessor

from my_types.java import (
    class_cache_field,
    interface_cache_field,
    models_cache,
    packages_to_importables,
    JavaMethodDict,
    JavaFullType,
)

class JavaPreprocessor(Preprocessor):
    def preprocess(self):
        JavaContext.method_dict = self.makeMethodDict()
        JavaContext.cache.packages_to_importables = self.makePackgesToImportables()
        JavaContext.cache.models_cache = self.makeModelsCache()

    def makeMethodDict(self) -> JavaMethodDict:
        method_dict: JavaMethodDict = defaultdict()
        query = Environment.language.query(
            """
				(method_declaration
					name: (identifier) @method_name
					parameters: (formal_parameters) @method_params) @method
				(constructor_declaration
					name: (identifier) @method_name
					parameters: (formal_parameters) @method_params) @method
				"""
        )
        for path in JavaContext.files:
            with open(path, "rb") as file:
                src = file.read()
                root_node = Environment.parser.parse(src).root_node
                captures = query.captures(root_node)
                # indices whose corresponding values in captures are methods
                method_indices = [
                    i for i, capture in enumerate(captures) if capture[1] == "method"
                ]

                for i in method_indices:
                    method_node = captures[i][0]
                    method_name_node = find_first_child_of_type(
                        method_node, "identifier", 1
                    )
                    method_params_node = find_first_child_of_type(
                        method_node, "formal_parameters", 1
                    )

                    method_name = (
                        method_name_node.text.decode("utf8") if method_name_node else ""
                    )

                    method_params = (
                        method_params_node.text.decode("utf8")
                        if method_params_node
                        else ""
                    )

                    method_container = get_contained_by(method_node)

                    method_params_count = len(
                        [
                            arg
                            for arg in method_params[1 : len(method_params) - 1].split(
                                ","
                            )
                            if arg
                        ]
                    )

                    modifiers_node = find_first_child_of_type(
                        method_node, JavaGrammarKeywords.MODIFIERS, 1
                    )
                    modifiers = (
                        (modifiers_node.text.decode("utf8")).split()
                        if modifiers_node
                        else []
                    )
                    return_type_captures = group_by_type_capture_up_to_depth(method_node, f"[(method_declaration (modifiers)? {type_query}) (constructor_declaration (identifier)@type)]", 2)
                    return_type = return_type_captures["type"][len(return_type_captures["type"])-1].text.decode("utf8")
                    # Append to method_dict
                    key = JavaMethodKey(
                        method_container,
                        method_name,
                        method_params_count,
                    )
                    method_dict[key] = {"node": method_node, "modifiers": modifiers, "return_type": return_type}

        return dict(method_dict)

    def makePackgesToImportables(self) -> packages_to_importables:
        # Example: {"edu.com": { "Wizard" : {"type": "class"}, { "IDriver": {"type": "interface"}} }, "edu.com.ui": { "Drawer": {"type": "class"} }}
        packages2importables: packages_to_importables = defaultdict(list)
        packages2importables["unnamed"]
        for path in JavaContext.files:
            with open(path, "rb") as file:
                src = file.read()
                tree = Environment.parser.parse(src)
                tree_node = tree.root_node

                package_capture = group_by_type_capture(
                    tree_node,
                    "(package_declaration [(identifier)@package_name (scoped_identifier)@package_name])",
                )
                package = (
                    package_capture["package_name"][0].text.decode("utf8")
                    if "package_name" in package_capture
                    else "unnamed"
                )

                top_level_importables_capture = group_by_type_capture(
                    tree_node,
                    "(program [(class_declaration)@importable (interface_declaration)@importable (enum_declaration)@importable])",
                )
                top_level_nodes = (
                    top_level_importables_capture["importable"]
                    if "importable" in top_level_importables_capture
                    else []
                )

                for top_level_node in top_level_nodes:

                    def recur_gather_importable(prefix: List[str], curNode: Node):
                        # precondition: curNode is class/interface
                        assert curNode.type in [
                            JavaGrammarKeywords.CLASS_DECLARATION,
                            JavaGrammarKeywords.INTERFACE_DECLARATION,
                            JavaGrammarKeywords.ENUM_DECLARATION
                        ]

                        # enroll curNode into packages_to_importables
                        capture = group_by_type_capture_up_to_depth(
                            curNode,
                            "[(class_declaration (modifiers)?@modifiers (identifier)@importable_name)@importable (interface_declaration (modifiers)?@modifiers (identifier)@importable_name)@importable (enum_declaration (modifiers)?@modifiers (identifier)@importable_name)]",
                            1,
                        )

                        importable_name = capture["importable_name"][0].text.decode(
                            "utf8"
                        )

                        contained_by = ".".join(prefix)
                        packages2importables[package].append(JavaFullType(package, contained_by, importable_name))
                    

                        nested_class_declarations = get_all_children_at_level_of_type(
                            curNode, JavaGrammarKeywords.CLASS_DECLARATION, 2
                        )
                        nested_interface_declarations = (
                            get_all_children_at_level_of_type(
                                curNode, JavaGrammarKeywords.INTERFACE_DECLARATION, 2
                            )
                        )
                        nested_enum_declarations = get_all_children_at_level_of_type(
                            curNode, JavaGrammarKeywords.ENUM_DECLARATION, 2
                        )

                        # enroll curNode's children into packages_to_importables
                        for child in chain(
                            nested_class_declarations, nested_interface_declarations, nested_enum_declarations
                        ):
                            recur_gather_importable(prefix + [importable_name], child)

                    recur_gather_importable([], top_level_node)

        return dict(packages2importables)

    # Class Cache Example: {"edu.com": { "fields": { "field1": {"type" : "ClassA"} } } }
    def makeModelsCache(self) -> models_cache:
        # Precondition: packages to importables cache is built. 
        # It is built either if the unnamed package has cached something (> 0) or if other package is cached (> 1)
        assert (
            len(JavaContext.cache.packages_to_importables["unnamed"]) > 0
            or len(JavaContext.cache.packages_to_importables) > 1
        )
        cache: models_cache = defaultdict()

        for path in JavaContext.files:
            with open(path, "rb") as file:
                src = file.read()
                tree = Environment.parser.parse(src)
                tree_node = tree.root_node

                package_capture = group_by_type_capture(
                    tree_node,
                    "(package_declaration [(identifier)@package_name (scoped_identifier)@package_name])",
                )
                package = (
                    package_capture["package_name"][0].text.decode("utf8")
                    if "package_name" in package_capture
                    else "unnamed"
                )

                importables = alias_map_from_program_node(tree_node)

                model_nodes = find_all_children_of_types(
                    tree_node,
                    [
                        JavaGrammarKeywords.CLASS_DECLARATION,
                        JavaGrammarKeywords.INTERFACE_DECLARATION,
                        JavaGrammarKeywords.ENUM_DECLARATION
                    ],
                )

                for model_node in model_nodes:
                    name_node = find_first_child_of_type(model_node, "identifier", 1)
                    model_name = name_node.text.decode("utf8") if name_node else ""
                    model_body_node = find_first_child_of_type(
                        model_node,
                        "class_body"
                        if model_node.type == JavaGrammarKeywords.CLASS_DECLARATION
                        else "interface_body",
                        1,
                    )

                    containing_models_nodes = reversed(
                        find_all_ancestors_of_types(
                            model_node,
                            [
                                JavaGrammarKeywords.CLASS_DECLARATION,
                                JavaGrammarKeywords.INTERFACE_DECLARATION,
                                JavaGrammarKeywords.ENUM_DECLARATION
                            ],
                        )
                    )
                    containing_models_names_nodes = map(
                        lambda node: find_first_child_of_type(
                            node, JavaGrammarKeywords.IDENTIFIER, 1
                        ),
                        containing_models_nodes,
                    )
                    containing_models_names = map(
                        lambda node: node.text.decode("utf8") if node else "",
                        containing_models_names_nodes,
                    )
                    containing_models = ".".join(list(containing_models_names))

                    model_modifiers_node = find_first_child_of_type(
                        model_node, JavaGrammarKeywords.MODIFIERS, 1
                    )
                    model_modifiers = (
                        model_modifiers_node.text.decode("utf8").split()
                        if model_modifiers_node
                        else []
                    )

                    def get_full_type_of_parent_model(type: str) -> Optional[JavaFullType]:
                        if type in importables:
                            return importables[type]
                        # same package
                        elif ("", type) in JavaContext.cache.packages_to_importables[package]:
                            return JavaFullType(package, "", type)
                        else:
                            print(
                                f"Warning: {type} is not found in file scope or imported files scope. Probably a default type"
                            )
                            # And I return err full type because we want to ignore default type.
                            return None

                    match model_node.type:
                        case JavaGrammarKeywords.CLASS_DECLARATION:
                            # cache fields
                            field_declaration_nodes = find_all_children_of_type(
                                model_body_node, "field_declaration", 1
                            )
                            fields = {}
                            for node in field_declaration_nodes:
                                query_str = f"(field_declaration (modifiers)?@modifiers {type_query} (variable_declarator (identifier)@variable_identifier))"
                                captures = group_by_type_capture(node, query_str)
                                modifiers = (
                                    (
                                        captures["modifiers"][0].text.decode("utf8")
                                    ).split()
                                    if "modifiers" in captures
                                    else []
                                )

                                field_type = (
                                    captures["type"][
                                        len(captures["type"]) - 1
                                    ].text.decode("utf8")
                                    if "type" in captures
                                    else ""
                                )
                                field_identifier = (
                                    captures["variable_identifier"][0].text.decode(
                                        "utf8"
                                    )
                                    if "variable_identifier" in captures
                                    else ""
                                )
                                fields[field_identifier] = {
                                    "modifiers": modifiers,
                                    "type": field_type,
                                }

                            # cache extends and implements

                            # One small note: tree-sitter playground seems to be using outdated java keywords. They use "interface_type_list" instead of "type_list"
                            inheritance_query = "(class_declaration (modifiers)?@modifiers (superclass (type_identifier)@super_class)? (super_interfaces (type_list (type_identifier)@interface))?)"
                            inheritance_captures = group_by_type_capture_up_to_depth(
                                model_node, inheritance_query, 3
                            )

                            super_class_full_type: Optional[JavaFullType] = None
                            implements: List[JavaFullType] = []
                            if "super_class" in inheritance_captures:
                                super_class = inheritance_captures["super_class"][
                                    0
                                ].text.decode("utf8")
                                super_class_full_type = get_full_type_of_parent_model(
                                    super_class
                                )
                            if "interface" in inheritance_captures:
                                implements = list(
                                    filter(None, map(
                                        lambda n: get_full_type_of_parent_model(
                                            n.text.decode("utf8")
                                        ),
                                        inheritance_captures["interface"],
                                    ))
                                )

                            class_cache_temp = class_cache_field(fields=fields, extends=super_class_full_type, implements=implements, type=JavaModelTypes.CLASS, modifiers=model_modifiers, methods=set())
                            cache[
                                JavaFullType(package, containing_models, model_name)
                            ] = class_cache_temp
                        case JavaGrammarKeywords.INTERFACE_DECLARATION:
                            # Cache "super interfaces".
                            inheritance_query = "(extends_interfaces (type_list (type_identifier)@interface))"
                            inheritance_captures = group_by_type_capture(
                                model_node, inheritance_query
                            )

                            extend_interfaces: List[JavaFullType] = (
                                list(
                                    filter(None, map(
                                        lambda n: get_full_type_of_parent_model(
                                            n.text.decode("utf8")
                                        ),
                                        inheritance_captures["interface"],
                                    ))
                                )
                                if "interface" in inheritance_captures
                                else []
                            )

                            # Cache constants. They are really just fields, but they are named constants here since all interface fields are final.
                            constant_nodes = find_all_children_of_type(
                                model_body_node, "constant_declaration", 1
                            )
                            constants = {}
                            for node in constant_nodes:
                                inheritance_query = f"(constant_declaration (modifiers)?@modifiers {type_query} (variable_declarator (identifier)@variable_identifier))"
                                captures = group_by_type_capture(
                                    node, inheritance_query
                                )
                                modifiers = (
                                    (
                                        captures["modifiers"][0].text.decode("utf8")
                                    ).split()
                                    if "modifiers" in captures
                                    else []
                                )
                                constant_type = (
                                    captures["type"][
                                        len(captures["type"]) - 1
                                    ].text.decode("utf8")
                                    if "type" in captures
                                    else ""
                                )
                                constant_identifier = (
                                    captures["variable_identifier"][0].text.decode(
                                        "utf8"
                                    )
                                    if "variable_identifier" in captures
                                    else ""
                                )
                                constants[constant_identifier] = {
                                    "modifiers": modifiers,
                                    "type": constant_type,
                                }
                            interface_cache_temp = interface_cache_field(constants=constants, extends=extend_interfaces, type=JavaModelTypes.INTERFACE, modifiers=model_modifiers, methods=set())

                            cache[
                                JavaFullType(package, containing_models, model_name)
                            ] = interface_cache_temp
                        case JavaGrammarKeywords.ENUM_DECLARATION:
                            # inheritance_query = "(class_declaration (super_interfaces (type_list (type_identifier)@interface))?)"
                            # inheritance_captures = group_by_type_capture_up_to_depth(
                                # model_node, inheritance_query, 3
                            # )
                            inheritance_query = "(super_interfaces (type_list (type_identifier)@interface))?"
                            inheritance_captures = group_by_type_capture_up_to_depth(
                                model_node, inheritance_query, 3
                            )

                            implements: List[JavaFullType] = []
                            if "interface" in inheritance_captures:
                                implements = list(
                                    filter(None, map(
                                        lambda n: get_full_type_of_parent_model(
                                            n.text.decode("utf8")
                                        ),
                                        inheritance_captures["interface"],
                                    ))
                                )
            
                            enum_constant_nodes = model_node.child_by_field_name("body").children_by_field_name("enum_constant")
                            enum_constants = map(lambda n: n.child_by_field_name("identifier").text.decode("utf8"), enum_constant_nodes)
                            enum_cache = enum_cache_field(implements=implements, modifiers=model_modifiers, type=JavaModelTypes.ENUM, enum_constants=enum_constants, methods=set())
                            cache[JavaFullType(package, containing_models, model_name)] = enum_cache

        # Cache what methods each model contains
        for method in JavaContext.method_dict: 
            method_container, _, _ = method 
            if method_container.shorthand:
                cache[method_container].methods.add(method)

        return map_dict(cache, dict)  # change all nested defaultdicts in cache to dicts
