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


import functools
import inspect
import os.path
import traceback


def protocol(func):
    """Decorator to create protocol decorators for views from simple funcs.

    A protocol is just a dictionary existing the 'protocols' property (which is
    a dictionary by itself) of a registered view function.
    Protocols should be used to tell something meaningful about a view to some
    blueprint. For example, authentication blueprint can distinguish protected
    views from views accessible by anonymous.
    """
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
    functools.update_wrapper(_decorated, func)
    return _decorated
