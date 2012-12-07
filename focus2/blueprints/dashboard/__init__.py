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

import jsonschema

import flask
from flask import blueprints

from focus2 import helpers


"""
===================
dashboard blueprint
===================

On load looks up in all registered blueprints for endpoints with 'dashboard'
in their  'protocols' property. Shows this at index page.
Rest is clear from mockups.
"""


@helpers.protocol
def pushpin(**kwargs):
    """Decorator to mark view function for dashboard.

    See schema for meaning of arguments.
    See tests/test_dashboard.py for examples of pushpin() usage.
    """
    options = {
        'p': False,
        'pw': 100,
        'wga': 100,
        'wgl': 100
    }
    options.update(kwargs)
    schema = {
        'properties': {
            'agt': {'description': 'Accordion group title for the link',
                    'required': True,
                    'type': 'string'},
            'bpu': {'description': 'Big picture URL',
                    'required': True,
                    'type': 'string'},
            'bt': {'description': 'Big Title',
                   'required': True,
                   'type': 'string'},
            'p': {'description': 'Pinned on dashboard by default',
                  'required': True,
                  'type': 'boolean'},
            'pw': {'description': 'Weight of dashboard by default if pinned',
                   'required': True,
                   'type': 'integer'},
            'spu': {'description': 'Small picture URL',
                    'required': True,
                    'type': 'string'},
            'st': {'description': 'Small title',
                   'required': True,
                   'type': 'string'},
            'wga': {'description': 'Weight of the group in accordion',
                    'required': True,
                    'type': 'integer'},
            'wgl': {'description': 'Weight in group list',
                    'required': True,
                    'type': 'integer'}},
        'required': False,
        'type': 'object'}
    jsonschema.validate(options, schema)
    return options


BP = blueprints.Blueprint('dashboard', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='')


DASHBOARD_OBJECTS = []


@BP.before_app_first_request
def enumerate_dashboard_objects(*args, **kwargs):
    """Lookup for stuff after all blueprints are registered."""
    for endpoint, view in flask.current_app.view_functions.items():
        try:
            blueprint_name = endpoint.split('.')[0]
        except IndexError:
            pass
        else:
            pushpin_info = pushpin.get(view)
            if pushpin_info is not None:
                pushpin_info['spu'] = flask.url_for(
                    '%s.static' % blueprint_name,
                    filename=pushpin_info['spu'])
                pushpin_info['bpu'] = flask.url_for(
                    '%s.static' % blueprint_name,
                    filename=pushpin_info['bpu'])
                pushpin_info['url'] = flask.url_for(endpoint)
                DASHBOARD_OBJECTS.append(pushpin_info)


@BP.route('/')
def index():
    return {'dashboard_objects': DASHBOARD_OBJECTS}
