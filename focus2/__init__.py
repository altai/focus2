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


import os.path
import pkgutil

import flask
import werkzeug
import werkzeug.utils

from _version import __version__

DEBUG = False
CSRF_ENABLED = False
API_ENDPOINT = ''
SECRET_KEY = '1ecdf1e7-306f-4b82-8d2e-bee89bffd6c9'

def application_factory(config=[], api_object=None, 
                        api_object_path='focus2.api:client'):
    """Application factory.
    Accepts list of objects or string file paths to python modules to configure from,
    optional custom Altai API object and path to Altai API client instance to import.
    Has meaningful defaults.
    """

    # load api client object
    if api_object is None:
        api_object = werkzeug.utils.import_string(api_object_path)

    # define custom applciaiton class
    class AppTemplate(flask.Flask):
        class request_globals_class(object):
            api = api_object

        jinja_options = werkzeug.ImmutableDict(
            extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_'],
            autoescape=True
            )

        def make_response(self, rv):
            """Extend Flask behavior. We can return a dict from blueprint 
            endpoint and will have corresponding template rendered with the dict
            as context.
            """
            if type(rv) is dict:
                template_name = os.path.join(
                    *flask.request.endpoint.split('.')) + '.html'
                result = flask.render_template(template_name , **rv)
            elif isinstance(rv, (list, tuple)) and len(rv) == 2:
                result = flask.render_template(rv[0], **rv[1])
            else:
                result = rv
            response = super(AppTemplate, self).make_response(result)
            return response


    app = AppTemplate(__name__)
    # configure
    app.config.from_object(__name__)
    for x in config:
        if isinstance(x, basestring):
            app.config.from_pyfile(x)
        else:
            app.config.from_object(x)
    app.session_interface = flask.sessions.SecureCookieSessionInterface()
    # register blueprints
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'blueprints')
    for importer, name, _ in pkgutil.iter_modules([path]):
        full_name = 'focus2.blueprints.%s' % name
        module = importer.find_module(full_name).load_module(full_name)
        if 'BP' in dir(module):
            app.register_blueprint(module.BP)

    return app
