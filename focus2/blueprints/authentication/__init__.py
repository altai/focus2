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

from focus2 import helpers, api

"""
========================
authentication blueprint
========================


"""


@helpers.view_metadata
def noauth():
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


class PasswordRecoveryForm(wtf.Form):
    identifier = wtf.TextField('Name or email', validators=[wtf.Required()])
    kind = wtf.RadioField('Name or email',
            choices=[('name', 'Name'), ('email', 'Email')])


@noauth
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


@noauth
@BP.route('/recover/password/', methods=['GET', 'POST'])
def recover_password():
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        link_template = flask.url_for('.confirm_password', token='{{code}}')
        flask.g.api.send_password_recovery_email(
                form.identifier.data, form.kind.data, link_template)
        flask.flash('Please check your email.', category='info')
        return flask.redirect(flask.request.path)
    form.identifier.placeholder = 'Registration email or login name'
    return {'form': form}


class RecoverPasswordForm(wtf.Form):
    password = wtf.PasswordField('New password', validators=[wtf.Required(),
            wtf.EqualTo('confirm_password',
                     'Field must be equal to "Confirm password"')])
    confirm_password = wtf.PasswordField('Confirm password',
            validators=[wtf.Required()])
    token = wtf.HiddenField(validators=[wtf.Required()])


@noauth
@BP.route('/recover/password/confirm/<token>/', methods=['GET', 'POST'])
def confirm_password(token):
    form = RecoverPasswordForm()
    if form.validate_on_submit():
        success, reason = flask.g.api.confirm_password_recovery(
                form.token.data, form.password.data)
        if success:
            flask.flash('Your password was updated', 'success')
            return flask.redirect(flask.url_for('authentication.login'))
        else:
            flask.flash(reason, 'error')

    form.token.data = token
    return {'form': form}


@noauth
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
            if not noauth.get(view):
                if not flask.g.api.are_credentials_correct():
                    return flask.redirect(
                        flask.url_for('authentication.login'))


@BP.app_errorhandler(api.LoginException)
def login_error(error):
    flask.flash('You are not logged in!', category='warning')
    return flask.redirect(flask.url_for('authentication.login'))
