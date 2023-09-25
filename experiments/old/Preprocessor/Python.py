import os
from collections import defaultdict
from itertools import chain
from typing import Dict, List
from TypeResolver.Python.Identifier import PythonIdentifierResolver
from TypeResolver.Python.Assignment import PythonAssignmentResolver
from my_enums.python import PythonGrammarKeywords, PythonModelTypes
from my_enums.shared import InvokeType
from Context.Python import PythonContext
from utils.tree_sitter import *
import logging
from Preprocessor.Base import Preprocessor

from my_types.python import (
    python_class_cache_field,
    python_function_cache_field,
    python_variable_cache_field,
    python_models_cache,
    return_types,
    python_model_cache_field
)


class PythonPreprocessor(Preprocessor):
    ct = 0
    no_Ext_Files = {}
    
    def preprocess(self):
        PythonContext.method_dict = self.makeMethodDict()
        #PythonContext.python_uniques = self.makeUniqueMethodsDict()
        #PythonContext.imports_by_file = self.makePathtoImportables()
        PythonContext.cache["models_cache"] = self.makeModelsCache()
        


    '''
    makeMethodDict creates a dictionary for all function definitions in PythonContext.files
    Outpute format: {(pathto_file, file_name, class_name, method_name):
                        'index': self.ct, 
                        'nodes': method_node, 
                        'method': method_name,
                        'type': invstr,
                        'argument_count' :  method_params_node.named_child_count}
    Requires: PythonContext.files, Environment.language, Environment.parser & Invoke.type
    Returns: methoddict
    '''
    def makeMethodDict(self) -> Dict:
        method_dict = defaultdict(dict)
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
		
        method_import_q = Environment.language.query("""
            (function_definition
                name: (identifier) @method_name
                parameters: (parameters) @method_params) @method
            (import_statement 
                name: (dotted_name) @import)
            (import_from_statement
                module_name: (dotted_name) @import)
            """)
        for path in PythonContext.files:
            #Check if Python File
            if path.split('.')[-1] != 'py':
                continue
            with open(path, 'rb') as file: 
                src = file.read()
                tree = Environment.parser.parse(src)
                captures = method_import_q.captures(tree.root_node)

				# indices whose corresponding values in captures are methods
                method_indices = [i for i, capture in enumerate(
					captures) if capture[1] == 'method']

                for i in method_indices:
                    method_node = captures[i][0]
                    class_declaration_node = find_closest_ancestor_of_type(
                		method_node, "class_definition")
                    class_name_node = find_first_child_of_type(
                		class_declaration_node, "identifier", 1)
                    method_name_node = find_first_child_of_type(
                		method_node, "identifier", 1)
                    descriptor_name_node = find_closest_ancestor_of_type(
                		method_node, "decorated_definition")
                    descriptor_name_node = find_first_child_of_type(
						descriptor_name_node, "decorator", 1)
                    method_params_node = find_first_child_of_type(
						method_node, "parameters", 1)
        
                    class_name = class_name_node.text.decode(
                		"utf8") if class_name_node else ""
                    method_name = method_name_node.text.decode(
                		"utf8") if method_name_node else ""
                    descriptor_name = descriptor_name_node.text.decode(
						"utf8") if  descriptor_name_node else ""


                    assert(method_params_node is not None) 

                    path_split = os.path.split(path)
                    
                    invstr = InvokeType.equivalent(descriptor_name, class_name)

                    key = (
                        path_split[0], 
                        path_split[1], 
                        class_name, 
                        method_name, 
                        )

                    method_dict[key] = { 
                        'index': self.ct, 
                        'nodes': method_node, 
                        'method': method_name,
                        'type': invstr,
                        'argument_count' :  method_params_node.named_child_count
                        } 
                

                    logging.info("(%s, %s, %s, %s, %d) : Key Added\n", path_split[0], path_split[1], class_name, method_name)

                    self.ct += 1

        return dict(method_dict)


    '''
    makePathtoImportable creates the import dictionary. each entry is of form
    {path : {(alias, imported): (path, contained)}}.
    Relies on instantiated PythonContext.language, PythonContext.files and Environment.parser 
    Returns: import dictionary
    Sets self.no_Ext_Files to dictionary of form {filenamenoextension : path}
    '''
    def makePathtoImportables(self):
        import_q = Environment.language.query("""(import_statement)@import
            (import_from_statement)@importfrom""") 
        imports_by_file_dict = {}
        filestoimportables ={file.split('\\')[-1].split('.')[0]: file \
                                for file in PythonContext.files if file.split('\\')[-1].split('.')[-1] == 'py'}
        self.no_Ext_Files = filestoimportables

        for path in PythonContext.files:
            import_dict = {}
            if path.split('.')[-1] != 'py':
                continue
            with open(path, 'rb') as file: 
                src = file.read()
                tree = Environment.parser.parse(src)
                captures = import_q.captures(tree.root_node)
                for capture in captures:
                    if capture[1] == "import":
                        imp_path, keys = self.importsToDictKeys(capture)
                        for key in keys:
                            import_dict[key[0], key[1]] = (self.no_Ext_Files.get(key[1]), key[2])

                    elif capture[1] == "importfrom":
                        relative = find_first_child_of_type(capture[0], "relative_import", 1)
                        #relativity is for "from .. import file" format, this line is incase we need
                        #relativity in the future
                        if relative:
                            relativity = find_first_child_of_type(relative, "import_prefix", 1)

                        imp_path, keys = self.importsToDictKeys(capture)
                        for key in keys:
                            import_dict[key[0], key[1]] = (imp_path, key[2])
            imports_by_file_dict[path] = import_dict

        return imports_by_file_dict

    '''
    importsToDictKeys helps makePathToImportables by producing the keys and
    values of an import statement.
    Input: self, capture (tree sitter node for an entire import statement)
    Returns: imp_path (path to importable file), info (list of tupels of form: 
             (str(alias), str(imported), list(containedby))
    '''
    def importsToDictKeys(self, capture):
        info = []
        imports = find_all_children_of_type(capture[0], "dotted_name",1)
        imports_text =  [i.text.decode("utf8") for i in imports] #if i.text in filestoimportables]
        imp_path = self.no_Ext_Files.get(imports_text[0], None)

        #Prescan to remove imports which aren't known files in repository
        if capture[1] == "importfrom" and not imp_path:
            return None, []
        aliased_imports = find_all_children_of_type(capture[0], "aliased_import",1)
        if capture[1] == "import":
            for imp in imports_text: #scanning import chain ex "import a, b, c"
                if not self.no_Ext_Files.get(imp, None):
                    imports_text.remove(imp)
            for aliased in aliased_imports: #scanning alias chain ex "import a as b, c as d, e"
                import_name = find_first_child_of_type(aliased, "dotted_name", 1).text.decode("utf8")
                if not self.no_Ext_Files.get(import_name, None):
                    aliased_imports.remove(aliased)
        #helper method which takes import str (ex "parent.child") and separates into object
        #and a list of where it is contained (ex. "child", ["parent"])
        def get_contained(key):
            contained = ''
            keysplit = key.split('.')
            if len(keysplit) > 1:
                contained = [name for name in keysplit[:-1]]
                key = keysplit[-1]
            return key, contained

        for imp in aliased_imports:
            import_alias = find_first_child_of_type(imp, "identifier", 1).text.decode("utf8")
            import_name = find_first_child_of_type(imp, "dotted_name", 1).text.decode("utf8")

            if import_name in imports_text:
                imports_text.remove(import_name)

            key, contained = get_contained(import_name)
            info.append((import_alias, key, contained))

        for imp in imports_text[0:]:
            key, contained = get_contained(imp)
            info.append(("", key, contained))

        return imp_path, info


    # Class Cache Example: {"edu.com": { "fields": { "field1": {"type" : "ClassA"} } } }
    def makeModelsCache(self) -> python_models_cache:
        path_to_importables : python_models_cache = defaultdict() 
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
        for path in PythonContext.files:
            with open(path, "rb") as file:
                src = file.read()
                tree = Environment.parser.parse(src)
                tree_node = tree.root_node
                top_level_importables_capture = group_by_type_capture(
                    tree_node,
                    "(module [(class_definition)@importable (function_definition)@importable (expression_statement)@importable])",
                )
                top_level_nodes = (
                    top_level_importables_capture["importable"]
                    if "importable" in top_level_importables_capture
                    else []
                )

                for top_level_node in top_level_nodes:

                    def recur_gather_importable(prefix: List[str], curNode: Node):
                        # precondition: curNode is in class_definiton, decorated_definition, 
                        # function_definition, expression_statement
                        assert curNode.type in [
                            PythonGrammarKeywords.CLASS_DEFINITION,
                            PythonGrammarKeywords.DECORATED_DEFINITION,
                            PythonGrammarKeywords.FUNCTION_DEFINITION,
                            PythonGrammarKeywords.EXPRESSION_STATEMENT
                        ]

                        value_to_add : python_model_cache_field

                        def create_function_value(curNode : Node, decorators : List[str]):
                            importable_name = curNode.named_children[0].text.decode(
                                "utf8"
                            )
                                
                            captures = group_by_type_capture_up_to_depth(
                                curNode,
                                "[(return_statement)@return_statement]",
                                2,
                            )
  
                            return_nodes = (
                                ( 
                                    captures["return_statement"]
                                ) if "return_statement" in captures
                                else []
                            ) 

                            resolver = PythonIdentifierResolver()
                            return_values : return_types = list(
                                map(
                                    lambda n: resolver.check_scope_up(n, (n.named_children[0],n.named_children[0].text) , None)[0].text.decode("utf8")
                                    ,
                                    return_nodes,
                                    )
                            )
                            function_value : python_function_cache_field = {
                                "return_types": return_values,
                                "decorators": decorators,
                                "type": PythonModelTypes.FUNCTION,
                                }

                            contained_by = ".".join(prefix)
                            path_to_importables[
                                (path, contained_by, importable_name)
                            ] = function_value
                                

                            logging.info("((%s, %s, %s) : [{}".format(' ,'.join(map(str, return_values))) + "] , %s, Function : Cache_Value Added\n", path, contained_by, importable_name, decorators)
                            


                        match curNode.type:
                            case PythonGrammarKeywords.CLASS_DEFINITION:
                                # class can have class, decorated_definiton, function,and variable importables
                                captures = group_by_type_capture_up_to_depth(
                                curNode,
                                "[(class_definition (identifier)@importable_name)@importable (function_definition (identifier)@importable_name)@importable (expression_statement (identifier)@importable_name)@importable (expression_statement (assignment (identifier))@importable_name)@importable]",
                                1,
                                )

                                importable_name = captures["importable_name"][0].text.decode(
                                 "utf8"
                                )

                                nested_class_definitions = get_all_children_at_level_of_type(
                                    curNode, PythonGrammarKeywords.CLASS_DEFINITION, 2
                                )

                                nested_decorated_definitions = get_all_children_at_level_of_type(
                                    curNode, PythonGrammarKeywords.DECORATED_DEFINITION, 2
                                )

                                nested_function_definitions = get_all_children_at_level_of_type(
                                    curNode, PythonGrammarKeywords.FUNCTION_DEFINITION, 2
                                )

                                nested_variable_defintions = get_all_children_at_level_of_type(
                                        curNode, PythonGrammarKeywords.EXPRESSION_STATEMENT, 2
                                )

                                # enroll curNode's children into packages_to_importables
                                for child in chain(
                                    nested_class_definitions, nested_function_definitions, nested_decorated_definitions, nested_variable_defintions
                                ):
                                    recur_gather_importable(prefix + [importable_name], child)
                                
                                class_value : python_class_cache_field = {
                                    "class_name" : importable_name,
                                    "type": PythonModelTypes.CLASS
                                } 
                                contained_by = ".".join(prefix)
                                path_to_importables[
                                    (path, contained_by, importable_name)
                                ] = class_value

                                logging.info("((%s, %s, %s) : %s, Variable) : Cache_Value Added", path, contained_by, importable_name, importable_name)

                            case PythonGrammarKeywords.DECORATED_DEFINITION:
                                captures = group_by_type_capture_up_to_depth(
                                curNode,
                                "[(decorator)@decorators]",
                                1,
                                )

                                decorator_nodes = (
                                    (
                                        captures["decorators"]
                                    )
                                    if "decorators" in captures
                                    else []
                                )
                                
                                decorators = list(
                                    map(
                                        lambda n:
                                            n.text.decode("utf8"),
                                            decorator_nodes,
                                    )
                                )

                                create_function_value(curNode.named_children[1], decorators)

                
                            case PythonGrammarKeywords.FUNCTION_DEFINITION:
                                create_function_value(curNode, [])
                                
                            case PythonGrammarKeywords.EXPRESSION_STATEMENT:
                                
                                assignment = find_first_child_of_type(curNode, "assignment", 1)
                                if(assignment is None): return

                                importable_name = assignment.named_children[0].text.decode(
                                 "utf8"
                                )

                                resolver = PythonAssignmentResolver()
                                type = resolver.resolve(assignment, (assignment.named_children[0],assignment.named_children[0].text))
                                type = type[0].text.decode("utf8") if(
                                    type[1] != "") else None
                                if(type is None): return

                                variable_value : python_variable_cache_field = {
                                    "assigned_type" : type,
                                    "type": PythonModelTypes.VARIABLE
                                } 

                                contained_by = ".".join(prefix)
                                path_to_importables[
                                    (path, contained_by, importable_name)
                                ] = variable_value

                                logging.info("((%s, %s, %s) : %s, Variable) : Cache_Value Added", path, contained_by, importable_name, type)

                       
                    recur_gather_importable([], top_level_node)
        return dict(path_to_importables)
        

    '''Create a dictionary of all uniques methods. Requires info from PythonContext.method_dict.
       keys are method names, items are PythonContext.metho_dict keys'''
    def makeUniqueMethodsDict(self):
        keys = PythonContext.method_dict.keys()
        method_entries = [m[3] for m in keys]
        method_set = {m[3]:m for m in keys if method_entries.count(m[3]) == 1}
        return method_set
    