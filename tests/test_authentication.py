import unittest

import mox

from focus2 import application_factory
from focus2.api import Api


class Debug(object):
    DEBUG = True

class Pages(unittest.TestCase):

    def get_client(self, api):
        return application_factory([Debug()], api).test_client()

    def test_endpoints_protected(self):
        mocker = mox.Mox()
        api = mocker.CreateMock(Api())
        api.are_credentials_correct().AndReturn(False)
        mocker.ReplayAll()

        client = self.get_client(api)

        rv = client.get('/authentication/login/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Login', rv.data)
        rv = client.get('/authentication/recover/password/')
        self.assertEqual(rv.status_code, 200)        
        self.assertIn('Recover Password', rv.data)
        rv = client.get('/authentication/recover/name/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Recover Name', rv.data)
        rv = client.get('/authentication/logout/')
        self.assertEqual(rv.status_code, 302)
        rv = client.get('/authentication/protection_check/')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 
                         'http://localhost/authentication/login/')
    
    def test_protection_works(self):
        mocker = mox.Mox()
        api = mocker.CreateMock(Api())
        api.are_credentials_correct('noname', 'nopass').AndReturn(False)
        api.are_credentials_correct('okname', 'okpass').AndReturn(True)
        api.are_credentials_correct().AndReturn(False)
        mocker.ReplayAll()

        client = self.get_client(api)

        rv = client.post('/authentication/login/', 
                         data={'name': 'noname', 'password': 'nopass'})
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Invalid credentials', rv.data)

        rv = client.post('/authentication/login/', 
                         data={'name': 'okname', 'password': 'okpass'})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 
                         'http://localhost/')  
            
        rv = client.get('/authentication/logout/')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 
                         'http://localhost/authentication/login/')
        rv = client.get('/authentication/login/')
        self.assertIn('You were logged out', rv.data)

        rv = client.get('/authentication/protection_check/')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 
                         'http://localhost/authentication/login/')
        
