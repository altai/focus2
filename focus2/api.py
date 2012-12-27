import flask
import urllib2


def get_credentials():
    return (flask.session.get('username'), flask.session.get('password'))

def get_endpoint():
    return flask.current_app.config['API_ENDPOINT']


class Api(object):
    def __init__(self, 
                 get_credentials=get_credentials, 
                 get_endpoint=get_endpoint):
        """Accept sources of credentials and endpoints to simplify testing
        """

        self._get_credentials = get_credentials
        self._get_endpoint = get_endpoint


    def are_credentials_correct(self, username=None, password=None):
        if username is None:
            username, password = self._get_credentials()
        endpoint = self._get_endpoint()
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, endpoint, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        endpoint = self._get_endpoint()
        with opener.open(endpoint) as rv:
            import pdb; pdb.set_trace()

client = Api(get_credentials)
