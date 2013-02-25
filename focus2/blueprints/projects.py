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
==================
projects blueprint
==================


"""

BP = blueprints.Blueprint('projects', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/projects')


dash = partial(basedash, agt='Projects', wga=2)


@dash(st='Summary',
      spu='focus2/img/small_summary.png',
      bt='Projects Summary',
      bpu='focus2/img/summary.png',
      wgl=0)
@BP.route('/')
def summary():

    def get_total(obj_list):
        res = {}
        for obj in obj_list:
            project_id = obj["project"]["id"]
            res[project_id] = res.get(project_id, 0) + 1
        return res

    api = flask.g.api
    projects = api.projects.list()["projects"]
    total_users = {}
    for usr in api.users.list()["users"]:
        for proj in usr["projects"]:
            total_users[proj["id"]] = total_users.get(proj["id"], 0) + 1
    total = {
        "vms": get_total(api.vms.list()["vms"]),
        "images": get_total(api.images.list()["images"]),
        "users": total_users,
    }
    for p in projects:
        p["network"] = api.networks.get(p["network"]["id"])
        for key, value in total.iteritems():
            p["total_%s" % key] = value.get(p["id"], 0)
    return {
        "data": {
            "projects": projects,
        },
    }


@BP.route('/<id>')
def show(id):
    api = flask.g.api
    project = api.projects.get(id, "stats")
    network = api.networks.list(
        filter={"project:eq": id})["networks"][0]
    return {
        "data": {
            "project": project,
            "network": network,
        },
    }


@dash(st='Security Groups',
      spu='focus2/img/small_security_groups.png',
      bt='Security Groups',
      bpu='focus2/img/security_groups.png',
      wgl=1)
@BP.route('/security-groups/')
def security_groups():
    return {}


@dash(st='Billing',
      spu='focus2/img/small_billing.png',
      bt='Billing',
      bpu='focus2/img/billing.png',
      wgl=2)
@BP.route('/billing/')
def billing():
    return {}


@dash(st='Members',
      spu='focus2/img/small_members.png',
      bt='Security Groups',
      bpu='focus2/img/members.png',
      wgl=3)
@BP.route('/members/')
def members():
    return {}


@BP.route('/members/<id>')
def members_show(id):
    api = flask.g.api
    user = api.users.find(id=id)
    my_projects = set(
        (p["id"]
         for p in api.projects.list(
                filter={"my-projects": True})["projects"]))
    user["projects"] = filter(
        lambda p: p["id"] in my_projects, user["projects"])
    return {
        "data": {
            "user": user,
        },
    }


@dash(st='Audit',
      spu='focus2/img/small_audit.png',
      bt='Audit',
      bpu='focus2/img/audit.png',
      wgl=4)
@BP.route('/audit/')
def audit():
    return {}


@dash(st='Invite',
      spu='focus2/img/small_invite.png',
      bt='Invite a Member',
      bpu='focus2/img/invite.png',
      wgl=5)
@BP.route('/invite/')
def invite():
    return {}
