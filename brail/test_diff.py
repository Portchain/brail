import unittest
from unittest.mock import Mock, call
import brail.diff as diff

class TestDiff(unittest.TestCase):
    def test_get_diff(self):
        mock_conf = {'some_conf_key': 'some_conf_value'}
        diff.list_records = Mock()
        diff.list_records.side_effect = [
          ['a', 'b', 'c'], # Comparison
          ['c', 'd', 'e'], # Base
        ]
        result = diff.get_diff(mock_conf, 'some_comparison_branch', 'some_base_branch')
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result[0]), {'a', 'b'})
        self.assertEqual(set(result[1]), {'d', 'e'})
        self.assertEqual(diff.list_records.mock_calls, [
            call(mock_conf, 'some_comparison_branch'),
            call(mock_conf, 'some_base_branch'),
        ])
