#!/usr/bin/env python
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


"""
========================
authentication blueprint
========================


"""

BP = blueprints.Blueprint('authentication', __name__,
    static_folder='static', 
    template_folder='templates',
    url_prefix='/authentication/')


class LoginForm(wtf.Form):
    email = wtf.TextField('Email', validators=[wtf.Required()])
    password = wtf.PasswordField('Password', validators=[wtf.Required()])
    remember_me = wtf.BooleanField('Remember me')
    next_url = wtf.HiddenField()


@BP.route('login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # do login
        # redirect wherever he came
        pass
    return locals()
    

