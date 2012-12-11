import unittest

from focus2 import application_factory

class Debug(object):
    DEBUG = True

class Pages(unittest.TestCase):
    def setUp(self):
        self.client = application_factory(Debug()).test_client()

    def test_exist(self):
        rv = self.client.get('/authentication/login/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Login', rv.data)
        rv = self.client.get('/authentication/recover/password/')
        self.assertEqual(rv.status_code, 200)        
        self.assertIn('Recover Password', rv.data)
        rv = self.client.get('/authentication/recover/name/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Recover Name', rv.data)
        rv = self.client.get('/authentication/logout/')
        self.assertEqual(rv.status_code, 302)
