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
from flask.ext import wtf
import werkzeug

from focus2.api import exceptions as api_exceptions

from focus2.blueprints.dashboard import dash as basedash
from focus2.blueprints.base import breadcrumbs, breadcrumb_button
from focus2.utils import search, pagination, forms


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

    stats = api.projects.get(id, "stats")
    network = api.networks.find(project=id)
    return {
        "data": {
            "project": stats["project"],
            "stats": stats,
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
    api = flask.g.api
    l = api.audit_log.list()
    query = flask.request.args.get("q", "")
    deconstruct = None  # search.transform_search_query(query, "name:eq")
    r = api.audit_log.list(filter=deconstruct, limit=0)
    try:
        p = pagination.Pagination(1, r["collection"]["size"])
    except werkzeug.exceptions.NotFound:
        paginator = None
        data = []
    else:
        r = api.audit_log.list(
            filter=deconstruct, limit=p.limit, offset=p.offset)
        paginator = pagination.Pagination(1, r["collection"]["size"])
        data = r["audit-log"]

    return {
        "query": query,
        "deconstruct": deconstruct,
        "data": data,
        "paginator": paginator,
        "predefined_searches": [
            {"title": "My VMs", "url": flask.request.path + "?my"},
        ] + [
            {"title": x["name"],
             "url": flask.request.path + "?project_id=" + x["id"]} for x
            in flask.g.api.projects.list()["projects"]
        ],
        "user_searches": flask.session.get("user_searches", []),
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
