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

from focus2.blueprints.dashboard import dash as basedash

"""
==================
settings blueprint
==================


"""

BP = blueprints.Blueprint('settings', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/settings')


dash = partial(basedash, agt='Personal Settings', wga=3)


@dash(st='SSH Keys',
      spu='focus2/img/small_ssh_keys.png',
      bt='SSH Keys',
      bpu='focus2/img/ssh_keys.png',
      wgl=0)
@BP.route('/ssh-keys/')
def ssh_keys():
    api = flask.g.api
    ssh_keys = api.my_ssh_keys.list()["ssh-keys"]
    return {
        "data": {
            "ssh_keys": ssh_keys,
        },
    }


class SshKeyCreateForm(wtf.Form):
    name = wtf.TextField('Name', validators=[wtf.Required()])
    public_key = wtf.TextField('Public Key')


@BP.route('/ssh-keys/create/', methods=["GET", "POST"])
def ssh_keys_create():
    form = SshKeyCreateForm()
    api = flask.g.api
    if form.validate_on_submit():
        ssh_key_data = {
            "name": form.name.data,
            "public-key": form.public_key.data,
        }
        api.my_ssh_keys.create(ssh_key_data)
        return flask.redirect(flask.request.path)
    return {
        "form": form,
    }


@dash(st='Credentials',
      spu='focus2/img/small_credentials.jpg',
      bt='Credentials',
      bpu='focus2/img/credentials.jpg',
      wgl=1)
@BP.route('/credentials/')
def credentials():
    if "download" in flask.request.args:
        project = flask.request.args.get("project", "")
    else:
        project = "{{project}}"
    credentials_text = flask.render_template(
        "settings/credentials.txt",
        **{
            "username": flask.session["name"],
            "auth_url": "url",
            "project": project,
        }
    )
    if "download" in flask.request.args:
        response = flask.make_response(credentials_text)
        response.headers["Content-Disposition"] = \
            "attachment; filename=altai-rc-%s" % project
        response.headers["Content-Type"] = "text/plain"
        return response
    api = flask.g.api
    return {
        "data": {
            "projects": api.projects.list()["projects"],
        },
        "credentials_text": credentials_text,
    }


@dash(st='Notifications',
      spu='focus2/img/small_notifications.png',
      bt='Notifications',
      bpu='focus2/img/notifications.png',
      wgl=2)
@BP.route('/notifications/')
def notifications():
    return {}


@dash(st='Avatar',
      spu='focus2/img/small_avatar.png',
      bt='Avatar',
      bpu='focus2/img/avatar.png',
      wgl=3)
@BP.route('/avatar/')
def avatar():
    return {}


class ChangePasswordForm(wtf.Form):
    current = wtf.TextField(
        'Current',
        widget=wtf.widgets.PasswordInput(),
        validators=[wtf.Required()])
    new = wtf.TextField(
        'New',
        widget=wtf.widgets.PasswordInput(),
        validators=[wtf.Required()])
    confirm = wtf.TextField(
        'Confirm',
        widget=wtf.widgets.PasswordInput(),
        validators=[wtf.Required(),
                    wtf.EqualTo("new", "Passwords must match")])

    def validate_current(self, field):
        if (not self.errors and field.data and
            not flask.g.api.are_credentials_correct(
                flask.session["name"], self.current.data)):
            raise wtf.ValidationError("Incorrect password")


@dash(st='Change Password',
      spu='focus2/img/small_change_password.png',
      bt='Change Password',
      bpu='focus2/img/change_password.png',
      wgl=4)
@BP.route('/change-password/', methods=["GET", "POST"])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        api = flask.g.api
        user = api.users.list(
            filter={"name:eq": flask.session["name"]})["users"][0]
        api.users.update(user["id"], {"password": form.new.data})
        flask.session["password"] = form.new.data
        return flask.redirect(flask.request.path)
    return {
        "form": form,
    }
