import unittest

import werkzeug

from focus2.utils.pagination import Pagination


class TC(unittest.TestCase):
    def test_empty(self):
        p = Pagination(1, 0, 10)
        self.assertEqual(list(p.iter_pages()), [])
        self.assertEqual(p.limit, 10)
        self.assertEqual(p.offset, 0)

    def test_firstlast(self):
        data_len = 15
        p = Pagination(1, data_len, 10)
        self.assertEqual(p.limit, 10)
        self.assertEqual(p.offset, 0)
        self.assert_(p.has_next)
        self.assertFalse(p.has_prev)

    def test_last(self):
        data_len = 15
        p = Pagination(2, data_len, 10)
        self.assertEqual(p.limit, 10)
        self.assertEqual(p.offset, 10)
        self.assertFalse(p.has_next)
        self.assert_(p.has_prev)

    def test_unknown_page(self):
        data_len = 15
        self.assertRaises(werkzeug.exceptions.NotFound,
                          Pagination, 5, data_len, 10)
