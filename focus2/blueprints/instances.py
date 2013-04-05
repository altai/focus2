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

from focus2.api import exceptions as api_exceptions

from focus2.blueprints.base import breadcrumbs, breadcrumb_button
from focus2.blueprints.dashboard import dash
from focus2.utils import billing as utils_billing
from focus2.utils import search, pagination, forms
from focus2.utils import jinja as utils_jinja

"""
=============
instances blueprint
=============

Spawn
Manage

"""

BP = blueprints.Blueprint('instances', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/instances')


BP = breadcrumbs('Instances')(BP)


@breadcrumbs('Manage')
@breadcrumb_button('instances.spawn', 'Spawn New Instance')
@dash(st='Manage',
         spu='focus2/img/small_manage.png',
         bt='Manage instances',
         bpu='focus2/img/manage.png',
         agt='Instances',
         wga=0,
         wgl=1,
         p=True,
         pw=1)
@BP.route('/')
def index():
    '''Manage'''

    if 'api_marker' in flask.request.args:
        query = flask.request.args.get('query')
        deconstruct = search.transform_search_query(query, 'name:eq')
        r = flask.g.api.instances.list(filter=deconstruct, limit=0)
        perPage = int(flask.request.args['perPage'])
        page = int(flask.request.args['page'])
        try:
            p = pagination.Pagination(page, r['collection']['size'], perPage)
        except werkzeug.exceptions.NotFound:
            data = []
            pages = []
            current = 1
        else:
            r = flask.g.api.instances.list(
                filter=deconstruct, limit=p.limit, offset=p.offset)
            paginator = pagination.Pagination(
                page, r['collection']['size'], perPage)
            data = r['instances']
            pages = list(paginator.iter_pages())
            current = paginator.page
        return flask.jsonify({
                'data': data,
                'pagination': {
                    'pages': pages,
                    'current': current
                    }
                })

    return {
        'predefined_searches': [
            {'title': 'My instances', 'url': flask.request.path + '?my'},
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
        'Firewall Rule Sets')
    expiration_never = wtf.BooleanField('Never')
    expiration_date = wtf.TextField('Expiration')


@breadcrumbs('Start instance')
@dash(st='Spawn',
         spu='focus2/img/small_spawn_instance.png',
         bt='Spawn instance',
         bpu='focus2/img/spawn_instance.png',
         agt='Instances',
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
        "project": api.projects.list(filter={"my-projects": True})["projects"],
        "image": filter(utils_jinja.image_spawnable,
                        api.images.list()["images"]),
        "instance_type": api.instance_types.list()["instance-types"],
        "ssh_key": api.my_ssh_keys.list()["ssh-keys"],
        "fw_rule_set": api.fw_rule_sets.list()["fw-rule-sets"],
    }
    if form.is_submitted():
        for key in ("project", "image", "instance_type",
                    "fw_rule_set"):
            getattr(form, key).choices = [
                (i["id"], None) for i in data[key]
            ]
        for key in ("ssh_key", ):
            getattr(form, key).choices = [
                (i["name"], None) for i in data[key]
            ]
    if form.validate_on_submit():
        instance_data = dict(
            ((k, getattr(form, k.replace("-", "_")).data)
             for k in ("name", "project",
                       "image", "instance-type"))
        )
        if form.fw_rule_set.data:
            instance_data["fw-rule-sets"] = form.fw_rule_set.data
        if form.ssh_key.data:
            instance_data["ssh-key-pair"] = form.ssh_key.data
        if not form.expiration_never.data:
            instance_data["expires-at"] = form.expiration_date.data
        try:
            instance = api.instances.create(instance_data)
        except api_exceptions.ClientException as ex:
            flask.flash("Cannot create instance: %s" % ex, "error")
        else:
            flask.flash(
                "Successfully created instance %s" % instance["name"],
                "success")
            return flask.redirect(
                flask.url_for("instances.show", id=instance["id"]))
    for fw_rule_set in data["fw_rule_set"]:
        fw_rule_set["rules"] = api.fw_rules(
            fw_rule_set_id=fw_rule_set["id"]).list()["rules"]
    bh = utils_billing.BillingHelper(flask.g.api)
    data["instance_type"] = bh.calculate_cost(
        data["instance_type"], bh.tariff_list())
    return {
        "form": form,
        "data": data,
    }


@BP.route('/<id>')
def show(id):
    api = flask.g.api
    instance = api.instances.get(id)
    image = api.images.get(instance["image"]["id"])
    instance_type = api.instance_types.get(instance["instance-type"]["id"])
    network = api.networks.find(project=instance["project"]["id"])
    fw_rule_sets = api.instance_fw_rule_sets(
        instance_id=id).list()["fw-rule-sets"]
    return {
        "data": {
            "instance": instance,
            "image": image,
            "instance_type": instance_type,
            "network": network,
            "fw_rule_sets": fw_rule_sets,
        },
    }


@BP.route('/<id>/<command>', methods=["GET", "POST"])
def action(id, command):
    if command not in ("console-output",
                       "reboot",
                       "remove",
                       "reset",
                       "vnc"):
        flask.abort(404)

    if (command not in ("console-output", "vnc") and
            flask.request.method == "GET"):
        flask.abort(405)

    resp = flask.g.api.instances.action(id, command)
    if command == "vnc":
        return flask.redirect(resp["url"])
    if command == "console-output":
        resp = flask.make_response(resp["console-output"])
        resp.headers["Content-type"] = "text/plain; charset=utf-8"
        return resp

    flask.flash("Successfully %s the virtual machine" % command, "success")
    return flask.redirect(flask.url_for("instances.show", id=id))


@breadcrumbs('Types')
@dash(st='Types of',
         spu='focus2/img/small_flavors.png',
         bt='Types of instances',
         bpu='focus2/img/flavors.png',
         agt='Instances',
         wga=0,
         wgl=2,
         p=True,
         pw=2)
@BP.route('/types/')
def types():
    '''Types'''
    bh = utils_billing.BillingHelper(flask.g.api)
    return {
        "data": {
            "types": bh.calculate_cost(
                flask.g.api.instance_types.list()["instance-types"],
                bh.tariff_list()),
        }
    }


@BP.route('/types/<id>')
def types_show(id):
    '''Show type'''
    bh = utils_billing.BillingHelper(flask.g.api)
    return {
        "data": {
            "instance_type":
                bh.calculate_cost([flask.g.api.instance_types.get(id)],
                                  bh.tariff_list())[0],
        }
    }
