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

import datetime
from functools import partial
import json

import flask
from flask import blueprints
from flask.ext import wtf
import werkzeug

from focus2.api import exceptions as api_exceptions

from focus2.blueprints.dashboard import dash as basedash
from focus2.blueprints.base import breadcrumbs, breadcrumb_button

from focus2.utils import forms
from focus2.utils import billing as utils_billing
from focus2.utils import pagination
from focus2.utils import search


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
        "instances": get_total(api.instances.list()["instances"]),
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

    stats = api.projects.get(id, "stats")
    network = api.networks.find(project=id)
    return {
        "data": {
            "project": stats["project"],
            "stats": stats,
            "network": network,
        },
    }


@dash(st='Firewall Rule Sets',
      spu='focus2/img/small_fw_rule_sets.png',
      bt='Firewall Rule Sets',
      bpu='focus2/img/fw_rule_sets.png',
      wgl=1)
@BP.route('/fw-rule-sets/')
def fw_rule_sets():
    api = flask.g.api
    api.fw_rule_sets.list()
    return {}


class FwRuleSetEditForm(wtf.Form):
    name = wtf.TextField("Name")
    description = wtf.TextField("Description")
    fw_rules = wtf.TextField("Rules")
    fw_deleted = wtf.TextField("Deleted")


@BP.route('/fw-rule-sets/<id>', methods=["GET", "POST"])
def fw_rule_sets_edit(id):
    api = flask.g.api
    form = FwRuleSetEditForm()
    fw_rule_set = api.fw_rule_sets.get(id)
    fw_rules = api.fw_rules(fw_rule_set_id=id).list()["rules"]
    if form.validate_on_submit():
        api_fw_rules = api.fw_rules(fw_rule_set_id=id)
        have_error = False
        try:
            fw_deleted = json.loads(form.fw_deleted.data)
            assert isinstance(fw_deleted, list)
        except:
            have_error = True
        else:
            for rule_id in fw_deleted:
                try:
                    api_fw_rules.delete(rule_id)
                except api_exceptions.AltaiApiException as ex:
                    have_error = True
                    flask.flash("Cannot delete firewall rule %s: %s" %
                                (rule_id, ex), "error")

        try:
            fw_rules = json.loads(form.fw_rules.data)
            assert isinstance(fw_deleted, list)
        except:
            have_error = True
        else:
            for rule in fw_rules:
                if "id" not in rule:
                    try:
                        api_fw_rules.create(rule)
                    except (ValueError,
                            api_exceptions.AltaiApiException) as ex:
                        have_error = True
                        flask.flash("Cannot create firewall rule: %s" %
                                    ex, "error")

        if not have_error:
            flask.flash("Successfully updated firewall rule set",
                        "success")
        return flask.redirect(flask.url_for(".fw_rule_sets"))
    else:
        form.name.data = fw_rule_set["name"]
        form.description.data = fw_rule_set["description"]
    return {
        "form": form,
        "data": {
            "fw_rule_set": fw_rule_set,
            "fw_rules": fw_rules,
        }
    }


@BP.route('/fw-rule-sets/<id>/<command>', methods=["POST"])
def fw_rule_sets_action(id, command):
    api = flask.g.api
    if command == "remove":
        fw_rule_set = api.fw_rule_sets.get(id)
        try:
            api.fw_rule_sets.delete(id)
        except api_exceptions.AltaiApiException as ex:
            flask.flash("Cannot delete %s: %s" %
                        (fw_rule_set["name"], ex),
                        "error")
        else:
            flask.flash("Successfully deleted %s" % fw_rule_set["name"],
                        "success")
            return flask.redirect(flask.url_for(".fw_rule_sets"))
        return flask.redirect(flask.request.path)
    flask.abort(404)


def billing_client():
    if not hasattr(flask.g, "billing_client"):
        from openstackclient_base.billing.client import BillingClient
        from openstackclient_base.client import HttpClient
        bc = BillingClient(
            HttpClient(endpoint=flask.current_app.config["BILLING_URL"],
                       token="unused"))
        flask.g.billing_client = bc
    return flask.g.billing_client


