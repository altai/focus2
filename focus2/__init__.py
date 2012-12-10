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

__version__ = '0.0.1'

import os.path
import pkgutil

import flask
import werkzeug


DEBUG = False
CSRF_ENABLED = False


class AppTemplate(flask.Flask):
    jinja_options = werkzeug.ImmutableDict(
        extensions=['jinja2.ext.autoescape'],
        autoescape=True
    )

    def make_response(self, rv):
        if type(rv) is dict:
            template_name = os.path.join(flask.request.endpoint.split('.'))
            result = flask.render_template(
                template_name + '.html', **rv)
        elif isinstance(rv, (list, tuple)) and len(rv) == 2:
            result = flask.render_template(rv[0], **rv[1])
        else:
            result = rv
        return super(FatFlask, self).make_response(result)
    
    

def application_factory(*args):
    app = AppTemplate(__name__)

    # configure
    app.config.from_object(__name__)
    for x in args:
        if isinstance(x, basestring):
            app.config.from_pyfile(x)
        else:
            app.config.from_object(x)
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'blueprints')
    for importer, name, _ in pkgutil.iter_modules([path]):
        full_name = 'focus2.blueprints.%s' % name
        module = importer.find_module(full_name).load_module(full_name)
        if 'BP' in dir(module):
            app.register_blueprint(module.BP)
    return app
