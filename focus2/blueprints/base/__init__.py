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


import flask
from flask import blueprints

from focus2 import _version
from focus2.helpers import protocol
from focus2.helpers import get_requested_view_and_blueprint


"""
==============
base blueprint
==============


"""

BP = blueprints.Blueprint('base', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/base')


@BP.app_context_processor
def inject_version():
    return {
        'application_version': _version.__version__,
        }


@protocol
def breadcrumbs(title):
    return title


@protocol
def breadcrumb_button(url, title):
    return url, title


@BP.app_context_processor
def inject_breadcrumbs():
    """Puts breadcrumbs info in template"""
    # if requested view is in blueprint
    # if requested view has breadcrumb title
    # if requested blueprint has breadcrumb title
    # return tuple of tuples enveloped in a dictionary
    try:
        view, bp = get_requested_view_and_blueprint()
    except TypeError:
        pass
    else:
        view_bc = breadcrumbs.get(view)
        bp_bc = breadcrumbs.get(bp)
        if view_bc is not None and bp_bc is not None:
            # second component of breadcrumb should be a link if endpoint
            # other than index is shown
            if flask.request.endpoint.endswith('.index'):
                bp_url = None
            else:
                bp_url = flask.url_for('.index')
            return {'breadcrumbs': (
                    ('Home', flask.url_for('dashboard.index')),
                    (bp_bc, bp_url),
                    (view_bc, None))}
    return {}


@BP.app_context_processor
def inject_breadcrumb_button():
    try:
        view, _ = get_requested_view_and_blueprint()
    except TypeError:
        pass
    else:
        try:
            endpoint, title = breadcrumb_button.get(view)
        except TypeError:
            pass
        else:
            return {'breadcrumb_button': (flask.url_for(endpoint), title)}
    return {}


@BP.app_errorhandler(RuntimeError)
def runtime_error(error):
    return flask.render_template('base/runtime_error.html', message=str(error))
