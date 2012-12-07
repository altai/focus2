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


import flask

from flask import blueprints

from focus2.blueprints.dashboard import pushpin
from focus2.blueprints.base import breadcrumbs, breadcrumb_button

"""
==================
projects blueprint
==================


"""

BP = blueprints.Blueprint('projects', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/projects')


@pushpin(st='Summary',
         spu='img/small_.png',
         bt='Projects Summary',
         bpu='img/manage.png',
         agt='Projects',
         wga=2,
         wgl=0)
@BP.route('/')
def summary():
    return {}


@pushpin(st='Security Groups',
         spu='img/small_.png',
         bt='Security Groups',
         bpu='img/manage.png',
         agt='Projects',
         wga=2,
         wgl=1)
@BP.route('/security-groups/')
def security_groups():
    return {}


@pushpin(st='Billing',
         spu='img/small_.png',
         bt='Billing',
         bpu='img/manage.png',
         agt='Projects',
         wga=2,
         wgl=2)
@BP.route('/billing/')
def billing():
    return {}


@pushpin(st='Members',
         spu='img/small_.png',
         bt='Security Groups',
         bpu='img/manage.png',
         agt='Members',
         wga=2,
         wgl=3)
@BP.route('/members/')
def members():
    return {}


@pushpin(st='Audit',
         spu='img/small_.png',
         bt='Audit',
         bpu='img/manage.png',
         agt='Projects',
         wga=2,
         wgl=4)
@BP.route('/audit/')
def audit():
    return {}


@pushpin(st='Invite',
         spu='img/small_.png',
         bt='invite a Member',
         bpu='img/manage.png',
         agt='Projects',
         wga=2,
         wgl=5)
@BP.route('/invite/')
def invite():
    return {}
