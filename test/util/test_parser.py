import unittest

from dagsim.utils.parser import DagSimSpec
import numpy as np


class TestParser(unittest.TestCase):

    def test_working_file(self):
        np.random.seed(1)
        parser = DagSimSpec(file_name="test_yaml.yml")
        data = parser.parse(draw=False, verbose=False)
        print(data)
        self.assertEqual(['aaa', 'aaaa'], data["result"])
        np.testing.assert_equal([3, 4], data["source"])


if __name__ == '__main__':
    unittest.main()
