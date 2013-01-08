import unittest
import mox
from urllib2 import HTTPError

from focus2 import application_factory
from focus2.api import Api


class Debug(object):
    DEBUG = True

class ApiCredentials(unittest.TestCase):
    def setUp(self):
        self.app = application_factory([type('Debug', (), {'DEBUG': True})])
        self.api_plug = mox.Mox()

        empty = lambda self: self

        self.ScabbardPlug = type('ScabbardPlug', (), {'get_opener': empty})
        self.OpenerPlug = type('OpenerPlug', (),
                {'open': lambda self, handler: self})
        self.ResponsePlug = type('ResponsePlug', (), {'__enter__': empty,
                '__exit__': lambda type, value, traceback: self,
                'code': empty, 'read': empty, 'close': empty})

    def tearDown(self):
        self.api_plug.VerifyAll()

# ===========================================================================
# Correct credentials scenario and test
# ===========================================================================
    def correct_credentials_scenario(self):
        mock_opener = self.api_plug.CreateMock(self.OpenerPlug)
        scabbard = self.api_plug.CreateMock(self.ScabbardPlug)
        mock_success = self.api_plug.CreateMock(self.ResponsePlug)

        mock_opener.open('http://example.com').AndReturn(mock_success)
        scabbard.get_opener().AndReturn(mock_opener)
        mock_success.close().AndReturn(None)

        self.api_plug.ReplayAll()
        return type('ApiTest', (Api,),
                {'_get_opener': scabbard.get_opener})

    def test_correct_credentials(self):
        with self.app.test_request_context():
            api = self.correct_credentials_scenario()
            return self.assertTrue(api().are_credentials_correct(
                    username='good guy', password='password'))

# ===========================================================================
# Incorrect credentials scenario and test
# ===========================================================================
    def incorrect_credentials_scenario(self):
        scabbard = self.api_plug.CreateMock(self.ScabbardPlug)
        mock_opener_403 = self.api_plug.CreateMock(self.OpenerPlug)
        HTTPError403 = HTTPError(url='http://wrong.com', code=403,
                msg='Unauthorized', hdrs=None, fp=None)

        scabbard.get_opener().AndReturn(mock_opener_403)
        mock_opener_403.open('http://example.com').AndRaise(HTTPError403)

        self.api_plug.ReplayAll()
        return type('ApiTest', (Api,),
                {'_get_opener': scabbard.get_opener})

    def test_incorrect_credentials(self):
        with self.app.test_request_context():
            api = self.incorrect_credentials_scenario()
            return self.assertFalse(api().are_credentials_correct(
                    username='bad guy', password='password'))
