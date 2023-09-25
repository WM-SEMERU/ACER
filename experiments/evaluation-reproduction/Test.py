from abc import abstractmethod
from dataclasses import dataclass
import os
import pprint
import re
import subprocess
import sys
from typing import Callable, Dict, Generic, List

from tqdm import tqdm
from src.acer import CG, UniqueMKey
from examples.Java.JavaNR.NR import NRGenerator, NRPreprocessor
from examples.Java.shared import get_files
from timeit import default_timer as timer
from typing import Dict, Callable
from collections import defaultdict

name = str

class ExternalGenerator(Generic[UniqueMKey]):
	'''
	A good class to organize generators invoked by outside commands.
	'''
	@abstractmethod
	def generate(self):
		'''
		Your logic probably wants to run some bash command from python.
		'''
		pass 

	@abstractmethod
	def standardize_callgraph(self) -> CG[UniqueMKey]: 
		'''
		Your logic probably wants to read the callgraph created (via .generate) 
		and manipulate it to some form that's in parallel to Generator methods.
		'''

def cg_difference(cg_1: CG[UniqueMKey], cg_2: CG[UniqueMKey]): 
	diff_edges: CG[UniqueMKey] = defaultdict(set)
	for k, v in cg_2.items():
		if k in cg_1:
			diff_edges[k] = v - cg_1[k]
		else:
			diff_edges[k] = v
	return diff_edges

def cg_format(cg: CG[UniqueMKey]) -> str:
    output_str = ""
    for node, neighbors in cg.items():
        for neighbor in neighbors:
            output_str += f"{node} -> {neighbor}\n"
    return output_str

@dataclass
class TestResult(Generic[UniqueMKey]):
	time_map: Dict[str, float]
	cg_map: Dict[str, CG[UniqueMKey]]
	edge_diff_cnt_tab: Dict[str, Dict[str, int]]
	edge_diff_tab: Dict[str, Dict[str, CG[UniqueMKey]]]

class Tester():
	def test(self, generators_run_cmds: Dict[str, Callable[..., CG[UniqueMKey]]], times:int=1) -> TestResult[UniqueMKey]:
		'''
		`times`: Run each generation cmd `times` times and average them in calculating the time_map
		
		Prints (potentially 3 dicts):
		1) Time map: How long it took for each generator to run
		2) Edge count diff edge_cnt_diff: # of different edges  between generators. 
		   cell = len(col_CG - row_CG) (set subtraction, as in, all elements that belong in col_CG but not row_CG)
		3) Edge diff edge_cnt_diff: Difference in callgraphs between different generators. 
		   cell = col_CG - row_CG (set subtraction, as in, all elements that belong in col_CG but not row_CG)
		'''
		time_map: Dict[str, float] = {}
		res_map: Dict[str, CG[UniqueMKey]] = {}

		# Running the functions and timing them
		for name, func in tqdm(generators_run_cmds.items(), desc="Running Generate Commands"):
			timings: List[float] = []
			for _ in range(times):
				start_time = timer()
				res_map[name] = func()
				end_time = timer()
				timings.append(end_time - start_time)
			time_map[name] = sum(timings) / len(timings)

		edge_cnt_diff: Dict[str, Dict[str, int]] = defaultdict(dict)
		edge_diff: Dict[str, Dict[str, CG[UniqueMKey]]] = defaultdict(dict)

		for name_A, cg_A in tqdm(res_map.items(), desc="Generating diff tables"):
			for name_B, cg_B in res_map.items():
				if name_A == name_B: 
					edge_cnt_diff[name_A][name_B] = 0
					continue
				edges_diff = cg_difference(cg_A, cg_B)
				edge_diff[name_A][name_B] = edges_diff
				edges_cnt_diff = len(cg_difference(cg_A, cg_B))
				edge_cnt_diff[name_A][name_B] = edges_cnt_diff

		return TestResult(time_map, res_map, edge_cnt_diff, edge_diff)


if __name__ == "__main__":
	class WALA(ExternalGenerator[UniqueMKey]):
		def __init__(self, jar_path: str) -> None:
			self.jar_path = jar_path
		def generate(self):
			subprocess.run(["~/repo-research/WALA-start/gradlew", "run", "--args=\"/home/andrew/java/jdk7-rt.jar\"", "> cha-results"])

		def standardize_callgraph(self) -> CG[UniqueMKey]:
			results_path =  os.path.join(os.path.expanduser("~"), "repo-research", "WALA-start", "cha-results")
			cg: CG[UniqueMKey] = defaultdict(set)
			with open(results_path, "r") as file: 
				for line in file: 
					line = line.strip()
					if "->" not in line: continue
					caller_text, callee_text = line.split("->")
					
			pass

	class Soot(ExternalGenerator[UniqueMKey]): 
		def generate(self): 
			pass 
		def standardize_callgraph(self) -> CG[UniqueMKey]:
			pass

	output_dir = sys.argv[1]
	os.makedirs(output_dir, exist_ok=True)
	t = Tester()
	
	files = get_files(str(os.path.join("evaluations", "jdk7", "src")), re.compile(r'\.java$'))
	NRGen = NRGenerator(NRPreprocessor("build/my-languages.so", 'java'))
	f1 = lambda: NRGen.generate(files, lambda p: list(p.method_dict.keys()))
	f2 = lambda: 
	
	# f3 = lambda: generator2.generate(files2, lambda p: list(p.method_dict.keys()))
	res = t.test({"NRGenerator": f1})
	time_map, callgraph_map, edge_diff_cnt_tab, edge_diff_tab = res.time_map, res.cg_map, res.edge_diff_cnt_tab, res.edge_diff_tab
	
	print("time map:")
	pprint.pprint(time_map)

	print("edge_diff_cnt_table")
	pprint.pprint(edge_diff_cnt_tab)	
	
	# print("edge diff")
	# print(edge_diff_tab)

	f = open(os.path.join(output_dir, "time_map"), "w")
	f.write(pprint.pformat(time_map))
	f.close()

	os.makedirs(os.path.join(output_dir, "callgraph_results"), exist_ok=True)
	for name, callgraph in callgraph_map.items():
		with open(os.path.join(output_dir, "callgraph_results", name), "w") as f:
			f.write(cg_format(callgraph))


	# os.makedirs(os.path.join(output_dir, "edge_diff_cnt_table"), exist_ok=True)
	with open(os.path.join(output_dir, "edge_diff_cnt_tab"), "w") as f:
			f.write(pprint.pformat(edge_diff_cnt_tab))


	# os.makedirs(os.path.join(output_dir, "edge_diff_tab"), exist_ok=True)
	with open(os.path.join(output_dir, "edge_diff_tab"), "w") as f:
			f.write(str(edge_diff_tab))