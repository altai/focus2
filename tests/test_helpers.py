import unittest


class Protocols(unittest.TestCase):
    def test_simple(self):
        from focus2.helpers import protocol

        @protocol
        def exempt():
            return True

        @exempt
        def view():
            return 'foo'
        self.assertTrue(view.protocols['test_helpers']['exempt'])

    def test_packaged(self):
        from focus2 import helpers

        @helpers.protocol
        def exempt():
            return True

        @exempt
        def view():
            return 'foo'
        self.assertTrue(view.protocols['test_helpers']['exempt'])

    def test_args(self):
        from focus2 import helpers

        @helpers.protocol
        def pushpin(*args):
            return args

        data = ('foo', 'bar', '/bazz/', 'foo.bar'), ('tequilla', 42)

        @pushpin(*data)
        def view():
            pass
        self.assertEqual(view.protocols['test_helpers']['pushpin'], data)