@dash(st='Billing',
      spu='focus2/img/small_billing.png',
      bt='Billing',
      bpu='focus2/img/billing.png',
      wgl=2)
@BP.route('/billing/')
def billing():
    bh = utils_billing.BillingHelper(flask.g.api, billing_client())
    if flask.request.args.get("api_marker"):
        perPage = int(flask.request.args['perPage'])
        page = int(flask.request.args['page'])
        date_range = flask.request.args['date_range'].split(" - ")
        for i in xrange(2):
            date_range[i] = datetime.datetime.strptime(
                    date_range[i], "%m.%d.%Y")
        date_range[1] = date_range[1] + datetime.timedelta(days=1)
        for i in xrange(2):
            date_range[i] = ("%sZ" % date_range[i].isoformat())
        resources = flask.request.args["resources"]
        if not resources:
            resources = ["nova/instance", "glance/image"]
        else:
            resources = resources.lower().split(",")
            tmp_res = []
            if "instances" in resources:
                tmp_res.append("nova/instance")
            if "images" in resources:
                tmp_res.append("glance/image")
            resources = tmp_res
        data = bh.report(period_start=date_range[0],
                         period_end=date_range[1])
        data = filter(lambda x: x["rtype"] in resources, data)
        paginator = pagination.Pagination(
            page, len(data), perPage, abort=False)
        data = bh.add_details(data[paginator.page_slice])
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
        "tariffs": bh.tariff_list(),
    }


@dash(st="Members",
      spu="focus2/img/small_members.png",
      bt="Members",
      bpu="focus2/img/members.png",
      wgl=3)
@BP.route("/members/")
def members():
    api = flask.g.api
    if flask.request.args.get("api_marker"):
        perPage = int(flask.request.args["perPage"])
        page = int(flask.request.args["page"])
        query = flask.request.args.get("query")
        data_filter = search.transform_search_query(query, "name:eq")
        projects = flask.request.args["projects"]
        if projects:
            project_by_name = dict((u["name"], u)
                                for u in api.projects.list()["projects"])
            project_ids = []
            for u in projects.split(","):
                try:
                    project_ids.append(project_by_name[u]["id"])
                except KeyError:
                    pass
            data_filter["projects:any"] = "|".join(project_ids)
        paginator = pagination.Pagination(
            page,
            api.users.list(
                filter=data_filter, limit=0)["collection"]["size"],
            perPage,
            abort=False)
        data = api.users.list(filter=data_filter,
                              limit=paginator.limit,
                              offset=paginator.offset)["users"]
        # filter my projects
        my_projects = set(
            (p["id"]
             for p in api.projects.list(
                    filter={"my-projects": True})["projects"]))
        for user in data:
            user["projects"] = filter(
                lambda p: p["id"] in my_projects, user["projects"])

        pages = list(paginator.iter_pages())
        current = paginator.page
        return flask.jsonify({
            "data": data,
            "pagination": {
                "pages": pages,
                "current": current,
            },
        })

    return {
        "data": {
            "projects": api.projects.list()["projects"],
        },
    }


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


# TODO: show human-readable audit messages and search their content
@dash(st='Audit',
      spu='focus2/img/small_audit.png',
      bt='Audit',
      bpu='focus2/img/audit.png',
      wgl=4)
