import os
import shutil
import unittest
import time
from pathlib import Path

import yaml

from dagsim.utils.parser import DagSimSpec
import numpy as np


class TestParser(unittest.TestCase):

    def test_basic_parsing(self):
        np.random.seed(1)
        parser = DagSimSpec(file_name="yaml_files/basic.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual(['aaa', 'aaaa'], data["result"])
        self.assertEqual([3, 4], data["source"])

    def test_basic_parsing_num_type(self):
        np.random.seed(1)
        parser = DagSimSpec(file_name="yaml_files/basic_num_type.yml")
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual([0, 1, 0, 0, 0], data["X"][0].tolist())
        self.assertEqual([0, 0, 0, 0, 1], data["Y"][0].tolist())

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

    def test_parser_with_alt_paths(self):
        tmp_path = Path("./tmp_folder/")
        os.makedirs(str(tmp_path), exist_ok=True)

        original_path = Path("yaml_files/basic.yml")
        with original_path.open('r') as file:
            specs = yaml.safe_load(file)

        tmp_python_file = tmp_path / str(Path(specs['graph']['python_file']).name)
        shutil.copyfile(specs['graph']['python_file'], tmp_python_file)

        tmp_specs_file = tmp_path / str(Path('tmp_basic.yml'))
        specs['graph']['python_file'] = str(tmp_python_file)
        with tmp_specs_file.open('w') as file:
            yaml.dump(specs, file)

        np.random.seed(1)
        parser = DagSimSpec(file_name=str(tmp_specs_file))
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual(['aaa', 'aaaa'], data["result"])
        self.assertEqual([3, 4], data["source"])

        shutil.rmtree(tmp_path)


if __name__ == '__main__':
    unittest.main()
