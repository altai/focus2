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
from flask.ext import wtf
import werkzeug

from focus2.blueprints.base import breadcrumbs, breadcrumb_button
from focus2.blueprints.dashboard import dash
from focus2.utils import search, pagination, forms

"""
=============
vms blueprint
=============

Spawn
Manage

"""

BP = blueprints.Blueprint('vms', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/vms')


BP = breadcrumbs('Virtual Machines')(BP)


@breadcrumbs('Manage')
@breadcrumb_button('vms.spawn', 'Spawn New VM')
@dash(st='Manage',
         spu='focus2/img/small_manage.png',
         bt='Manage VMs',
         bpu='focus2/img/manage.png',
         agt='Virtual Machines',
         wga=0,
         wgl=1,
         p=True,
         pw=1)
@BP.route('/')
def index():
    '''Manage'''
    query = flask.request.args.get('q', '')
    deconstruct = search.transform_search_query(query, 'name:eq')
    r = flask.g.api.vms.list(filter=deconstruct, limit=0)
    try:
        p = pagination.Pagination(1, r['collection']['size'])
    except werkzeug.exceptions.NotFound:
        paginator = None
        data = []
    else:
        r = flask.g.api.vms.list(
            filter=deconstruct, limit=p.limit, offset=p.offset)
        paginator = pagination.Pagination(1, r['collection']['size'])
        data = r['vms']

    return {
        'query': query,
        'deconstruct': deconstruct,
        'data': data,
        'paginator': paginator,
        'predefined_searches': [
            {'title': 'My VMs', 'url': flask.request.path + '?my'},
        ] + [
            {'title': x['name'],
             'url': flask.request.path + '?project_id=' + x['id']} for x
            in flask.g.api.projects.list()['projects']
        ],
        'user_searches': flask.session.get('user_searches', []),
    }


class CreateForm(wtf.Form):
    project = wtf.SelectField('Project', validators=[wtf.Required()])
    image = wtf.SelectField('Image', validators=[wtf.Required()])
    instance_type = wtf.SelectField('Type', validators=[wtf.Required()])
    name = wtf.TextField('Name', validators=[wtf.Required()])
    ssh_key = forms.SelectOptionalField('Key Pair')
    fw_rule_set = wtf.SelectMultipleField(
        'Security Groups')


@breadcrumbs('Start VM')
@dash(st='Spawn',
         spu='focus2/img/small_spawn_vm.png',
         bt='Spawn VM',
         bpu='focus2/img/spawn_vm.png',
         agt='Virtual Machines',
         wga=0,
         wgl=0,
         p=True,
         pw=0)
@BP.route('/spawn/', methods=['GET', 'POST'])
def spawn():
    '''Spawn'''
    form = CreateForm()
    api = flask.g.api
    data = {
        "project": api.projects.list()["projects"],
        "image": api.images.list()["images"],
        "instance_type": api.instance_types.list()["instance-types"],
        "ssh_key": api.my_ssh_keys.list()["ssh-keys"],
        "fw_rule_set": api.fw_rule_sets.list()["fw-rule-sets"],
    }
    if form.is_submitted():
#        import pdb; pdb.set_trace()
        for key in ("project", "image", "instance_type",
                    "fw_rule_set"):
            getattr(form, key).choices = [
                (i["id"], None) for i in data[key]
            ]
        for key in ("ssh_key", ):
            getattr(form, key).choices = [
                (i["name"], None) for i in data[key]
            ]
        if not form.validate():
            return {
                "form": form,
                "data": data,
            }
        vm_data = dict(
            ((k, getattr(form, k.replace("-", "_")).data)
             for k in ("name", "project",
                       "image", "instance-type"))
        )
        vm = api.vms.create(vm_data)
        return flask.redirect(url_for("vms.show", id=vm["id"]))
    return {
        "form": form,
        "data": data,
    }


@BP.route('/<id>')
def show(id):
    api = flask.g.api
    vm = api.vms.get(id)
    image = api.images.get(vm["image"]["id"])
    instance_type = api.instance_types.get(vm["instance-type"]["id"])
    return {
        "data": {
            "vm": vm,
            "image": image,
            "instance_type": instance_type,
        },
    }


@breadcrumbs('Types')
@dash(st='Types of',
         spu='focus2/img/small_flavors.png',
         bt='Types of VM',
         bpu='focus2/img/flavors.png',
         agt='Virtual Machines',
         wga=0,
         wgl=2,
         p=True,
         pw=2)
@BP.route('/types/')
def types():
    '''Types'''
    return {
        "data": {
            "types": flask.g.api.instance_types.list()["instance-types"],
        }
    }


@BP.route('/types/<id>')
def types_show(id):
    '''Show type'''
    return {
        "data": {
            "instance_type": flask.g.api.instance_types.get(id),
        }
    }
