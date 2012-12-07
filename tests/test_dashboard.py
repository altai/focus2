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

import unittest

import jsonschema

from focus2 import application_factory
from focus2.api import Api
from focus2.blueprints import dashboard


class Dashboard(unittest.TestCase):
    def test_pushpin(self):
        def test():
            @dashboard.pushpin(st='Short title',
                               spu='small pic',
                               bt='full title',
                               bpu=' big pic',
                               agt='group name',
                               wga='group priority',
                               wgl='position in group list (int)',
                               p='shown on dashboard by default')
            def foo():
                pass
        self.assertRaises(jsonschema.ValidationError,
                          test)

        @dashboard.pushpin(st='Short title',
                           spu='small pic',
                           bt='full title',
                           bpu=' big pic',
                           agt='group name',
                           wga=200,
                           wgl=0,
                           p=True,
                           pw=0)
        def foo():
            pass

        @dashboard.pushpin(st='Short title',
                           spu='small pic',
                           bt='full title',
                           bpu=' big pic',
                           agt='group name',
                           wga=200,
                           wgl=0,
                           p=True)
        def foo():
            pass

        @dashboard.pushpin(st='Short title',
                           spu='small pic',
                           bt='full title',
                           bpu=' big pic',
                           agt='group name',
                           wga=200,
                           wgl=0)
        def foo():
            pass

        @dashboard.pushpin(st='Short title',
                           spu='small pic',
                           bt='full title',
                           bpu=' big pic',
                           agt='group name')
        def foo():
            pass
