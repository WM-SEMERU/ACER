
import unittest
import pandas as pd

from experiments.old.driver import main

class Test(unittest.TestCase):
	edge_df = pd.read_csv("expected_edge_dict.csv")
	method_df = pd.read_csv("expected_method_dict.csv")

	
	def setUp(self):
		#name = virtual
		args = {"language": "python", "directory": "files"}
		main(args) # creates output

		#Read CSVs in Output 
		self.compare_edge_df = pd.read_csv("output\\fileA_edge.csv")
		self.compare_method_df = pd.read_csv("output\\fileA_method.csv")
	
	def test_compare_edge_callee(self):
		if(self.compare_edge_df['callee_index'].equals(self.edge_df['callee_index'])):
			assert True
		else:
			assert False

	def test_compare_edge_called(self):
		if(self.compare_edge_df['called_index'].equals(self.edge_df['called_index'])):
			assert True
		else:
			assert False
	
	def test_compare_edge_call_type(self):
		if(self.compare_edge_df['call_type'].equals(self.edge_df['call_type'])):
			assert True
		else:
			assert False
	
	def test_compare_method_class_name(self):
		if(self.compare_method_df['class_name'].equals(self.method_df['class_name'])):
			assert True
		else:
			assert False

	def test_compare_method_method_name(self):
		if(self.compare_method_df['method_name'].equals(self.method_df['method_name'])):
			assert True
		else:
			assert False
	
	def test_compare_method_descriptor_name(self):
		if(self.compare_method_df['descriptor_name'].equals(self.method_df['descriptor_name'])):
			assert True
		else:
			assert False

	def test_compare_method_file_name(self):
		if(self.compare_method_df['file_name'].equals(self.method_df['file_name'])):
			assert True
		else:
			assert False
	
	def test_compare_method_line_number(self):
		if(self.compare_method_df['line_number'].equals(self.method_df['line_number'])):
			assert True
		else:
			assert False