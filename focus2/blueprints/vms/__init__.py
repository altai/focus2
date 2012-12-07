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

import itertools

import flask
from flask import blueprints

from focus2.blueprints.dashboard import pushpin
from focus2.blueprints.base import breadcrumbs, breadcrumb_button

"""
=============
vms blueprint
=============

Spawn
Manage
Types

"""

BP = blueprints.Blueprint('vms', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/vms')


BP = breadcrumbs('Virtual Machines')(BP)


@breadcrumbs('Manage')
@breadcrumb_button('vms.spawn', 'Spawn New VM')
@pushpin(st='Manage',
         spu='img/small_manage.png',
         bt='Manage VMs',
         bpu='img/manage.png',
         agt='Virtual Machines',
         wga=0,
         wgl=1,
         p=True,
         pw=1)
@BP.route('/')
def index():
    '''Manage'''
    return {}


@breadcrumbs('Start VM')
@pushpin(st='Spawn',
         spu='img/small_spawn_vm.png',
         bt='Spawn VM',
         bpu='img/spawn_vm.png',
         agt='Virtual Machines',
         wga=0,
         wgl=0,
         p=True,
         pw=0)
@BP.route('/spawn/', methods=['GET', 'POST'])
def spawn():
    '''Spawn'''
    return {}


@breadcrumbs('Types')
@pushpin(st='Types of',
         spu='img/small_flavors.png',
         bt='Types of VM',
         bpu='img/flavors.png',
         agt='Virtual Machines',
         wga=0,
         wgl=2,
         p=True,
         pw=2)
@BP.route('/types/')
def types():
    '''Types'''
    return flask.g.api.get_instance_types()
