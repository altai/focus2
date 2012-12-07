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
    

