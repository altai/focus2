# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012-2013 Grid Dynamics Consulting Services, Inc
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


import logging
import urllib
import urlparse
import sys

try:
    import simplejson as json
except ImportError:
    import json

import requests

from . import exceptions


class Collection(object):
    def __init__(self, requester, resource_name):
        self.requester = requester
        self.resource_name = resource_name

    def list(self, limit=None, offset=None, sort=None, filter=None):
        params = filter or {}
        if sort:
            params["sortby"] = sort
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self.requester.get("%s/" % self.resource_name,
                                  params=params or None)

    def get(self, id, field=None):
        if field:
            field = "/%s" % field
        else:
            field = ""
        return self.requester.get("%s/%s%s" % (self.resource_name, id, field))

    def find(self, **kwargs):
        lst = self.list(
            filter=dict((("%s:eq" % k, v)
                         for k, v in kwargs.iteritems())))
        return lst[lst["collection"]["name"]][0]

    def create(self, body=None):
        return self.requester.post("%s/" % self.resource_name, body=body)

    def update(self, id, body=None):
        return self.requester.put(
            "%s/%s" % (self.resource_name, id), body=body)

    def action(self, id, command, params=None, body=None):
        return self.requester.post(
            "%s/%s/%s" % (self.resource_name, id, command),
            params=params,
            body=body)

    def delete(self, id):
        return self.requester.delete(
            "%s/%s" % (self.resource_name, id))

    def __call__(self, **kwargs):
        return Collection(self.requester,
                          self.resource_name % kwargs)


class MeCollection(object):
    def __init__(self, requester, resource_name):
        self.requester = requester
        self.resource_name = resource_name

    def get_current_user(self):
        return self.requester.get("me")

    def check_credentials(self, auth=None):
        if auth is None:
            auth = self.requester.auth
        try:
            self.requester.get("me", auth=auth)
        except (exceptions.Unauthorized, exceptions.Forbidden):
            return False
        else:
            return True

    def reset_password(self, kind, identifier, link_template):
        return self.requester.post(
            "me/reset-password",
            body={kind: identifier, "link-template": link_template},
            auth=None)

    def apply_password_reset(self, token, password):
        return self.requester.post(
            "me/reset-password/%s" % token,
            body={"password": password},
            auth=None)


class AltaiApiClient(object):
    USER_AGENT = "altai-api-client"

    def __init__(self, endpoint, auth=None,
                 api_prefix="v1/", timeout=None,
                 http_log_debug=False):
        self.endpoint = endpoint
        self.auth = auth
        self.api_prefix = api_prefix
        self.timeout = timeout
        self.http_log_debug = http_log_debug

        self._logger = logging.getLogger(__name__)

        self._add_collections()

    def http_log_req(self, method, url, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ["curl -i"]
        try:
            string_parts.append(" -u '%s:%s'" % self.auth)
        except TypeError:
            pass
        string_parts.append(" -X %s" % method)

        params = kwargs.get("params", None)
        if params:
            url = "?".join(
                (url, urllib.urlencode(params)))
        string_parts.append(" '%s'" % url)

        for element in kwargs["headers"]:
            header = " -H '%s: %s'" % (element, kwargs["headers"][element])
            string_parts.append(header)

        if kwargs.get("data") is not None:
            string_parts.append(" -d '%s'" % (kwargs["data"]))
        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        self._logger.debug(
            "RESP: [%s] %s\nRESP BODY: %s\n",
            resp.status_code,
            resp.headers,
            resp.text)

    def request(self, method, url, **kwargs):
        kwargs.setdefault("headers", kwargs.get("headers", {}))
        kwargs["headers"]["User-Agent"] = self.USER_AGENT
        kwargs["headers"]["Accept"] = "application/json"
        if kwargs.get("body") is not None:
            kwargs["headers"]["Content-Type"] = "application/json"
            kwargs["data"] = json.dumps(kwargs["body"])
            del kwargs["body"]
        if self.timeout is not None:
            kwargs.setdefault("timeout", self.timeout)
        if self.auth is not None:
            kwargs.setdefault("auth", self.auth)

        url = urlparse.urljoin(urlparse.urljoin(
            self.endpoint, self.api_prefix), url)
        self.http_log_req(method, url, kwargs)
        resp = requests.request(
            method,
            url,
            **kwargs)
        self.http_log_resp(resp)

        if not (200 <= resp.status_code < 400):
            raise exceptions.from_response(resp)
        return resp.json()

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)

    def _add_collections(self):
        for obj in ("projects", "networks", "fw_rule_sets",
                    "users", "vms", "images",
                    "invites", "audit_log", "me",
                    "instance_types"):
            setattr(self, obj, Collection(self, obj.replace("_", "-")))
        self.fw_rules = Collection(
            self, "fw-rule-sets/%(fw_rule_set_id)s/rules")
        self.project_users = Collection(
            self, "projects/%(project_id)s/users")
        self.vm_fw_rule_sets = Collection(
            self, "vms/%(vm_id)s/fw-rule-sets"),
        self.users_ssh_keys = Collection(
            self, "/users/%(user_id)s/ssh-keys")
        self.my_ssh_keys = Collection(
            self, "me/ssh-keys")
        self.me = MeCollection(self, "me")
