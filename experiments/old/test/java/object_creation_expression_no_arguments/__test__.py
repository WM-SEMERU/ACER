
import unittest

from experiments.old.driver import main


class Test(unittest.TestCase):
	def test_generated_edge(self):
		args = {"language": "java", "directory": "files"}
		main(args) # creates output
		