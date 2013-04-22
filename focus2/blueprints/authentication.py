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

from focus2.api import client
from focus2.api import exceptions
from focus2.utils import views

"""
========================
authentication blueprint
========================


"""


@views.view_metadata
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
            if not flask.g.api.me.check_credentials(auth=(
                    self.name.data, self.password.data)):
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
        return flask.redirect(flask.url_for("dashboard.index"))
    return locals()


@noauth
@BP.route('/recover/password/', methods=['GET', 'POST'])
def recover_password():
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        link_template = flask.url_for('.confirm_password', token='{{code}}')
        flask.g.api.me.reset_password(
            form.kind.data, form.identifier.data, link_template)
        flask.flash('Please check your email.', category='info')
        return flask.redirect(flask.request.path)
    form.identifier.placeholder = 'Registration email or login name'
    return {'form': form}


class RecoverPasswordForm(wtf.Form):
    password = wtf.PasswordField(
        'New password',
        validators=[wtf.Required(),
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
        success, reason = flask.g.api.me.apply_password_reset(
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
    flask.g.is_authenticated = False
    if (flask.request.endpoint is None or
            flask.request.endpoint == 'static'):
        return
    bp, ep = flask.request.endpoint.split('.')
    view = werkzeug.utils.import_string(
        'focus2.blueprints.%s:%s' % (bp, ep))
#    print 'VIEW: ', view
    if not (noauth.get(view) or flask.g.api.me.check_credentials()):
        return flask.redirect(
            flask.url_for('authentication.login'))
    flask.g.is_authenticated = True


@BP.app_errorhandler(exceptions.Forbidden)
def login_error(error):
    flask.flash('You are not logged in!', category='warning')
    return flask.redirect(flask.url_for('authentication.login'))
