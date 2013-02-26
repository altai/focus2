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

import json

import jsonschema

import flask
from flask import blueprints

from focus2.utils import views

"""
===================
dashboard blueprint
===================

Collects views with data about dashboard appearance.
"""


@views.view_metadata
def dash(**kwargs):

    """Decorator to mark view function for dashboard.

    See schema for meaning of arguments.
    See tests/test_dashboard.py for examples of dash() usage.
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
            dashboard_info = dash.get(view)
            if dashboard_info is not None:
                dashboard_info['spu'] = flask.url_for(
                    'static',
                    filename=dashboard_info['spu'])
                dashboard_info['bpu'] = flask.url_for(
                    'static',
                    filename=dashboard_info['bpu'])
                dashboard_info['url'] = flask.url_for(endpoint)
                DASHBOARD_OBJECTS.append(dashboard_info)


@BP.route('/', methods=['GET', 'POST'])
def index():
    cursor = flask.g.db.cursor()
    exist = cursor.execute('SELECT body FROM dashboard_objects WHERE id = %s',
                     (flask.session['name'],)) > 0
    if exist:
        do = json.loads(cursor.fetchone()[0])
    else:
        _groups = {}
        cells = []
        for x in DASHBOARD_OBJECTS:
            value = _groups.setdefault(x['agt'], {})
            value['key'] = x['agt']
            value['weight'] = x['wga']
            links = value.setdefault('links', [])
            links.append(dict(
                href=x['url'],
                small=x['spu'],
                title=x['st'],
                big_url=x['bpu'],
                big_title=x['bt'],
                weight=x['wgl'],
                employed=x['p']
            ))
            if x['p']:
                cells.append({
                    'href': x['url'],
                    'img': x['bpu'],
                    'full_title': x['bt']
                })
        do = {
            'groups': sorted(_groups.itervalues(), key=lambda x: x['weight']),
            'cells': cells + [None for x in xrange(15 - len(cells))]
        }
    if flask.request.method == 'POST':
        is_dirty = False
        if 'employ' in flask.request.json:
            href = flask.request.json['href']
            employ = flask.request.json['employ']
            x = None
            for g in do['groups']:
                if x is not None:
                    break
                for l in g['links']:
                    if l['href'] == href:
                        l['employed'] = employ
                        x = l
                        break
            for i, c in enumerate(do['cells']):
                if employ:
                    if c is None:
                        do['cells'][i] = {
                            'href': x['href'],
                            'img': x['big_url'],
                            'full_title': x['big_title']
                            }
                        break
                else:
                    if c is not None:
                        if c['href'] == href:
                            do['cells'][i] = None
                            break
            is_dirty = True
        elif 'changes' in flask.request.json:
            for d in flask.request.json['changes']:
                x = None
                for g in do['groups']:
                    if x is not None:
                        break
                    for l in g['links']:
                        if d['href'] == l['href']:
                            l['employed'] = bool(d['index'])
                            x = l
                            break
                # remove occurences of the item in wrong places
                for i, c in enumerate(do['cells']):
                    item_match = c is not None and c['href'] == d['href']
                    i_ok = d['index'] and i == d['index']
                    if item_match and not i_ok:
                        do['cells'][i] = None
                # ensure the item occurs in right place
                if bool(d['index']) and x is not None:
                    do['cells'][d['index']] = {
                        'href': x['href'],
                        'img': x['big_url'],
                        'full_title': x['big_title']
                        }
            is_dirty = True  # quite frequently
        if is_dirty:
            cursor.execute(
                'UPDATE dashboard_objects SET body = %(body)s '
                'WHERE id = %(id)s'
                if exist else
                'INSERT INTO dashboard_objects (body, id) '
                'VALUES (%(body)s, %(id)s)',
                {'body': json.dumps(do),
                 'id': flask.session['name']})
        return flask.jsonify({})
    else:
        return {'dashboard_objects': do}
