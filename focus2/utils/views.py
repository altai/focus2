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

import functools
import inspect

import flask


def view_metadata(func):
    """
    Return decorator creating vew decorator.

    Usage:

    >>> @view_metadata
    ... def noauth():
    ...     return True
    ...
    >>> @noauth
    ... def a_view():
    ...     pass
    ...
    >>> assert(noauth.get(a_view) == True)
    >>> @view_metadata
    ... def page_title(title_text):
    ...     return 'This is title: %s' % title_text
    ...
    >>> @page_title('foo')
    ... @noauth
    ... def a_view():
    ...     pass
    ...
    >>> assert page_title.get(a_view) ==  'This is title: %s' % 'foo'
    >>> assert noauth.get(a_view)


    It should be used to set data at view declarations and get data
    in service code like error handlers, context processors, etc.
    """
    a = inspect.getargspec(func)
    if len(a.args) == 0 and a.varargs is None and a.keywords is None:
        def _decorated(view):
            if not hasattr(view, 'view_metadata'):
                view.view_metadata = {}
            if func not in view.view_metadata:
                view.view_metadata[func] = {}
            view.view_metadata[func] = func()
            return view
    else:
        def _decorated(*args, **kwargs):
            def _inner(view):
                if not hasattr(view, 'view_metadata'):
                    view.view_metadata = {}
                if func not in view.view_metadata:
                    view.view_metadata[func] = {}
                view.view_metadata[func] = func(*args, **kwargs)
                return view
            return _inner

    def getter(carrier, default_no=None):
        """Get data back."""
        if hasattr(carrier, 'view_metadata'):
            metadata = getattr(carrier, 'view_metadata')
            return metadata.get(func, default_no)
        return default_no
    func.get = getter
    functools.update_wrapper(_decorated, func)
    return _decorated


def get_requested_view_and_blueprint():
    """Returns view function current request was dispatched to
    if the view was registered in a blueprint and the blueprint it was
    registered in. Otherwise returns None."""
    if flask.request.blueprint:
        return (flask.current_app.view_functions[flask.request.endpoint],
                flask.current_app.blueprints[flask.request.blueprint])
