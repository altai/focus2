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


import re


class AltaiApiException(Exception):
    """Exception raised by Altai API"""

    def __init__(self, message, response):
        super(AltaiApiException, self).__init__(message)
        self.response = response


class ClientException(AltaiApiException):
    """Exception for cases in which the client seems to have erred"""

    pass


class ServerException(AltaiApiException):
    """Exception for cases in which the server is aware that it has
    erred or is incapable of performing the request"""

    pass


class BadRequest(ClientException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    reason = "Bad request"


class Unauthorized(ClientException):
    """
    HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    reason = "Unauthorized"


class Forbidden(ClientException):
    """
    HTTP 403 - Forbidden: your credentials don't give you access to this
    resource.
    """
    http_status = 403
    reason = "Forbidden"


class NotFound(ClientException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    reason = "Not found"


class OverLimit(ClientException):
    """
    HTTP 413 - Over limit: you're over the API limits for this time period.
    """
    http_status = 413
    reason = "Over limit"


class MethodNotAllowed(ClientException):
    """
    HTTP 405 - Method not allowed: the method specified in the Request-Line
    is not allowed for the resource identified by the Request-URI.
    """
    http_status = 405
    reason = "Method not allowed"


class LengthRequired(ClientException):
    """
    HTTP 411 - Length Required: the server refuses to accept the request
    without a defined Content- Length.
    """
    http_status = 411
    reason = "Length Required"


class ExpectationFailed(ClientException):
    """
    HTTP 417 - Expectation Failed: the expectation given in an Expect
    request-header field could not be met by this server.
    """
    http_status = 417
    reason = "Expectation Failed"


class InvalidRequest(BadRequest):
    """Exception raised on invalid requests"""

    match = '(.*)'


class UnknownElement(InvalidRequest):
    """Exception raised when required request elements are missing"""

    match = r'Unknown resource element: (.*)'


class MissingElement(InvalidRequest):
    """Exception raised when required request elements are missing"""

    match = r'Required element is missing: (.*)'


class IllegalValue(InvalidRequest):
    """Exception raised when resource element has illegal value"""

    match = r'Illegal value for element ([^ ]*) of type ([^:]*): (.*)'


class UnknownArgument(InvalidRequest):
    """Exception raised when required request elements are missing"""

    match = r'Unknown request argument: (.*)'


_code_map = dict((c.http_status, c)
                 for c in ClientException.__subclasses__())


def from_response(response):
    """
    Return an instance of an AltaiApiException or subclass
    based on an requests response.

    Usage::

        resp = requests.request(...)
        if not (200 <= resp.status_code < 400):
            raise exceptions.from_response(resp)
    """
    try:
        json = response.json()
        message = json["message"]
    except:
        message = response.content

    if 500 <= response.status_code < 600:
        return ServerException(message, response)
    if response.status_code == 400:
        for cls in InvalidRequest.__subclasses__():
            if re.compile(cls.match).match(message):
                return cls(message, response)
        return InvalidRequest(message, response)
    cls = _code_map.get(response.status_code, ClientException)
    return cls(message, response)
