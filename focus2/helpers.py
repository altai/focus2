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
import os.path
import traceback

import flask


def protocol(func):
    """Decorator to create protocol decorators for views from simple funcs.

    A protocol is just a dictionary existing the 'protocols' property (which is
    a dictionary by itself) of a registered view function.
    Protocols should be used to tell something meaningful about a view to some
    blueprint. For example, authentication blueprint can distinguish protected
    views from views accessible by anonymous.

    Protocol decorator has static method get() returning protocol info.
    """
    # define module/package name where protocol was called
    for filename, lineno, func_name, code in traceback.extract_stack():
        if 'traceback.extract_stack()' in code:
            # blueprint name is used as protocol name
            # all blueprints are packages
            assert 'protocol' in last_code
            dname, fname = os.path.split(last_filename)
            if fname == '__init__.py':
                dname, protocol_name = os.path.split(dname)
            else:
                protocol_name = fname.replace('.py', '')
            break
        last_filename = filename
        last_code = code
    else:
        raise RuntimeError('protocol was called in a unusual way')
    # does decorated decorator accept arguments?
    a = inspect.getargspec(func)
    if len(a.args) == 0 and a.varargs is None and a.keywords is None:
        def _decorated(view):
            if not hasattr(view, 'protocols'):
                view.protocols = {}
            if protocol_name not in view.protocols:
                view.protocols[protocol_name] = {}
            view.protocols[protocol_name][func.func_name] = func()
            return view
    else:
        def _decorated(*args, **kwargs):
            def _inner(view):
                if not hasattr(view, 'protocols'):
                    view.protocols = {}
                if protocol_name not in view.protocols:
                    view.protocols[protocol_name] = {}
                view.protocols[protocol_name][func.func_name] = func(
                    *args, **kwargs)
                return view
            return _inner

    def getter(protocol_carrier):
        """Get protocol info back.
        Returns info if present or None otherwise.
        """
        if hasattr(protocol_carrier, 'protocols'):
            protocols = getattr(protocol_carrier, 'protocols')
            if protocol_name in protocols:
                protocol = protocols[protocol_name]
                if func.func_name in protocol:
                    return protocol[func.func_name]
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
