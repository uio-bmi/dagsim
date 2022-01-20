import unittest

from dagsim.utils.parser import DagSimSpec
import numpy as np


class TestParser(unittest.TestCase):

    def test_working_file(self):
        np.random.seed(0)
        parser = DagSimSpec(file_name="test_yaml.yml")
        data = parser.parse(draw=False, verbose=False)
        print(data)
        self.assertEqual(['aaaaaa', ''], data["result"])
        np.testing.assert_almost_equal([1.7640, 0.4001], data["source"], decimal=4)


if __name__ == '__main__':
    unittest.main()
