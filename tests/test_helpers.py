import unittest
from focus2.utils import views


class Protocols(unittest.TestCase):
    def test_simple(self):

        @views.view_metadata
        def exempt():
            return True

        @exempt
        def view():
            return 'foo'
        self.assertTrue(exempt.get(view))

    def test_packaged(self):
        @views.view_metadata
        def exempt():
            return True

        @exempt
        def view():
            return 'foo'
        self.assertTrue(exempt.get(view))

    def test_args(self):
        @views.view_metadata
        def pushpin(*args):
            return args

        data = ('foo', 'bar', '/bazz/', 'foo.bar'), ('tequilla', 42)

        @pushpin(*data)
        def view():
            pass
        self.assertEqual(pushpin.get(view), data)
