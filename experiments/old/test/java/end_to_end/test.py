import subprocess
import unittest
import sys
from pathlib import Path
from test.utils import edge_csv_diff


class Test(unittest.TestCase):
    def test_Natty(self):
        """
        Test suite should be executed
        """
        args = "driver.py vendor/natty/src/main/java/com/joestelmach/natty/ --language=java -o output/"
        process = subprocess.run(
            [sys.executable, *args.split()], capture_output=True, text=True
        )

        if process.returncode != 0:
            assert (
                False
            ), f"Running the subprocess failed. A common failure might be not running python>3.10.8. Here's the stderr: \n\n {process.stderr}"

        current_dir = Path(__file__).parent

        generated_csv_path = current_dir / '..' / '..' / '..' / 'output' / 'edge.csv'
        ground_truth_path = current_dir / '..' / '..' / 'comparison' / 'java__joelstelmach--natty.csv'

        diff = edge_csv_diff(str(generated_csv_path.resolve()), str(ground_truth_path.resolve()))
        if diff: 
            assert False, f"There are {len(diff)} edges missing from ground truth. Here they are: \n {diff}"

    def test_KenBurnsView(self):
        """
        Test suite should be executed
        """
        args = "driver.py vendor/KenBurnsView/library/src/main/java/com/flaviofaria/kenburnsview/ --language=java -o output/"
        process = subprocess.run(
            [sys.executable, *args.split()], capture_output=True, text=True
        )

        if process.returncode != 0:
            assert (
                False
            ), f"Running the subprocess failed. A common failure might be not running python>3.10.8. Here's the stderr: \n\n {process.stderr}"

        current_dir = Path(__file__).parent

        generated_csv_path = current_dir / '..' / '..' / '..' / 'output' / 'edge.csv'
        ground_truth_path = current_dir / '..' / '..' / 'comparison' / 'java__flavioarfaria--KenBurnsView.csv'

        diff = edge_csv_diff(str(generated_csv_path.resolve()), str(ground_truth_path.resolve()))
        if diff: 
            assert False, f"There are {len(diff)} edges missing from ground truth. Here they are: \n {diff}"

    def test_GuavaRetrying(self):
        """
        Test suite should be executed
        """
        args = "driver.py vendor/guava-retrying/src/main/java/com/github/rholder/retry --language=java -o output/"
        process = subprocess.run(
            [sys.executable, *args.split()], capture_output=True, text=True
        )

        if process.returncode != 0:
            assert (
                False
            ), f"Running the subprocess failed. A common failure might be not running python>3.10.8. Here's the stderr: \n\n {process.stderr}"

        current_dir = Path(__file__).parent

        generated_csv_path = current_dir / '..' / '..' / '..' / 'output' / 'edge.csv'
        ground_truth_path = current_dir / '..' / '..' / 'comparison' / 'java__rholder--guava-retrying.csv'

        diff = edge_csv_diff(str(generated_csv_path.resolve()), str(ground_truth_path.resolve()))
        if diff: 
            assert False, f"There are {len(diff)} edges missing from ground truth. Here they are: \n {diff}"

    def test_ImageGallery(self):
        """
        Test suite should be executed
        """
        args = "driver.py vendor/ImageGallery/library/src/main/java/com/etiennelawlor/imagegallery/library --language=java -o output/"
        process = subprocess.run(
            [sys.executable, *args.split()], capture_output=True, text=True
        )

        if process.returncode != 0:
            assert (
                False
            ), f"Running the subprocess failed. A common failure might be not running python>3.10.8. Here's the stderr: \n\n {process.stderr}"

        current_dir = Path(__file__).parent

        generated_csv_path = current_dir / '..' / '..' / '..' / 'output' / 'edge.csv'
        ground_truth_path = current_dir / '..' / '..' / 'comparison' / 'java__lawloretienne--ImageGallery.csv'

        diff = edge_csv_diff(str(generated_csv_path.resolve()), str(ground_truth_path.resolve()))
        if diff: 
            assert False, f"There are {len(diff)} edges missing from ground truth. Here they are: \n {diff}"