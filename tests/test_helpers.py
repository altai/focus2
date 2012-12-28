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
