import unittest
from unittest.mock import MagicMock
import brail.postgrator as postgrator

class TestPostgrator(unittest.TestCase):
    def test_list_records(self):
        postgrator.list_tree = MagicMock(return_value=[
            '012.do.something.sql', # Matches migration pattern
            'random_script.sql', # Does not match migration pattern
            '001.do.something.json', # Does not match migration pattern
        ])
        results = postgrator.list_postgrator_records({'postgrator_dir': 'db/pgdir'}, 'some_branch')
        self.assertEqual(results, ['pg/012.do.something.sql'])
        postgrator.list_tree.assert_called_once_with('some_branch', 'db/pgdir/')