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

"""
==================
settings blueprint
==================


"""

BP = blueprints.Blueprint('settings', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/settings')


@pushpin(st='SSH Keys',
         spu='img/small_ssh_keys.png',
         bt='SSH Keys',
         bpu='img/ssh_keys.png',
         agt='Personal Settings',
         wga=3,
         wgl=0)
@BP.route('/ssh-keys/')
def ssh_keys():
    return {}


@pushpin(st='Credentials',
         spu='img/small_credentials.jpg',
         bt='Credentials',
         bpu='img/credentials.jpg',
         agt='Personal Settings',
         wga=3,
         wgl=1)
@BP.route('/credentials/')
def credentials():
    return {}


@pushpin(st='Notifications',
         spu='img/small_notifications.png',
         bt='Notifications',
         bpu='img/notifications.png',
         agt='Personal Settings',
         wga=3,
         wgl=2)
@BP.route('/notifications/')
def notifications():
    return {}


@pushpin(st='Avatar',
         spu='img/small_avatar.png',
         bt='Avatar',
         bpu='img/avatar.png',
         agt='Personal Settings',
         wga=3,
         wgl=3)
@BP.route('/avatar/')
def avatar():
    return {}


@pushpin(st='Change Password',
         spu='img/small_change_password.png',
         bt='Change Password',
         bpu='img/change_password.png',
         agt='Personal Settings',
         wga=3,
         wgl=4)
@BP.route('/change-password/')
def change_password():
    return {}
