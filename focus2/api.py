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
try:
    import simplejson as json
except ImportError:
    import json
import httplib2
import logging
import urllib
import urlparse
import os.path
import sys

import flask


class LoginException(Exception):
    pass


def get_credentials():
    try:
        return (flask.session['name'], flask.session['password'])
    except KeyError:
        raise LoginException


def get_endpoint():
    return flask.current_app.config['API_ENDPOINT']


class Requester(object):
    api_prefix = 'v1/'

    def __init__(self, get_endpoint, get_credentials):
        self.get_endpoint = get_endpoint
        self.get_credentials = get_credentials

    def request(self, method, path, data=None,
                is_anonymous=False, username=None, password=None):
        if is_anonymous:
            h = httplib2.Http()
        else:
            if username is None:
                username, password = self.get_credentials()
            h = httplib2.Http(os.path.join(
                flask.current_app.config['APP_TEMP_DIR'], ".cache"))
            h.add_credentials(username, password)
        url = urlparse.urljoin(urlparse.urljoin(
            self.get_endpoint(), self.api_prefix), path)
        kwargs = dict(headers={'Content-Type': 'application/json'})

        if method in ['GET', 'DELETE'] and data is not None:
            url = "%s?%s" % (url, urllib.urlencode(data))
            body = None
        else:
            body = json.dumps(data)
            kwargs['body'] = body
        resp, content = h.request(url, method, **kwargs)
        if resp.status == 403:
            raise LoginException
        elif resp.status in range(200, 300):
            if flask.current_app.debug:
                flask.current_app.logger.debug('%s \n %s', url, content)
            if resp.status == 204:
                return None
            try:
                return json.loads(content)
            except ValueError:
                flask.current_app.log_exception(sys.exc_info())
                raise RuntimeError('Invalid API response')
        else:
            logging.error('''
API Error
URL: %s
Anonymous request: %s
Credentials: %s
Method: %s
Body: %s
content: %s
Headers: %s
''', url, str(is_anonymous), (username, password), method, body, content, resp)
            raise RuntimeError('API Error')

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)


class Collection(object):
    def __init__(self, requester, resource_name):
        self.requester = requester
        self.resource_name = resource_name

    def get(self, limit=None, offset=None, sort=None, filter=None):
        query = filter or {}
        if sort:
            query["sortby"] = sort
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset
        return self.requester.get(self.resource_name, data=query or None)

    def __call__(self, **kwargs):
        return Collection(self.requester,
                          self.resource_name % kwargs)


class Api(object):
    def __init__(self,
                 get_credentials=get_credentials,
                 get_endpoint=get_endpoint):
        """Accept sources of credentials and endpoints to simplify testing
        """
        self.r = Requester(get_endpoint, get_credentials)
        for obj in ("projects", "networks", "fw_rule_sets",
                    "users", "vms", "images",
                    "invites", "audit_log", "me"):
            setattr(self, obj, Collection(self.r, obj.replace("_", "-")))
        self.fw_rules = Collection(
            self.r, "fw-rule-sets/%(fw_rule_set_id)s/rules")
        self.project_users = Collection(
            self.r, "projects/%(project_id)s/users")
        self.vm_fw_rule_sets = Collection(
            self.r, "vms/%(vm_id)s/fw-rule-sets"),
        self.users_ssh_keys = Collection(
            self.r, "/users/%(user_id)s/ssh-keys")
        self.my_ssh_keys = Collection(
            self.r, "me/ssh-keys")

    def are_credentials_correct(self, username=None, password=None):
        try:
            self.r.get('/', username=username, password=password)
        except LoginException:
            return False
        else:
            return True

    def send_password_recovery_email(self, identifier, kind, link_template):
        return self.r.post('/me/reset-password',
                           data={kind: identifier,
                           'link-template': link_template}, is_anonymous=True)

    def confirm_password_recovery(self, token, password):
        return self.r.post('/me/reset-password/{}'.format(token),
                           data={'password': password}, is_anonymous=True)


client = Api(get_credentials)
