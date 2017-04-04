#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test runner for data toolbox."""

import unittest
from os import path
from bptbx import b_iotools


class MainTestSuite(unittest.TestCase):
    """Test suite for data toolbox."""

    def _get_res_path(self, basename):
        if basename is None:
            self.fail('Test resource cannot be empty')
        script_path = path.dirname(path.abspath(__file__))
        res_path = path.join(script_path, 'resource', basename)
        if not b_iotools.file_exists(res_path):
            self.fail('Test resource {} not found.'.format(res_path))
        return res_path

    def test_lists(self):
        """Test the b_lists package."""
        from bdatbx import b_lists

        # ------------
        result = b_lists.split_list_to_equal_buckets(
            [1, 2, 3, 4, 5, 6, 7, 8], 3)
        self.assertEqual(
            result,
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
        """Test the b_math package."""
        from bdatbx import b_math
        # ------------
        self.assertEqual(2.8, b_math.round_ns(2.82323, 1))
        self.assertEqual(2.83, b_math.round_ns(2.82523, 2))
        self.assertEqual(2.83, b_math.round_ns(2.82523, 2))
        self.assertEqual(None, b_math.round_ns(None, 2))
        self.assertEqual('-', b_math.round_ns(None, 2, '-'))
        # ------------

    def test_parse(self):
        """Test the b_parse package."""
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
        self.assertEqual(
            -1232.23,
            b_parse.parse_basic_money_format_to_float('-1.232,23'))
        # ------------
        dat_in = '\n'.join(
            b_iotools.read_file_to_list(
                self._get_res_path('html-in.txt')))
        dat_out = '\n'.join(
            b_iotools.read_file_to_list(
                self._get_res_path('raw-text-out.txt')))
        raw_text = b_parse.extract_main_text_content(dat_in)
        self.assertEqual(dat_out, raw_text)
        # ------------
        self.assertEqual(b_parse.get_domain_from_uri(
            'https://www.google.de/asf?sfas=sfa'), 'www.google.de')
        self.assertEqual(b_parse.get_domain_from_uri(
            'http://google.de/asf?sfas=sfa'), 'google.de')
        self.assertEqual(b_parse.get_domain_from_uri(
            'http://google.de:80/asf?sfas=sfa'), 'google.de')
        self.assertEqual(b_parse.get_domain_from_uri(None), None)

    def test_stats(self):
        """Test the b_stats package."""
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

    def test_mongo(self):
        """Test the b_mongo package."""
        from bdatbx import b_mongo
        col = b_mongo.get_client_for_collection('bonnerblogs')
        self.assertTrue(col is not None)
        b_mongo.clear_collection(col)

        doc1 = {'_id': '1', 'name': 'brian', 'sur': 'may'}
        doc2 = {'_id': '2', 'name': 'freddie', 'sur': 'mercury'}
        doc3 = {'_id': '3', 'name': 'roger', 'sur': 'taylor'}
        doc4 = {'_id': '4', 'name': 'john', 'sur': 'deacon'}

        b_mongo.insert_doc(col, doc1)
        b_mongo.insert_doc(col, doc2)
        b_mongo.insert_doc(col, doc3)
        b_mongo.insert_doc(col, doc3)
        b_mongo.insert_doc(col, doc4)

        self.assertEqual(b_mongo.get_collection_size(col), 4)

        self.assertTrue(b_mongo.has_doc(col, 'name', 'freddie'))
        self.assertFalse(b_mongo.has_doc(col, 'name', 'paula'))
        self.assertFalse(b_mongo.get_doc_or_none(
            col, 'name', 'freddie') is None)
        self.assertTrue(b_mongo.get_doc_or_none(col, 'name', 'paula') is None)

        # update a document as a whole
        doc3['sur'] = 'meddows-taylor'
        b_mongo.replace_doc(col, doc3)
        new_roger = b_mongo.get_doc_or_none(col, 'name', 'roger')
        self.assertFalse(new_roger is None)
        self.assertTrue(new_roger['sur'] == 'meddows-taylor')

        # update only one value
        self.assertTrue(new_roger['sur'] == 'meddows-taylor')  # before
        b_mongo.update_value_nullsafe(col, new_roger, 'sur', 'taylor')
        self.assertTrue(new_roger['sur'] == 'taylor')  # object in memory
        updated_roger = b_mongo.get_doc_or_none(col, 'name', 'roger')
        self.assertFalse(updated_roger is None)
        self.assertTrue(updated_roger['sur'] == 'taylor')
        b_mongo.update_value_nullsafe(col, updated_roger, 'sur')
        self.assertTrue(updated_roger['sur'] is None)
        updated_roger = b_mongo.get_doc_or_none(col, 'name', 'roger')
        self.assertFalse(updated_roger is None)
        self.assertTrue(updated_roger['sur'] is None)

        i = 10
        for doc in b_mongo.get_snapshot_cursor(col):
            b_mongo.change_id(col, doc, i)
            i += 1

        self.assertEquals(b_mongo.get_collection_size(col), 4)

        for doc in b_mongo.get_snapshot_cursor(col):
            b_mongo.delete_doc(col, doc)

        self.assertEquals(b_mongo.get_collection_size(col), 0)
        col.drop()


def main():
    """Main test controller."""
    from bdatbx import b_util

    b_util.log('Invoking test suite...')
    suite = unittest.TestLoader().loadTestsFromTestCase(MainTestSuite)
    unittest.TextTestRunner(verbosity=2).run(suite)
    b_util.log('Finished test suite...')


if __name__ == '__main__':
    main()
