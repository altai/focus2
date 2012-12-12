import flask


def get_credentials():
    if 'username' in flask.session and 'password' in flask.session:
        return {
            'username': flask.session['username'],
            'password': flask.session['password']
            }


class Api(object):
    def __init__(self, get_credentials):
        self._get_credentials = get_credentials


client = Api(get_credentials)
