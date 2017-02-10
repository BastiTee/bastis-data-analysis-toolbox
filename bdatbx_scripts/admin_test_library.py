#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tempfile import mkdtemp
from shutil import rmtree
import unittest
from os import path


class MainTestSuite(unittest.TestCase):

    def test_lists(self):
        from bdatbx import b_lists
        # ------------
        result = b_lists.split_list_to_equal_buckets(
            [1, 2, 3, 4, 5, 6, 7, 8], 3)
        self.assertEqual(result,
                         [[1.0, 2.0, 3.0], [4.0, 5.0], [6.0, 7.0, 8.0]])
        self.assertRaises(
            ValueError, b_lists.split_list_to_equal_buckets, None)
        self.assertRaises(ValueError, b_lists.split_list_to_equal_buckets, [])
        self.assertEqual([[1.0]], b_lists.split_list_to_equal_buckets([1], 4))
        # ------------
        result = b_lists.reduce_list([1, 3, 4, 3], 2)
        self.assertEqual(result, [2.0, 3.5])
        self.assertRaises(ValueError, b_lists.reduce_list, None)
        self.assertRaises(ValueError, b_lists.reduce_list, [])
        self.assertEqual([1.0], b_lists.reduce_list([1], 4))
        # ------------
        result = b_lists.intersect([1, 3, 4, 3], [1, 2, 4, 5, 6])
        self.assertEqual(result, [1, 4])
        self.assertRaises(ValueError, b_lists.intersect, None, [])
        self.assertRaises(ValueError, b_lists.intersect, [], None)
        self.assertRaises(ValueError, b_lists.intersect, None, None)
        # ------------

    def test_math(self):
        from bdatbx import b_math
        # ------------
        self.assertEqual(2.8, b_math.round_ns(2.82323, 1))
        self.assertEqual(2.83, b_math.round_ns(2.82523, 2))
        self.assertEqual(2.83, b_math.round_ns(2.82523, 2))
        self.assertEqual(None, b_math.round_ns(None, 2))
        self.assertEqual('-', b_math.round_ns(None, 2, '-'))
        # ------------

    def test_parse(self):
        from bdatbx import b_parse
        # ------------
        self.assertRaises(ValueError, b_parse.contains, None, None)
        self.assertRaises(ValueError, b_parse.contains, None, 'sd')
        self.assertEqual(False, b_parse.contains('test', None))
        self.assertEqual(True, b_parse.contains('test', 'stringtestst'))
        # ------------
        self.assertRaises(ValueError,
                          b_parse.parse_basic_money_format_to_float, None)
        self.assertRaises(ValueError,
                          b_parse.parse_basic_money_format_to_float, 'sasd')
        self.assertEqual(-1232.23,
                         b_parse.parse_basic_money_format_to_float('-1.232,23'))
        # ------------

    def test_stats(self):
        from bdatbx import b_stats
        # ------------
        empty_expected = {'sum': None, 'mean': None, 'min': None,
                          'len': 0, 'med': None, 'stdev': None, 'max': None}
        one_entry_expected = {'stdev': None, 'sum': 2, 'med': None, 'len': 1,
                              'mean': None, 'min': 2, 'max': 2}
        full_expected = {'max': 323, 'min': 1, 'stdev':
                         120.40586127166496, 'len': 7, 'med': 6, 'sum': 481,
                         'mean': 68.71428571428571}
        self.assertEqual(empty_expected,
                         b_stats.gather_basic_numerical_stats(None))
        self.assertEqual(empty_expected,
                         b_stats.gather_basic_numerical_stats([]))
        self.assertEqual(one_entry_expected,
                         b_stats.gather_basic_numerical_stats([2]))
        self.assertEqual(full_expected, b_stats.gather_basic_numerical_stats(
            [1, 2, 3, 6, 123, 323, 23]))
        # ------------


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(MainTestSuite)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
