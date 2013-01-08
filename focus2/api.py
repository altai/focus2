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

import flask
import urllib2


class Api(object):
    __credentials = None

    def _set_credetials(self, username, password):
        self.__credentials = (username, password)

    def _get_credentials(self):
        """ Needed to deliver credentials to the method _get_passman. Just once.
        """
        cre = self.__credentials or (flask.session.get('name'),
                flask.session.get('password'))
        self.__credentials = None
        return cre

    def _get_endpoint(self):
        return flask.current_app.config['API_ENDPOINT'] or\
                'http://example.com'

    def _get_passman(self):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        endpoint = self._get_endpoint()
        username, password = self._get_credentials()
        passman.add_password(None, endpoint, username, password)
        return passman

    def _get_authhandler(self):
        return urllib2.HTTPBasicAuthHandler(self._get_passman())

    def _get_opener(self):
        return urllib2.build_opener(self._get_authhandler())

    def are_credentials_correct(self, username=None, password=None):
        if username and password:
            self._set_credetials(username=username, password=password)

        opener = self._get_opener()
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


client = Api()
