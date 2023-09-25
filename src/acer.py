'''
IMPORTANT: Enable strict python static type check to ensure classes are written correctly.
'''

from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import chain
import logging
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Set, Tuple, TypeVar, Generic, cast, final
from tqdm import tqdm
from tree_sitter import Node

from tree_sitter_utils import load_tree_sitter

UniqueMKey = TypeVar("UniqueMKey") # Ought to contain the complete information for how you wish to identify an unique method.
NonUniqueMKey = TypeVar("NonUniqueMKey") # Examples: For NR, this is just a str (method_name). For basic CHA, this might just be the (caller_class + method_name), without method params.
CH = TypeVar("CH")
CG = Dict[UniqueMKey, Set[UniqueMKey]]

logger = logging.getLogger('ACER Logger')

@dataclass
class MethodDictValue():
    node: Node

MDV = TypeVar("MDV", bound=MethodDictValue) 
@dataclass
class PreprocessResult(Generic[UniqueMKey, NonUniqueMKey, MDV]):
    method_dict: Dict[UniqueMKey, MDV]
    unique_dict: Dict[NonUniqueMKey, List[UniqueMKey]]

class Preprocessor(ABC, Generic[UniqueMKey, NonUniqueMKey, MDV]): 
    def __init__(self, load_path: str, language: str) -> None:
        self.language, self.parser = load_tree_sitter(load_path, language)

    @final
    def files_to_roots(self, files: List[str]): 
        '''
        Function motivation: We do not want to ever read the same file twice.
        This function yields the root_node of the files. We can achieve the 
        effect of reading once by invoking `iter_files` once, and then 
        passing the generator down to preprocessor methods that needs 
        to scan over files.
        '''
        roots: List[Node] = []
        pbar = tqdm(files, desc="Parsing files to tree-sitter roots")
        for path in pbar: 
            with open(path, "rb") as file: 
                src = file.read()
                root = self.parser.parse(src).root_node
                roots.append(root)
        return roots
    

    
    @abstractmethod
    def preprocess(self, files: List[str]) -> PreprocessResult[UniqueMKey, NonUniqueMKey, MDV]:
        pass

T = TypeVar("T")
def force_list(inp: T | List[T]) -> List[T]:
    if isinstance(inp, list): return cast(List[T], inp) 
    return [inp]
def foreach(function: Callable[[T], Any], list: List[T]):
    for element in list:
        function(element)

TraversalMethod = Literal["BFS"] | Literal["DFS"] # Uses a queue and stack, respectively.

@dataclass 
class AnalysisContext(Generic[UniqueMKey]):
    caller_key: Optional[UniqueMKey]
class AnalysisDeque(Generic[UniqueMKey]):
    def __init__(self, initial_call_sites: List[Tuple[AnalysisContext[UniqueMKey], Node]], mode: TraversalMethod = "DFS"):
        self.deque = deque(initial_call_sites)
        self.mode = mode
        self.pbar = tqdm(total=len(self.deque), desc=f"Generating.", dynamic_ncols=True, mininterval=1.0)  # Set refresh rate to 1s

    def append(self, item: Tuple[AnalysisContext[UniqueMKey], Node]):
        self.deque.append(item)
        self.pbar.total += 1

    def pop(self) -> Tuple[AnalysisContext[UniqueMKey], Node]:
        if self.deque:
            if self.mode == "DFS":
                item = self.deque.pop()
            else: 
                item = self.deque.popleft()
            self.pbar.update(1)
            # self.pbar.set_postfix_str(f"Items in deque: {len(self.deque)}") # Uncomment for high-refreshing pbar at the cost of very bad performance.
            return item
        else:
            self.pbar.close()
            raise IndexError("pop from an empty NodeAnalysisDeque")

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[AnalysisContext[UniqueMKey], Node]:
        try:
            return self.pop()
        except IndexError:
            raise StopIteration

    def __len__(self) -> int:
        return len(self.deque)

