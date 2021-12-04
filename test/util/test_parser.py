import unittest

from dagsim.utils.parser import Parser
import numpy as np


class TestStratify(unittest.TestCase):

    def test_selection(self):
        np.random.seed(0)
        parser = Parser(file_name="test_yaml.yml")
        data = parser.parse()
        self.assertEqual([5.1, 2.2], data["result"])
        np.testing.assert_almost_equal([1.764052345967664, 0.4001572083672233], data["source"])


if __name__ == '__main__':
    unittest.main()