@BP.route('/audit/')
def audit():
    api = flask.g.api
    if flask.request.args.get("api_marker"):
        perPage = int(flask.request.args['perPage'])
        page = int(flask.request.args['page'])
        date_range = flask.request.args['date_range'].split(" - ")
        for i in xrange(2):
            date_range[i] = datetime.datetime.strptime(
                    date_range[i], "%m.%d.%Y")
        date_range[1] = date_range[1] + datetime.timedelta(days=1)
        for i in xrange(2):
            date_range[i] = ("%sZ" % date_range[i].isoformat())
        data_filter = {
            "timestamp:ge": date_range[0],
            "timestamp:le": date_range[1],
        }
        users = flask.request.args["users"]
        if users:
            user_by_name = dict((u["name"], u)
                                for u in api.users.list()["users"])
            user_ids = []
            for u in users.split(","):
                try:
                    user_ids.append(user_by_name[u]["id"])
                except KeyError:
                    pass
            data_filter["user:in"] = "|".join(user_ids)
        paginator = pagination.Pagination(
            page,
            api.audit_log.list(
                filter=data_filter, limit=0)["collection"]["size"],
            perPage,
            abort=False)
        data = api.audit_log.list(filter=data_filter,
                                  limit=paginator.limit,
                                  offset=paginator.offset)["audit-log"]
        pages = list(paginator.iter_pages())
        current = paginator.page
        return flask.jsonify({
            "data": data,
            "pagination": {
                "pages": pages,
                "current": current,
            },
        })

    users = api.users.list()["users"]
    return {
        "data": {
            "users": users,
        },
    }


# TODO: make it configurable with Focus2 UI
def get_invitation_domains():
    return flask.current_app.config["INVITATION_DOMAINS"]


class InviteForm(wtf.Form):
    projects = wtf.SelectMultipleField("Projects", validators=[wtf.Required()])
    email = wtf.TextField("Email", validators=[wtf.Required(), wtf.Email()])

    def validate_email(self, field):
        if not self.errors and field.data:
            domains = get_invitation_domains()
            if field.data.split("@", 1)[1] not in domains:
                raise wtf.ValidationError("Domain is not allowed")


@dash(st='Invite',
      spu='focus2/img/small_invite.png',
      bt='Invite a Member',
      bpu='focus2/img/invite.png',
      wgl=5)
@BP.route('/invite/', methods=("GET", "POST"))
def invite():
    api = flask.g.api
    form = InviteForm()
    projects = api.projects.list(filter={"my-projects": True})["projects"]
    if form.is_submitted():
        form.projects.choices = [(p["id"], None) for p in projects]
        if form.validate():
            email = form.email.data
            try:
                user = api.users.find(email=email)
            except IndexError:
                user = api.users.create({
                    "email": email,
                    "projects": form.projects.data,
                    "invite": True,
                    "send-invite-mail": True,
                    "link-template": "%s{{code}}" % flask.url_for(
                            ".invite_accept", code="",
                            _external=True)
                })
                flask.flash("Successfully invited user %s" % email, "success")
                return flask.redirect(flask.request.path)
            else:
                # TODO: invite existing user when Altai API allows it
                flask.flash("Cannot invite user %s that already exists" %
                            email, "error")
    domains = get_invitation_domains()
    return {
        "form": form,
        "data": {
            "projects": projects,
            "domains": domains,
        },
    }


class InviteAcceptForm(wtf.Form):
    login = wtf.TextField(
        "Login",
        validators=[wtf.Required()])
    password = wtf.TextField(
        "Password",
        widget=wtf.widgets.PasswordInput(),
        validators=[wtf.Required(), wtf.Length(min=6)],
        default="")
    confirm = wtf.TextField(
        "Confirm",
        widget=wtf.widgets.PasswordInput(),
        validators=[wtf.Required(),
                    wtf.EqualTo("password", "Passwords must match")],
        default="")


@BP.route('/invite/accept/<code>', methods=("GET", "POST"))
def invite_accept(code):
    api = flask.g.api
    form = InviteAcceptForm()
    if form.validate_on_submit():
        try:
            api.invites.accept_invite(
                code, {
                    "password": form.password.data,
                    "name": form.login.data,
                })
        except api_exceptions.NotFound:
            flask.flash(
                "It seems that your invitation code is invalid or expired",
                "error")
        else:
            flask.flash("Successfully registered as %s"
                        % form.login.data, "success")
        return flask.redirect(flask.url_for("dashboard.index"))

    try:
        user = api.invites.get_user_by_code(code)
    except api_exceptions.NotFound:
        flask.flash(
            "It seems that your invitation code is invalid or expired",
            "error")
        return flask.redirect(flask.url_for("dashboard.index"))
    return {
        "form": form,
        "data": {
            "user": user,
        }
    }
