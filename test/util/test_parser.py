import unittest

from dagsim.utils.parser import Parser
import numpy as np

not_working = {'graph':
                   {'python_file': 'functions_for_parser_test',
                    'name': 'my_graph',
                    'nodes':
                        {'result':
                             {'function': 'square(param=source, add_param=2)',
                              'kwargs':
                                  {'scale': 1}},
                         'source':
                             {'function': 'numpy.random.normal',
                              'kwargs':
                                  {'scale': 1,
                                   'loc': 0}}}},
               'instructions':
                   {'simulation':
                        {'num_samples': 2,
                         'csv_name': 'parser'}}}

working_1 = {'graph':
                 {'python_file': 'functions_for_parser_test',
                  'name': 'my_graph',
                  'nodes':
                      {'result':
                           {'function': 'square(param=source, add_param=2)'},
                       'source':
                           {'function': 'numpy.random.normal',
                            'kwargs':
                                {'scale': 1,
                                 'loc': 0}}}},
             'instructions':
                 {'simulation':
                      {'num_samples': 2,
                       'csv_name': 'parser'}}}

working_2 = {'graph':
                 {'python_file': 'functions_for_parser_test',
                  'name': 'my_graph',
                  'nodes':
                      {'result':
                           {'function': 'square(param=source, add_param=2)'},
                       'source':
                           {'function': 'numpy.random.normal(0, scale=1.0)',
}}},
             'instructions':
                 {'simulation':
                      {'num_samples': 2,
                       'csv_name': 'parser'}}}


class TestParser(unittest.TestCase):

    def test_working_1(self):
        np.random.seed(0)
        parser = Parser(file_name=working_1)
        data = parser.parse(draw=False, verbose=False)
        self.assertEqual([5.1, 2.2], data["result"])
        np.testing.assert_almost_equal([1.7640, 0.4001], data["source"], decimal=4)

    def test_working_2(self):
        np.random.seed(0)
        parser = Parser(file_name=working_2)
        data = parser.parse(draw=False)
        self.assertEqual([5.1, 2.2], data["result"])
        np.testing.assert_almost_equal([1.7640, 0.4001], data["source"], decimal=4)

    def test_not_working(self):
        parser = Parser(file_name=not_working)
        with self.assertRaises(SyntaxError):
            parser.parse(draw=False, verbose=False)


if __name__ == '__main__':
    unittest.main()