logging_levels = Literal["CRITICAL"] | Literal["ERROR"] | Literal["WARNING"] | Literal["INFO"] | Literal["DEBUG"] | Literal["NOTSET"]
class Generator(ABC, Generic[UniqueMKey, NonUniqueMKey, MDV]): 
    '''
    The base abstract Generator class. Its only public facing method is `generate`. 
    '''

    def __init__(self, preprocessor: Preprocessor[UniqueMKey, NonUniqueMKey, MDV], call_site_types: List[str] = [], caller_types: List[str] = [], logging_level: logging_levels = "INFO", traversal_method: TraversalMethod = "BFS") -> None:
        self.preprocessor = preprocessor
        self.callgraph: CG[UniqueMKey] = defaultdict(set) # graph is represented as adjacency list
        self.deque: AnalysisDeque[UniqueMKey] = AnalysisDeque([])
        self.call_site_types = call_site_types
        self.caller_types = caller_types
        logger.setLevel(logging_level)

    @final
    def call_site_check(self, call_site: Node): 
        if self.call_site_types and call_site.type not in self.call_site_types: 
            logger.error(f"A node of type {call_site.type} is to be resolved as a call site, but {call_site.type} is not in your call_site_types list")

    @final
    def caller_check(self, caller: Node): 
        if self.caller_types and caller.type not in self.caller_types: 
            logger.error(f"A node of type {caller.type} is to be resolved as a caller, but {caller.type} is not in your caller_types list")


    @abstractmethod
    def _seek_call_sites(self, caller: Node) -> Sequence[Tuple[Optional[AnalysisContext[UniqueMKey]], Node]]: 
        pass

    def _seek_caller(self, call_site: Node) -> Node: 
        '''
        Not every method needs a _seek_caller, hence, this method is not abstract.
        It must be implemented if you wish to add call_sites to the AnalysisDeque.
        '''
        raise NotImplementedError

    @final
    def _resolve_caller_wrapper(self, caller: Node) -> UniqueMKey:
        self.caller_check(caller)
        return self._resolve_caller(caller)
        
    def _resolve_caller(self, caller: Node) -> UniqueMKey: 
        '''
        Usually very simple to write. And usually, the caller Node itself is all one needs to resolve a UniqueMKey. 
        '''
        raise NotImplementedError

    @final 
    def _resolve_call_site_wrapper(self, call_site: Node, caller_key: Optional[UniqueMKey] = None) -> Tuple[List[NonUniqueMKey], List[UniqueMKey]]:
        self.call_site_check(call_site)
        return self._resolve_call_site(call_site, caller_key)
    
    @abstractmethod
    def _resolve_call_site(self, call_site: Node, caller_key: Optional[UniqueMKey] = None) -> Tuple[List[NonUniqueMKey], List[UniqueMKey]]:
        '''
        The return type is a rather complicated `Tuple[List[NonUniqueMKey], List[UniqueMKey]]`.
        
        The first tuple element, List[NonUniqueMKey], is the set of "real keys". They are real in that they exist in the `method_dict` and 
        are added to the deque for further analysis.

        The second tuple element, List[UniqueMKey], is the set of "fake keys". They are fake in that they don't exist in the `method_dict`. 
        The fake keys are thus not added for the deque. This is good when deadling with implicit methods. By the way, the fake keys are
        `UniqueMKey`s because there's no way a non-existent NonUniqueMethodKey can go to the list of UniqueMethodKeys via `self._non_unique_2_unique`.
        Thus, it is the user's responsibility to create the list of fake keys as unique.
        '''
        pass

    def _context(self, caller_key: UniqueMKey) -> AnalysisContext[UniqueMKey]:
        '''
        When implementing context-sensitive generators, this should be overriden.
        '''
        return AnalysisContext(caller_key=caller_key)

    def _generate(self, initial_keys: List[UniqueMKey]):
        for initial_caller_key in initial_keys: 
            caller_node = self.preprocessorResults.method_dict[initial_caller_key].node
            call_sites = self._seek_call_sites(caller_node)
            for (context, call_site) in call_sites: 
                # TODO: Be careful about the appending order here. Appending order should be reversed for DFS...
                self.deque.append((context or AnalysisContext(caller_key=initial_caller_key), call_site))
        logger.info(f"AnalysisDeque is initialized with {len(self.deque)} call sites.")
        # pbar = tqdm(self.deque, desc=f"Generating. Max iteration possible is {len(self.preprocessorResults.method_dict.keys())}")
        visited: Set[int] = set()
        for (analysis_context, call_site) in self.deque:
            caller_key = analysis_context.caller_key
            if call_site.id in visited: continue # Usually checked before the self.deque.append below, here is for call_site in initial queue
            visited.add(call_site.id)
            # if last_caller_key != caller_key and caller_key in self.callgraph: continue
            # last_caller_key = caller_key
            self.call_site_check(call_site)
            if not caller_key:
                caller = self._seek_caller(call_site)
                caller_key = self._resolve_caller_wrapper(caller)

            real_keys, fake_keys = self._resolve_call_site_wrapper(call_site)

            for fk in fake_keys:
                if fk not in self.callgraph: 
                    for (context, call_site) in self._seek_call_sites(self.preprocessorResults.method_dict[fk].node):
                        if call_site.id in visited: continue
                        self.deque.append((context or AnalysisContext(caller_key=fk), call_site))
                self.callgraph[caller_key].add(fk)

            for rk in chain(*[self.preprocessorResults.unique_dict.get(k, []) for k in real_keys]):
                if rk not in self.callgraph: # The method body that the call site corresponds to has not been analyzed before
                    for (context, call_site) in self._seek_call_sites(self.preprocessorResults.method_dict[rk].node):
                        if call_site.id in visited: continue
                        self.deque.append((context or AnalysisContext(caller_key=rk), call_site))
                
                self.callgraph[caller_key].add(rk)
            
        return dict(self.callgraph)

    @final
    def _get_entry_points(self, entry_points_or_calc_function: List[UniqueMKey] | Callable[[PreprocessResult[UniqueMKey, NonUniqueMKey, MDV]], List[UniqueMKey]]) -> List[UniqueMKey]: 
        if isinstance(entry_points_or_calc_function, list): 
            return []
        elif callable(entry_points_or_calc_function): 
            return entry_points_or_calc_function(self.preprocessorResults)

    def generate(self, files: List[str], entry_points_or_calc_function: List[UniqueMKey] | Callable[[PreprocessResult[UniqueMKey, NonUniqueMKey, MDV]], List[UniqueMKey]]) -> CG[UniqueMKey]:
        self.preprocessorResults = self.preprocessor.preprocess(files)
        entry_points = self._get_entry_points(entry_points_or_calc_function)
        # The basic generator enqueues all method nodes (treats all nodes as entries).
        return self._generate(entry_points)