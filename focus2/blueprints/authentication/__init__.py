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
from flask.ext import wtf
import werkzeug.utils

from focus2 import helpers

"""
========================
authentication blueprint
========================


"""


@helpers.protocol
def exempt():
    """Decorate view to omit authentication."""
    return True


BP = blueprints.Blueprint('authentication', __name__,
                          static_folder='static',
                          template_folder='templates',
                          url_prefix='/authentication')


class LoginForm(wtf.Form):
    name = wtf.TextField('Name', validators=[wtf.Required()])
    password = wtf.PasswordField('Password', validators=[wtf.Required()])
    remember_me = wtf.BooleanField('Remember me')
    next_url = wtf.HiddenField()

    def validate_password(self, field):
        if not self.errors and self.name.data and field.data:
            if not flask.g.api.are_credentials_correct(self.name.data,
                                                       self.password.data):
                raise wtf.ValidationError('Invalid credentials')


class DestinationForm(wtf.Form):
    email = wtf.TextField('Email', validators=[wtf.Required()])


@exempt
@BP.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flask.session.clear()
        flask.session.permanent = form.remember_me.data
        flask.session['name'] = form.name.data
        flask.session['password'] = form.password.data
        return flask.redirect('/')
    return locals()


@exempt
@BP.route('/recover/password/', methods=['GET', 'POST'])
def recover_password():
    form = DestinationForm()
    if form.validate_on_submit():
        pass
    return locals()


@exempt
@BP.route('/recover/name/', methods=['GET', 'POST'])
def recover_name():
    form = DestinationForm()
    if form.validate_on_submit():
        pass
    return locals()


@exempt
@BP.route('/logout/')
def logout():
    flask.session.clear()
    flask.flash('You were logged out', 'success')
    return flask.redirect(flask.url_for('.login'))


@BP.route('/protection_check/')
def protection_check():
    return "OK"


@BP.before_app_request
def run_authentication_check(*args, **kwargs):
    if flask.request.endpoint is not None:
        # None is possible for nonexisting URL
        bp, ep = flask.request.endpoint.split('.')
        if ep != 'static':
            view = werkzeug.utils.import_string(
                'focus2.blueprints.%s:%s' % (bp, ep))
            protocols = getattr(view, 'protocols', {})
            authentication_protocol = protocols.get('authentication', {})
            if not authentication_protocol.get('exempt', False):
                if not flask.g.api.are_credentials_correct():
                    return flask.redirect(
                        flask.url_for('authentication.login'))
