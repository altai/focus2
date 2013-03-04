import testtools

from focus2.utils.search import transform_search_query as dsq


class TestCase(testtools.TestCase):
    def test_empty(self):
        self.assertEqual(dsq('', 'id:in'), {})

    def test_a_few(self):
        self.assertEqual(dsq('foo:eq=bar name:eq=buzz', 'id:in'),
                         {'foo:eq': 'bar', 'name:eq': 'buzz'})

    def test_with_freearg(self):
        self.assertEqual(dsq('long way to go foo:eq=bar name:in=buzz',
                             'id:in'),
                         {'id:in': 'long way to go',
                          'foo:eq': 'bar', 'name:in': 'buzz'})
