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


from functools import partial

import flask

from flask import blueprints

from focus2.blueprints.dashboard import dash as basedash
from focus2.blueprints.base import breadcrumbs, breadcrumb_button

"""
================
images blueprint
================


"""

BP = blueprints.Blueprint('images', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/images')


BP = breadcrumbs('Images')(BP)


dash = partial(basedash, agt='Images', wga=1)


@breadcrumb_button('images.register', 'Register Image')
@breadcrumbs('Manage')
@dash(st='Manage',
         spu='img/small_manage.png',
         bt='Manage Images',
         bpu='img/manage.png',
         wgl=1)
@BP.route('/')
def index():
    return {}


@breadcrumbs('Register')
@dash(st='Register',
         spu='img/small_upload.png',
         bt='Register an Image',
         bpu='img/upload.png',
         wgl=0)
@BP.route('/register/')
def register():
    return {}
