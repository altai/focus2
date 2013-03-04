import fixtures
import testtools

import Cookie

from focus2 import application_factory
from focus2.api import client as api_client


class Debug(object):
    DEBUG = True


class Authentication(testtools.TestCase):

    def get_client(self):
        self.useFixture(fixtures.MonkeyPatch(
            "focus2.api.client.MeCollection.check_credentials",
            lambda self, auth=None: auth == ('okname', 'okpass')))
        return application_factory().test_client()

    def test_endpoints_protected(self):
        """Test non-exempted endpoints are restricted from anonynous"""
        client = self.get_client()

        rv = client.get('/authentication/login/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Login', rv.data)
        rv = client.get('/authentication/recover/password/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('Recover Password', rv.data)
        rv = client.get('/authentication/logout/')
        self.assertEqual(rv.status_code, 302)
        rv = client.get('/authentication/protection_check/')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location,
                         'http://localhost/authentication/login/')

    def test_protection_works(self):
        """Anonymous is able to login with correct credentials"""
        client = self.get_client()

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

    def test_remember_me(self):
        """Temporal cookie is set w/o checkbox and persistent with checkbox"""
        client = self.get_client()

        rv = client.post('/authentication/login/',
                         data={'name': 'okname', 'password': 'okpass'})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location,
                         'http://localhost/')
        c = Cookie.SimpleCookie(rv.headers['Set-Cookie'])
        self.assertEqual('', c['session']['expires'])

        rv = client.post('/authentication/login/',
                         data={'name': 'okname',
                               'password': 'okpass',
                               'remember_me': True})
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location,
                         'http://localhost/')
        c = Cookie.SimpleCookie(rv.headers['Set-Cookie'])
        self.assertNotEqual('', c['session']['expires'])
