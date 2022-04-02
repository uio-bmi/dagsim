import unittest
import time
from dagsim.utils.parser import DagSimSpec
import numpy as np


class TestParser(unittest.TestCase):

    def test_basic_parsing(self):
        np.random.seed(1)
        parser = DagSimSpec(file_name="yaml_files/basic.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual(['aaa', 'aaaa'], data["result"])
        self.assertEqual([3, 4], data["source"])

    def test_basic_one_liner_parsing(self):
        np.random.seed(1)
        parser = DagSimSpec(file_name="yaml_files/basic_one_line.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual(['aaa', 'aaaa'], data["result"])
        self.assertEqual([3, 4], data["source"])

    def test_selection_parsing(self):
        parser = DagSimSpec(file_name="yaml_files/selection.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual([0, 2, 4], data["source"])

    def test_stratify_parsing(self):
        parser = DagSimSpec(file_name="yaml_files/stratify.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertIn("Odd", data)
        self.assertIn("Even", data)
        self.assertEqual(data["Odd"], {'source': [1]})
        self.assertEqual(data["Even"], {'source': [0, 2]})

    def test_missing_parsing(self):
        parser = DagSimSpec(file_name="yaml_files/missing.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertIn("source", data)
        self.assertIn("index", data)
        self.assertIn("missing_source", data)
        self.assertEqual(data["index"], [True, False, True])
        self.assertEqual(data["missing_source"], ['NaN', 1, 'NaN'])


if __name__ == '__main__':
    unittest.main()
