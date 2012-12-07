#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.


from contextlib import closing
import json

import flask
import urllib2


def get_credentials():
    return (flask.session.get('name'), flask.session.get('password'))


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

    def _get(self, path):
        username, password = self._get_credentials()
        endpoint = self._get_endpoint()
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, endpoint, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        endpoint = self._get_endpoint()
        try:
            with closing(opener.open(endpoint + path)) as rv:
                content = rv.read()
                flask.current_app.logger.debug(endpoint + path)
                flask.current_app.logger.debug(content)
                return json.loads(content)
        except urllib2.HTTPError as e:
            if e.code != 403:
                flask.current_app.logger.error(
                    'API error: "%s" was "%s" in response to "%s"/"%s"' % (
                        str(e), username, password, endpoint))
            raise LogoutException

    def are_credentials_correct(self, username=None, password=None):
        if username is None:
            username, password = self._get_credentials()
        endpoint = self._get_endpoint()
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, endpoint, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        endpoint = self._get_endpoint()
        try:
            with closing(opener.open(endpoint)) as rv:
                return True
        except urllib2.HTTPError as e:
            if e.code != 403:
                flask.current_app.logger.error(
                    'API error: "%s" was "%s" in response to "%s"/"%s"' % (
                        str(e), username, password, endpoint))
            return False

    def get_instance_types(self):
        return self._get('/v1/instance-types/')['instance-types']

client = Api(get_credentials)
