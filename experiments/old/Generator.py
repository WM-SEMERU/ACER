from typing import Dict, List, Tuple
from Context.pickContext import pickContext
from my_enums.shared import ProgrammingLanguage
from old.Environment import Environment

class Generator():
    '''
    A Facade who constructs sub components polymorphically with a factory
    Ultimately generates and returns `(method_dict, edge_dict)`
    '''
    
    def __init__ (self, language:ProgrammingLanguage):
        # Since Context owns a componentsFactory, Context shouldn't be created through componentsFactory
        # And so, there's a pickContext function that handles Context's polymorphism
        context = self.context = pickContext(language)
        Environment.language = context.componentsFactory.create_language()
        Environment.parser = context.componentsFactory.create_tree_sitter_parser()
        context.extension = context.componentsFactory.create_extension()
        self.preprocessor = context.componentsFactory.create_preprocessor()
        self.edgeBuilder = context.componentsFactory.create_edge_builder()
        
    def generate(self, files: List[str]) -> Tuple[Dict, Dict]:
        preprocessor, edgeBuilder, context = self.preprocessor, self.edgeBuilder, self.context
        context.files = files 
        preprocessor.preprocess() # creates method_dict and caches language-specific objects
        edge_dict = edgeBuilder.buildEdges()
        return (context.method_dict, edge_dict)
